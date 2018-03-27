#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract business insights into a JSON file given a tagged bundle (tagged frames and tags data) and a camera configuration file."""

import argparse
import json
import os

import skimage.io
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

  # Remove white margin:
  # https://stackoverflow.com/a/27227718
  ax.set_axis_off()
  ax.set_title("")
  plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
  plt.margins(0, 0)
  ax.get_xaxis().set_major_locator(plt.NullLocator())
  ax.get_yaxis().set_major_locator(plt.NullLocator())

  for frame in tagged_bundle['frames']:
    tagged_frame_image = load_image(frame['tagged_frame_image_path'])
    for roi in camera_config['rois']:
      x1, y1, x2, y2 = roi['box']
      p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                            alpha=0.5, linestyle="dashed",
                            edgecolor=(0.0, 0.2, 0.8), facecolor='none')
      ax.add_patch(p)
    ax.imshow(tagged_frame_image)
    output_filename = tnt.add_suffix_to_basename(frame['tagged_frame_image_path'], "-cameraroi")
    plt.savefig(output_filename, bbox_inches="tight", pad_inches=0)

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
