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

def color_warn(s):
  return bcolors.WARNING + s + bcolors.ENDC

def color_fail(s):
  return bcolors.FAIL + s + bcolors.ENDC

def color_ok(s):
  return bcolors.OKGREEN + s + bcolors.ENDC

def extract_video_name(dir):
  return os.path.basename(os.path.normpath(dir))

def extract_video_fps(dir):
  return int(extract_video_name(dir).split("-")[-1])