import math
from boundingbox import BBox

def track_humans(det_result, config, params):
    return []

def is_intersecting_any(bboxes, base_bbox_idx, min_intersec_area_perc):
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
            if area_perc > min_intersec_area_perc or area_perc_vice_versa > min_intersec_area_perc:
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
