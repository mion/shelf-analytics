import json
import argparse
from enum import Enum, unique
import numpy as np 
import cv2
from boundingbox import load_bboxes_per_frame
from humantracking import Track, Transition

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
    def __init__(self, frames, bboxes_per_frame, tracks, params):
        self.frames = frames
        self.bboxes_per_frame = bboxes_per_frame
        self.tracks = tracks
        self.params = params
        self.state = {
            'track_id': 1,
            'frame_index': 0,
            'footer_view': FooterView.calibration.value
        }
    
    def copy_frame(self, index):
        # We need to copy a frame because it's going to be mutated.
        orig_frame = self.frames[index]
        orig_height, orig_width, orig_channels = orig_frame.shape
        frame = np.zeros((orig_height, orig_width, orig_channels), np.uint8)
        frame[0:(orig_height - 1), 0:(orig_width - 1)] = orig_frame[0:(orig_height - 1), 0:(orig_width - 1)]
        return frame
    
    def render_bbox_rect(self, frame, bbox, color=(255, 255, 255), thickness=1):
        top_left = (bbox.x1, bbox.y1) 
        bottom_right = (bbox.x2, bbox.y2)
        cv2.rectangle(frame, top_left, bottom_right, color=color, thickness=thickness)
        return frame
    
    def render_bbox_props(self, frame, bbox, scale=0.75, color=(255, 255, 255), thickness=1, margin=6):
        FONT = cv2.FONT_HERSHEY_PLAIN
        text = '#{:d} ({:d},{:d}) {:d}x{:d} {:d}%'.format(bbox.id, bbox.x1, bbox.y1, bbox.width, bbox.height, int(100 * bbox.score))
        cv2.putText(frame, text, (bbox.x1, bbox.y1 - margin), FONT, scale, color, thickness, cv2.LINE_AA)
        return frame
    
    def render_track_bbox_props(self, frame, bbox, transition, scale=0.75, color=(255, 255, 255), thickness=1, margin=12):
        FONT = cv2.FONT_HERSHEY_PLAIN
        trans_label = {
            Transition.first: 'F',
            Transition.snapped: 'S',
            Transition.tracked: 'T',
            Transition.patched: 'P',
            Transition.interpolated: 'I'
        }[transition]
        text = '<{}> #{:d} ({:d},{:d}) {:d}x{:d}'.format(trans_label, bbox.id, bbox.x1, bbox.y1, bbox.width, bbox.height)
        cv2.putText(frame, text, (bbox.x1, bbox.y2 + margin), FONT, scale, color, thickness, cv2.LINE_AA)
        return frame

    def render_bbox(self, frame, bbox):
        frame = self.render_bbox_rect(frame, bbox)
        frame = self.render_bbox_props(frame, bbox)
        return frame
    
    def render_bboxes(self, frame, bboxes):
        for bbox in bboxes:
            frame = self.render_bbox(frame, bbox)
        return frame
    
    def render_footer_bg(self, frame, footer_height):
        """Renders a black rectangle at the bottom of the frame."""
        frame_height, frame_width, frame_channels = frame.shape
        frame_with_footer = np.zeros((frame_height + footer_height, frame_width, frame_channels), np.uint8)
        frame_with_footer[0:(frame_height - 1), 0:(frame_width - 1)] = frame[0:(frame_height - 1), 0:(frame_width - 1)]
        return frame_with_footer
    
    def get_text_size(self, text, scale=1.0, font=cv2.FONT_HERSHEY_PLAIN, thickness=1):
        size = cv2.getTextSize(text, font, scale, thickness)
        width, height = size[0]
        return (width, height)
    
    def get_text_width(self, text, scale=1.0, font=cv2.FONT_HERSHEY_PLAIN, thickness=1):
        width, _ = self.get_text_size(text, scale, font, thickness)
        return width
    
    def find_max_rendered_size(self, texts, scale=1.0, font=cv2.FONT_HERSHEY_PLAIN, thickness=1):
        """Returns a pair of (max width, max height) from a set of texts when rendered.
        Each value of the pair may come from a different text."""
        max_width, max_height = (0, 0)
        for text in texts:
            width, height = self.get_text_size(text, scale=scale, font=font, thickness=thickness)
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height
        return (max_width, max_height)

    def render_horizontal_line(self, frame, orig, width, color=(255, 255, 255), thickness=1):
        cv2.line(frame, orig, (orig[0] + width, orig[1]), color, thickness, cv2.LINE_AA)
        return frame

    def render_vertical_line(self, frame, orig, height, color=(255, 255, 255), thickness=1):
        cv2.line(frame, orig, (orig[0], orig[1] + height), color, thickness, cv2.LINE_AA)
        return frame
    
    def render_text(self, frame, text, orig, color=(255, 255, 255), scale=1.0, font=cv2.FONT_HERSHEY_PLAIN, thickness=1):
        cv2.putText(frame, text, orig, font, scale, color, thickness, cv2.LINE_AA)
        return frame

    def render_tracks_footer(self, frame):
        TEXT_SCALE = 0.5
        PADDING = 5
        frame_height, frame_width, _ = frame.shape
        labels = ['Frame: {}'.format(len(self.frames) - 1)] + ['Track #{}'.format(track.id) for track in self.tracks]
        max_text_width, max_text_height = self.find_max_rendered_size(labels, scale=TEXT_SCALE)
        # A row is a label followed by a line to its right;
        # The first row has "Frame XYZ" and the rest has "Track ABC";
        row_height = max_text_height + (2 * PADDING)
        footer_height = row_height * (1 + len(self.tracks)) # the 1 is for the header
        line_base_start_x = max_text_width + (2 * PADDING)
        line_max_width = frame_width - line_base_start_x
        rows = [('Frame: {}'.format(self.state['frame_index']), line_base_start_x, line_max_width)]
        for track in tracks:
            if not track.is_empty():
                start_i, end_i = track.get_start_end_indexes()
                line_perc_width = int(((end_i - start_i) / len(self.frames)) * line_max_width)
                line_perc_start_x = line_base_start_x + int((start_i / len(self.frames)) * line_max_width)
                rows.append(('Track #{}'.format(track.id), line_perc_start_x, line_perc_width))
            else:
                rows.append(('Track #{}'.format(track.id), line_base_start_x, 0))
        # Draw rows
        frame_with_footer = self.render_footer_bg(frame, footer_height)
        current_y = frame_height + PADDING + max_text_height # (the first y where we draw is at the bottom of the original frame)
        for text, line_start_x, line_width in rows:
            text_color = (0, 0, 255) if text.startswith('Frame') else (255, 255, 255)
            frame_with_footer = self.render_text(frame_with_footer, text, (PADDING, current_y), color=text_color, scale=TEXT_SCALE)
            line_color = (125, 125, 125) if text.startswith('Frame') else (255, 255, 255)
            frame_with_footer = self.render_horizontal_line(frame_with_footer, (line_start_x, current_y), line_width, color=line_color)
            current_y += row_height
        # Draw marker
        marker_offset_x = int(line_max_width * (self.state['frame_index'] / len(self.frames)))
        frame_with_footer = self.render_vertical_line(frame_with_footer, (line_base_start_x + marker_offset_x, frame_height), footer_height, color=(0, 0, 255))
        return frame_with_footer

    def render_calibration_footer(self, frame):
        TEXT_SCALE = 0.5
        PADDING = 5
        LINE_COLOR = (0, 220, 220) # Yellow (OpenCV uses BGR instead of RGB)
        TEXT_COLOR = (255, 255, 255)
        frame_height, frame_width, _ = frame.shape
        labels = []
        distances = []
        for key, val in self.params.items():
            if key.endswith("_DISTANCE"):
                labels.append(key)
                distances.append(val)
        max_text_width, max_text_height = self.find_max_rendered_size(labels, scale=TEXT_SCALE)
        row_height = (2 * PADDING) + max_text_height
        footer_height = row_height * len(labels)
        line_base_start_x = max_text_width + (2 * PADDING)
        frame_with_footer = self.render_footer_bg(frame, footer_height)
        current_y = frame_height + PADDING + max_text_height
        for i in range(len(labels)):
            label = labels[i]
            distance = distances[i]
            frame_with_footer = self.render_text(frame_with_footer, label, (PADDING, current_y), color=TEXT_COLOR, scale=TEXT_SCALE)
            frame_with_footer = self.render_horizontal_line(frame_with_footer, (line_base_start_x, current_y), distance, color=LINE_COLOR)
            current_y += row_height
        return frame_with_footer

    def render_footer(self, frame):
        if self.state['footer_view'] == FooterView.calibration.value:
            return self.render_calibration_footer(frame)
        elif self.state['footer_view'] == FooterView.tracks.value:
            return self.render_tracks_footer(frame)
        else:
            raise RuntimeError('invalid footer view')
    
    def render_track(self, frame, frame_index, bboxes, track):
        bbox, transition = track.get_bbox_transition_for(frame_index=frame_index)
        frame = self.render_bbox_rect(frame, bbox, color=(0, 255, 0))
        frame = self.render_track_bbox_props(frame, bbox, transition, color=(0, 255, 0))
        return frame
    
    def get_track(self, track_id):
        for track in self.tracks:
            if track.id == track_id:
                return track
        return None
    
    def render(self):
        fr_idx = self.state['frame_index']
        bboxes_in_frame = self.bboxes_per_frame[fr_idx]
        frame = self.copy_frame(fr_idx)
        frame = self.render_bboxes(frame, bboxes_in_frame)
        frame = self.render_footer(frame)
        curr_track = self.get_track(track_id=self.state['track_id'])
        if not curr_track:
            raise RuntimeError('no track found with currently selected track ID')
        if curr_track.exists_at(frame_index=fr_idx):
            self.render_track(frame, fr_idx, bboxes_in_frame, curr_track)
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
    parser.add_argument('--bboxes_path', help='Path to the detected bboxes per frame JSON file')
    parser.add_argument('--params_path', help='Path to the params JSON file')
    # TODO parser.add_argument('--events_path')
    args = parser.parse_args()
    # TODO check for files existance
    loaded_frames = load_frames(path=args.video_path)
    bboxes_json = load_json(args.bboxes_path)
    bboxes = load_bboxes_per_frame(bboxes_json)
    tracks_json = load_json(args.tracks_path)
    params_json = load_json(args.params_path)
    tracks = [Track.parse(t_json) for t_json in tracks_json['tracks']]
    tool = InspectionTool(frames=loaded_frames, bboxes_per_frame=bboxes, tracks=tracks, params=params_json)
    tool.start()
