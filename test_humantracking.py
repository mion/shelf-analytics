import unittest
from point import Point
from boundingbox import BBox, DetectedBBox
from humantracking import find_bbox_to_snap, is_intersecting_any, find_start, average_bbox_velocity, look_ahead, interpolate, Transition, filter_bboxes

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class FakeObjectTracker:
    def __init__(self, frame, bbox, opencv_obj_tracker_type):
        self.fake_orig = Point(0, 0)

    def update(self, frame):
        self.fake_orig = self.fake_orig.add(Point(1, 0))
        return BBox(self.fake_orig, width=10, height=10)

    def restart(self, frame, bbox):
        pass # TODO

class TestFindSomeTrack(unittest.TestCase):
    def test_find_some_track(self):
        pass

class TestFilterBboxes(unittest.TestCase):
    def test_filter_bboxes(self):
        det_bbox1 = DetectedBBox(Point(0, 0), 50, 50, 0.5, 'human')
        det_bbox2 = DetectedBBox(Point(5, 4), 50, 50, 0.93, 'human')
        det_bbox3 = DetectedBBox(Point(90, 15), 50, 50, 0.85, 'bicycle')
        det_bbox4 = DetectedBBox(Point(20, 30), 50, 50, 0.96, 'human')
        det_bbox5 = DetectedBBox(Point(60, 10), 500, 500, 0.97, 'human')
        det_bbox6 = DetectedBBox(Point(100, 33), 5, 5, 0.98, 'human')
        det_bboxes_per_frame = [
            (None, [
                det_bbox1,
                det_bbox2,
            ]),
            (None, [
                det_bbox3,
                det_bbox4,
                det_bbox5,
            ]),
            (None, [
                det_bbox6,
            ])
        ]
        min_det_score = 0.95
        min_bbox_area = 25 * 25
        max_bbox_area = 100 * 100

        bboxes_per_frame = filter_bboxes(det_bboxes_per_frame, min_det_score, min_bbox_area, max_bbox_area)

        self.assertEqual(len(bboxes_per_frame), 3)
        self.assertEqual(len(bboxes_per_frame[0][1]), 0)
        self.assertEqual(len(bboxes_per_frame[1][1]), 1)
        self.assertIs(bboxes_per_frame[1][1][0], det_bbox4)
        self.assertEqual(len(bboxes_per_frame[2][1]), 0)

class TestInterpolate(unittest.TestCase):
    def test_interpolate(self):
        base_bbox = mkbox(0, 0, w=100, h=100)
        start_idx = 0
        end_bbox = mkbox(30, 30, w=100, h=100)
        end_idx = 2

        steps = interpolate(base_bbox, start_idx, end_bbox, end_idx)
        # steps = [(idx, bbox, transition), ...]
        self.assertEqual(2, len(steps))
        # indexes
        self.assertEqual(steps[0][0], 0)
        self.assertEqual(steps[1][0], 1)
        # bboxes
        self.assertTrue(steps[0][1].is_similar(mkbox(10, 10, w=100, h=100)))
        self.assertTrue(steps[1][1].is_similar(mkbox(20, 20, w=100, h=100)))
        # trans
        self.assertEqual(steps[0][2], Transition.interpolated)
        self.assertEqual(steps[1][2], Transition.interpolated)

class TestLookAhead(unittest.TestCase):
    def test_should_ignore_tracked_bboxes(self):
        base_bbox = mkbox(1, 0)
        target_bbox = mkbox(5, 0)
        bboxes_per_frame = [
            (None, [base_bbox]), # fr_idx = 0
            (None, []), # fr_idx = 1
            (None, [mkbox(3, 0, ptid=1)]), # fr_idx = 2
            (None, [mkbox(4, 0, ptid=1)]), # fr_idx = 3
            (None, [target_bbox]), # fr_idx = 4
        ]
        base_fr_idx = 1
        avg_bbox_vel = Point(1, 0)
        max_front_hops = 3
        max_snap_distance = 100

        idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance)

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
        base_fr_idx = 1
        avg_bbox_vel = Point(1, 0)
        max_front_hops = 3
        max_snap_distance = 25

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance)

        self.assertEqual(fr_idx, 3)
        self.assertIs(bbox, target_bbox)
    
    def test_should_not_find_bbox_in_other_direction(self):
        base_bbox = mkbox(0, 0, w=5, h=5)
        bboxes_per_frame = [
            (None, [base_bbox]),
            (None, [mkbox(10, 0, w=5, h=5)]),
            (None, [mkbox(20, 0, w=5, h=5)])
        ]
        base_fr_idx = 1
        avg_bbox_vel = Point(-10, 0)
        max_front_hops = 2
        max_snap_distance = 15

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance)

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
        base_fr_idx = 0
        avg_bbox_vel = Point(1, 1)
        max_front_hops = 3
        max_snap_distance = 5

        fr_idx, bbox = look_ahead(base_bbox, bboxes_per_frame, base_fr_idx, avg_bbox_vel, max_front_hops, max_snap_distance)

        self.assertEqual(fr_idx, 2)
        self.assertIs(bbox, target_bbox)

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
    def test_should_not_find_tracked_bbox(self):
        bboxes_per_frame = [
            (None, [mkbox(ptid=0), mkbox(ptid=1)]),
            (None, [mkbox(ptid=2), mkbox(ptid=1)]),
            (None, [mkbox(ptid=2), mkbox()])
        ]
        intersec_area_perc_thresh = 1.0

        fr_idx, bbox_id = find_start(bboxes_per_frame, intersec_area_perc_thresh)

        self.assertEqual(fr_idx, 2)
        self.assertEqual(bbox_id, 1)

    def test_should_not_find_intersecting_bbox(self):
        bboxes_per_frame = [
            (None, [mkbox(0, 0), mkbox(1, 1)]),
            (None, [mkbox(2, 2), mkbox(3, 3), mkbox(4, 4)]),
            (None, [mkbox(5, 5)])
        ]
        intersec_area_perc_thresh = 0.0

        fr_idx, bbox_id = find_start(bboxes_per_frame, intersec_area_perc_thresh)

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
    def test_should_return_none_when_empty(self):
        self.assertTupleEqual(find_bbox_to_snap([], BBox(Point(0, 0), 50, 50), 250), (None, None))

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
