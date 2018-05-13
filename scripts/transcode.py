#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Transcode a video file before splitting it into frames."""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import subprocess
import shutil

from colorize import red, green, yellow, header
from tnt import extract_video_name, has_ffmpeg_installed, DEFAULT_TRANSCODED_VIDEO_NAME


def add_fps_suffix(video_filename, fps):
  video_name, video_ext = os.path.splitext(video_filename)
  return video_name + "-fps-" + str(fps) + video_ext


def transcode(input_video_path, output_dir_path, fps):
  orig_video_filename = extract_video_name(input_video_path)
  final_video_filename = add_fps_suffix(orig_video_filename, fps)
  output_path = os.path.join(output_dir_path, final_video_filename)
  # https://stackoverflow.com/questions/11004137/re-sampling-h264-video-to-reduce-frame-rate-while-maintaining-high-image-quality
  cmd_template = "ffmpeg -i {0} -r {1} -c:v libx264 -b:v 3M -strict -2 -movflags faststart {2}" 
  # [!] WARNING: shell=True is not secure.
  result = subprocess.call(cmd_template.format(input_video_path, fps, output_path), shell=True)
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
  
  print("Transcoding...")
  success = transcode(args.video_path, args.output_dir_path, args.fps)
  if success:
    print(green("SUCCESS: transcoded video file saved in output directory."))
    sys.exit(0)
  else:
    print(red("ERROR: failed to transcode video"))
    sys.exit(1)
