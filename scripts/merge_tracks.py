import pdb

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import argparse
import numpy as np
import cv2
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tnt import load_frames
from tracking2 import TrackingResult
from cvutil import show_image, crop_image, save_image

def cut_bbox_image(frame, bbox):
    img = crop_image(frame, bbox.x1, bbox.y1, bbox.width, bbox.height)
    return img

def merge_tracks(tracking_result):
    histogram_by_track_id = {}
    for track in tracking_result.tracks:
        images = []
        for index, bbox, _ in track.steps:
            frame = tracking_result.frame_bundles[index].frame
            images.append(cut_bbox_image(frame, bbox))
        # See: https://www.pyimagesearch.com/2014/07/14/3-ways-compare-histograms-using-opencv-python/
        hist = cv2.calcHist(images, [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten() # fix for cv2, see: https://github.com/mconigliaro/smtptester/issues/2
        histogram_by_track_id[track.id] = hist
    pdb.set_trace()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    # parser.add_argument('output_dir_path', help='path to the output directory where a JSON file with the tracks will be saved')
    args = parser.parse_args()
    
    frames = load_frames(args.video_path)
    tr = TrackingResult()
    tr.load_from_json(frames, args.tracking_result_path)
    merge_tracks(tr)
