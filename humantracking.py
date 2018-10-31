import math
from boundingbox import BBox, Format, DetectedBBox
from point import Point

class Track:
    next_id = 1
    def __init__(self):
        self.id = Track.next_id
        Track.next_id += 1
        self.steps = []
    
    def __len__(self):
        return len(self.steps)

    def add(self, frame_index, bbox, transition):
        # We can't use the bbox index here because we may want to add a bbox
        # that wasn't detected (it may be have come from object tracking or
        # the look ahead/interpolation algorithm).
        # For this reason we added an `id` field to the BBox class though
        # we also use indexes throughout the code when possible as it's simpler.
        bbox.parent_track_id = self.id
        self.steps.append((frame_index, bbox, transition))
    
    def get_bbox(self, idx):
        if idx >= len(self.steps):
            raise IndexError('bbox index out of bounds')
        _, bbox, _ = self.steps[idx]
        return bbox

    def get_last_bbox(self):
        if not self.steps:
            raise RuntimeError('cannot get last bbox from an empty track')
        _, bbox, _ = self.steps[len(self.steps) - 1]
        return bbox
    
    def get_bboxes(self):
        return [bbox for _, bbox, _ in self.steps]

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
        if not ok: # TODO Is this a good use of exceptions?
            raise RuntimeError('failed to init OpenCV tracker')

    def update(self, frame):
        ok, xywh_tuple = self.opencv_tracker.update(frame)
        return BBox.parse(xywh_tuple, Format.x1_y1_w_h) if ok else None

    def restart(self, frame, bbox):
        self.opencv_tracker.clear() # Dig into OpenCV docs/code to figure out
        # why this is needed and what's going on under the hood.
        self.opencv_tracker = self._create_opencv_tracker(self._opencv_obj_tracker_type)
        ok = self.opencv_tracker.init(frame, bbox.to_tuple(Format.x1_y1_w_h))
        if not ok: # TODO Is this a good use of exceptions?
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

def track_humans(det_bboxes_per_frame, config, params):
    """
    bboxes_per_frame is a list of pairs:
        (frame, bboxes)
    At first they are in fact DetectedBBox, but that doesn't matter
    being filtering.
    """
    is_filtered = filter_bboxes(det_bboxes_per_frame, params)
    tracks = find_all_tracks(det_bboxes_per_frame, is_filtered, params)
    return tracks

def filter_bboxes(det_bboxes_per_frame, params):
    is_filtered = {}
    for fr_idx, (frame, det_bboxes) in enumerate(det_bboxes_per_frame):
        for bbox_idx, det_bbox in enumerate(det_bboxes):
            too_uncertain = det_bbox.score < params['MIN_OBJ_DET_SCORE']
            too_small = det_bbox.area < params['MIN_BBOX_AREA']
            too_large = det_bbox.area > params['MAX_BBOX_AREA']
            if too_uncertain or too_small or too_large:
                is_filtered[(fr_idx, bbox_idx)] = True
    return is_filtered

def find_all_tracks(bboxes_per_frame, is_filtered, params):
    count = 0
    tracks = []
    while count < params['MAX_TRACK_COUNT']:
        track = find_some_track(bboxes_per_frame, is_filtered, params)
        count += 1
        if track is not None:
            tracks.append(track)
        else:
            break
    return tracks

def unfiltered_and_untracked(fr_idx, bboxes, is_filtered):
    clean_bboxes = []
    for bbox_idx, bbox in enumerate(bboxes):
        unfiltered = (fr_idx, bbox_idx) not in is_filtered
        untracked = bbox.parent_track_id is not None
        if unfiltered and untracked:
            clean_bboxes.append(bbox)
    return clean_bboxes

