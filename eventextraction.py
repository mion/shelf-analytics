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
        super().__init__('traverse', roi_name, step_index)

class HoverEvent(Event):
    def __init__(self, roi_name, step_index):
        super().__init__('hover', roi_name, step_index)

class InOutEvent(Event):
    def __init__(self, roi_name, step_index):
        super().__init__('in_out', roi_name, step_index)

def intersection_area_over_time(bboxes, roi_bbox):
    return [roi_bbox.intersection_area(bbox) for bbox in bboxes]

def extract_traverse_events_for(bboxes, roi, min_duration, min_area):
    return []

def extract_events_for(bboxes, roi, params):
    return []

def extract_events(tracks, rois, params):
    return reduce(operator.concat, [reduce(operator.concat, [extract_events_for(track.get_bboxes(), roi, params) for roi in rois]) for track in tracks])
