#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Main Shelf Analytics script."""
import os
import argparse
import json

from colorize import red, green, yellow, header


def load_json(path):
    with open(path, "r") as tags_file:
      return json.loads(tags_file.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("video_file_path", help="path to a video file")
    parser.add_argument(
        "rois_file_path", help="path to the Regions of Interest JSON file")
    parser.add_argument("output_dir_path", help="path to the output directory")
    args = parser.parse_args()

    print("Video file:", args.video_file_path, sep=" ")
    print("Regions of Interest JSON file:", args.rois_file_path, sep=" ")
    print("Output directory:", args.output_dir_path, sep=" ")
