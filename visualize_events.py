#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract given a JSON file with the intersection area over time for each track."""

import argparse
import json
import os
import sys
import cv2

import cvutil

def load_video(path):
  video = cv2.VideoCapture(args.video_path)
  if not video.isOpened():
    return None
  else:
    return video

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

def get_tracked_objects_by_frame_index(tracks):
  tracked_objects_by_frame_index = {}
  for track_index in range(len(tracks)):
    track = tracks[track_index]
    for step in track:
      frame_index = step["index"]
      track_name = "track_" + str(track_index)
      if track_name not in tracked_objects_by_frame_index[frame_index]:
        tracked_objects_by_frame_index[frame_index][track_name] = {}
      tracked_objects_by_frame_index[frame_index][track_name] = step["bbox"]
  return tracked_objects_by_frame_index

def visualize_events(output_path, video, events, rois, tracks, intersection_area_over_time):
  # frames = cvutil.read_frames_from_video(video)
  # for index in range(len(frames)):
  #   frame = frames[index]
  #   pass
  print(get_tracked_objects_by_frame_index(tracks))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("output_path", help="path to output directory")
  parser.add_argument("video_path", help="path to video file")
  parser.add_argument("events_path", help="path to JSON file")
  parser.add_argument("rois_path", help="path to JSON file")
  parser.add_argument("tracks_path", help="path to JSON file")
  parser.add_argument("iaot_path", help="path to JSON file")
  args = parser.parse_args()

  video = load_video(args.video_path)
  if video is None:
    print("ERROR: could not load video")
    sys.exit()
  events = load_json(args.events_path)
  rois = load_json(args.rois_path)
  tracks = load_json(args.tracks_path)
  intersection_area_over_time = load_json(args.iaot_path)

  visualize_events(args.output_path, video, events, rois, tracks, intersection_area_over_time)
