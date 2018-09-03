"""
Shelf Analytics
Transcode a video file using a ffmpeg subprocess.

Copyright (c) 2018 TonetoLabs.
Author: Gabriel Luis Vieira (gluisvieira@gmail.com)
"""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))
import subprocess

from tnt import has_ffmpeg_installed

def transcode(input_video_path, output_video_path, fps):
  if not has_ffmpeg_installed():
    raise RuntimeError('ffmpeg is not installed')
  # About the ffmpeg command: 
  # https://stackoverflow.com/questions/11004137/re-sampling-h264-video-to-reduce-frame-rate-while-maintaining-high-image-quality
  cmd_template = "ffmpeg -i {0} -r {1} -c:v libx264 -b:v 3M -strict -2 -movflags faststart {2}" 
  cmd = cmd_template.format(input_video_path, fps, output_video_path)
  # FIXME: using 'subprocess.call' with shell=True is not secure, search Python 3 docs for explanation.
  result = subprocess.call(cmd, shell=True)
  return result == 0

def generate_thumbnail(input_video_path, output_image_path, width, height):
  if not has_ffmpeg_installed():
    raise RuntimeError('ffmpeg is not installed')
  # About the ffmpeg command: 
  # https://networking.ringofsaturn.com/Unix/extractthumbnail.php
  cmd_template = "ffmpeg -i {0} -vframes 1 -an -s {1}x{2} -ss 1 {3}"
  cmd = cmd_template.format(input_video_path, width, height, output_image_path)
  # FIXME: using 'subprocess.call' with shell=True is not secure, search Python 3 docs for explanation.
  result = subprocess.call(cmd, shell=True)
  return result == 0
