#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color_info(s):
  return bcolors.HEADER + str(s) + bcolors.ENDC

def color_warn(s):
  return bcolors.WARNING + str(s) + bcolors.ENDC

def color_fail(s):
  return bcolors.FAIL + str(s) + bcolors.ENDC

def color_ok(s):
  return bcolors.OKGREEN + str(s) + bcolors.ENDC

def extract_video_name(dir):
  return os.path.basename(os.path.normpath(dir))

def extract_video_fps(dir):
  return int(extract_video_name(dir).split("-")[-1])

def add_suffix_to_basename(path, suffix):
  base_path, base_name = os.path.split(os.path.normpath(path))
  name, ext = os.path.splitext(base_name)
  return os.path.join(base_path, name + suffix + ext)
