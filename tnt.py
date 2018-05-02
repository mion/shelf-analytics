#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os
import shutil

def has_ffmpeg_installed():
  return shutil.which("ffmpeg") != None

def extract_video_name(dir):
  return os.path.basename(os.path.normpath(dir))

def extract_video_fps(dir):
  return int(extract_video_name(dir).split("-")[-1])

def add_suffix_to_basename(path, suffix):
  base_path, base_name = os.path.split(os.path.normpath(path))
  name, ext = os.path.splitext(base_name)
  return os.path.join(base_path, name + suffix + ext)
