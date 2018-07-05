import cv2
import numpy as np
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tnt import load_json

cfg = load_json('shan/calibration-config.json')

TRANSITION_COLOR = (0, 155, 255)

def draw_transition_line(frame, orig_bbox, dest_bbox, color=(0, 155, 255)):
    cv2.line(frame, orig_bbox.center, dest_bbox.center, color, 1)
    return frame

def draw_text(frame, text, orig, color=(255, 255, 255)):
  cv2.putText(frame, text, orig, cv2.FONT_HERSHEY_DUPLEX, 0.50, color, 1, cv2.LINE_AA)
  return frame

def draw_line(frame, orig, dest, color=(255, 255, 255), thickness=1):
    cv2.line(frame, orig, dest, color, thickness, cv2.LINE_AA)
    return frame

def draw_rect(frame, bbox, color=(255, 255, 255), thickness=1):
    cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), color, thickness)
    return frame

def draw_footer(frame, height):
    frame_height, frame_width, frame_channels = frame.shape
    frame_with_footer = np.zeros((frame_height + height, frame_width, frame_channels), np.uint8)
    frame_with_footer[0:(frame_height - 1), 0:(frame_width - 1)] = frame[0:(frame_height - 1), 0:(frame_width - 1)]
    return frame_with_footer

def draw_calibration_config(frame, cfg):
    frame_height, frame_width, _ = frame.shape
    columns_count = 0
    for key, _ in cfg.items():
        if key.endswith('DISTANCE'):
            columns_count += 1
    column_width = frame_width / columns_count
    padding = 10
    x, y = (0, frame_height + padding)
    for key, value in cfg.items():
        frame = draw_text(frame, key, (x + padding, y + padding))
        frame = draw_line(frame, (x + padding, y + 2 * padding), (x + padding + value, y + 2 * padding), thickness=2)
        x += column_width
    return frame
