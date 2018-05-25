#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract given a JSON file with the intersection area over time for each track."""

import argparse
import json
import os
import sys
import cv2
import numpy
from scipy.signal import find_peaks, peak_widths, lfilter, lfilter_zi, filtfilt, butter 

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

def area_of_bbox(bbox):
  y1, x1, y2, x2 = bbox
  w = x2 - x1
  h = y2 - y1
  return w * h

WALKED_EVENT_MIN_INTERSEC_AREA_PERCENTAGE = 0.20

def smooth_without_delay(xn):
  """
  Smooth the signal using the function scipy.signal.filtfilt, a linear filter 
  that achieves zero phase delay by applying an IIR filter to a signal twice, once forwards and once backwards. 

  Source: http://scipy-cookbook.readthedocs.io/items/FiltFilt.html
  """
  b, a = butter(1, 0.30) # TODO I tuned these parameters by hand on the Jupyter Notebook. WTF are they?!
  # Apply the filter to xn.  Use lfilter_zi to choose the initial condition
  # of the filter.
  zi = lfilter_zi(b, a)
  z, _ = lfilter(b, a, xn, zi=zi*xn[0])
  # Apply the filter again, to have a result filtered at an order
  # the same as filtfilt.
  z2, _ = lfilter(b, a, z, zi=zi*z[0])
  # Use filtfilt to apply the filter.
  return filtfilt(b, a, xn)

def extract_interacted_events_indexes(iaot, frame_indexes):
  """
  The array `iaot` contains a signal representing the intersection area over time.
  Each index corresponds to a point in time and each value is the area of intersection
  at that point in time.

  In order to understand how this function works, check the 
  `notebook_extracting_events_from_iaot.ipynb` Jupyter notebook.
  """
  x = numpy.array(frame_indexes)
  y = numpy.array(iaot)
  smooth_y = smooth_without_delay(y)
  indexes, props = find_peaks(smooth_y, height=10000, width=7)

  MIN_DURATION_MS_FOR_INTERACTED = 1500
  MIN_INTERSECTION_AREA_PX_FOR_INTERACTED = 5000
  fps = 5

  events_indexes = []

  for i in range(len(indexes)):
    frame_index = indexes[i]
    duration_in_frames = props["widths"][i]
    intersection_area_in_pixels = props["peak_heights"][i]
    # here is where the detection happens
    duration_ms = int(1000 * (duration_in_frames / fps))
    if duration_ms > MIN_DURATION_MS_FOR_INTERACTED and intersection_area_in_pixels > MIN_INTERSECTION_AREA_PX_FOR_INTERACTED:
      events_indexes.append(int(frame_index))
  return events_indexes

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
      # walked events
      for i in range(len(intersections_by_name[name])):
        intersec = intersections_by_name[name][i]
        frame_index = intersec["index"]
        intersec_perc = intersec["area"] / area_of_bbox(bbox_by_roi_name[name])
        if intersec_perc > WALKED_EVENT_MIN_INTERSEC_AREA_PERCENTAGE:
          event = {"type": "walked", "index": frame_index, "roi_name": name, "track": track_index}
          events.append(event)
          break
      # interacted events
      frame_indexes = []
      iaot = []
      for i in range(len(intersections_by_name[name])):
        x = intersections_by_name[name][i]["index"]
        y = intersections_by_name[name][i]["area"]
        frame_indexes.append(x)
        iaot.append(y)
      interacted_events_indexes = extract_interacted_events_indexes(iaot, frame_indexes)
      for frame_index in interacted_events_indexes:
        events.append({
          "type": "interacted",
          "index": frame_index + 2, # skip 2 frames (arbitrary) to (try) to match the moment the hand touches the shelf
          "roi_name": name,
          "track": track_index
        })

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
