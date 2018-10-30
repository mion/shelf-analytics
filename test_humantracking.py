import unittest
from point import Point
from boundingbox import BBox
from humantracking import find_bbox_to_snap, is_intersecting_any, find_start

def mkbox(x=0, y=0, w=200, h=100, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class TestFindStart(unittest.TestCase):
    def test_should_not_find_tracked_nor_filtered(self):
        bboxes_per_frame = [
            (None, [mkbox(ptid=0), mkbox(ptid=1)]),
            (None, [mkbox(ptid=2), mkbox()]),
            (None, [mkbox(ptid=3), mkbox()])
        ]
        is_filtered = {
            (1, 1): True
        }
        intersec_area_perc_thresh = 1.0

        fr_idx, bbox_id = find_start(bboxes_per_frame, is_filtered, intersec_area_perc_thresh)

        self.assertEqual(fr_idx, 2)
        self.assertEqual(bbox_id, 1)

class TestIsIntersectingAny(unittest.TestCase):
    def test_should_raise_an_exception_when_empty(self):
        with self.assertRaises(RuntimeError):
            is_intersecting_any([], 2, 0.35)

    def test_should_return_false_below_thresh(self):
        bboxes = [
            BBox(Point(10, 10), 200, 150),
            BBox(Point(110, 85), 350, 250)
        ]

        self.assertEqual(is_intersecting_any(bboxes, 0, 0.40), False)

    def test_should_return_true_above_thresh(self):
        bboxes = [
            BBox(Point(10, 10), 200, 150),
            BBox(Point(20, 20), 350, 250)
        ]

        self.assertTrue(is_intersecting_any(bboxes, 0, 0.40), True)

    def test_should_return_false_without_a_single_intersec(self):
        bboxes = [
            BBox(Point(10, 10), 200, 150),
            BBox(Point(200, 170), 350, 250)
        ]

        self.assertEqual(is_intersecting_any(bboxes, 0, 0.75), False)

class TestFindBBoxToSnap(unittest.TestCase):
    def test_should_raise_an_exception_when_empty(self):
        with self.assertRaises(RuntimeError):
            find_bbox_to_snap([], BBox(Point(0, 0), 50, 50), 250)

    def test_should_find_first_in_line(self):
        bboxes = [
            BBox(Point(25, 100), 200, 150),
            BBox(Point(25, 175), 200, 150)
        ]

        base_bbox = BBox(Point(25, 25), 200, 150)
        idx, dist = find_bbox_to_snap(bboxes, base_bbox, 1000)

        self.assertEqual(idx, 0)
        self.assertEqual(dist, 75)

    def test_should_find_earlier_in_the_list(self):
        bboxes = [
            BBox(Point(25, 25), 200, 150),
            BBox(Point(25, 500), 200, 150)
        ]

        base_bbox = BBox(Point(25, 100), 200, 150)
        idx, dist = find_bbox_to_snap(bboxes, base_bbox, 1000)

        self.assertEqual(idx, 0)
        self.assertEqual(dist, 75)

    def test_should_not_find_beyond_max(self):
        bboxes = [
            BBox(Point(25, 25), 200, 150),
            BBox(Point(25, 325), 200, 150)
        ]

        base_bbox = BBox(Point(25, 175), 200, 150)
        idx, dist = find_bbox_to_snap(bboxes, base_bbox, 149)

        self.assertEqual(idx, None)
        self.assertEqual(dist, None)

if __name__ == '__main__':
    unittest.main()
