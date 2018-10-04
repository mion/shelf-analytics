import os, sys
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
import json
import math

from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from bounding_box_filter import BoundingBoxFilter as BBoxFilter
from util import load_json, create_object_tracker
from frame_bundle import FrameBundle

def track_humans(calib, frame_bundles, max_tracks):
    #
    # FIXME implicit exporting of tracking-result is bad
    #
    """This exports a tracking-result.json file at the same path of the tracks.json file"""
    print('Filtering bounding boxes inside frame bundles...')
    bbox_filter = BBoxFilter(calib)
    for frame_bundle in frame_bundles:
        bbox_filter.filter_frame_bundle(frame_bundle)
    print('Analyzing tracks...')
    tracking_result, analyzer = compute_tracking_result(calib, frame_bundles, max_tracks)
    print('Exporting tracks...')
    return ([track.to_dict() for track in analyzer.tracks], tracking_result)

def compute_tracking_result(calib, frame_bundles, max_track_count):
    analyzer = HumanTrackAnalyzer(calib, frame_bundles)
    tracks = analyzer.find_all_tracks(max_track_count)
    return (TrackingResult(tracks, frame_bundles), analyzer)

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

def normalized_direction(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    norm = math.sqrt((dx * dx) + (dy * dy))
    return (dx / norm, dy / norm)

class HumanTrackAnalyzer:
    """
    A track represents a bounding box that was identified as being the
    same person across a sequence of frames.
    """
    def __init__(self, calib, frame_bundles):
        self.calib = calib
        self.frame_bundles = frame_bundles
        self.tracks = []
        self.tracker = None
        self.bboxes_per_frame = []
        for index in range(len(self.frame_bundles)):
            self.bboxes_per_frame.append([])
            for bbox in self.frame_bundles[index].bboxes:
                self.bboxes_per_frame[index].append(bbox)

    def get_frame_at(self, index):
        return self.frame_bundles[index].frame

    def get_bboxes_at(self, index):
        return self.frame_bundles[index].bboxes
    
    def get_frames_count(self):
        return len(self.frame_bundles)

    def start_tracker(self, frame, bbox):
        if self.tracker is not None:
            self.tracker.clear()
        tracker = create_object_tracker('KCF')
        ok = tracker.init(frame, bbox.to_tuple(BBoxFormat.x1_y1_w_h))
        if not ok:
            raise RuntimeError('failed to init OpenCV tracker')
        return tracker
    
    def add_to_track(self, track, index, bbox, transition):
        track.add(index, bbox, transition)
        bbox.parent_track_ids.append(track.id)
        if bbox.id not in [b.id for b in self.bboxes_per_frame[index]]:
            self.bboxes_per_frame[index].append(bbox)

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

        # for index in range(start_index + 1, self.get_frames_count()):
        index = start_index + 1
        while index < self.get_frames_count():
            current_frame = self.get_frame_at(index)
            ok, xywh_tuple = self.tracker.update(current_frame)
            if ok: # tracker manage to keep track of a bbox, let's try to snap onto it
                tracker_bbox = BBox(xywh_tuple, BBoxFormat.x1_y1_w_h)
                snap_bbox, snap_distance = self.find_bbox_to_snap(index, tracker_bbox, self.calib['MAX_SNAP_DISTANCE'])
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
                far_snap_bbox, far_snap_distance = self.find_bbox_to_snap(index, last_bbox, self.calib['MAX_TRACKER_FAILED_SNAP_DISTANCE'])
                if far_snap_bbox is not None:
                    print("\t(retaken) at frame {0} moved to bbox {1}".format(index, far_snap_bbox))
                    self.add_to_track(track, index, far_snap_bbox, Transition('retaken', last_bbox, far_snap_distance))
                    self.tracker = self.start_tracker(current_frame, far_snap_bbox)
                    last_bbox = far_snap_bbox
                else:
                    print("\ttrack lost at frame {0}".format(index))
                    LOOK_AHEAD_MAX_SNAP_DISTANCE = 50
                    target_index, target_bbox = self.look_ahead(track, index, max_front_hops=4, max_back_hops=20, threshold_distance=LOOK_AHEAD_MAX_SNAP_DISTANCE)
                    if target_index is not None and target_bbox is not None:
                        print("\t\tlook ahead found target {} at index {}".format(str(target_bbox), str(target_index)))
                        delta_per_hop = (last_bbox.distance_to(target_bbox) / ((target_index - index) + 1))
                        dir_vec = normalized_direction(last_bbox.center, target_bbox.center) 
                        print("\t\twalking {} pixels in direction ({},{})".format(str(delta_per_hop), str(dir_vec[0]), str(dir_vec[1])))
                        curr_x = last_bbox.x1
                        curr_y = last_bbox.y1
                        past_bbox = last_bbox
                        print("\t\tstarting on frame {} at ({},{})".format(str(index), str(curr_x), str(curr_y)))
                        for idx in range(index, target_index):
                            curr_x += int(dir_vec[0] * delta_per_hop)
                            curr_y += int(dir_vec[1] * delta_per_hop)
                            interpolated_bbox = BBox([curr_x, curr_y, last_bbox.width, last_bbox.height], BBoxFormat.x1_y1_w_h)
                            self.add_to_track(track, idx, interpolated_bbox, Transition('interpol', past_bbox, past_bbox.distance_to(interpolated_bbox)))
                            print("\t\t(interpol) at frame {} moved to {} (track {})".format(str(idx), str(interpolated_bbox), str(track.id)))
                            past_bbox = interpolated_bbox
                        self.tracker = self.start_tracker(self.frame_bundles[target_index - 1].frame, past_bbox)
                        last_bbox = past_bbox
                        index = target_index - 1
                    else:
                        print("\t\tlook ahead FAILED")
                        break
            index += 1
        self.tracks.append(track)
        print("done tracking human, tracks found: {0}".format(str(len(self.tracks))))
        return True
    
    def look_ahead(self, track, base_index, max_front_hops, max_back_hops, threshold_distance):
        start_i = len(track.steps) - max_back_hops
        avg_vel_x = 0
        avg_vel_y = 0
        back_hops = 0
        for i in range(start_i if start_i >= 0 else 0, len(track.steps) - 1):
            _, bbox, _ = track.steps[i]
            _, next_bbox, _ = track.steps[i + 1]
            avg_vel_x += (next_bbox.center[0] - bbox.center[0])
            avg_vel_y += (next_bbox.center[1] - bbox.center[1])
            back_hops += 1
        if back_hops > 0:
            avg_vel_x = int(avg_vel_x / back_hops)
            avg_vel_y = int(avg_vel_y / back_hops)
        CORRECTION_FACTOR = 2.5 # bc bboxes change shape
        avg_vel = (CORRECTION_FACTOR * avg_vel_x, CORRECTION_FACTOR * avg_vel_y)
        print("\t\t\tavg vel for the past {} hops is ({}, {})".format(back_hops, avg_vel[0], avg_vel[1]))
        _, tail_bbox, _ = track.steps[len(track.steps) - 1]
        translocated_center = [tail_bbox.center[0], tail_bbox.center[1]]
        target_bbox = None
        target_index = None
        for index in range(base_index, min(base_index + max_front_hops + 1, len(self.frame_bundles))):
            translocated_center[0] += avg_vel[0]
            translocated_center[1] += avg_vel[1]
            print("\t\t\tat frame {} looking for candidates around ({})".format(index, translocated_center))
            # search for the closest candidate
            closest_distance = 9999999
            closest_bbox = None
            for bbox in self.frame_bundles[index].bboxes:
                if bbox.is_filtered() or not bbox.is_available():
                    continue
                distance = bbox.distance_to_point(translocated_center)
                if distance < threshold_distance and distance < closest_distance:
                    closest_bbox = bbox
                    closest_distance = distance
            if closest_bbox is not None:
                target_bbox = closest_bbox
                target_index = index
                break
        if target_bbox is not None and target_index is not None:
            return (target_index, target_bbox)
        else:
            return (None, None)

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
    
    def is_in_intersection(self, base_bbox, index):
        INTERSECTION_AREA_PERC_THRESHOLD = 0.50
        for bbox in self.bboxes_per_frame[index]:
            if bbox.id == base_bbox.id: # same bbox
                continue
            if bbox.intersection_area(base_bbox) is None: # no intersection
                continue
            area_perc = bbox.intersection_area(base_bbox) / base_bbox.area
            area_perc_vice_versa = bbox.intersection_area(base_bbox) / bbox.area
            if area_perc > INTERSECTION_AREA_PERC_THRESHOLD or area_perc_vice_versa > INTERSECTION_AREA_PERC_THRESHOLD:
                return True
        return False

    def find_available_bbox(self):
        for index in range(self.get_frames_count()):
            for bbox in self.get_bboxes_at(index):
                if not bbox.is_filtered() and bbox.is_available() and not self.is_in_intersection(bbox, index):
                    return (index, bbox)
        return None
