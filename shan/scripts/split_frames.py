#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Split a video file into many images."""

import os
import sys
import argparse
import subprocess
from shan.core.frame_splitting import split_frames

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video_path", help="input video file path")
    parser.add_argument("output_dir_path", help="output directory")
    parser.add_argument("--ext", default="png", help="frame image file extension: 'png' (default) or 'jpg'")
    args = parser.parse_args()

    try:
        success = split_frames(args.input_video_path, args.output_dir_path, args.ext)
        if success:
            sys.exit(0)
        else:
            print("Failed to split frames. ERROR: subprocess did not return 0")
            sys.exit(1)
    except Exception as exc:
        print("Failed to split frames video. ERROR:\n{}".format(str(exc)))
        sys.exit(1)
