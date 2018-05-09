#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract given a JSON file with the intersection area over time for each track."""

import argparse
import json
import os
import sys
import cv2

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

def area_of_bbox(bbox):
  y1, x1, y2, x2 = bbox
  w = x2 - x1
  h = y2 - y1
  return w * h

WALKED_EVENT_MIN_INTERSEC_AREA_PERCENTAGE = 0.25

def extract_events(rois, intersection_area_over_time):
  # walked
  # pondered
  # interacted
  bbox_by_roi_name = {}
  for roi in rois:
    bbox_by_roi_name[roi["name"]] = roi["bbox"]
  
  events = []
  for track_index in range(len(intersection_area_over_time)):
    intersections_by_name = intersection_area_over_time[track_index]
    roi_names = intersections_by_name.keys()
    for name in roi_names:
      for i in range(len(intersections_by_name[name])):
        intersec = intersections_by_name[name][i]
        frame_index = intersec["index"]
        intersec_perc = intersec["area"] / area_of_bbox(bbox_by_roi_name[name])
        if intersec_perc > WALKED_EVENT_MIN_INTERSEC_AREA_PERCENTAGE:
          # for now let's look for walked events only
          event = {"type": "walked", "index": frame_index, "roi_name": name, "track": track_index}
          events.append(event)
          break
  return events

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("rois_path", help="path to JSON file")
  parser.add_argument("iaot_path", help="path to JSON file")
  args = parser.parse_args()

  rois = load_json(args.rois_path)
  intersection_area_over_time = load_json(args.iaot_path)

  events = extract_events(rois, intersection_area_over_time)
  print(json.dumps(events))
