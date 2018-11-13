import unittest
from humantracking import Track, Transition
from point import Point
from boundingbox import BBox
from eventextraction import intersection_area_over_time, extract_events_for, RegionOfInterest as Roi

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class TestExtractTraverseEvents(unittest.TestCase):
    def test_no_intersection(self):
        bboxes = [
            mkbox(0, 0),
            mkbox(5, 0),
            mkbox(10, 0)
        ]
        roi = Roi('roi0', mkbox(-20, 0))
        events = extract_events_for(bboxes, roi)
        self.assertEqual(len(events), 0)

class TestIntersectionOverTime(unittest.TestCase):
    def test_intersection_over_time(self):
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
