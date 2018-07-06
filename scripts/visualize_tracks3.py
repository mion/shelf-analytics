import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tracking2 import Track, Transition
from drawing import draw_bbox_outline, draw_bbox_line_between_centers, draw_bbox_coords, draw_bbox_header, draw_calibration_config, draw_footer, draw_text
from frame_bundle import FrameBundle

AVAILABLE_BBOX_OUTLINE_COLOR = (192, 192, 192)
AVAILABLE_BBOX_OUTLINE_THICKNESS = 1
FILTERED_BBOX_OUTLINE_COLOR = (128, 128, 128)
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
    def __init__(self, frames, tracks, config):
        self.frames = frames
        self.tracks = tracks
        self.config = config
        # the render function uses the `state` variable to
        # draw the image to be displayed, and nothing else
        self.state = {}
        self.state['track_id'] = 0
        self.state['frame_index'] = 0
        self.state['footer_view'] = TrackingVisualizationTool.FOOTER_VIEW_CALIBRATION
    
    def render_bboxes(self, frame, bboxes, transition_by_bbox_track_ids):
        for bbox in bboxes:
            if bbox.is_available():
                frame = draw_bbox_outline(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, AVAILABLE_BBOX_OUTLINE_THICKNESS)
                frame = draw_bbox_coords(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR)
            elif bbox.is_filtered():
                frame = draw_bbox_outline(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, FILTERED_BBOX_OUTLINE_THICKNESS)
                frame = draw_bbox_coords(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR)
            else:
                if bbox.is_child_of(self.state['track_id']):
                    # transition
                    key = (bbox.id, self.state['track_id'])
                    if key not in transition_by_bbox_track_ids:
                        raise RuntimeError('pair (bboxID, selected trackID) not found in transition_by_bbox_track_ids where bboxID={0}, trackID={1}'.format(str(bbox.id), str(self.state['track_id'])))
                    transition = transition_by_bbox_track_ids[key]
                    frame = draw_bbox_outline(frame, transition.orig_bbox, TRANSITION_TRACKED_BBOX_OUTLINE_COLOR, TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS)
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
    
    def render_stacked_tracks_footer(self, frame):
        footer_height = 200
        frame_with_footer = draw_footer(frame, footer_height)
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
        # begintest
        past_bbox = BBox([90, 90, 300, 200], BBoxFormat.x1_y1_w_h)
        past_bbox.id = 120
        past_bbox.parent_track_ids.append(1)
        bboxes = [
            BBox([100, 100, 300, 200], BBoxFormat.x1_y1_w_h)    
        ]
        bboxes[0].id = 123
        bboxes[0].parent_track_ids.append(1)
        transition_by_bbox_track_ids = {
            (123, 1): Transition('snapped', past_bbox, past_bbox.distance_to(bboxes[0]))
        }
        # endtest
        frame = self.render_footer(frame)
        frame = self.render_bboxes(frame, bboxes, transition_by_bbox_track_ids)
        return frame
    
    def on_change_frame_index(self, new_value):
        self.state['frame_index'] = new_value

    def on_change_track_id(self, new_value):
        self.state['track_id'] = new_value
    
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

def _create_bbox(x, y):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    # parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    args = parser.parse_args()

    cfg = load_json('shan/calibration-config.json')

    frames = load_frames(args.video_path)
    # tracking_result = load_json(args.tracking_result_path)
    # Assemble test setup
    bboxes_per_frame = [[] for frame in frames]
    scores_per_frame = [[] for frame in frames]
    frame_bundles = []
    frame_index = 0
    for frame in frames:
        fb = FrameBundle(frame, frame_index, bboxes_per_frame[frame_index], scores_per_frame[frame_index])
        frame_bundles.append(fb)
        frame_index += 1
    tracks = [
        Track(),
        Track(),
        Track()
    ]
    # add one bbox on frame 0
    b1 = BBox([100, 100, 50, 100], BBoxFormat.x1_y1_w_h)
    b1.score = 0.987
    frame_bundles[0].bboxes.append(b1)
    tracks[0].add(0, b1, Transition('first', b1, 0))
    # b2 = BBox([300, 300, 50, 100], BBo
    # frame_bundles[1].bboxes.append(BBox([120, 110, 50, 100], BBoxFormat.x1_y1_w_h))
    # frame_bundles[2].bboxes.append(BBox([140, 120, 50, 100], BBoxFormat.x1_y1_w_h))

    tool = TrackingVisualizationTool(frames, tracks, cfg)
    tool.start()
