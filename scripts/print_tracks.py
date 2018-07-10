import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import subprocess
import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tracking2 import Track, Transition, TrackingResult
from drawing import draw_bbox_outline, draw_bbox_line_between_centers, draw_bbox_coords, draw_bbox_header, draw_calibration_config, draw_footer, draw_text, get_text_size, draw_line, draw_line_right_of
from frame_bundle import FrameBundle
from cvutil import save_image

AVAILABLE_BBOX_OUTLINE_COLOR = (192, 192, 192)
AVAILABLE_BBOX_OUTLINE_THICKNESS = 1
FILTERED_BBOX_OUTLINE_COLOR = (64, 64, 64)
FILTERED_BBOX_OUTLINE_THICKNESS = 1
DESELECTED_TRACKED_BBOX_OUTLINE_COLOR = (255, 255, 255)
DESELECTED_TRACKED_BBOX_OUTLINE_THICKNESS = 2
SELECTED_TRACKED_BBOX_OUTLINE_COLOR = (255, 225, 75)
SELECTED_TRACKED_BBOX_OUTLINE_THICKNESS = 2
TRANSITION_TRACKED_BBOX_OUTLINE_COLOR = (0, 150, 250)
TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS = 1

def draw_bbox_simple_header(frame, bbox, bg_color=(0, 0, 0), fg_color=(255, 255, 255)):
    header_text = 'Customer #' + ','.join([str(track_id) for track_id in bbox.parent_track_ids])
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

