import json
import argparse
from enum import Enum, unique
import numpy as np 
import cv2

def load_json(path):
    with open(path, "r") as file:
        return json.loads(file.read())

def read_frames_from_video(video):
    is_first_frame = True
    frames = []
    while True:
        ok, frame = video.read()
        if not ok and is_first_frame:
            return None
        elif not ok and not is_first_frame:
            break
        else:
            is_first_frame = False
            frames.append(frame)
    return frames

def load_frames(path):
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        return None
    return read_frames_from_video(video)

@unique
class FooterView(Enum):
    calibration = 0
    tracks = 1

class InspectionTool:
    def __init__(self, frames):
        self.frames = frames
        self.tracks = [1, 2, 3]
        self.state = {
            'track_id': 1,
            'frame_index': 0,
            'footer_view': FooterView.calibration
        }
    
    def copy_frame(self, index):
        orig_frame = self.frames[index]
        orig_height, orig_width, orig_channels = orig_frame.shape
        frame = np.zeros((orig_height, orig_width, orig_channels), np.uint8)
        frame[0:(orig_height - 1), 0:(orig_width - 1)] = orig_frame[0:(orig_height - 1), 0:(orig_width - 1)]
        return frame
    
    def render(self):
        frame = self.copy_frame(self.state['frame_index'])
        # frame = self.render_footer(frame)
        # frame = self.render_bboxes(frame, self.bboxes_by_frame_index[self.state['frame_index']], self.transition_by_bbox_track_ids)
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
            current_rendered_frame = self.render()
            cv2.imshow('Inspection Tool', current_rendered_frame)
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
    parser.add_argument('video_path', help='Path to the video file')
    parser.add_argument('--tracks_path', help='Path to the tracks JSON file')
    parser.add_argument('--rois_path', help='Path to the ROIs JSON file')
    parser.add_argument('--det_bboxes_path', help='Path to the detected bboxes per frame JSON file')
    # TODO parser.add_argument('--events_path')
    args = parser.parse_args()

    loaded_frames = load_frames(path=args.video_path)
    tool = InspectionTool(frames=loaded_frames)
    tool.start()
