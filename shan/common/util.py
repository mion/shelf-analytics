#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os, sys
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
import shutil
import json
import cv2
import skimage
import datetime
import time
import subprocess

from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat

def create_object_tracker(obj_tracker_type):
    major_ver, minor_ver, subminor_ver = cv2.__version__.split(".")
    if int(minor_ver) < 3:
        return cv2.Tracker_create(obj_tracker_type)
    else:
        if obj_tracker_type == 'BOOSTING':
            return cv2.TrackerBoosting_create()
        elif obj_tracker_type == 'MIL':
            return cv2.TrackerMIL_create()
        elif obj_tracker_type == 'KCF':
            return cv2.TrackerKCF_create()
        elif obj_tracker_type == 'TLD':
            return cv2.TrackerTLD_create()
        elif obj_tracker_type == 'MEDIANFLOW':
            return cv2.TrackerMedianFlow_create()
        elif obj_tracker_type == 'GOTURN':
            return cv2.TrackerGOTURN_create()
        else:
            raise RuntimeError("invalid object tracker type")

def make_video(video_filename, evented_frames_dir_path, videos_path):
    fps = 10
    output_video_name = 'evented-' + video_filename
    cmd_tmpl = 'cd {}; ffmpeg -framerate {} -pattern_type glob -i "*.png" -c:v libx264 -r {} -pix_fmt yuv420p {}'
    cmd = cmd_tmpl.format(evented_frames_dir_path, fps, fps, output_video_name)
    # WARNING shell=True is dangerous
    result = subprocess.call(cmd, shell=True)
    if result != 0:
        raise RuntimeError('Command "{}" returned non-zero'.format(cmd))
    shutil.move(os.path.join(evented_frames_dir_path, output_video_name), videos_path)

def current_local_time_isostring(): # This method is currently not being used anywhere.
    # See: https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

def has_ffmpeg_installed():
    return shutil.which("ffmpeg") != None

def add_suffix_to_basename(path, suffix):
    base_path, base_name = os.path.split(os.path.normpath(path))
    name, ext = os.path.splitext(base_name)
    return os.path.join(base_path, name + suffix + ext)

def load_json(path):
    with open(path, "r") as tags_file:
        return json.loads(tags_file.read())

def save_json(obj, path):
    with open(path, "w") as jsonfile:
        json.dump(obj, jsonfile)

def save_image(img, name, path):
  cv2.imwrite(os.path.join(path, name), img)

def read_frames_from_video(video):
    is_first_frame = True
    frames = []
    while True:
        ok, frame = video.read()
        if not ok and is_first_frame:
            return None
        elif not ok and not is_first_frame:
            break
        else:
            is_first_frame = False
            frames.append(frame)
    return frames

def load_frames(path):
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        return None
    return read_frames_from_video(video)

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
    sorted_image_file_paths = sorted(image_file_paths)
    return [skimage.io.imread(img_path) for img_path in sorted_image_file_paths]

def make_events_per_frame(events):
    events_per_frame = {}
    for evt in events:
        if evt['index'] not in events_per_frame:
            events_per_frame[evt['index']] = []
        events_per_frame[evt['index']].append(evt)
    return events_per_frame
