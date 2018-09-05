import os, sys
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/workers'))
from cv2 import VideoCapture
from cvutil import read_frames_from_video
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat

def load_frames(video_path):
    video = VideoCapture(video_path)
    if not video.isOpened():
        return None
    return read_frames_from_video(video)

def load_frame_bundles(video_path, tags):
    frames = load_frames(video_path)
    frame_bundles = []
    if len(frames) != len(tags['frames']):
        raise RuntimeError('frames array mismatch between tags JSON and original video file')
    for raw_obj in tags['frames']:
        idx = int(raw_obj['frame_index'])
        frame_bundles.append(FrameBundle(frames[idx], raw_obj['frame_index'], raw_obj['boxes'], raw_obj['scores']))
    return frame_bundles
    
class FrameBundle:
    """
    A frame bundle is simply a container for these things:
        - The frame image data loaded with OpenCV.
        - The frame index in the original video.
        - The bounding boxes inside it with the probability of each bounding box being a human.
    """
    def __init__(self, frame, raw_frame_index, raw_bboxes, raw_scores):
        self.frame = frame
        self.frame_index = int(raw_frame_index)
        self.bboxes = []
        for i in range(len(raw_bboxes)):
            bbox = BBox(raw_bboxes[i], BBoxFormat.y1_x1_y2_x2)
            bbox.score = float(raw_scores[i])
            self.bboxes.append(bbox)
    