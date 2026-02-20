#!/usr/bin/env python3

'''
convert the yml to json.

see README.md for more information.
'''

import hashlib
import json
import os
import re
import sys
from typing import Any

import yaml

CDN_BASE_URL = "https://d107e1o0dn11sc.cloudfront.net/"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
YML_PATH = os.path.join(DIR_PATH, "discography.yml")
TS_PATH = os.path.join(DIR_PATH, "discography.ts")

SPECIAL_SLUG_MAPS = {
  "ΑΙΓΑΙΙΣ": "AIGAIIS",
  "ＤＲＥＡＭＲＯＡＤ": "dreamroad",
  "nausicaä": "nausicaa",
}

# there are some encoding issues with the # character
SPECIAL_TITLE_MAPS = {
  'A White USB Drive With "HEXAGON" iStock Logo #1135496271': 'A White USB Drive With "HEXAGON" iStock Logo &num;1135496271'
}

VALID_TYPES = {"Mix", "LP", "EP", "Single", "OST", "Compilation", "Triple LP", "Demo"}
VALID_FORMATS = {"Digital", "CD-R", "Vinyl", "CD", "CD, Digital", "Cassette, Digital"}
VALID_ROLES = {"DJ", "Artist", "Producer", "Musician", "Band Member", "Principal Musician", "Operator"}


def make_id(text: str) -> str:
  return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_slug(text: str) -> str:
  if text in SPECIAL_SLUG_MAPS:
    text = SPECIAL_SLUG_MAPS[text]
  text = text.lower()
  # convert & to and
  text = re.sub(r'&', 'and', text)
  # only alphanumeric characters, spaces, and hyphens
  text = re.sub(r'[^a-z0-9\s-]', '', text)
  # replace spaces with hyphens
  text = re.sub(r'\s+', '-', text)
  # replace multiple hyphens with single hyphen
  text = re.sub(r'--+', '-', text)
  return text


def make_track_title(text: str) -> str:
  if text in SPECIAL_TITLE_MAPS:
    return SPECIAL_TITLE_MAPS[text]
  return text


def parse_length_seconds(length_str: str) -> int:
  """Parse a track length string (HH:MM:SS or MM:SS) into total seconds."""
  parts = length_str.split(":")
  if len(parts) == 3:
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
  elif len(parts) == 2:
    return int(parts[0]) * 60 + int(parts[1])
  return 0


def format_runtime(total_seconds: int) -> str:
  """Format total seconds as HH:MM:SS, omitting hours if under one hour."""
  hours = total_seconds // 3600
  minutes = (total_seconds % 3600) // 60
  seconds = total_seconds % 60
  if hours > 0:
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
  return f"{minutes:02d}:{seconds:02d}"


def make_html_paragraphs(text: str) -> str:
  text = text.rstrip("\n")
  text = "<p>" + text + "</p>"
  text = text.replace("\n", "</p><p>")
  return text


def cdn_path(project_slug: str, release_slug: str) -> str:
  """Build the CDN base path for a release."""
  return f"{CDN_BASE_URL}{project_slug}/{release_slug}"


def validate_release(release: dict[str, Any]) -> None:
  """Validate required fields and field values for a release."""
  title = release.get("title", "unknown")

  required_fields = ["project", "title", "type", "format", "role", "mp3", "wav", "notes", "credits"]
  for field in required_fields:
    if field not in release:
      raise ValueError(f"Release missing required field '{field}': {title}")

  if release["type"] not in VALID_TYPES:
    raise ValueError(f"Release '{title}' has invalid type '{release['type']}'. Valid: {sorted(VALID_TYPES)}")

  if release["format"] not in VALID_FORMATS:
    raise ValueError(f"Release '{title}' has invalid format '{release['format']}'. Valid: {sorted(VALID_FORMATS)}")

  if release["role"] not in VALID_ROLES:
    raise ValueError(f"Release '{title}' has invalid role '{release['role']}'. Valid: {sorted(VALID_ROLES)}")

  if not isinstance(release["mp3"], bool):
    raise ValueError(f"Release '{title}' has non-boolean mp3: {release['mp3']!r}")

  if not isinstance(release["wav"], bool):
    raise ValueError(f"Release '{title}' has non-boolean wav: {release['wav']!r}")


def enrich_release(release: dict[str, Any]) -> dict[str, Any]:
  """Enrich a release with generated slugs, URLs, IDs, and HTML formatting."""
  validate_release(release)

  project_slug = make_slug(release["project"])
  release_slug = release.get("slug") or make_slug(release["title"])
  base = cdn_path(project_slug, release_slug)

  release["project_slug"] = project_slug
  release["release_slug"] = release_slug
  release["cover_url"] = f"{base}/{release_slug}.jpg"

  if release["mp3"]:
    release["mp3_url"] = f"{base}/{release_slug}-mp3.zip"

  if release["wav"]:
    release["wav_url"] = f"{base}/{release_slug}-wav.zip"

  release["id"] = make_id(release["project"] + release["title"])

  # format notes as HTML
  if release["notes"] is not None:
    if "monospaceNotes" in release:
      release["notes"] = "<pre>" + release["notes"] + "</pre>"
    else:
      release["notes"] = make_html_paragraphs(release["notes"])

  # always turn \n into paragraphs on the credits
  release["credits"] = make_html_paragraphs(release["credits"])

  # enrich tracks
  if "tracks" in release:
    for track in release["tracks"]:
      track_title_slug = track.get("slug") or make_slug(track["title"])
      slug = str(track["number"]).zfill(2) + "-" + track_title_slug
      track_base = f"{base}/{slug}"

      if release["mp3"]:
        track["mp3_url"] = track_base + ".mp3"

      if release["wav"]:
        track["wav_url"] = track_base + ".wav"

      track["id"] = make_id(release["project"] + release["title"] + str(track["number"]) + track["title"] + track["length"])
      track["title"] = make_track_title(track["title"])

  # calculate runtime as sum of all track lengths
  if "tracks" in release:
    total_seconds = sum(parse_length_seconds(track["length"]) for track in release["tracks"])
    release["runtime"] = format_runtime(total_seconds)

  # generate an id for each stream
  if "streams" in release:
    for stream in release["streams"]:
      stream["id"] = make_id(release["project"] + release["title"] + stream["platform"])

  return release


def main() -> None:
  # load data
  try:
    with open(YML_PATH) as yml_file:
      data = yaml.safe_load(yml_file)
  except FileNotFoundError:
    print(f"Error: Could not find {YML_PATH}", file=sys.stderr)
    sys.exit(1)
  except yaml.YAMLError as e:
    print(f"Error: Invalid YAML in {YML_PATH}: {e}", file=sys.stderr)
    sys.exit(1)

  if not data:
    print("Error: No data found in YAML file", file=sys.stderr)
    sys.exit(1)

  # enrich data
  try:
    enriched = [enrich_release(release) for release in data]
  except ValueError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

  # write discography data as TypeScript export
  try:
    with open(TS_PATH, "w") as ts_file:
      ts_file.write("export const discography = ")
      json.dump(enriched, ts_file, indent=2)
  except OSError as e:
    print(f"Error: Could not write to {TS_PATH}: {e}", file=sys.stderr)
    sys.exit(1)

  print(f"Successfully converted {len(enriched)} releases to {TS_PATH}")

if __name__ == "__main__":
  main()
