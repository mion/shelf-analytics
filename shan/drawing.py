import pdb
import cv2
import numpy as np
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tnt import load_json

TRANSITION_COLOR = (0, 155, 255)

def draw_bbox_line_between_centers(frame, orig_bbox, dest_bbox, color=(255, 255, 255), thickness=1):
    cv2.line(frame, orig_bbox.center, dest_bbox.center, color, thickness)
    return frame

def draw_bbox_outline(frame, bbox, color=(255, 255, 255), thickness=1):
    cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), color, thickness)
    return frame

# FIXME rename to draw_bbox_props
def draw_bbox_coords(frame, bbox, color=(255, 255, 255), offset_y=0):
    coords_text = "({0},{1}) {2}x{3} {4:.2f} {5}".format(str(bbox.x1), str(bbox.y1), str(bbox.width), str(bbox.height), bbox.score, bbox.get_filtering_results_label())
    text_width, _ = get_text_size(coords_text)
    frame = draw_text(frame, coords_text, (bbox.center[0] - int(text_width / 2), bbox.center[1] + offset_y), color)
    return frame

def draw_bbox_header(frame, bbox, transition, bg_color=(0, 0, 0), fg_color=(255, 255, 255)):
    header_text = '{' + ','.join([str(track_id) for track_id in bbox.parent_track_ids]) + '}'
    if transition is not None:
        header_text += ' (' + transition.kind + ')'
    padding = 2
    _, text_height = get_text_size(header_text)
    cv2.rectangle(frame, 
                (bbox.x1, bbox.y1), 
                (bbox.x1 + bbox.width, bbox.y1 + text_height + (3 * padding)), 
                bg_color, 
                cv2.FILLED, 
                cv2.LINE_AA)
    frame = draw_text(frame, header_text, (bbox.x1, bbox.y1 + text_height + (2 * padding)), fg_color)
    return frame

def draw_calibration_config(frame_with_footer, footer_height, cfg):
    frame_with_footer_height, frame_width, _ = frame_with_footer.shape
    frame_height = frame_with_footer_height - footer_height
    columns_count = 0
    for key, _ in cfg.items():
        if key.endswith('DISTANCE'):
            columns_count += 1
    column_width = int(frame_width / columns_count)
    padding = 10
    x, y = (0, frame_height + padding)
    for key, value in cfg.items():
        if key.endswith('DISTANCE'):
            frame_with_footer = draw_text(frame_with_footer, key, (x + padding, y + padding))
            frame_with_footer = draw_line(frame_with_footer, (x + padding, y + 2 * padding), (x + padding + value, y + 2 * padding), thickness=2)
            x += column_width
    return frame_with_footer

def draw_text(frame, text, orig, color=(255, 255, 255), scale=0.75, thickness=1):
  cv2.putText(frame, text, orig, cv2.FONT_HERSHEY_PLAIN, scale, color, thickness, cv2.LINE_AA)
  return frame

def get_text_size(text, scale=0.75, thickness=1):
  size = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, scale, thickness)
  width, height = size[0]
  return (width, height)

def draw_line(frame, orig, dest, color=(255, 255, 255), thickness=1):
    cv2.line(frame, orig, dest, color, thickness, cv2.LINE_AA)
    return frame

def draw_line_right_of(frame, orig, length, color=(255, 255, 255), thickness=1):
    return draw_line(frame, orig, (orig[0] + length, orig[1]), color, thickness)

def draw_footer(frame, height):
    frame_height, frame_width, frame_channels = frame.shape
    frame_with_footer = np.zeros((frame_height + height, frame_width, frame_channels), np.uint8)
    frame_with_footer[0:(frame_height - 1), 0:(frame_width - 1)] = frame[0:(frame_height - 1), 0:(frame_width - 1)]
    return frame_with_footer