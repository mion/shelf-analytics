import operator
from functools import reduce
from enum import Enum

class EventType(Enum):
    traverse = 'traverse'
    hover = 'hover'
    in_out = 'in_out'

ALL_EVENT_TYPES = [EventType.traverse, EventType.hover, EventType.in_out]

class RegionOfInterest:
    def __init__(self, name, bbox, event_types=ALL_EVENT_TYPES):
        self.name = name
        self.bbox = bbox
        self.event_types = event_types

class Event:
    def __init__(self, _type, roi_name, step_index):
        self.type = _type
        self.roi_name = roi_name
        self.step_index = step_index

class TraverseEvent(Event):
    def __init__(self, roi_name, step_index):
        super().__init__(EventType.traverse, roi_name, step_index)

class HoverEvent(Event):
    def __init__(self, roi_name, step_index):
        super().__init__(EventType.hover, roi_name, step_index)

class InOutEvent(Event):
    def __init__(self, roi_name, step_index):
        super().__init__(EventType.in_out, roi_name, step_index)

def intersection_area_over_time(bboxes, roi_bbox):
    return [roi_bbox.intersection_area(bbox) for bbox in bboxes]

def extract_traverse_event_for(bboxes, roi, min_duration, min_area):
    # We are looking for a step signal, mathematically speaking. TODO Use numpy?
    iaot = intersection_area_over_time(bboxes, roi.bbox)
    for i in range(len(iaot)):
        if iaot[i] < min_area:
            continue
        small_area_found = False
        for j in range(i, i + min_duration):
            if j >= len(iaot):
                small_area_found = True # not enough time
                break
            if iaot[j] < min_area:
                small_area_found = True
                break
        if not small_area_found:
            return TraverseEvent(roi.name, i)
    return None

def extract_events_for(bboxes, roi, params):
    return []

def extract_events(tracks, rois, params):
    return reduce(operator.concat, [reduce(operator.concat, [extract_events_for(track.get_bboxes(), roi, params) for roi in rois]) for track in tracks])
