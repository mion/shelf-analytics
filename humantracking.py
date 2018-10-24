import math
from boundingbox import BBox, DetectedBBox

def track_humans(bboxes_per_frame, config, params):
    """
    dbboxes_per_frame is a list of pairs:
        (frame, bboxes)
    """
    is_filtered = filter_bboxes(bboxes_per_frame)
    tracks = find_all_tracks(bboxes_per_frame, is_filtered, params['MAX_TRACK_COUNT'])
    return tracks

def filter_bboxes(bboxes_per_frame): # TODO
    return {}

def find_all_tracks(bboxes_per_frame, is_filtered, max_track_count):
    count = 0
    tracks = []
    parent_of = {}
    while count < max_track_count:
        track = find_some_track(bboxes_per_frame, is_filtered, parent_of)
        count += 1
        if track is not None:
            tracks.append(track)
        else:
            break
    return tracks

def find_some_track(bboxes_per_frame, is_filtered, parent_of):
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
    tracker = create_tracker(start_frame, start_bbox)
    # WIP
    return None

def create_tracker(frame, bbox):
    # FIXME I removed the call to tracker.clear(), this probably brakes something.
    pass

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

def find_bbox_to_snap(bboxes, base_bbox_index, max_snap_distance):
    if not bboxes:
        raise RuntimeError("bboxes must not be empty")
    closest_dist = math.inf
    closest_bbox_idx = None
    base_bbox = bboxes[base_bbox_index]
    for idx, bbox in enumerate(bboxes):
        if bbox is base_bbox:
            continue
        dist = base_bbox.distance_to(bbox)
        if dist < max_snap_distance and dist < closest_dist:
            closest_bbox_idx = idx
            closest_dist = dist
    if closest_bbox_idx is not None:
        return (closest_bbox_idx, closest_dist)
    return (None, None)
