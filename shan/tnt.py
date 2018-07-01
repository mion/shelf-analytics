#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os
import shutil
import json
import cv2
import cvutil

from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat

DEFAULT_TRANSCODED_VIDEO_NAME = "video"

def has_ffmpeg_installed():
    return shutil.which("ffmpeg") != None

def extract_video_name(path):
    return os.path.basename(os.path.normpath(path))

def extract_video_fps(dir):
    return int(extract_video_name(dir).split("-")[-1])

def add_suffix_to_basename(path, suffix):
    base_path, base_name = os.path.split(os.path.normpath(path))
    name, ext = os.path.splitext(base_name)
    return os.path.join(base_path, name + suffix + ext)

def load_json(path):
    with open(path, "r") as tags_file:
        return json.loads(tags_file.read())

def load_frames(path):
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        return None
    return cvutil.read_frames_from_video(video)

def load_bboxes_per_frame(tags):
    bboxes_per_frame = []
    for i in range(len(tags["frames"])):
        bboxes_per_frame.append([])
        for bbox in tags["frames"][i]["boxes"]:
            bboxes_per_frame[i].append(BBox(bbox, BBoxFormat.y1_x1_y2_x2))
    return bboxes_per_frame

def filter_bounding_boxes_with_score_below(tags, min_value):
    """
    `min_value` is a float between 0 and 1
    """
    pass # TODO
