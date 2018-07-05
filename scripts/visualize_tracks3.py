import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tracking2 import Transition
from drawing import draw_bbox_outline, draw_bbox_line_between_centers

AVAILABLE_BBOX_OUTLINE_COLOR = (192, 192, 192)
AVAILABLE_BBOX_OUTLINE_THICKNESS = 1
FILTERED_BBOX_OUTLINE_COLOR = (128, 128, 128)
FILTERED_BBOX_OUTLINE_THICKNESS = 1
DESELECTED_TRACKED_BBOX_OUTLINE_COLOR = (255, 255, 255)
DESELECTED_TRACKED_BBOX_OUTLINE_THICKNESS = 2
SELECTED_TRACKED_BBOX_OUTLINE_COLOR = (250, 150, 0)
SELECTED_TRACKED_BBOX_OUTLINE_THICKNESS = 2
TRANSITION_TRACKED_BBOX_OUTLINE_COLOR = (0, 150, 250)
TRANSITION_TRACKED_BBOX_OUTLINE_THICKNESS = 1

class TrackingVisualizationTool:
    def __init__(self, frames, tracking_result):
        self.frames = frames
        self.tracking_result = tracking_result
        # the render function uses the `state` variable to
        # draw the image to be displayed, and nothing else
        self.state = {}
        self.state['track_id'] = 1
        self.state['frame_index'] = 0
        self.state['footer_view'] = 1
    
    def render_bboxes(self, frame, bboxes, transition_by_bbox_track_ids):
        for bbox in bboxes:
            if bbox.is_available():
                frame = draw_bbox_outline(frame, bbox, AVAILABLE_BBOX_OUTLINE_COLOR, AVAILABLE_BBOX_OUTLINE_THICKNESS)
            elif bbox.is_filtered():
                frame = draw_bbox_outline(frame, bbox, FILTERED_BBOX_OUTLINE_COLOR, FILTERED_BBOX_OUTLINE_THICKNESS)
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
                else:
                    frame = draw_bbox_outline(frame, bbox, DESELECTED_TRACKED_BBOX_OUTLINE_COLOR, DESELECTED_TRACKED_BBOX_OUTLINE_THICKNESS)
        return frame
    
    def render(self):
        frame = self.frames[self.state['frame_index']]
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
        frame = self.render_bboxes(frame, bboxes, transition_by_bbox_track_ids)
        return frame
    
    def on_change_frame_index(self, new_value):
        self.state['frame_index'] = new_value
    
    def start(self):
        rendered_image = self.render()
        cv2.namedWindow('shan', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('shan', 800, 200)
        cv2.createTrackbar('frame index', 'shan', 0, len(self.frames), self.on_change_frame_index)
        while(1):
            cv2.imshow('Current frame', rendered_image)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
            if k == 2: # left
                if self.state['frame_index'] > 0:
                    self.state['frame_index'] -= 1
                    cv2.setTrackbarPos('frame index', 'shan', self.state['frame_index'])
            if k == 3: # right
                if self.state['frame_index'] < (len(self.frames) - 1):
                    self.state['frame_index'] += 1
                    cv2.setTrackbarPos('frame index', 'shan', self.state['frame_index'])
            rendered_image = self.render()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    # parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    args = parser.parse_args()

    cfg = load_json('shan/calibration-config.json')

    frames = load_frames(args.video_path)
    # tracking_result = load_json(args.tracking_result_path)
    tracking_result = {}

    tool = TrackingVisualizationTool(frames, tracking_result)
    tool.start()
