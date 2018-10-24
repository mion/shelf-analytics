import math
from boundingbox import BBox, Format, DetectedBBox

class Track:
    def __init__(self):
        self.steps = []

    def add(self, frame_index, bbox, transition):
        # We can't use the bbox index here because we may want to add a bbox
        # that wasn't detected (it may be have come from object tracking or
        # the look ahead/interpolation algorithm).
        self.steps.append((frame_index, bbox, transition))
    
    def get_last_bbox(self):
        # TODO implement this
        return None

from enum import Enum
class Transition(Enum):
    first = 1
    snapped = 2
    tracked = 3
    patched = 4
    interpolated = 5

class ObjectTracker:
    def __init__(self, frame, bbox, opencv_obj_tracker_type):
        self._opencv_obj_tracker_type = opencv_obj_tracker_type
        self.opencv_tracker = self._create_opencv_tracker(opencv_obj_tracker_type)
        ok = self.opencv_tracker.init(frame, bbox.to_tuple(Format.x1_y1_w_h))
        if not ok:
            raise RuntimeError('failed to init OpenCV tracker')

    def update(self, frame):
        ok, xywh_tuple = self.opencv_tracker.update(frame)
        if ok:
            return BBox(xywh_tuple, Format.x1_y1_w_h)
        else:
            return None

    def restart(self, frame, bbox):
        self.opencv_tracker.clear()
        self.opencv_tracker = self._create_opencv_tracker(self._opencv_obj_tracker_type)
        ok = self.opencv_tracker.init(frame, bbox.to_tuple(Format.x1_y1_w_h))
        if not ok:
            raise RuntimeError('failed to restart OpenCV tracker')

    def _create_opencv_tracker(self, obj_tracker_type):
        major_ver, minor_ver, subminor_ver = cv2.__version__.split(".")
        if int(minor_ver) < 3:
            return cv2.Tracker_create(obj_tracker_type)
        else:
            if obj_tracker_type == 'BOOSTING':
                return cv2.TrackerBoosting_create()
            elif obj_tracker_type == 'MIL':
                return cv2.TrackerMIL_create()
            elif obj_tracker_type == 'KCF':
                return cv2.TrackerKCF_create()
            elif obj_tracker_type == 'TLD':
                return cv2.TrackerTLD_create()
            elif obj_tracker_type == 'MEDIANFLOW':
                return cv2.TrackerMedianFlow_create()
            elif obj_tracker_type == 'GOTURN':
                return cv2.TrackerGOTURN_create()
            else:
                raise RuntimeError("invalid object tracker type")

def track_humans(bboxes_per_frame, config, params):
    """
    bboxes_per_frame is a list of pairs:
        (frame, bboxes)
    """
    is_filtered = filter_bboxes(bboxes_per_frame)
    tracks = find_all_tracks(bboxes_per_frame, is_filtered, params)
    return tracks

def filter_bboxes(bboxes_per_frame): # TODO
    return {}

def find_all_tracks(bboxes_per_frame, is_filtered, params):
    count = 0
    tracks = []
    parent_of = {}
    while count < params['MAX_TRACK_COUNT']:
        track = find_some_track(bboxes_per_frame, is_filtered, parent_of, params)
        count += 1
        if track is not None:
            tracks.append(track)
            # TODO add all bboxes from this track to parent_of
        else:
            break
    return tracks

