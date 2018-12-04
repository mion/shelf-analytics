import unittest
import math
import random
import numpy as np
from humantracking import Track, Transition
from point import Point
from boundingbox import BBox
from eventextraction import intersection_area_over_time, index_for_step_event, index_for_in_out_event, extract_peaks, RegionOfInterest as Roi, EventType, extract_event_for, extract_events
from fixtures import iaot_signals

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

def noisify(raw_seq, amp=0.2):
    """Artificially makes a smooth sequence noisy."""
    seq = np.array(raw_seq)
    random.seed(1) # ensure some determinism
    noise_amp = amp * abs(seq.max() - seq.min())
    return np.array([(y + (random.random()*noise_amp/2) - (random.random()*noise_amp/2)) for y in seq])

class TestExtractEvents(unittest.TestCase):
    def test_empty(self):
        events = extract_events([[], [], []], [], {})
        self.assertEqual(len(events), 0)

class TestExtractEventFor(unittest.TestCase):
    def test_empty(self):
        event = extract_event_for([], '', {})
        self.assertIsNone(event)
    
    def test_flat_signal(self):
        flat_seq = np.array([105, 99, 102, 98, 96, 99, 101, 100, 97, 103])
        params_for_event_type = {
            EventType.traverse: {'min_area': 80, 'min_duration': 3},
            EventType.hover: {'min_area': 80, 'min_duration': 3},
            EventType.in_out: {'min_area': 80, 'min_duration': 3}
        }
        event = extract_event_for(flat_seq, 'roi0', params_for_event_type)
        self.assertIsNotNone(event)
        # Currently there's nothing in the extract_event_for function 
        # that looks for a "ramp" in the beginning and ending of the signal.
        # It actually looks for a straight line, so in this case the
        # first three values match the duration of 3 for a hover event.
        #
        # NOTE: If we make the function look for a ramp, does it improve accuracy?
        #
        self.assertEqual(event.type, EventType.hover)
        self.assertEqual(event.index, 1)

    def test_short_step(self):
        seq = [100*i for i in range(15)] + [100*15 for i in range(15, 30)] + [100*(45 - i) for i in range(30, 45)]
        short_step = noisify(np.array(seq), amp=0.65)
        params_for_event_type = {
            EventType.traverse: {'min_area': 1000, 'min_duration': 20},
            EventType.hover: {'min_area': 1000, 'min_duration': 60},
        }
        event = extract_event_for(short_step, 'roi0', params_for_event_type)
        self.assertIsNotNone(event)
        self.assertEqual(event.type, EventType.traverse)
        self.assertEqual(event.roi_name, 'roi0')
        self.assertLess(15, event.index)
        self.assertLess(event.index, 25)
    
    def test_long_step(self):
        seq = [100*i for i in range(10)] + [100*10 for i in range(10, 100)] + [100*(110 - i) for i in range(100, 110)]
        long_step = noisify(np.array(seq), amp=0.45)
        params_for_event_type = {
            EventType.traverse: {'min_area': 800, 'min_duration': 30},
            EventType.hover: {'min_area': 800, 'min_duration': 80},
        }
        event = extract_event_for(long_step, 'roi0', params_for_event_type)
        self.assertIsNotNone(event)
        self.assertEqual(event.roi_name, 'roi0')
        self.assertEqual(event.type, EventType.hover)
        self.assertLess(40, event.index)
        self.assertLess(event.index, 70)
    
    def test_small_peak_then_big_peak(self):
        seq = [math.pow(i, 3) for i in range(15)] + [math.pow(15 - i, 3) for i in range(15)] + [math.pow(i, 2.5) for i in range(15)] + [math.pow(15 - i, 2.5) for i in range(15)]
        seq.reverse()
        small_peak_big_peak = noisify(np.array(seq), amp=0.35)
        params_for_event_type = {
            EventType.in_out: {'min_area': 1500, 'min_duration': 10}
        }
        event = extract_event_for(small_peak_big_peak, 'roi0', params_for_event_type)
        self.assertIsNotNone(event)
        self.assertEqual(event.roi_name, 'roi0')
        self.assertEqual(event.type, EventType.in_out)
        self.assertTrue(40 < event.index < 50)

class TestIndexForInOutEvent(unittest.TestCase):
    def test_empty(self):
        index = index_for_in_out_event([], min_duration=1, min_area=1)
        self.assertIsNone(index)
    
    def test_signals(self):
        for msg, exp_idxs, iaot, (min_height, min_width), should_noisify in iaot_signals:
            if should_noisify:
                iaot = noisify(iaot, amp=0.45)
            # NOTE: We're using the module defaults for the Buttersworth filter.
            index = index_for_in_out_event(iaot, min_duration=min_width, min_area=min_height)
            if len(exp_idxs) == 0:
                self.assertIsNone(index, msg)
            else:
                idx = exp_idxs[0]
                self.assertEqual(index, idx, msg)

class TestExtractPeaks(unittest.TestCase):
    def test_empty(self):
        iaot = []
        peaks = extract_peaks(iaot, min_height=1, min_width=1)
        self.assertEqual(len(peaks), 0)

    def test_signals(self):
        for msg, exp_idxs, iaot, (min_height, min_width), _ in iaot_signals:
            peaks = extract_peaks(iaot, min_height=min_height, min_width=min_width)
            self.assertEqual([p.index for p in peaks], exp_idxs, msg)
    
class TestIndexForStepEvent(unittest.TestCase):
    def test_no_intersection(self):
        iaot = [0, 0, 0]
        index = index_for_step_event(iaot, min_duration=1, min_area=1)
        self.assertIsNone(index)

    def test_below_min_duration(self):
        iaot = [0, 25, 25, 0]
        index = index_for_step_event(iaot, min_duration=3, min_area=1)
        self.assertIsNone(index)

    def test_below_min_area(self):
        iaot = [0, 25, 25, 0]
        index = index_for_step_event(iaot, min_duration=1, min_area=26)
        self.assertIsNone(index)

    def test_traverse_single_intersec(self):
        iaot = [0, 25, 0, 0]
        index = index_for_step_event(iaot, min_duration=1, min_area=5)
        self.assertIsNotNone(index)
        self.assertEqual(index, 1)

    def test_traverse_long_multiple_intersec(self):
        iaot = [0, 0, 7, 6, 2, 0, 6, 6, 7, 6, 5]
        index = index_for_step_event(iaot, min_duration=4, min_area=5)
        self.assertIsNotNone(index)
        self.assertEqual(index, 8)

class TestIntersectionAreaOverTime(unittest.TestCase):
    def test_intersection_area_over_time(self):
        bboxes = [
            mkbox(0, 0, 10, 10),
            mkbox(10, 0, 10, 10),
            mkbox(20, 0, 10, 10)
        ]
        iaot = intersection_area_over_time(bboxes, mkbox(15, 0, 10, 10))
        self.assertEqual(len(iaot), len(bboxes))
        self.assertSequenceEqual(iaot, [0, 50, 50])

if __name__ == '__main__':
    unittest.main()