class TrackingVisualizationTool:
    def __init__(self, frame_bundles, tracks, config):
        self.frame_bundles = frame_bundles
        self.frames = [fb.frame for fb in self.frame_bundles]
        self.tracks = tracks
        self.config = config
        # helper transition dict
        self.transition_by_bbox_track_ids = {}
        for track in self.tracks:
            for _, bbox, transition in track.steps:
                self.transition_by_bbox_track_ids[(bbox.id, track.id)] = transition
        # helper bbox dict with bboxes that are inside tracks only
        self.bboxes_by_frame_index = {}
        self.bboxes_by_id = {}
        for index in range(len(self.frames)):
            self.bboxes_by_frame_index[index] = []
            for bbox in self.frame_bundles[index].bboxes:
                self.bboxes_by_id[bbox.id] = bbox
                self.bboxes_by_frame_index[index].append(bbox)
        for track in self.tracks:
            for frame_index, bbox, transition in track.steps:
                if bbox.id not in self.bboxes_by_id:
                    self.bboxes_by_frame_index[frame_index].append(bbox)
                    self.bboxes_by_id[bbox.id] = bbox
    
    def render_bboxes(self, frame, bboxes, transition_by_bbox_track_ids):
        for bbox in bboxes:
            if bbox.is_available():
                frame = draw_bbox_outline(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, AVAILABLE_BBOX_OUTLINE_THICKNESS)
                # frame = draw_bbox_coords(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, offset_y=20)
            elif bbox.is_filtered():
                frame = draw_bbox_outline(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, FILTERED_BBOX_OUTLINE_THICKNESS)
                # frame = draw_bbox_coords(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, offset_y=20)
            else:
                if len(bbox.parent_track_ids) > 0:
                    # transition
                    key = (bbox.id, bbox.parent_track_ids[0])
                    if key not in transition_by_bbox_track_ids:
                        raise RuntimeError('pair (bboxID, selected trackID) not found in transition_by_bbox_track_ids where bboxID={0}, trackID={1}'.format(str(bbox.id), str(self.state['track_id'])))
                    # transition = transition_by_bbox_track_ids[key]
                    # frame = draw_bbox_outline(frame, transition.orig_bbox, TRANSITION_TRACKED_BBOX_OUTLINE_COLOR, TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS)
                    # frame = draw_bbox_line_between_centers(frame, transition.orig_bbox, bbox, TRANSITION_TRACKED_BBOX_OUTLINE_COLOR, TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS)
                    # actual bbox
                    frame = draw_bbox_outline(frame, bbox, SELECTED_TRACKED_BBOX_OUTLINE_COLOR, SELECTED_TRACKED_BBOX_OUTLINE_THICKNESS)
                    # frame = draw_bbox_coords(frame, bbox, SELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                    frame = draw_bbox_simple_header(frame, bbox, bg_color=(50, 50, 50), fg_color=SELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                else:
                    frame = draw_bbox_outline(frame, bbox, DESELECTED_TRACKED_BBOX_OUTLINE_COLOR, DESELECTED_TRACKED_BBOX_OUTLINE_THICKNESS)
                    # frame = draw_bbox_coords(frame, bbox, DESELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                    frame = draw_bbox_simple_header(frame, bbox, bg_color=(25, 25, 25), fg_color=DESELECTED_TRACKED_BBOX_OUTLINE_COLOR)
        return frame
    
    def render_stacked_tracks_footer(self, frame, frame_index): # FIXME refactor
        TEXT_SCALE = 0.5
        frame_height, frame_width, _ = frame.shape
        footer_height = 300
        frame_with_footer = draw_footer(frame, footer_height)
        padding = 5
        space_after_label = 2
        space_between_tracks = 5
        # draw frame line
        max_text = "Frame {}".format(len(self.frames) - 1)
        label_max_size = get_text_size(max_text, scale=TEXT_SCALE)[0] + space_after_label
        line_max_width = frame_width - (2 * padding) - label_max_size
        text = "Frame {}".format(str(frame_index))
        _, text_height = get_text_size(text, scale=TEXT_SCALE)
        current_y = frame_height + padding + text_height
        line_start_x = padding + label_max_size
        text_start_x = padding
        frame_with_footer = draw_text(frame_with_footer, text, (text_start_x, current_y), scale=TEXT_SCALE)
        frame_with_footer = draw_line_right_of(frame_with_footer, (line_start_x, current_y), line_max_width)
        # draw marker
        MARKER_SIZE = 5
        marker_perc = frame_index / len(self.frames)
        marker_offset_x = int(marker_perc * line_max_width)
        frame_with_footer = draw_line(frame_with_footer, (line_start_x + marker_offset_x, current_y - MARKER_SIZE), (line_start_x + marker_offset_x, current_y), color=(0, 0, 255), thickness=3)
        frame_with_footer = draw_line(frame_with_footer, (line_start_x + marker_offset_x, current_y + frame_height), (line_start_x + marker_offset_x, current_y), color=(0, 0, 255), thickness=1)
        # draw tracks
        for track in self.tracks:
            text = 'Customer #' + str(track.id)
            _, text_height = get_text_size(text, scale=TEXT_SCALE)
            current_y += space_between_tracks + text_height
            frame_with_footer = draw_text(frame_with_footer, text, (text_start_x, current_y), scale=TEXT_SCALE)
            if not track.is_empty():
                start_i, end_i = track.get_start_end_indexes()
                line_perc_width = int(((end_i - start_i) / len(self.frames)) * line_max_width)
                line_perc_x = line_start_x + int((start_i / len(self.frames)) * line_max_width)
                frame_with_footer = draw_line_right_of(frame_with_footer, (line_perc_x, current_y), line_perc_width)
        return frame_with_footer

    def get_fresh_frame(self, index):
        orig_frame = self.frames[index]
        orig_height, orig_width, orig_channels = orig_frame.shape
        frame = np.zeros((orig_height, orig_width, orig_channels), np.uint8)
        frame[0:(orig_height - 1), 0:(orig_width - 1)] = orig_frame[0:(orig_height - 1), 0:(orig_width - 1)]
        return frame
    
    def render(self, frame_index):
        frame = self.get_fresh_frame(frame_index)
        frame = self.render_stacked_tracks_footer(frame, frame_index)
        frame = self.render_bboxes(frame, self.bboxes_by_frame_index[frame_index], self.transition_by_bbox_track_ids)
        return frame

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    parser.add_argument('output_dir_path', help='path to the output directory')
    args = parser.parse_args()

    frames = load_frames(args.video_path)
    tr = TrackingResult()
    tr.load_from_json(frames, args.tracking_result_path)
    cfg = load_json('shan/calibration-config.json')
    tool = TrackingVisualizationTool(tr.frame_bundles, tr.tracks, cfg)
    for index in range(len(frames)):
        img = tool.render(index)
        save_image(img, "tracked-frame-{:07}.png".format(index), args.output_dir_path)
        print("Saved frame {:07}".format(index))
    print("Creating video...")

    result = subprocess.call('ffmpeg -framerate 10 -pattern_type glob -i "{}/*.png" -c:v libx264 -r 10 -pix_fmt yuv420p tracked-video.mp4'.format(args.output_dir_path), shell=True)
