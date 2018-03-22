#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Split a video file into many images."""

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

def split_frames(input_path, output_dir, ext):
  frame_number_format = '%07d'
  _, input_name = os.path.split(input_path)
  name, _ = os.path.splitext(input_name)
  video_dir = os.path.join(output_dir, name)
  try:
    os.mkdir(video_dir)
  except FileExistsError as err:
    print(bcolors.WARNING + "ERROR: could not create directory at {0}".format(video_dir) + bcolors.ENDC)
    print(err)
    return False
  output_path = os.path.join(video_dir, "frame-{0}.{1}".format(frame_number_format, ext))
  cmd_template = "ffmpeg -i {0} {1} -hide_banner"
  #
  # [!] WARNING: shell=True is dangerous
  #
  cmd = cmd_template.format(input_path, output_path)
  print("\n\n\t" + cmd + "\n\n")
  result = subprocess.call(cmd, shell=True)
  return result == 0

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("input_path", help="input video file path")
  parser.add_argument("output_dir", help="output directory")
  parser.add_argument("--ext", default="png", help="frame image file extension: png (default) or jpg")
  args = parser.parse_args()

  if has_ffmpeg_installed():
    print(bcolors.WARNING + "Input video: " + bcolors.ENDC + args.input_path)
    print(bcolors.WARNING + "Output directory: " + bcolors.ENDC + args.output_dir)
    print(bcolors.WARNING + "Frame images extension: " + bcolors.ENDC + str(args.ext))
    print("Working...")
    success = split_frames(args.input_path, args.output_dir, args.ext)
    if success:
      print(bcolors.OKGREEN + "Done!" + bcolors.ENDC)
    else:
      print(bcolors.FAIL + "ERROR: failed to split video into frames" + bcolors.ENDC)
  else:
    print(bcolors.FAIL + "ERROR: could not find 'ffmpeg' executable" + bcolors.ENDC)
