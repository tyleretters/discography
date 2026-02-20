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

def make_id(text):
  md5_hash = hashlib.md5()
  md5_hash.update(text.encode("utf-8"))
  return md5_hash.hexdigest()

def make_slug(text):
  if text in SPECIAL_SLUG_MAPS:
    text = SPECIAL_SLUG_MAPS[text]
  text = text.lower()
  # convert & to and
  text = re.sub(r'&', 'and', text)
  # only alphanumeric characters, spaces, and hyphens
  text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
  # replace spaces with hyphens
  text = re.sub(r'\s+', '-', text)
  # replace multiple hyphens with single hyphen
  text = re.sub(r'--+', '-', text)
  return text

def make_track_title(text):
  if text in SPECIAL_TITLE_MAPS:
    return SPECIAL_TITLE_MAPS[text]
  return text

def parse_length_seconds(length_str):
  """Parse a track length string (HH:MM:SS or MM:SS) into total seconds."""
  parts = length_str.split(":")
  if len(parts) == 3:
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
  elif len(parts) == 2:
    return int(parts[0]) * 60 + int(parts[1])
  return 0

def format_runtime(total_seconds):
  """Format total seconds as HH:MM:SS, omitting hours if under one hour."""
  hours = total_seconds // 3600
  minutes = (total_seconds % 3600) // 60
  seconds = total_seconds % 60
  if hours > 0:
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
  return f"{minutes:02d}:{seconds:02d}"

def make_html_paragraphs(text):
  text = text.rstrip("\n")
  text = "<p>" + text + "</p>"
  text = text.replace("\n", "</p><p>")
  return text

def main():
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
  for release in data:
    # validate required fields
    required_fields = ["project", "title", "mp3", "wav", "notes", "credits"]
    for field in required_fields:
      if field not in release:
        print(f"Error: Release missing required field '{field}': {release.get('title', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    # generate a project slug
    release["project_slug"] = make_slug(release["project"])

    # generate a release slug (use explicit slug if provided)
    release["release_slug"] = release.get("slug") or make_slug(release["title"])

    # generate a cover
    release["cover_url"] = CDN_BASE_URL + release["project_slug"] + "/" + release["release_slug"] + "/" + release["release_slug"] + ".jpg"

    # generate an mp3 and wav download links
    zip_slug = CDN_BASE_URL + release["project_slug"] + "/" + release["release_slug"] + "/" + release["release_slug"]

    if release["mp3"]:
      release["mp3_url"] = zip_slug + "-mp3.zip"

    # generate a wave download link
    if release["wav"]:
      release["wav_url"] = zip_slug + "-wav.zip"

    # generate an id
    release["id"] = make_id(release["project"] + release["title"])

    # handle monospaced notes if monospaceNotes is present
    if release["notes"] is not None:
      if "monospaceNotes" in release:
        # preserve \n for monospace
        release["notes"] = "<pre>" + release["notes"] + "</pre>"
      else:
        release["notes"] = make_html_paragraphs(release["notes"])

    # always turn turn \n into paragraphs on the credits
    release["credits"] = make_html_paragraphs(release["credits"])


    # generate a slug for each track
    if "tracks" in release:
      for track in release["tracks"]:

        # generate a track slugs for available formats
        # outcome example: project-title/release-title/01-track-title.mp3
        track_title_slug = track.get("slug") or make_slug(track["title"])
        slug = str(track["number"]).zfill(2) + "-" + track_title_slug
        track_slug = release["project_slug"] + "/" + release["release_slug"] + "/" + slug
        if release["mp3"]:
          track["mp3_url"] = CDN_BASE_URL + track_slug + ".mp3"

        if release["wav"]:
          track["wav_url"] = CDN_BASE_URL + track_slug + ".wav"

        # generate an id (ARTIST + RELEASE + NUMBER + TITLE + LENGTH)
        track["id"] = make_id(release["project"] + release["title"] + str(track["number"]) + track["title"] + track["length"])

        # generate a track title
        track["title"] = make_track_title(track["title"])

    # calculate runtime as sum of all track lengths
    if "tracks" in release:
      total_seconds = sum(parse_length_seconds(track["length"]) for track in release["tracks"])
      release["runtime"] = format_runtime(total_seconds)

    # generate an id for each stream
    if "streams" in release:
      for stream in release["streams"]:
        stream["id"] = make_id(release["project"] + release["title"] + stream["platform"])

  # write discography data as TypeScript export in one pass
  try:
    with open(TS_PATH, "w") as ts_file:
      ts_file.write("export const discography = ")
      json.dump(data, ts_file, indent=2)
  except OSError as e:
    print(f"Error: Could not write to {TS_PATH}: {e}", file=sys.stderr)
    sys.exit(1)

  print(f"Successfully converted {len(data)} releases to {TS_PATH}")

if __name__ == "__main__":
  main()
