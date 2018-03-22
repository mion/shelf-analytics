#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Takes a video file and split it into frames."""

import argparse
import shutil
import ffmpeg

def has_ffmpeg_installed():
  return shutil.which("ffmpeg") != None

def split_video_into_frames(filename, output_dir, fps, extension):
  print("Input filename: {0}".format(filename))
  print("Output directory: {0}".format(output_dir))
  print("FPS: {0}".format(fps))
  print("Image extension: {0}".format(extension))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="the raw input video filename")
  parser.add_argument("output_dir", help="the output directory path")
  parser.add_argument("--fps", default=10, type=int, help="output frames per second")
  parser.add_argument("--extension", default="png", help="extension of image files (PNG or JPG)")
  args = parser.parse_args()

  if has_ffmpeg_installed():
    split_video_into_frames(args.filename, args.output_dir, args.fps, args.extension)
  else:
    print("ERROR: could not find 'ffmpeg' executable")
