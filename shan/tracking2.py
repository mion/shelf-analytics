import pdb

from cvutil import create_object_tracker
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tnt import load_json
from frame_bundle import FrameBundle
import json

cfg = load_json('shan/calibration-config.json')

def extract_tracks(frame_bundles, max_track_count):
    analyzer = HumanTrackAnalyzer(frame_bundles)
    tracks = analyzer.find_all_tracks(max_track_count)
    return [track.to_dict() for track in tracks]

def compute_tracking_result(frame_bundles, max_track_count):
    analyzer = HumanTrackAnalyzer(frame_bundles)
    tracks = analyzer.find_all_tracks(max_track_count)
    return TrackingResult(tracks, frame_bundles)

class TrackingResult: #FIXME refactor
    def __init__(self, tracks=None, frame_bundles=None):
        self.tracks = [] if tracks is None else tracks
        self.frame_bundles = [] if frame_bundles is None else frame_bundles
    
    def save_as_json(self, path):
        result = {}
        result['frame_bundles'] = []
        for bundle in self.frame_bundles:
            result['frame_bundles'].append({
                'frame_index': bundle.frame_index,
                'bboxes': [bbox.to_json() for bbox in bundle.bboxes]
            })
        result['tracks'] = []
        for track in self.tracks:
            result['tracks'].append(track.to_json())
        with open(path, 'w')  as output_file:
            json.dump(result, output_file)
    
    def load_from_json(self, frames, path):
        self.tracks = []
        self.frame_bundles = []
        result = load_json(path)
        bbox_by_id = {}
        for bundle_json in result['frame_bundles']:
            idx = int(bundle_json['frame_index'])
            frame_bundle = FrameBundle(frames[idx], idx, [], [])
            for bbox_json in bundle_json['bboxes']:
                bbox = BBox.from_json(bbox_json)
                # bbox = BBox(bbox_json['y1_x1_y2_x2'], BBoxFormat.y1_x1_y2_x2)
                # bbox.id = bbox_json['id']
                # bbox.score = bbox_json['score']
                # bbox.filtering_results = bbox_json['filtering_results']
                # bbox.parent_track_ids = bbox_json['parent_track_ids']
                frame_bundle.bboxes.append(bbox)
                bbox_by_id[bbox.id] = bbox
            self.frame_bundles.append(frame_bundle)
        for track_json in result['tracks']:
            track = Track()
            track.id = track_json['id']
            for step_json in track_json['steps']:
                index, bbox_json, transition_json = step_json
                bbox = None
                if bbox_json['id'] in bbox_by_id:
                    bbox = bbox_by_id[bbox_json['id']]
                else:
                    bbox = BBox.from_json(bbox_json)
                    bbox_by_id[bbox.id] = bbox
                orig_bbox = BBox.from_json(transition_json['from_bbox'])
                if orig_bbox not in bbox_by_id:
                    bbox_by_id[orig_bbox.id] = orig_bbox
                transition = Transition(transition_json['type'], bbox_by_id[orig_bbox.id], transition_json['distance'])
                track.add(index, bbox, transition)
            self.tracks.append(track)

class Track:
    next_track_id = 1
    def __init__(self):
        self.id = Track.next_track_id
        Track.next_track_id += 1
        self.steps = []
    
    def add(self, index, bbox, transition):
        self.steps.append((index, bbox, transition))
    
    def is_empty(self):
        return len(self.steps) == 0
    
    def get_start_end_indexes(self):
        if self.is_empty():
            raise RuntimeError('trying to get start and end indexes from empty track')
        first_step = self.steps[0]
        last_step = self.steps[len(self.steps) - 1]
        start_index, _, _ = first_step
        end_index, _, _ = last_step
        return (start_index, end_index)
    
    def to_dict(self):
        return [{'index': i, 'bbox': [int(n) for n in b.to_tuple(BBoxFormat.y1_x1_y2_x2)], 'transition': t.to_dict()} for i, b, t in self.steps]
    
    def to_json(self):
        return {
            'id': self.id,
            'steps': [[index, bbox.to_json(), transition.to_json()] for index, bbox, transition in self.steps]
        }

class Transition:
    def __init__(self, kind, orig_bbox, distance):
        self.kind = kind
        self.orig_bbox = orig_bbox
        self.distance = distance
    
    def to_dict(self):
        return {
            'type': self.kind,
            'from_bbox': [int(n) for n in self.orig_bbox.to_tuple(BBoxFormat.y1_x1_y2_x2)],
            'distance': self.distance
        }
    
    def to_json(self):
        return {
            'type': self.kind,
            'from_bbox': self.orig_bbox.to_json(),
            'distance': self.distance
        }

