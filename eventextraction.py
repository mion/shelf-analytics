import operator
from functools import reduce
from enum import Enum
from collections import namedtuple

class EventType(Enum):
    traverse = 'traverse'
    hover = 'hover'
    in_out = 'in_out'

ALL_EVENT_TYPES = [EventType.traverse, EventType.hover, EventType.in_out]

Peak = namedtuple('Peak', ('index', 'duration', 'height'))

class RegionOfInterest:
    def __init__(self, name, bbox, event_types=ALL_EVENT_TYPES):
        self.name = name
        self.bbox = bbox
        self.event_types = event_types

class Event:
    def __init__(self, _type, roi_name, index):
        self.type = _type
        self.roi_name = roi_name
        self.index = index

class TraverseEvent(Event):
    def __init__(self, roi_name, index):
        super().__init__(EventType.traverse, roi_name, index)

class HoverEvent(Event):
    def __init__(self, roi_name, index):
        super().__init__(EventType.hover, roi_name, index)

class InOutEvent(Event):
    def __init__(self, roi_name, index):
        super().__init__(EventType.in_out, roi_name, index)

def intersection_area_over_time(bboxes, roi_bbox):
    return [roi_bbox.intersection_area(bbox) for bbox in bboxes]

def extract_in_out_event_for(peaks, roi_name, min_duration, min_area):
    return None

def extract_peaks(iaot, butter_ord, butter_crit_freq, peak_height, peak_width):
    return []

def extract_traverse_event_for(iaot, roi_name, min_duration, min_area):
    # We are simply looking for a step signal, mathematically speaking. TODO Use numpy?
    for i, area in enumerate(iaot):
        if area < min_area:
            continue
        valid_step_signal = True
        for j in range(i, i + min_duration):
            if j >= len(iaot) or iaot[j] < min_area:
                valid_step_signal = False
                break
        if valid_step_signal:
            return TraverseEvent(roi_name, i)
    return None

def extract_events_for(bboxes, roi, params):
    return []

def extract_events(tracks, rois, params):
    return reduce(operator.concat, [reduce(operator.concat, [extract_events_for(track.get_bboxes(), roi, params) for roi in rois]) for track in tracks])
