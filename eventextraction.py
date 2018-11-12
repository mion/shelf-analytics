class Event:
    def __init__(self, _type, roi_name):
        self.type = _type
        self.roi_name = roi_name

class TraverseEvent(Event):
    def __init__(self, roi_name):
        super().__init__('traverse', roi_name)

class HoverEvent(Event):
    def __init__(self, roi_name):
        super().__init__('hover', roi_name)

class InOutEvent(Event):
    def __init__(self, roi_name):
        super().__init__('in_out', roi_name)

def intersection_area_over_time(bboxes, roi_bbox):
    return [roi_bbox.intersection_area(bbox) for bbox in bboxes]

def extract_events(tracks, rois):
    return []
