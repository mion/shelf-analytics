#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Detect objects inside one or more images, usually frames extracted from a video."""
import pdb

import argparse
import json
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt

import coco
import utils
import model as modellib
import visualize

from colorize import red, green, yellow
from tnt import extract_video_fps, extract_video_name, has_ffmpeg_installed, DEFAULT_TRANSCODED_VIDEO_NAME


class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


def scan_images(input_dir):
  file_names = next(os.walk(input_dir))[2]
  images_file_paths = []
  images_file_names = []
  for i in range(0, len(file_names)):
    file_name = file_names[i]
    if file_name.endswith("png") or file_name.endswith("jpg") or file_name.endswith("jpeg"):
      images_file_names.append(file_name)
      images_file_paths.append(os.path.join(input_dir, file_name))
    else:
      print(yellow("Found file '") + file_name + yellow("' inside directory but it is not an image, skipping..."))
  return (images_file_names, images_file_paths)


def load_images(img_file_paths):
  images = []
  for i in range(0, len(img_file_paths)):
    file_path = img_file_paths[i]
    images.append(skimage.io.imread(file_path))
  return images


def detect_objects(input_dir, video_fps, output_dir, model, visually=False):
  # COCO Class names
  # Index of the class in the list is its ID. For example, to get ID of
  # the teddy bear class, use: class_names.index('teddy bear')
  class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                'bus', 'train', 'truck', 'boat', 'traffic light',
                'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                'kite', 'baseball bat', 'baseball glove', 'skateboard',
                'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                'teddy bear', 'hair drier', 'toothbrush']

  # scan and load images
  img_file_names, img_file_paths = scan_images(input_dir)
  images = load_images(img_file_paths)
  tags = {}
  tags['frames'] = []
  tags['frames_per_second'] = video_fps # TODO: fix this
  # run the Mask RCNN code for each one of them
  for i in range(0, len(images)):
    print(green("Processing image ") + str(i + 1) + green(" of ") + str(len(images)) + "...")
    image = images[i]
    name = img_file_names[i]
    results = model.detect([image], verbose=1)
    r = results[0]
    tagged_filename = os.path.join(output_dir, "tagged-{0}".format(name))
    if visually:
      tagged_frame = visualize.tag_frame_visually(tagged_filename, image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
    else:
      tagged_frame = visualize.tag_frame(tagged_filename, image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
    tagged_frame['frame_index'] = i
    tags['frames'].append(tagged_frame)
  return (True, tags)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("input_dir", help="input directory representing a video with its frames inside")
  parser.add_argument("--fps", default=10, type=int, help="frames per second for output video")
  parser.add_argument("output_dir", help="output directory")
  parser.add_argument("format", help="can be either 'json' or 'visual'")
  args = parser.parse_args()

  print(yellow("Input directory: ") + args.input_dir)
  print(yellow("Output directory: ") + args.output_dir)

  if not os.path.exists(args.input_dir):
    print(red("ERROR: unable to open (or missing permissions) for input directory: ") + args.input_dir)
    exit(1)
  
  if not os.path.exists(args.output_dir):
    print(red("ERROR: unable to open (or missing permissions) for output directory: ") + args.output_dir)
    exit(1)

  print("Working, please wait...")

  config = InferenceConfig()
  config.display()

  ROOT_DIR = os.getcwd()
  MODEL_DIR = os.path.join(ROOT_DIR, "logs")
  COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

  # Create model object in inference mode.
  model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

  # Load weights trained on MS-COCO
  model.load_weights(COCO_MODEL_PATH, by_name=True)

  visually = (args.format == 'visual')
  success, tags = detect_objects(args.input_dir, args.fps, args.output_dir, model, visually)

  if success:
    print(green("Done!") + " Saving tags into a JSON file...")
    tags_file_path = os.path.join(args.output_dir, "tags.json")
    with open(tags_file_path, "w") as tags_file:
      json.dump(tags, tags_file)
    print(green("Success! Tag JSON file saved to: ") + tags_file_path)
    exit(0)
  else:
    print(red("ERROR: failed to detect objects"))
    exit(1)
