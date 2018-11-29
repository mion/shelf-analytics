import unittest
import random
import numpy as np
from humantracking import Track, Transition
from point import Point
from boundingbox import BBox
from eventextraction import intersection_area_over_time, index_for_step_event, index_for_in_out_event, extract_peaks, RegionOfInterest as Roi, EventType
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
        iaot = [0, 0, 7, 6, 2, 0, 6, 6, 7, 6]
        index = index_for_step_event(iaot, min_duration=4, min_area=5)
        self.assertIsNotNone(index)
        self.assertEqual(index, 6)

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
