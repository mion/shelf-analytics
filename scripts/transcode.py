"""
Shelf Analytics
Transcode a video file before splitting it into frames.

Copyright (c) 2018 TonetoLabs.
Author: Gabriel Luis Vieira (gluisvieira@gmail.com)
"""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import subprocess
import shutil

from tnt import extract_video_name
from transcoding import transcode

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video_path", help="input video file path")
    parser.add_argument("output_video_path", help="output video file path")
    parser.add_argument("--fps", default=10, type=int, help="frames per second for output video (default is 10)")
    args = parser.parse_args()

    try:
        success = transcode(args.input_video_path, args.output_video_path, args.fps)
        if success:
            sys.exit(0)
        else:
            print("Failed to transcode video. ERROR: subprocess did not return 0")
            sys.exit(1)
    except Exception as exc:
        print("Failed to transcode video. ERROR:\n{}".format(str(exc)))
        sys.exit(1)
