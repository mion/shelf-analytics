#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Transcode a video file before splitting it into frames."""

import argparse
import subprocess
import shutil
import sys
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


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("video_path", help="input video file path")
  parser.add_argument("output_dir_path", help="output directory where a bundle will be created")
  parser.add_argument("--fps", default=10, type=int, help="frames per second for output video")
  args = parser.parse_args()

  if not has_ffmpeg_installed():
    print(red("ERROR: could not find 'ffmpeg' executable"))
    sys.exit(1)
  
  orig_video_filename = extract_video_name(args.video_path)
  final_video_filename = add_fps_suffix(orig_video_filename, args.fps)

  final_video_name, _ = os.path.splitext(final_video_filename)
  bundle_path = os.path.join(args.output_dir_path, final_video_name)

  if os.path.exists(bundle_path):
    print(red("ERROR: a directory already exists at ") + bundle_path)
    sys.exit(1)
  else:
    os.mkdir(bundle_path)

  print(yellow("Final video name with FPS suffix: ") + final_video_filename)
  print("Transcoding...")
  success = transcode(args.video_path, bundle_path, args.fps)
  if success:
    print(green("Done! Bundle created: ") + bundle_path)
    sys.exit(0)
  else:
    print(red("ERROR: failed to transcode video"))
    sys.exit(1)
