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

special_maps = {
  "ΑΙΓΑΙΙΣ": "AIGAIIS",
  "nausicaä": "nausicaa"
}

dir_path = os.path.dirname(os.path.realpath(__file__))

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
  return str

# load data
with open(dir_path + "/data.yml", "r") as yml_file:
  data = yaml.safe_load(yml_file)

# enrich data
for release in data:
  # generate a release slug
  release["release_slug"] = make_slug(release["title"])

  # generate a project slug
  release["project_slug"] = make_slug(release["project"])

  # generate an id
  release["id"] = make_id(release["project"] + release["title"])

  # generate a slug for each track
  if "tracks" in release:
    for track in release["tracks"]:

      # generate a track slug
      track["track_slug"] = make_slug(track["title"])

      # generate an id (ARTIST + RELEASE + NUMBER + TITLE + LENGTH)
      track["id"] = make_id(release["project"] + release["title"] + str(track["number"]) + track["title"] + track["length"])

# write data
with open(dir_path + "/../dist/data.json", "w") as json_file:
  json.dump(data, json_file, indent=2)