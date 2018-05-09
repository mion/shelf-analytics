"""
Transcode video files using a ffmpeg subprocess.

Copyright (c) 2018 TonetoLabs. All rights reserved.
Written by Gabriel Vieira
"""
import sys
import subprocess
import os

from colorize import red, green, yellow, header
from tnt import extract_video_name, has_ffmpeg_installed, DEFAULT_TRANSCODED_VIDEO_NAME


def add_fps_suffix(video_filename, fps):
  video_name, video_ext = os.path.splitext(video_filename)
  return video_name + "-fps-" + str(fps) + video_ext


def transcode(video_path, bundle_path, fps):
  # https://stackoverflow.com/questions/11004137/re-sampling-h264-video-to-reduce-frame-rate-while-maintaining-high-image-quality
  _, ext = os.path.splitext(video_path)
  output_path = os.path.join(bundle_path, DEFAULT_TRANSCODED_VIDEO_NAME + ext)
  cmd_template = "ffmpeg -i {0} -r {1} -c:v libx264 -b:v 3M -strict -2 -movflags faststart {2}" 
  # [!] WARNING: shell=True is not secure.
  result = subprocess.call(cmd_template.format(video_path, fps, output_path), shell=True)
  return result == 0
