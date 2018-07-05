import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames

class TrackingVisualizationTool:
    def __init__(self, frames, tracking_result):
        self.frames = frames
        self.tracking_result = tracking_result
        self.selected_track_id = 0
        self.selected_frame_index = 0
        self.selected_footer_view = 1
    
    def render(self):
        img = np.zeros((300, 512, 3), np.uint8)
        return img
    
    def start(self):
        rendered_image = self.render()
        cv2.namedWindow('Tracking Visualization Tool')
        while(1):
            cv2.imshow('image', rendered_image)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
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
