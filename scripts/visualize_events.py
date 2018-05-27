#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Extract given a JSON file with the intersection area over time for each track."""

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import json
import cv2
import numpy as np
import time

import cvutil

FAKE_START_TIME = time.localtime()

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
      if frame_index not in tracked_objects_by_frame_index:
        tracked_objects_by_frame_index[frame_index] = {}
      track_name = "Cliente #" + str(track_index + 1)
      if track_name not in tracked_objects_by_frame_index[frame_index]:
        tracked_objects_by_frame_index[frame_index][track_name] = {}
      tracked_objects_by_frame_index[frame_index][track_name] = step["bbox"]
  return tracked_objects_by_frame_index

def event_type_to_text(type):
  if type == 'interacted':
    return "+1 interagiu"
  elif type == 'walked':
    return "+1 passou"
  else:
    return "+1 evento"

def event_index_to_time(index):
  FPS = 5
  delta_ms_from_start = int(index * (1000 / FPS))
  start_time_s = time.mktime(FAKE_START_TIME)
  event_time = time.localtime(start_time_s + int(delta_ms_from_start / 1000))
  return time.strftime("%H:%M:%S", event_time)

def draw_detail(image, orig, label, value, value_text_color=(255, 255, 255)):
    FONT_SCALE = 1.0
    FONT_THICKNESS = 1
    FONT_LINE = cv2.LINE_AA
    FONT_TYPE = cv2.FONT_HERSHEY_PLAIN
    LABEL_TEXT_COLOR = (175, 175, 175)
    SPACE_AFTER_LABEL = 5
    label_size, _ = cv2.getTextSize(label, FONT_TYPE, FONT_SCALE, FONT_THICKNESS)
    label_width, _ = label_size
    cv2.putText(image, label, orig, FONT_TYPE, FONT_SCALE, LABEL_TEXT_COLOR, FONT_THICKNESS, FONT_LINE)
    cv2.putText(image, value, (orig[0] + label_width + SPACE_AFTER_LABEL, orig[1]), FONT_TYPE, FONT_SCALE, value_text_color, FONT_THICKNESS, FONT_LINE)
    value_size, _ = cv2.getTextSize(value, FONT_TYPE, FONT_SCALE, FONT_THICKNESS)
    value_width, _ = value_size
    return label_width + value_width + SPACE_AFTER_LABEL

def draw_watermark(image, orig, text):
    FONT_SCALE = 0.75
    FONT_THICKNESS = 1
    FONT_LINE = cv2.LINE_AA
    FONT_TYPE = cv2.FONT_HERSHEY_PLAIN
    cv2.putText(image, text, orig, FONT_TYPE, FONT_SCALE, (200, 200, 200), FONT_THICKNESS, FONT_LINE)

def draw_events(image, orig, events, section_width):
    FONT_SCALE = 1
    FONT_THICKNESS = 1
    FONT_LINE = cv2.LINE_AA
    FONT_TYPE = cv2.FONT_HERSHEY_PLAIN
    LINE_HEIGHT = 30
    GOLD = (68, 198, 245) # gold
    BLACK = (0, 0, 0)
    curr_x = orig[0]
    curr_y = orig[1]
    for (timestamp, text) in events:
        cv2.rectangle(image, (curr_x, curr_y), (curr_x + section_width, curr_y + LINE_HEIGHT), GOLD, -1)
        curr_y += LINE_HEIGHT
        cv2.putText(image, timestamp + " " + text, (curr_x + 10, curr_y - 10), FONT_TYPE, FONT_SCALE, BLACK, FONT_THICKNESS, FONT_LINE)