def find_some_track(bboxes_per_frame, is_filtered, params):
    """
    Returns None if no track found.
    """
    print("Searching for a bbox that is a good starting point...")
    fr_idx, bbox_idx = find_start(bboxes_per_frame, is_filtered, params['MIN_INTERSEC_AREA_PERC'])
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
        clean_bboxes = unfiltered_and_untracked(curr_idx, curr_bboxes, is_filtered)
        tracker_bbox = tracker.update(curr_frame)
        if tracker_bbox: 
            # If the OpenCV obj tracker managed to keep track of the bbox,
            # let's see if we can also snap it onto a detected bbox to
            # increase accuracy.
            closest_bbox_idx, _ = find_bbox_to_snap(clean_bboxes, tracker_bbox, params['MAX_SNAP_DISTANCE_SHORT'])
            if closest_bbox_idx is not None:
                closest_bbox = clean_bboxes[closest_bbox_idx]
                print("\tAt frame {:d} SNAPPED tracker bbox {} to closest detected bbox {}".format(curr_idx, tracker_bbox, closest_bbox))
                track.add(curr_idx, closest_bbox, Transition.snapped)
                # Let's reset the tracker to make its algorithm "forget" what happened previously.
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
            closest_bbox_idx, _ = find_bbox_to_snap(clean_bboxes, track.get_last_bbox(), params['MAX_SNAP_DISTANCE_LARGE'])
            if closest_bbox_idx is not None:
                closest_bbox = clean_bboxes[closest_bbox_idx]
                print("\tAt frame {:d} PATCHED the track by snapping from the previous bbox to {} in current frame".format(curr_idx, closest_bbox))
                track.add(curr_idx, closest_bbox, Transition.patched)
                tracker.restart(curr_frame, closest_bbox)
            else:
                print("\tTrack lost at frame {:d}!".format(curr_idx))
                avg_bbox_vel = average_bbox_velocity(track.get_bboxes(), params['AVG_BBOX_VEL_MAX_BACK_HOPS'])
                target_idx, target_bbox = look_ahead(track.get_last_bbox(), bboxes_per_frame, curr_idx, avg_bbox_vel, params['LOOK_AHEAD_MAX_FRONT_HOPS'], params['LOOK_AHEAD_MAX_SNAP_DISTANCE'], is_filtered)
                if target_idx is not None:
                    print("\tLooked ahead and found a good target for intepolation: {} at index {:d}".format(target_bbox, target_idx))
                    steps = interpolate(track.get_last_bbox(), curr_idx, target_bbox, target_idx)
                    for step in steps:
                        track.add(*step)
                    curr_idx = target_idx - 1
                    frame, _ = bboxes_per_frame[curr_idx]
                    tracker.restart(frame, track.get_last_bbox())
                else:
                    print("\tLook ahead failed, track lost.")
        curr_idx += 1
    return track

def interpolate(start_bbox, start_idx, end_bbox, end_idx):
    n_hops = end_idx - start_idx + 1
    delta_per_hop = start_bbox.distance_to(end_bbox) / n_hops
    dir_vec = start_bbox.center.normalized_direction(end_bbox.center)
    interpol_orig = start_bbox.copy()
    steps = []
    for idx in range(start_idx, end_idx):
        interpol_orig = interpol_orig.add(dir_vec.multiply(delta_per_hop))
        interpol_bbox = BBox(interpol_orig, start_bbox.width, start_bbox.height)
        steps.append((idx, interpol_bbox, Transition.interpolated))
    return steps

# TODO Refactor this function after testing.
def average_bbox_velocity(track_bboxes, max_back_hops):
    start_i = max(len(track_bboxes) - max_back_hops, 0)
    avg_vel_x = 0
    avg_vel_y = 0
    back_hops = 0
    for i in range(start_i, len(track_bboxes) - 1):
        bbox = track_bboxes[i]
        next_bbox = track_bboxes[i + 1]
        avg_vel_x += (next_bbox.center.x - bbox.center.x)
        avg_vel_y += (next_bbox.center.y - bbox.center.y)
        back_hops += 1
    if back_hops > 0: # FIXME This is weird, compute it beforehand and refactor to use exceptions.
        avg_vel_x = int(avg_vel_x / back_hops)
        avg_vel_y = int(avg_vel_y / back_hops)
        return Point(avg_vel_x, avg_vel_y)
    else:
        return Point(0, 0)

# TODO Refactor this function after testing.
def look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance, is_filtered):
    moving_center = base_bbox.center.copy()
    for idx in range(base_fr_idx, min(base_fr_idx + max_front_hops + 1, len(bboxes_per_frame))):
        moving_center = moving_center.add(avg_bbox_vel)
        closest_dist = math.inf
        closest_bbox = None
        _, bboxes = bboxes_per_frame[idx]
        for bbox_idx, bbox in enumerate(bboxes):
            filtered = (idx, bbox_idx) in is_filtered
            tracked = bbox.parent_track_id is not None
            if filtered or tracked:
                continue
            dist = bbox.center.distance_to(moving_center)
            if dist < max_snap_distance and dist < closest_dist:
                closest_bbox = bbox
                closest_dist = dist
        if closest_bbox is not None:
            return (idx, closest_bbox)
    return (None, None)

def find_start(bboxes_per_frame, is_filtered, intersec_area_perc_thresh):
    for fr_idx, (frame, bboxes) in enumerate(bboxes_per_frame):
        for bbox_idx, bbox in enumerate(bboxes):
            unfiltered = (fr_idx, bbox_idx) not in is_filtered
            untracked = bbox.parent_track_id is None
            without_large_intersections = not is_intersecting_any(bboxes, bbox_idx, intersec_area_perc_thresh)
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
            # Since we don't know if base bbox is "the large one" or not
            # let's calculate the intersection area percentage both ways.
            area_perc = intersec_area / base_bbox.area
            area_perc_vice_versa = intersec_area / bbox.area
            if area_perc > intersec_area_perc_thresh or area_perc_vice_versa > intersec_area_perc_thresh:
                return True
    return False

def find_bbox_to_snap(bboxes, base_bbox, max_snap_distance):
    # FIXME refactor to return a bbox instead of idx, and no distance
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