def find_some_track(bboxes_per_frame, is_filtered, parent_of, params):
    """
    Returns None if no track found.
    """
    print("Searching for a bbox that is a good starting point...")
    fr_idx, bbox_idx = find_start(bboxes_per_frame, is_filtered, parent_of, params)
    if fr_idx is None:
        print("None found. All humans have been tracked.")
        return None
    print("Found start bbox at frame index {:d} and bbox index {:d}".format(fr_idx, bbox_idx))
    start_frame, start_bboxes = bboxes_per_frame[fr_idx]
    start_bbox = start_bboxes[bbox_idx]
    tracker = ObjectTracker(start_frame, start_bbox, params['OPENCV_OBJ_TRACKER_TYPE'])
    track = Track()
    track.add(fr_idx, start_bbox, Transition.first)
    print("Tracking started:")
    curr_idx = fr_idx + 1
    while curr_idx < len(bboxes_per_frame):
        curr_frame, curr_bboxes = bboxes_per_frame[curr_idx]
        tracker_bbox = tracker.update(curr_frame)
        if tracker_bbox: 
            # If the OpenCV obj tracker managed to keep track of the bbox,
            # let's see if we can also snap it onto a detected bbox to
            # increase accuracy.
            closest_bbox_idx, _ = find_bbox_to_snap(curr_bboxes, tracker_bbox, params['MAX_SNAP_DISTANCE_SHORT'])
            if closest_bbox_idx is not None:
                closest_bbox = curr_bboxes[closest_bbox_idx]
                print("\tAt frame {:d} SNAPPED tracker bbox {} to closest detected bbox {}".format(curr_idx, tracker_bbox, closest_bbox))
                track.add(curr_idx, closest_bbox, Transition.snapped)
                # Let's reset the tracker to start tracking from here
                tracker.clear() # TODO Without this line this doesn't work,
                # we should understand what is going under the hoods.
                tracker = tracker.restart(curr_frame, closest_bbox)
            else:
                print("\tAt frame {:d} TRACKED previous bbox to {} in current frame, but could not snap it to any detected bbox".format(curr_idx, tracker_bbox))
                track.add(curr_idx, tracker_bbox, Transition.tracked)
        else:
            # When the obj tracker fails, let's see if there is some detected
            # bbox near the last bbox that was succesfully tracked that
            # happens to be available (ie, doesn't belong to any track).
            #
            # We'll use a slightly larger max snapping distance because when
            # the tracking fails it may be because the tracker got sidetracked
            # (no pun intended) by another object or part of the human that
            # it was tracking. We don't want it to be too large since when 
            # tracking fails it could also be failing correctly (ie, that the
            # human left the scene, went underneath something, etc).
            closest_bbox_idx, _ = find_bbox_to_snap(curr_bboxes, track.get_last_bbox(), params['MAX_SNAP_DISTANCE_LARGE'])
            if closest_bbox_idx is not None:
                closest_bbox = curr_bboxes[closest_bbox_idx]
                print("\tAt frame {:d} PATCHED the track by snapping from the previous bbox to {} in current frame".format(curr_idx, closest_bbox))
                track.add(curr_idx, closest_bbox, Transition.patched)
                tracker.restart(curr_frame, closest_bbox)
            else:
                print("\tTrack lost at frame {:d}!".format(curr_idx))

        curr_idx += 1
    return track

def find_start(bboxes_per_frame, is_filtered, parent_of, params):
    for fr_idx, (frame, bboxes) in enumerate(bboxes_per_frame):
        for bbox_idx, bbox in enumerate(bboxes):
            unfiltered = (fr_idx, bbox_idx) not in is_filtered
            untracked = (fr_idx, bbox_idx) not in parent_of
            without_large_intersections = not is_intersecting_any(bboxes, bbox_idx, params['MIN_INTERSEC_AREA_PERC'])
            if unfiltered and untracked and without_large_intersections:
                return (fr_idx, bbox_idx)
    return (None, None)

def is_intersecting_any(bboxes, base_bbox_idx, intersec_area_perc_thresh):
    if not bboxes:
        raise RuntimeError("bboxes must not be empty")
    base_bbox = bboxes[base_bbox_idx]
    for bbox in bboxes:
        if bbox is base_bbox:
            continue
        intersec_area = bbox.intersection_area(base_bbox)
        if intersec_area is None:
            continue
        else:
            area_perc = intersec_area / base_bbox.area
            area_perc_vice_versa = intersec_area / bbox.area
            if area_perc > intersec_area_perc_thresh or area_perc_vice_versa > intersec_area_perc_thresh:
                return True
    return False

def find_bbox_to_snap(bboxes, base_bbox, max_snap_distance):
    if not bboxes:
        raise RuntimeError("bboxes must not be empty")
    closest_dist = math.inf
    closest_bbox_idx = None
    for idx, bbox in enumerate(bboxes):
        dist = base_bbox.distance_to(bbox)
        if dist < max_snap_distance and dist < closest_dist:
            closest_bbox_idx = idx
            closest_dist = dist
    if closest_bbox_idx is not None:
        return (closest_bbox_idx, closest_dist)
    return (None, None)
