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

s3_bucket = "https://intertext.s3.us-west-1.amazonaws.com/"
dir_path = os.path.dirname(os.path.realpath(__file__))
yml_path = dir_path + "/" + "discography.yml"
ts_path = dir_path + "/" + "discography.ts"

special_maps = {
  "ΑΙΓΑΙΙΣ": "AIGAIIS",
  "nausicaä": "nausicaa"
}

def make_id(str):
  md5_hash = hashlib.md5()
  md5_hash.update(str.encode("utf-8"))
  return md5_hash.hexdigest()

def make_slug(str):
  if str in special_maps:
    str = special_maps[str]
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
  release["cover_url"] =  s3_bucket + release["project_slug"] + "/" + release["release_slug"] + "/" + release["release_slug"] + ".jpg"

  # generate an id
  release["id"] = make_id(release["project"] + release["title"])

  # generate a slug for each track
  if "tracks" in release:
    for track in release["tracks"]:

      # generate a track slugs for available formats
      # outcome example: project-title/release-title/01-track-title.mp3
      slug = make_slug(str(track["number"]).zfill(2) + "-" + track["title"]) # zero pad track number
      track_slug = release["project_slug"] + "/" + release["release_slug"] + "/" + slug
      if (release["mp3"]):
        track["mp3_url"] =  s3_bucket + track_slug + ".mp3"

      if (release["wav"]):
        track["wav_url"] =  s3_bucket + track_slug + ".wav"

      # generate an id (ARTIST + RELEASE + NUMBER + TITLE + LENGTH)
      track["id"] = make_id(release["project"] + release["title"] + str(track["number"]) + track["title"] + track["length"])

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