class HumanTrackAnalyzer:
    """
    A track represents a bounding box that was identified as being the
    same person across a sequence of frames.
    """
    def __init__(self, frame_bundles):
        self.frame_bundles = frame_bundles
        self.tracks = []
        self.tracker = None

    def get_frame_at(self, index):
        return self.frame_bundles[index].frame

    def get_bboxes_at(self, index):
        return self.frame_bundles[index].bboxes
    
    def get_frames_count(self):
        return len(self.frame_bundles)

    def start_tracker(self, frame, bbox):
        tracker = create_object_tracker('KCF')
        tracker.init(frame, bbox.to_tuple(BBoxFormat.x1_y1_w_h))
        return tracker
    
    def add_to_track(self, track, index, bbox, transition):
        track.add(index, bbox, transition)
        bbox.parent_track_ids.append(track.id)

    def find_all_tracks(self, max_track_count):
        track_count = 0
        has_untracked_humans = True
        while track_count < max_track_count and has_untracked_humans:
            has_untracked_humans = self.find_some_track()
            track_count += 1
        return self.tracks

    def find_some_track(self):
        print("searching untracked humans...")
        pair = self.find_available_bbox()
        if pair is None:
            print("all humans have been tracked")
            return False
        start_index, last_bbox = pair

        print("found someone at frame {0} at bbox {1}".format(str(start_index), str(last_bbox)))
        start_frame = self.get_frame_at(start_index)
        self.tracker = self.start_tracker(start_frame, last_bbox)
        track = Track()
        self.add_to_track(track, start_index, last_bbox, Transition('first', last_bbox, 0))

        print("tracking human:")
        for index in range(start_index + 1, self.get_frames_count()):
            current_frame = self.get_frame_at(index)
            ok, xywh_tuple = self.tracker.update(current_frame)
            if ok: # tracker manage to keep track of a bbox, let's try to snap onto it
                tracker_bbox = BBox(xywh_tuple, BBoxFormat.x1_y1_w_h)
                snap_bbox, snap_distance = self.find_bbox_to_snap(index, tracker_bbox, cfg['MAX_SNAP_DISTANCE'])
                if snap_bbox is not None:
                    print("\t(snapped) at frame {0} moved to bbox {1}".format(index, snap_bbox))
                    self.add_to_track(track, index, snap_bbox, Transition('snapped', last_bbox, snap_distance))
                    self.tracker = self.start_tracker(current_frame, snap_bbox)
                    last_bbox = snap_bbox
                else: # could not snap, let's go with whatever the tracker found
                    print("\t(tracked) at frame {0} moved to bbox {1}".format(index, tracker_bbox))
                    self.add_to_track(track, index, tracker_bbox, Transition('tracked', last_bbox, last_bbox.distance_to(tracker_bbox)))
                    last_bbox = tracker_bbox
            else: # tracker failed, try to find some available bbox nearby
                far_snap_bbox, far_snap_distance = self.find_bbox_to_snap(index, last_bbox, cfg['MAX_TRACKER_FAILED_SNAP_DISTANCE'])
                if far_snap_bbox is not None:
                    print("\t(retaken) at frame {0} moved to bbox {1}".format(index, far_snap_bbox))
                    self.add_to_track(track, index, far_snap_bbox, Transition('retaken', last_bbox, far_snap_distance))
                    self.tracker = self.start_tracker(current_frame, snap_bbox)
                    last_bbox = far_snap_bbox
                else:
                    print("\ttrack lost at frame {0}".format(index))
                    break
        self.tracks.append(track)
        print("done tracking human, tracks found: {0}".format(str(len(self.tracks))))
        return True

    def find_bbox_to_snap(self, index, base_bbox, max_snap_distance):
        closest_distance = 9999999 # FIXME
        closest_bbox = None
        for bbox in self.get_bboxes_at(index):
            if bbox.is_filtered() or not bbox.is_available():
                continue
            distance = base_bbox.distance_to(bbox)
            if distance < max_snap_distance and distance < closest_distance:
                closest_bbox = bbox
                closest_distance = distance
        return (closest_bbox, closest_distance)

    def find_available_bbox(self):
        for index in range(self.get_frames_count()):
            for bbox in self.get_bboxes_at(index):
                if not bbox.is_filtered() and bbox.is_available():
                    return (index, bbox)
        return None
