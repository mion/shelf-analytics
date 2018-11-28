"""Currently we only extract the first event we find."""
import operator
from functools import reduce
from enum import Enum
from collections import namedtuple
import numpy
from scipy.signal import find_peaks, peak_widths, lfilter, lfilter_zi, filtfilt, butter

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
    """This bboxes array should have a len() equal to the number of frames.
    It contains only one bbox in each position because it was extracted from a track.
    """
    return [roi_bbox.intersection_area(bbox) for bbox in bboxes]

def extract_in_out_event_for(peaks, roi_name, min_duration, min_area):
    return None

def smooth_without_delay(xn, butter_ord, butter_crit_freq):
    # Butterworth filter
    b, a = butter(butter_ord, butter_crit_freq)
    # Apply the filter to xn.  Use lfilter_zi to choose the initial condition
    # of the filter.
    zi = lfilter_zi(b, a)
    z, _ = lfilter(b, a, xn, zi=zi*xn[0])
    # Apply the filter again, to have a result filtered at an order
    # the same as filtfilt.
    z2, _ = lfilter(b, a, z, zi=zi*z[0])
    # Use filtfilt to apply the filter.
    return filtfilt(b, a, xn)

def extract_peaks(iaot, butter_ord, butter_crit_freq, min_height, min_width):
    # Here we are using this method from the SciPy cookbook: https://scipy-cookbook.readthedocs.io/items/FiltFilt.html
    # There are others we could use such as the Savitzky-Golay filter approach, see: https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    if len(iaot) == 0:
        return []
    iaot = numpy.array(iaot)
    # try
    peaks = []
    smooth_iaot = smooth_without_delay(iaot, butter_ord, butter_crit_freq)
    indexes, props = find_peaks(smooth_iaot, height=min_height, width=min_width)
    import pdb; pdb.set_trace()
    for i in range(len(indexes)):
        peaks.append(Peak(
            indexes[i],
            props['widths'][i], # in frames
            props['peak_heights'][i] # intersection area in pixels
        ))
    return peaks

def extract_traverse_event_for(iaot, roi_name, min_duration, min_area):
    # TODO We are simply looking for a step signal, mathematically speaking, so we could use numpy
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
