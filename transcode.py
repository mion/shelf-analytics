#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Transcode a video file before splitting it into frames."""

import argparse
import subprocess
import shutil
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
  parser.add_argument("input_path", help="input video file path")
  parser.add_argument("output_dir", help="output directory")
  parser.add_argument("--fps", default=10, type=int, help="frames per second for output video")
  args = parser.parse_args()

  if has_ffmpeg_installed():
    print(bcolors.WARNING + "Input video: " + bcolors.ENDC + args.input_path)
    print(bcolors.WARNING + "Output directory: " + bcolors.ENDC + args.output_dir)
    print(bcolors.WARNING + "Output video FPS: " + bcolors.ENDC + str(args.fps))
    print("Transcoding...")
    success = transcode(args.input_path, args.output_dir, args.fps)
    if success:
      print(bcolors.OKGREEN + "Done!" + bcolors.ENDC)
    else:
      print(bcolors.FAIL + "ERROR: failed to transcode video" + bcolors.ENDC)
  else:
    print(bcolors.FAIL + "ERROR: could not find 'ffmpeg' executable" + bcolors.ENDC)
