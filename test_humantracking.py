import unittest
from point import Point
from boundingbox import BBox
from humantracking import find_bbox_to_snap, is_intersecting_any, find_start, average_bbox_velocity, look_ahead

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class TestLookAhead(unittest.TestCase):
    def test_should_ignore_filtered_or_tracked_bboxes(self):
        tail_bbox = mkbox(1, 0)
        target_bbox = mkbox(5, 0)
        bboxes_per_frame = [
            (None, [tail_bbox]), # fr_idx = 0
            (None, []), # fr_idx = 1
            (None, [mkbox(3, 0, ptid=1)]), # fr_idx = 2
            (None, [mkbox(4, 0)]), # fr_idx = 3
            (None, [target_bbox]), # fr_idx = 4
        ]
        is_filtered = {(3, 0): True}
        fr_idx = 1
        avg_bbox_vel = Point(1, 0)
        max_front_hops = 3
        max_snap_distance = 100

        idx, bbox = look_ahead(tail_bbox, bboxes_per_frame, fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance, is_filtered)

        self.assertEqual(idx, 4)
        self.assertIs(bbox, target_bbox)

    def test_should_ignore_far_away_bboxes(self):
        base_bbox = mkbox(0, 0)
        target_bbox = mkbox(3, 0)
        bboxes_per_frame = [
            (None, [base_bbox]),
            (None, [mkbox(1, 100)]),
            (None, [mkbox(2, 100)]),
            (None, [mkbox(3, 100), target_bbox, mkbox(3, 200)]),
        ]
        is_filtered = {}
        base_fr_idx = 1
        avg_bbox_vel = Point(1, 0)
        max_front_hops = 3
        max_snap_distance = 25

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance, is_filtered)

        self.assertEqual(fr_idx, 3)
        self.assertIs(bbox, target_bbox)
    
    def test_should_not_find_bbox_in_other_direction(self):
        base_bbox = mkbox(0, 0, w=5, h=5)
        bboxes_per_frame = [
            (None, [base_bbox]),
            (None, [mkbox(10, 0, w=5, h=5)]),
            (None, [mkbox(20, 0, w=5, h=5)])
        ]
        is_filtered = {}
        base_fr_idx = 1
        avg_bbox_vel = Point(-10, 0)
        max_front_hops = 2
        max_snap_distance = 15

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance, is_filtered)

        self.assertIsNone(fr_idx)
        self.assertIsNone(bbox)

    def test_should_work_when_bbox_is_not_in_bboxes_per_frame(self):
        base_bbox = mkbox(0, 0)
        target_bbox = mkbox(3, 3)
        bboxes_per_frame = [
            (None, []),
            (None, []),
            (None, [target_bbox]),
        ]
        is_filtered = {}
        base_fr_idx = 0
        avg_bbox_vel = Point(1, 1)
        max_front_hops = 3
        max_snap_distance = 5

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance, is_filtered)

        self.assertEqual(fr_idx, 2)
        self.assertIs(bbox, target_bbox)

    # test_should_not_find_itself

class TestAverageBboxVelocity(unittest.TestCase):
    def test_should_be_zero_for_empty_track(self):
        track_bboxes = []
        max_back_hops = 10

        avg_vel = average_bbox_velocity(track_bboxes, max_back_hops)

        self.assertEqual(avg_vel.x, 0)
        self.assertEqual(avg_vel.y, 0)

    def test_should_be_zero_for_single_item(self):
        track_bboxes = [mkbox()]
        max_back_hops = 3

        avg_vel = average_bbox_velocity(track_bboxes, max_back_hops)

        self.assertEqual(avg_vel.x, 0)
        self.assertEqual(avg_vel.y, 0)

    def test_should_work_when_hops_is_within_length(self):
        track_bboxes = [
            mkbox(2, 0),
            mkbox(3, 0),
            mkbox(6, 0)
        ]
        max_back_hops = 2

        avg_vel = average_bbox_velocity(track_bboxes, max_back_hops)

        self.assertEqual(avg_vel.x, 3)
        self.assertEqual(avg_vel.y, 0)

    def test_should_work_when_hops_is_larger_than_length(self):
        track_bboxes = [
            mkbox(4, 3),
            mkbox(8, 6),
            mkbox(12, 9)
        ]
        max_back_hops = 5

        avg_vel = average_bbox_velocity(track_bboxes, max_back_hops)

        self.assertEqual(avg_vel.x, 4)
        self.assertEqual(avg_vel.y, 3)

class TestFindStart(unittest.TestCase):
    def test_should_not_find_tracked_nor_filtered_bbox(self):
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

    def test_should_not_find_intersecting_bbox(self):
        bboxes_per_frame = [
            (None, [mkbox(0, 0), mkbox(1, 1)]),
            (None, [mkbox(2, 2), mkbox(3, 3), mkbox(4, 4)]),
            (None, [mkbox(5, 5)])
        ]
        is_filtered = {}
        intersec_area_perc_thresh = 0.0

        fr_idx, bbox_id = find_start(bboxes_per_frame, is_filtered, intersec_area_perc_thresh)

        self.assertEqual(fr_idx, 2)
        self.assertEqual(bbox_id, 0)

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
