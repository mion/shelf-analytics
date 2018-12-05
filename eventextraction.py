"""Currently we only extract the first event we find."""
import operator
from functools import reduce
from enum import Enum
from collections import namedtuple
import numpy
from scipy.signal import find_peaks, peak_widths, lfilter, lfilter_zi, filtfilt, butter
from copy import deepcopy

class EventType(Enum):
    traverse = 'traverse'
    hover = 'hover'
    in_out = 'in_out'

ALL_EVENT_TYPES = (EventType.traverse, EventType.hover, EventType.in_out)

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

DEFAULT_BUTTER_ORD = 1
DEFAULT_BUTTER_CRIT_FREQ = 0.05

def index_for_in_out_event(raw_iaot, **kwargs):
    if len(raw_iaot) == 0:
        return None
    min_duration = kwargs['min_duration']
    min_area = kwargs['min_area']
    butter_ord = kwargs['butter_ord'] if 'butter_ord' in kwargs else DEFAULT_BUTTER_ORD
    butter_crit_freq = kwargs['butter_crit_freq'] if 'butter_crit_freq' in kwargs else DEFAULT_BUTTER_CRIT_FREQ
    iaot = numpy.array(raw_iaot)
    smooth_iaot = smooth_without_delay(iaot, butter_ord, butter_crit_freq)
    interp_iaot = interpolate_to_match(smooth_iaot, iaot)
    peaks = extract_peaks(interp_iaot, min_height=min_area, min_width=min_duration)
    if len(peaks) > 0:
        # Currently we use the first peak that matches our conditions.
        peak = peaks[0]
        return peak.index
    else:
        return None

def smooth_without_delay(xn, butter_ord, butter_crit_freq):
    if len(xn) == 0:
        return []
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
    return numpy.array(filtfilt(b, a, xn))

def interpolate_to_match(seq_orig, seq_dest):
    """Interpoaltes signal (numpy array) `seq_orig` to match 
    the amplitude of `seq_dest` (also a numpy array)."""
    return numpy.interp(seq_orig, (seq_orig.min(), seq_orig.max()), (seq_dest.min(), seq_dest.max()))

def extract_peaks(smooth_iaot, min_height, min_width):
    # Here we are using this method from the SciPy cookbook: https://scipy-cookbook.readthedocs.io/items/FiltFilt.html
    # There are others we could use such as the Savitzky-Golay filter approach, see: https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    if len(smooth_iaot) == 0:
        return []
    smooth_iaot = numpy.array(smooth_iaot)
    # try
    peaks = []
    indexes, props = find_peaks(smooth_iaot, height=min_height, width=min_width)
    for i in range(len(indexes)):
        peaks.append(Peak(
            indexes[i],
            props['widths'][i], # in frames
            props['peak_heights'][i] # intersection area in pixels
        ))
    return peaks

def index_for_step_event(iaot, min_duration, min_area):
    # We are simply looking for a step signal, mathematically speaking.
    # (We should refactor this to use numpy.)
    for i, area in enumerate(iaot):
        if area < min_area:
            continue
        valid_step_signal = True
        for j in range(i, i + min_duration):
            if j >= len(iaot) or iaot[j] < min_area:
                valid_step_signal = False
                break
        if valid_step_signal:
            # We return index right in the middle of the step
            return int(float(i) + (float(min_duration) / 2.0))
    return None

def extract_event_for(iaot, roi_name, params_for_event_type):
    if EventType.hover in params_for_event_type:
        params = params_for_event_type[EventType.hover]
        idx = index_for_step_event(iaot, params['min_duration'], params['min_area'])
        if idx:
            return HoverEvent(roi_name, idx)
    if EventType.traverse in params_for_event_type:
        params = params_for_event_type[EventType.traverse]
        idx = index_for_step_event(iaot, params['min_duration'], params['min_area'])
        if idx:
            return TraverseEvent(roi_name, idx)
    if EventType.in_out in params_for_event_type:
        params = params_for_event_type[EventType.in_out]
        idx = index_for_in_out_event(iaot, **params)
        if idx:
            return InOutEvent(roi_name, idx)
    return None

def extract_events(bboxes_per_track, rois, params_for_event_type):
    events = []
    for bboxes in bboxes_per_track:
        for roi in rois:
            iaot = intersection_area_over_time(bboxes, roi.bbox)
            roi_params = {}
            for evt_type in roi.event_types:
                roi_params[evt_type] = deepcopy(params_for_event_type[evt_type])
            evt = extract_event_for(iaot, roi.name, roi_params)
            if evt:
                events.append(evt)
    return events
