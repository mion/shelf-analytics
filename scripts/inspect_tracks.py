import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tracking2 import Track, Transition, TrackingResult
from drawing import draw_bbox_outline, draw_bbox_line_between_centers, draw_bbox_coords, draw_bbox_header, draw_calibration_config, draw_footer, draw_text, get_text_size, draw_line, draw_line_right_of
from frame_bundle import FrameBundle

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

class TrackingVisualizationTool:
    FOOTER_VIEW_CALIBRATION = 0
    FOOTER_VIEW_STACKED_TRACKS = 1
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
        # the render function uses the `state` variable to
        # draw the image to be displayed, and nothing else
        self.state = {}
        self.state['track_id'] = 1
        self.state['frame_index'] = 0
        self.state['footer_view'] = TrackingVisualizationTool.FOOTER_VIEW_CALIBRATION
    
    def render_bboxes(self, frame, bboxes, transition_by_bbox_track_ids):
        for bbox in bboxes:
            if bbox.is_available():
                frame = draw_bbox_outline(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, AVAILABLE_BBOX_OUTLINE_THICKNESS)
                frame = draw_bbox_coords(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, offset_y=20)
            elif bbox.is_filtered():
                frame = draw_bbox_outline(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, FILTERED_BBOX_OUTLINE_THICKNESS)
                frame = draw_bbox_coords(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, offset_y=20)
            else:
                if bbox.is_child_of(self.state['track_id']):
                    # transition
                    key = (bbox.id, self.state['track_id'])
                    if key not in transition_by_bbox_track_ids:
                        raise RuntimeError('pair (bboxID, selected trackID) not found in transition_by_bbox_track_ids where bboxID={0}, trackID={1}'.format(str(bbox.id), str(self.state['track_id'])))
                    transition = transition_by_bbox_track_ids[key]
                    # frame = draw_bbox_outline(frame, transition.orig_bbox, TRANSITION_TRACKED_BBOX_OUTLINE_COLOR, TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS)
                    frame = draw_bbox_line_between_centers(frame, transition.orig_bbox, bbox, TRANSITION_TRACKED_BBOX_OUTLINE_COLOR, TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS)
                    # actual bbox
                    frame = draw_bbox_outline(frame, bbox, SELECTED_TRACKED_BBOX_OUTLINE_COLOR, SELECTED_TRACKED_BBOX_OUTLINE_THICKNESS)
                    frame = draw_bbox_coords(frame, bbox, SELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                    frame = draw_bbox_header(frame, bbox, transition, bg_color=(50, 50, 50), fg_color=SELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                else:
                    frame = draw_bbox_outline(frame, bbox, DESELECTED_TRACKED_BBOX_OUTLINE_COLOR, DESELECTED_TRACKED_BBOX_OUTLINE_THICKNESS)
                    frame = draw_bbox_coords(frame, bbox, DESELECTED_TRACKED_BBOX_OUTLINE_COLOR)
                    frame = draw_bbox_header(frame, bbox, transition=None, bg_color=(25, 25, 25), fg_color=DESELECTED_TRACKED_BBOX_OUTLINE_COLOR)
        return frame
    
    def render_calibration_footer(self, frame):
        footer_height = 200
        frame_with_footer = draw_footer(frame, footer_height)
        final_frame = draw_calibration_config(frame_with_footer, footer_height, cfg)
        return final_frame
    
    def render_stacked_tracks_footer(self, frame): # FIXME refactor
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
        text = "Frame {}".format(str(self.state['frame_index']))
        _, text_height = get_text_size(text, scale=TEXT_SCALE)
        current_y = frame_height + padding + text_height
        line_start_x = padding + label_max_size
        text_start_x = padding
        frame_with_footer = draw_text(frame_with_footer, text, (text_start_x, current_y), scale=TEXT_SCALE)
        frame_with_footer = draw_line_right_of(frame_with_footer, (line_start_x, current_y), line_max_width)
        # draw marker
        MARKER_SIZE = 5
        marker_perc = self.state['frame_index'] / len(self.frames)
        marker_offset_x = int(marker_perc * line_max_width)
        frame_with_footer = draw_line(frame_with_footer, (line_start_x + marker_offset_x, current_y - MARKER_SIZE), (line_start_x + marker_offset_x, current_y), color=(0, 0, 255), thickness=3)
        # draw tracks
        for track in self.tracks:
            text = 'Track #' + str(track.id)
            _, text_height = get_text_size(text, scale=TEXT_SCALE)
            current_y += space_between_tracks + text_height
            frame_with_footer = draw_text(frame_with_footer, text, (text_start_x, current_y), scale=TEXT_SCALE)
            if not track.is_empty():
                start_i, end_i = track.get_start_end_indexes()
                line_perc_width = int(((end_i - start_i) / len(self.frames)) * line_max_width)
                line_perc_x = line_start_x + int((start_i / len(self.frames)) * line_max_width)
                frame_with_footer = draw_line_right_of(frame_with_footer, (line_perc_x, current_y), line_perc_width)
        return frame_with_footer

    def render_footer(self, frame):
        if self.state['footer_view'] == TrackingVisualizationTool.FOOTER_VIEW_CALIBRATION:
            return self.render_calibration_footer(frame)
        elif self.state['footer_view'] == TrackingVisualizationTool.FOOTER_VIEW_STACKED_TRACKS:
            return self.render_stacked_tracks_footer(frame)
        else:
            raise RuntimeError('invalid selected footer view')

    def get_fresh_frame(self, index):
        orig_frame = self.frames[index]
        orig_height, orig_width, orig_channels = orig_frame.shape
        frame = np.zeros((orig_height, orig_width, orig_channels), np.uint8)
        frame[0:(orig_height - 1), 0:(orig_width - 1)] = orig_frame[0:(orig_height - 1), 0:(orig_width - 1)]
        return frame
    
    def render(self):
        frame = self.get_fresh_frame(self.state['frame_index'])
        frame = self.render_footer(frame)
        # bboxes = self.frame_bundles[self.state['frame_index']].bboxes
        frame = self.render_bboxes(frame, self.bboxes_by_frame_index[self.state['frame_index']], self.transition_by_bbox_track_ids)
        return frame
    
    def on_change_frame_index(self, new_value):
        self.state['frame_index'] = new_value

    def on_change_track_id(self, new_value):
        self.state['track_id'] = new_value + 1
        print('Track ID = {}'.format(self.state['track_id']))
    
    def on_change_footer_view(self, new_value):
        self.state['footer_view'] = new_value
    
    def start(self):
        cv2.namedWindow('shan', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('shan', 800, 200)
        cv2.createTrackbar('Frame Index', 'shan', 0, len(self.frames) - 1, self.on_change_frame_index)
        cv2.createTrackbar('Track ID', 'shan', 0, len(self.tracks) - 1, self.on_change_track_id)
        cv2.createTrackbar('Footer View', 'shan', 0, 1, self.on_change_footer_view)
        while(1):
            cv2.imshow('Current frame', self.render())
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
            if k == 2: # left
                if self.state['frame_index'] > 0:
                    self.state['frame_index'] -= 1
                    cv2.setTrackbarPos('Frame Index', 'shan', self.state['frame_index'])
            if k == 3: # right
                if self.state['frame_index'] < (len(self.frames) - 1):
                    self.state['frame_index'] += 1
                    cv2.setTrackbarPos('Frame Index', 'shan', self.state['frame_index'])
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    args = parser.parse_args()

    frames = load_frames(args.video_path)
    tr = TrackingResult()
    tr.load_from_json(frames, args.tracking_result_path)

    # tracking_result = load_json(args.tracking_result_path)
    # # Assemble test setup
    # bboxes_per_frame = [[] for frame in frames]
    # scores_per_frame = [[] for frame in frames]
    # frame_bundles = []
    # frame_index = 0
    # for frame in frames:
    #     fb = FrameBundle(frame, frame_index, bboxes_per_frame[frame_index], scores_per_frame[frame_index])
    #     frame_bundles.append(fb)
    #     frame_index += 1
    # tracks = [
    #     Track(),
    #     Track(),
    #     Track()
    # ]
    # # add one bbox on frame 0
    # b1 = BBox([100, 100, 50, 100], BBoxFormat.x1_y1_w_h)
    # b1.score = 0.987
    # frame_bundles[0].bboxes.append(b1)
    # tracks[0].add(0, b1, Transition('first', b1, 0))
    # # b2 = BBox([300, 300, 50, 100], BBo
    # # frame_bundles[1].bboxes.append(BBox([120, 110, 50, 100], BBoxFormat.x1_y1_w_h))
    # # frame_bundles[2].bboxes.append(BBox([140, 120, 50, 100], BBoxFormat.x1_y1_w_h))

    cfg = load_json('shan/calibration-config.json')
    tool = TrackingVisualizationTool(tr.frame_bundles, tr.tracks, cfg)
    tool.start()
