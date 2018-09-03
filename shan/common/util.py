#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto helper module."""

import os
import shutil
import json
import cv2
import skimage
import datetime
import time

from shan.core.bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat

def replace_ext(path, new_ext):
    basepath, _ = os.path.splitext(path)
    return basepath + '.' + new_ext

def current_local_time_isostring():
    # See: https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

def has_ffmpeg_installed():
    return shutil.which("ffmpeg") != None

def extract_video_name(path):
    return os.path.basename(os.path.normpath(path))

def extract_video_fps(dir):
    return int(extract_video_name(dir).split("-")[-1])

def get_name_without_ext(path):
    _, base_name = os.path.split(os.path.normpath(path))
    name, _ = os.path.splitext(base_name)
    return name

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
    return [skimage.io.imread(img_path) for img_path in image_file_paths]

def get_filenames_at(path):
    return next(os.walk(path))[2]

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

# Source:
# https://gist.github.com/jhcepas/5884168
def print_table(items, header=None, wrap=True, max_col_width=20, wrap_style="wrap", row_line=False, fix_col_width=False):
    ''' Prints a matrix of data as a human readable table. Matrix
    should be a list of lists containing any type of values that can
    be converted into text strings.
    Two different column adjustment methods are supported through
    the *wrap_style* argument:
    
       wrap: it will wrap values to fit max_col_width (by extending cell height)
       cut: it will strip values to max_col_width
    If the *wrap* argument is set to False, column widths are set to fit all
    values in each column.
    This code is free software. Updates can be found at
    https://gist.github.com/jhcepas/5884168
    
    '''
        
    if fix_col_width:
        c2maxw = dict([(i, max_col_width) for i in range(len(items[0]))])
        wrap = True
    elif not wrap:
        c2maxw = dict([(i, max([len(str(e[i])) for e in items])) for i in range(len(items[0]))])
    else:
        c2maxw = dict([(i, min(max_col_width, max([len(str(e[i])) for e in items])))
                        for i in range(len(items[0]))])
    if header:
        current_item = -1
        row = header
        if wrap and not fix_col_width:
            for col, maxw in c2maxw.items():
                c2maxw[col] = max(maxw, len(header[col]))
                if wrap:
                    c2maxw[col] = min(c2maxw[col], max_col_width)
    else:
        current_item = 0
        row = items[current_item]
    while row:
        is_extra = False
        values = []
        extra_line = [""]*len(row)
        for col, val in enumerate(row):
            cwidth = c2maxw[col]
            wrap_width = cwidth
            val = str(val)
            try:
                newline_i = val.index("\n")
            except ValueError:
                pass
            else:
                wrap_width = min(newline_i+1, wrap_width)
                val = val.replace("\n", " ", 1)
            if wrap and len(val) > wrap_width:
                if wrap_style == "cut":
                    val = val[:wrap_width-1]+"+"
                elif wrap_style == "wrap":
                    extra_line[col] = val[wrap_width:]
                    val = val[:wrap_width]
            val = val.ljust(cwidth)
            values.append(val)
        print(' | '.join(values))
        if not set(extra_line) - set(['']):
            if header and current_item == -1:
                print(' | '.join(['='*c2maxw[col] for col in range(len(row)) ]))
            current_item += 1
            try:
                row = items[current_item]
            except IndexError:
                row = None
        else:
            row = extra_line
            is_extra = True
 
        if row_line and not is_extra and not (header and current_item == 0):
            if row:
                print(' | '.join(['-'*c2maxw[col] for col in range(len(row)) ]))
            else:
                print(' | '.join(['='*c2maxw[col] for col in range(len(extra_line)) ]))
