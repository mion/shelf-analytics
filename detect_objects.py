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

import tnt


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
      print(tnt.color_warn("Found file '") + file_name + tnt.color_warn("' inside directory but it is not an image, skipping..."))
  return (images_file_names, images_file_paths)


def load_images(img_file_paths):
  images = []
  for i in range(0, len(img_file_paths)):
    file_path = img_file_paths[i]
    images.append(skimage.io.imread(file_path))
  return images


def detect_objects(input_dir, output_dir, model):
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

  video_name = os.path.basename(os.path.normpath(input_dir))
  final_output_dir = os.path.join(output_dir, video_name)
  # create output dir
  try:
    os.mkdir(final_output_dir)
  except FileExistsError as err:
    print(tnt.color_warn("ERROR: could not create directory at {0}".format(final_output_dir)))
    print(err)
    return (False, None)
  # scan and load images
  img_file_names, img_file_paths = scan_images(input_dir)
  images = load_images(img_file_paths)
  tags = {}
  # run the Mask RCNN code for each one of them
  for i in range(0, len(images)):
    print(tnt.color_ok("Processing image ") + str(i + 1) + tnt.color_ok(" of ") + str(len(images)) + "...")
    image = images[i]
    name = img_file_names[i]
    results = model.detect([image], verbose=1)
    r = results[0]
    tagged_filename = os.path.join(final_output_dir, "tagged-{0}".format(name))
    tag = visualize.save_image_instances(tagged_filename, image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
    tag['frame_index'] = i
    tags[name] = tag
  return (True, tags)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("input_dir", help="input directory representing a video with its frames inside")
  parser.add_argument("output_dir", help="output directory")
  args = parser.parse_args()

  print(tnt.color_warn("Input directory: ") + args.input_dir)
  print(tnt.color_warn("Output directory: ") + args.output_dir)

  if not os.path.exists(args.input_dir):
    print(tnt.color_fail("ERROR: unable to open (or missing permissions) for input directory: ") + args.input_dir)
    exit(1)
  
  if not os.path.exists(args.output_dir):
    print(tnt.color_fail("ERROR: unable to open (or missing permissions) for output directory: ") + args.output_dir)
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

  success, tags = detect_objects(args.input_dir, args.output_dir, model)

  if success:
    print(tnt.color_ok("Done!") + " Saving tags into a JSON file...")
    video_name = tnt.extract_video_name(args.input_dir)
    tags_file_name = "tags-" + video_name + ".json"
    tags_dir = os.path.join(args.output_dir, video_name)
    tags_file_path = os.path.join(tags_dir, tags_file_name)
    with open(tags_file_path, "w") as tags_file:
      json.dump(tags, tags_file)
    print(tnt.color_ok("Success! Tag JSON file saved to: ") + tags_file_path)
    exit(0)
  else:
    print(tnt.color_fail("ERROR: failed to detect objects"))
    exit(1)
