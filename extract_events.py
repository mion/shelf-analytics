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

def extract_events(video, tracks, rois):
  events = []
  return events

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("video_path", help="path a transcoded video")
  parser.add_argument("tracks_path", help="path to JSON file")
  parser.add_argument("rois_path", help="path a JSON file")
  args = parser.parse_args()

  video = load_video(args.video_path)
  if video is None:
    print("Could not load video")
    sys.exit()
  tracks = load_json(args.tracks_path)
  rois = load_json(args.rois_path)

  events = extract_events(video, tracks, rois)
  print(json.dumps(events))
