#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Transcode a video file before splitting it into frames."""

import argparse
import subprocess
import shutil
import os

from colorize import red, green, yellow, header

def has_ffmpeg_installed():
  return shutil.which("ffmpeg") != None

def transcode(input_path, output_dir, fps):
  # https://stackoverflow.com/questions/11004137/re-sampling-h264-video-to-reduce-frame-rate-while-maintaining-high-image-quality
  _, input_name = os.path.split(input_path)
  name, ext = os.path.splitext(input_name)
  output_name = str.join("-", [name, "fps", str(fps)]) + ext
  output_path = os.path.join(output_dir, output_name)
  cmd_template = "ffmpeg -i {0} -r {1} -c:v libx264 -b:v 3M -strict -2 -movflags faststart {2}" 
  #
  # [!] WARNING: shell=True is dangerous
  #
  result = subprocess.call(cmd_template.format(input_path, fps, output_path), shell=True)
  return result == 0

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("video_path", help="input video file path")
  parser.add_argument("output_dir_path", help="output directory")
  parser.add_argument("--fps", default=10, type=int, help="frames per second for output video")
  args = parser.parse_args()

  if has_ffmpeg_installed():
    print(yellow("Input video: ") + args.video_path)
    print(yellow("Output directory: ") + args.output_dir_path)
    print(yellow("Output video FPS: ") + str(args.fps))
    print("Transcoding...")
    success = transcode(args.video_path, args.output_dir_path, args.fps)
    if success:
      print(green("Done!"))
    else:
      print(red("ERROR: failed to transcode video"))
  else:
    print(red("ERROR: could not find 'ffmpeg' executable"))
