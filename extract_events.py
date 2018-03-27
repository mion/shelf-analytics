#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract business insights into a JSON file given a tagged bundle (tagged frames and tags data) and a camera configuration file."""

import argparse
import json
import os

import skimage
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import tnt

def load_tagged_bundle(path):
  tags_file_path = os.path.join(path, "tags.json")
  with open(tags_file_path, "r") as tags_file:
    return json.loads(tags_file.read())

def load_camera_config(path):
  return {
    "rois": [
      {
        "name": "left",
        "box": [0, 180, 160, 270]
      },
      {
        "name": "middle",
        "box": [190, 110, (190 + 240), (110 + 150)]
      }
    ]
  }

def load_image(path):
  return skimage.io.imread(path)

def extract_events(camera_config, tagged_bundle, figsize=(16, 16), ax=None):
  if not ax:
    _, ax = plt.subplots(1, figsize=figsize)

  frames = tagged_bundle['frames']
  for i in range(len(frames)):
    frame = frames[i]
    # tagged_frame_image = load_image(frame['tagged_frame_image_path'])

  return {}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("tagged_bundle_path", help="path to a directory containing both a set of tagged frames and a tags data file")
  parser.add_argument("camera_config_path", help="path to JSON file containing the camera's image ROI configuration")
  parser.add_argument("--output_path", default="same", help="path to a directory where the events JSON file will be saved")
  args = parser.parse_args()

  output_path = args.tagged_bundle_path
  if args.output_path != "same":
    output_path = args.output_path

  camera_config = load_camera_config(args.camera_config_path)
  tagged_bundle = load_tagged_bundle(args.tagged_bundle_path)

  print(tnt.color_warn("Tagged bundle: ") + json.dumps(tagged_bundle, sort_keys=True, indent=3))
  print(tnt.color_warn("Camera config: ") + json.dumps(camera_config, sort_keys=True, indent=3))
  print(tnt.color_warn("Output path: ") + output_path)

  print("Extracting events...")
  events = extract_events(camera_config, tagged_bundle)
  print(tnt.color_ok("Done!"))

  print("Saving to JSON...")
  print(json.dumps(events, sort_keys=True, indent=4))
  print(tnt.color_ok("Done!"))
