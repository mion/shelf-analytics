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
        # the render function uses the `state` variable to
        # draw the image to be displayed, and nothing else
        self.state = {}
        self.state['track_id'] = 0
        self.state['frame_index'] = 0
        self.state['footer_view'] = 1
    
    def render(self):
        # img = np.zeros((300, 512, 3), np.uint8)
        return self.frames[self.state['frame_index']]
    
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
