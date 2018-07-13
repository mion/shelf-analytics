#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Split a video file into many images."""

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import subprocess
import shutil

from colorize import red, green, yellow, header
from tnt import extract_video_name, has_ffmpeg_installed, DEFAULT_TRANSCODED_VIDEO_NAME


def split_frames(input_path, output_dir, ext):
  frame_number_format = '%07d' # FIXME count total number of frames beforehand
  output_path = os.path.join(output_dir, "frame-{0}.{1}".format(frame_number_format, ext))
  cmd_template = "ffmpeg -i {0} {1} -hide_banner"
  # [!] WARNING: shell=True is dangerous
  cmd = cmd_template.format(input_path, output_path)
  result = subprocess.call(cmd, shell=True)
  return result == 0


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("input_path", help="input video file path")
  parser.add_argument("output_dir", help="output directory")
  parser.add_argument("--ext", default="all", help="frame image file extension: 'png', 'jpg' or 'all' (default)")
  args = parser.parse_args()

  if has_ffmpeg_installed():
    success = False
    if args.ext == 'all':
      success = split_frames(args.input_path, args.output_dir, 'png')
      success = split_frames(args.input_path, args.output_dir, 'jpg')
    else:
      success = split_frames(args.input_path, args.output_dir, args.ext)
    if success:
      print(green("DONE! Image files created in output directory."))
    else:
      print(red("ERROR: failed to split video into frames"))
  else:
    print(red("ERROR: could not find 'ffmpeg' executable"))
