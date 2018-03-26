#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Detect objects inside one or more images, usually frames extracted from a video."""

import argparse

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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def warn(s):
  return bcolors.WARNING + s + bcolors.ENDC

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

config = InferenceConfig()
config.display()

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

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


def get_images_file_names(input_dir):
  # TODO: rename "names" to "basenames"
  # TODO: rename "images_file_names" to "images_full_paths"
  names = next(os.walk(input_dir))[2]
  images_file_names = []
  for i in range(0, len(names)):
    name = names[i]
    images_file_names.append(os.path.join(input_dir, name))
  return (names, images_file_names)


def load_images(images_file_names):
  images = []
  for i in range(0, len(images_file_names)):
    file_name = images_file_names[i]
    images.append(skimage.io.imread(file_name))
  return images


def detect_objects(input_dir, output_dir):
  video_name = os.path.basename(os.path.normpath(input_dir))
  final_output_dir = os.path.join(output_dir, video_name)

  try:
    os.mkdir(final_output_dir)
  except FileExistsError as err:
    print(bcolors.WARNING + "ERROR: could not create directory at {0}".format(final_output_dir) + bcolors.ENDC)
    print(err)
    return False

  names, images_file_names = get_images_file_names(input_dir)
  images = load_images(images_file_names)

  for i in range(0, len(images)):
    print(warn("Processing image ") + str(i + 1) + warn(" of ") + str(len(images)) + "...")
    image = images[i]
    name = names[i]
    results = model.detect([image], verbose=1)
    r = results[0]
    tagged_filename = os.path.join(final_output_dir, "tagged-{0}".format(name))
    visualize.save_image_instances(tagged_filename, image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
  
  return True


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("input_dir", help="input directory representing a video with its frames inside")
  parser.add_argument("output_dir", help="output directory")
  args = parser.parse_args()

  print(bcolors.WARNING + "Input directory: " + bcolors.ENDC + args.input_dir)
  print(bcolors.WARNING + "Output directory: " + bcolors.ENDC + args.output_dir)
  print("Working, please wait...")
  success = detect_objects(args.input_dir, args.output_dir)
  if success:
    print(bcolors.OKGREEN + "Done!" + bcolors.ENDC)
  else:
    print(bcolors.FAIL + "ERROR: failed to detect objects" + bcolors.ENDC)
