import unittest
import json
import cv2
from point import Point
from boundingbox import BBox, load_bboxes_per_frame
from humantracking import track_humans
from eventextraction import RegionOfInterest as Roi, EventType, extract_events

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

class TraverseTest(unittest.TestCase):
    def test_traverse_simple(self):
        json_path = '/Users/gvieira/shan-test/traverse-simple.json'
        raw_json = load_json(json_path)
        bboxes_per_frame = load_bboxes_per_frame(raw_json)
        video_path = '/Users/gvieira/shan-test/traverse-simple.mp4'
        frames = load_frames(video_path)
        if len(frames) != len(bboxes_per_frame):
            raise RuntimeError('frames and bboxes per frame lists have different length')
        # TODO
        # The `bboxes_per_frame` of the tracking module is different
        # from the `bboxes_per_frame` that comes from the object 
        # detection JSON. This is confusing and should be fixed.
        bboxes_per_frame = []
        for idx, frame in enumerate(frames):
            bboxes_per_frame.append((frame, bboxes_per_frame[idx]))
        params = {
            'MAX_TRACK_COUNT': 40,
            'OPENCV_OBJ_TRACKER_TYPE': 'KCF',
            'MIN_OBJ_DET_SCORE': 0.8,
            'MIN_BBOX_AREA': 5000,
            'MAX_BBOX_AREA': 15000,
            'MAX_INTERSEC_AREA_PERC': 0.25,
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 50,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 150,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 5,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 5
        }
        tracks = track_humans(bboxes_per_frame, params)

        # <hack> save this to test the inspection tool
        with open('traverse-simple-track.json', 'w') as f:
            json.dump({'tracks': [track.to_dict() for track in tracks]}, f)
        # </hack>

        self.assertEqual(len(tracks), 1)
        self.assertGreater(len(tracks[0]), 40)
        self.assertLess(tracks[0].get_step(0).frame_index, 30)
        self.assertGreater(tracks[0].get_last_step().frame_index, 110)
        rois = [
            Roi('aisle', BBox(Point(176, 125), 219, 120), [EventType.traverse])
        ]
        
        # <hack> save this to test the inspection tool
        with open('traverse-simple-rois.json', 'w') as f:
            json.dump({'rois': [roi.to_dict() for roi in rois]}, f)
        # </hack>

        bboxes_per_track = [track.get_bboxes() for track in tracks]
        params_for_event_type = {
            EventType.traverse: {'min_duration': 20, 'min_area': 10000}
        }
        events = extract_events(bboxes_per_track, rois, params_for_event_type)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].type, EventType.traverse)
        self.assertEqual(events[0].roi_name, 'aisle')
        self.assertGreater(events[0].index, 50)
        self.assertLess(events[0].index, 90)

if __name__ == '__main__':
    unittest.main()
