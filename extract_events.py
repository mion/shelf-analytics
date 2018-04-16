#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract business insights into a JSON file given a tagged bundle (tagged frames and tags data) and a camera configuration file."""

import argparse
import json
import os
import sys
import cv2

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

def load_video(path):
  video = cv2.VideoCapture(args.video_path)
  if not video.isOpened():
    return None
  else:
    return video

def find_intersection_bbox(bbox_a, bbox_b): # TODO this method has NOT been tested
  y1_a, x1_a, y2_a, x2_a = bbox_a
  y1_b, x1_b, y2_b, x2_b = bbox_b
  x1 = max(x1_a, x1_b)
  y1 = max(y1_a, y1_b)
  x2 = min(x2_a, x2_b)
  y2 = min(y2_a, y2_b)
  if x1 < x2 and y1 < y2:
    return (y1, x1, y2, x2)
  else:
    return None

def extract_events(tracks, rois):
  # walked
  # pondered
  # interacted
  return []

def extract_intersection_area_by_frame_by_roi(tracks, rois):
  intersection_area_by_frame_by_roi = {}
  for roi in rois:
    name = roi["name"]
    intersection_area_by_frame_by_roi[name] = {}
  for track in tracks:
    for i in range(len(track)):
      frame_index = track[i]["index"]
      bbox = track[i]["bbox"]
      for roi in rois:
        name = roi["name"]
        bbox = roi["bbox"]
        intersection_area_by_frame_by_roi[name][frame_index] = 
  return events

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("tracks_path", help="path to JSON file")
  parser.add_argument("rois_path", help="path a JSON file")
  args = parser.parse_args()

  tracks = load_json(args.tracks_path)
  rois = load_json(args.rois_path)

  events = extract_events(tracks, rois)
  print(json.dumps(events))
