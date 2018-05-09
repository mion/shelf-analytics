#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""For each frame, extract the area of intersection between a tracked object and every region of interest."""

import argparse
import json
import os
import sys

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

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

def area_of_bbox(bbox):
  y1, x1, y2, x2 = bbox
  w = x2 - x1
  h = y2 - y1
  return w * h

def extract_intersection_area_over_time(tracks, rois):
  intersection_area_over_time = []
  for track in tracks:
    intersection_area_by_roi = {}
    for roi in rois:
      name = roi["name"]
      intersection_area_by_roi[name] = []
    for i in range(len(track)):
      frame_index = track[i]["index"]
      track_bbox = track[i]["bbox"]
      for roi in rois:
        roi_name = roi["name"]
        roi_bbox = roi["bbox"]
        intersection_bbox = find_intersection_bbox(track_bbox, roi_bbox)
        intersection_area = 0
        if intersection_bbox != None:
          intersection_area = area_of_bbox(intersection_bbox)
        intersection_area_by_roi[roi_name].append({"index": frame_index, "area": intersection_area, "bbox": intersection_bbox})
    intersection_area_over_time.append(intersection_area_by_roi)
  return intersection_area_over_time

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("tracks_path", help="path to JSON file")
  parser.add_argument("rois_path", help="path a JSON file")
  args = parser.parse_args()

  tracks = load_json(args.tracks_path)
  rois = load_json(args.rois_path)

  intersection_area_over_time = extract_intersection_area_over_time(tracks, rois)
  print(json.dumps(intersection_area_over_time))
