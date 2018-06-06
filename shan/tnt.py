#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os
import shutil
import json

DEFAULT_TRANSCODED_VIDEO_NAME = "video"

def has_ffmpeg_installed():
  return shutil.which("ffmpeg") != None

def extract_video_name(path):
  return os.path.basename(os.path.normpath(path))

def extract_video_fps(dir):
  return int(extract_video_name(dir).split("-")[-1])

def add_suffix_to_basename(path, suffix):
  base_path, base_name = os.path.split(os.path.normpath(path))
  name, ext = os.path.splitext(base_name)
  return os.path.join(base_path, name + suffix + ext)

def load_json(path):
  with open(path, "r") as tags_file:
    return json.loads(tags_file.read())