def draw_technical_info(original_image, events):
  height, width, channels = original_image.shape
  # Add footer
  ROW_PADDING = 10
  COL_PADDING = 20
  ROW_LINE_HEIGHT = 5
  ROW_HEIGHT = 30
  FOOTER_HEIGHT = 3 * ROW_HEIGHT
  img_with_footer = np.zeros((height + FOOTER_HEIGHT, width, channels), np.uint8)
  img_with_footer[0:(height - 1), 0:(width - 1)] = original_image[0:(height - 1), 0:(width - 1)]

  # Draw details
  detail_widths = []
  detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 1 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Produto:", "GARRAFAS PET 2L ESQ"))
  detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 2 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Conversao:", "1,04% (ult. 30 dias)", (0, 255, 0)))
  detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 3 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Sell Out:", "63,2% (ult. 30 dias)", (0, 100, 255)))
  max_width = max(detail_widths)
  second_col_x = max_width + ROW_PADDING + COL_PADDING
  draw_detail(img_with_footer, (second_col_x, height + 1 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Loja:", "PREZUNIC BOTAFOGO")
  draw_detail(img_with_footer, (second_col_x, height + 2 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Camera:", "CORREDOR BEBIDAS SEC 3")
  draw_detail(img_with_footer, (second_col_x, height + 3 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Data:", time.strftime("%d %b %Y %H:%M:%S %Z", FAKE_START_TIME))

  # Add water mark
  draw_watermark(img_with_footer, (ROW_PADDING, 2 * ROW_PADDING), "Shelf Analytics (v1.0.9)  |  Copyright (c) 2018 TonetoLabs Inc. All rights reserved.")
  # draw_watermark(img_with_footer, (ROW_PADDING, 2 * ROW_PADDING), "shelf-analytics-v1.0.9")
  # draw_watermark(img_with_footer, (ROW_PADDING, 4 * ROW_PADDING), "Copyright (c) 2018 TonetoLabs Inc. All rights reserved.")

  # Add events section
  EVENTS_WIDTH = 250
  height_with_footer = height + FOOTER_HEIGHT
  img_with_events = np.zeros((height + FOOTER_HEIGHT, width + EVENTS_WIDTH, channels), np.uint8)
  img_with_events[0:(height_with_footer - 1), 0:(width - 1)] = img_with_footer[0:(height_with_footer - 1), 0:(width - 1)]
  # events = [
  #     ("[15:32:23]", "+1 passou"),
  #     ("[15:32:25]", "+1 interagiu"),
  #     ("[15:35:45]", "+1 passou")
  # ]
  draw_events(img_with_events, (width, 0), events, EVENTS_WIDTH)
  return img_with_events

def visualize_events(output_path, video, events, rois, tracks, intersection_area_over_time):
  tracked_objects_by_frame_index = get_tracked_objects_by_frame_index(tracks)
  frames = cvutil.read_frames_from_video(video)
  toasts = []
  events_to_be_drawn_at_side = []
  for index in range(len(frames)):
    frame = frames[index]
    if index in tracked_objects_by_frame_index:
      tracked_objects = tracked_objects_by_frame_index[index]
      for track_name in tracked_objects.keys():
        tracked_bbox = tracked_objects[track_name]
        frame = cvutil.draw_bbox_on_frame(frame, tracked_bbox, (0, 75, 255), (150, 225, 250), track_name)
    for roi in rois:
      captured = False
      for event in events:
        if event["index"] == index and event["roi_name"] == roi["name"]:
          events_to_be_drawn_at_side.append((event_index_to_time(event["index"]), event_type_to_text(event["type"])))
          # frame = cvutil.draw_bbox_on_frame(frame, roi["bbox"], (0, 255, 0), (50, 225, 50), roi["name"] + " +1 " + event["type"])
          frame = cvutil.draw_subtitled_bbox_on_frame(frame, roi["bbox"], roi["name"], rect_color=(0, 255, 0))
          toasts.append({
            "text": event_type_to_text(event["type"]),
            "x": roi["bbox"][1],
            "y": roi["bbox"][2],
            "life": 0
          })
          captured = True
      if not captured:
        # frame = cvutil.draw_bbox_on_frame(frame, roi["bbox"], (255, 125, 25), (255, 225, 200), roi["name"])
        frame = cvutil.draw_subtitled_bbox_on_frame(frame, roi["bbox"], roi["name"])
    
    for toast in toasts:
      if toast["life"] > 10:
        continue
      else:
        toast["life"] += 1
        toast["y"] -= 3
        cvutil.draw_text_on_frame(frame, toast["text"], toast["x"], toast["y"], (0, 231, 255))

    frame_with_info = draw_technical_info(frame, events_to_be_drawn_at_side)

    NUMBER_OF_DIGITS = 4
    cvutil.save_image(frame_with_info, "frame-{0}.png".format(str(index).zfill(NUMBER_OF_DIGITS)), output_path)

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
