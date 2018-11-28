import unittest
from humantracking import Track, Transition
from point import Point
from boundingbox import BBox
from eventextraction import intersection_area_over_time, extract_traverse_event_for, extract_peaks, RegionOfInterest as Roi, EventType

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class TestExtractPeaks(unittest.TestCase):
    def test_empty(self):
        iaot = []
        peaks = extract_peaks(iaot, min_height=1, min_width=1)
        self.assertEqual(len(peaks), 0)

    def test_signals(self):
        from fixtures import iaot_signals
        for msg, exp_idxs, iaot, (min_height, min_width) in iaot_signals:
            peaks = extract_peaks(iaot, min_height=min_height, min_width=min_width)
            self.assertEqual([p.index for p in peaks], exp_idxs, msg)
    
class TestExtractTraverseEvent(unittest.TestCase):
    def test_no_intersection(self):
        iaot = [0, 0, 0]
        event = extract_traverse_event_for(iaot, '', min_duration=1, min_area=1)
        self.assertIsNone(event)

    def test_below_min_duration(self):
        iaot = [0, 25, 25, 0]
        event = extract_traverse_event_for(iaot, '', min_duration=3, min_area=1)
        self.assertIsNone(event)

    def test_below_min_area(self):
        iaot = [0, 25, 25, 0]
        event = extract_traverse_event_for(iaot, '', min_duration=1, min_area=26)
        self.assertIsNone(event)

    def test_traverse_single_intersec(self):
        iaot = [0, 25, 0, 0]
        event = extract_traverse_event_for(iaot, '', min_duration=1, min_area=5)
        self.assertIsNotNone(event)
        self.assertEqual(event.type, EventType.traverse)
        self.assertEqual(event.index, 1)

    def test_traverse_long_multiple_intersec(self):
        iaot = [0, 0, 7, 6, 2, 0, 6, 6, 7, 6]
        event = extract_traverse_event_for(iaot, 'foo', min_duration=4, min_area=5)
        self.assertIsNotNone(event)
        self.assertEqual(event.type, EventType.traverse)
        self.assertEqual(event.index, 6)
        self.assertEqual(event.roi_name, 'foo')

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
