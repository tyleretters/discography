#!/usr/bin/env python3

'''
convert the yml to json.

see README.md for more information.
'''

import os
import yaml
import json
import re
import hashlib
from datetime import datetime

cdn_base_url = "https://d107e1o0dn11sc.cloudfront.net/"
dir_path = os.path.dirname(os.path.realpath(__file__))
yml_path = dir_path + "/" + "discography.yml"
ts_path = dir_path + "/" + "discography.ts"

special_slug_maps = {
  "ΑΙΓΑΙΙΣ": "AIGAIIS",
  "nausicaä": "nausicaa"
}

# there are some encoding issues with the # character
special_title_maps = {
  'A White USB Drive With "HEXAGON" iStock Logo #1135496271': 'A White USB Drive With "HEXAGON" iStock Logo &num;1135496271'
}

def make_id(str):
  md5_hash = hashlib.md5()
  md5_hash.update(str.encode("utf-8"))
  return md5_hash.hexdigest()

def make_slug(str):
  if str in special_slug_maps:
    str = special_slug_maps[str]
  str = str.lower()
  # convert & to and
  str = re.sub(r'&', 'and', str)
  # only alphanumeric characters, spaces, and hyphens
  str = re.sub(r'[^a-zA-Z0-9\s-]', '', str)
  # replace spaces with hyphens
  str = re.sub(r'\s+', '-', str)
  # replace multiple hyphens with single hyphen
  str = re.sub(r'--+', '-', str)
  return str

def make_track_title(str):
  if str in special_title_maps:
    return special_title_maps[str]
  return str

def make_html_paragraphs(str):
  str = str.rstrip("\n")
  str = "<p>" + str + "</p>"
  str = str.replace("\n", "</p><p>")
  return str

# load data
with open(yml_path, "r") as yml_file:
  data = yaml.safe_load(yml_file)

# enrich data
for release in data:
  # generate a project slug
  release["project_slug"] = make_slug(release["project"])

  # generate a release slug
  release["release_slug"] = make_slug(release["title"])

  # generate a cover
  release["cover_url"] =  cdn_base_url + release["project_slug"] + "/" + release["release_slug"] + "/" + release["release_slug"] + ".jpg"

  # generate an mp3 and wav download links
  zip_slug = cdn_base_url + release["project_slug"] + "/" + release["release_slug"] + "/" + release["release_slug"]

  if (release["mp3"]):
    release["mp3_url"] = zip_slug + "-mp3.zip"

  # generate a wave download link
  if (release["wav"]):
    release["wav_url"] = zip_slug + "-wav.zip"

  # generate an id
  release["id"] = make_id(release["project"] + release["title"])

  # handle monospaced notes if monospaceNotes is present
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
      slug = make_slug(str(track["number"]).zfill(2) + "-" + track["title"]) # zero pad track number
      track_slug = release["project_slug"] + "/" + release["release_slug"] + "/" + slug
      if (release["mp3"]):
        track["mp3_url"] =  cdn_base_url + track_slug + ".mp3"

      if (release["wav"]):
        track["wav_url"] =  cdn_base_url + track_slug + ".wav"

      # generate an id (ARTIST + RELEASE + NUMBER + TITLE + LENGTH)
      track["id"] = make_id(release["project"] + release["title"] + str(track["number"]) + track["title"] + track["length"])

      # generate a track title
      track["title"] = make_track_title(track["title"])

  # generate an id for each stream
  if "streams" in release:
    for stream in release["streams"]:
      stream["id"] = make_id(release["project"] + release["title"] + stream["platform"])

# write discography data
with open(ts_path, "w") as json_file:
  json.dump(data, json_file, indent=2)

# make it a js export
with open(ts_path, "r") as file:
  existing_contents = file.read()

with open(ts_path, "w") as file:
  new_string = "export const discography = "
  file.write(new_string)
  file.write(existing_contents)