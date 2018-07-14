#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os
import shutil
import json
import cv2
import cvutil
import skimage

from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat

def has_ffmpeg_installed():
    return shutil.which("ffmpeg") != None

def extract_video_name(path):
    return os.path.basename(os.path.normpath(path))

def extract_video_fps(dir):
    return int(extract_video_name(dir).split("-")[-1])

def get_name_without_ext(path):
    base_path, base_name = os.path.split(os.path.normpath(path))
    name, ext = os.path.splitext(base_name)
    return name

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

def count_frames(path): 
    # FIXME: this is VERY SLOW, we should find a way to count faster
    frames = load_frames(path)
    if frames is None:
        raise RuntimeError('failed to load frames from video at: {}'.format(path))
    return len(frames)

def load_images(path, extension):
    """Load every image in this path that have this extension, 
    returns an array.
    """
    file_names = next(os.walk(path))[2]
    image_file_paths = []
    for fname in file_names:
        if fname.endswith(extension):
            image_file_paths.append(os.path.join(path, fname))
    return [skimage.io.imread(img_path) for img_path in image_file_paths]

def load_bboxes_per_frame(tags):
    bboxes_per_frame = []
    for i in range(len(tags["frames"])):
        bboxes_per_frame.append([])
        for bbox in tags["frames"][i]["boxes"]:
            bboxes_per_frame[i].append(BBox(bbox, BBoxFormat.y1_x1_y2_x2))
    return bboxes_per_frame

def make_events_per_frame(events):
    events_per_frame = {}
    for evt in events:
        if evt['index'] not in events_per_frame:
            events_per_frame[evt['index']] = []
        events_per_frame[evt['index']].append(evt)
    return events_per_frame

def filter_bounding_boxes_with_score_below(tags, min_value):
    """
    `min_value` is a float between 0 and 1
    """
    pass # TODO
