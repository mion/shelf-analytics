import unittest
from point import Point
from boundingbox import BBox
from humantracking import Track, find_bbox_to_snap, is_intersecting_any, find_start, average_bbox_velocity, look_ahead, interpolate, Transition, filter_bboxes, find_some_track

def mkbox(x=0, y=0, w=10, h=10, ptid=None):
    bbox = BBox(Point(x, y), w, h)
    bbox.parent_track_id = ptid
    return bbox

class FakeObjectTracker:
    def __init__(self, updates_before_failure):
        self.updates_before_failure = updates_before_failure

    def start(self, frame, bbox):
        self.fixed_w = bbox.width
        self.fixed_h = bbox.height
        self.orig = bbox.origin.copy()

    def update(self, frame):
        if self.updates_before_failure == 0:
            return None
        self.updates_before_failure -= 1
        self.orig = self.orig.add(Point(10, 0))
        return BBox(self.orig, width=self.fixed_w, height=self.fixed_h)

    def restart(self, frame, bbox):
        self.fixed_w = bbox.width
        self.fixed_h = bbox.height
        self.orig = bbox.origin.copy()

class TestFindSomeTrack(unittest.TestCase):
    def test_empty_frames(self):
        bboxes_per_frame = [
            (None, []),
            (None, []),
            (None, []),
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 0,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 0,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 0,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 0,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(999), params)

        self.assertIsNone(track)

    def test_single_bbox_track(self):
        bbox1 = mkbox()
        bboxes_per_frame = [
            (None, []),
            (None, []),
            (None, [bbox1]),
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 0,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 0,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 0,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 0,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(999), params)

        self.assertEqual(len(track), 1)
        self.assertEqual(track.steps[0].bbox, bbox1)
        self.assertEqual(track.steps[0].transition, Transition.first)

    def test_should_find_straight_continuous_track(self):
        bbox1 = mkbox(0, 0, 50, 50)
        bbox2 = mkbox(20, 0, 50, 50)
        bbox3 = mkbox(40, 0, 50, 50)
        bboxes_per_frame = [
            (None, []),
            (None, [bbox1]),
            (None, [bbox2]),
            (None, [bbox3]),
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 10,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 0,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 0,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 0,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(999), params)
        self.assertEqual(len(track), 3)
        self.assertTrue(bbox1 in track)
        self.assertTrue(bbox2 in track)
        self.assertTrue(bbox3 in track)

    def test_should_find_straight_intermittent_track(self):
        bbox1 = mkbox(0, 0, 50, 50)
        bbox2 = mkbox(20, 0, 50, 50)
        bbox3 = mkbox(60, 0, 50, 50)
        bboxes_per_frame = [
            (None, []),
            (None, [bbox1]),
            (None, [bbox2]),
            (None, []),
            (None, [bbox3])
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 20,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 0,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 0,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 0,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(999), params)

        self.assertEqual(len(track), 4)
        self.assertTrue(track.steps[0].bbox == bbox1)
        self.assertTrue(track.steps[0].transition == Transition.first)
        self.assertTrue(track.steps[1].bbox == bbox2)
        self.assertTrue(track.steps[1].transition == Transition.snapped)
        self.assertTrue(track.steps[2].transition == Transition.tracked)
        self.assertTrue(track.steps[3].bbox == bbox3)
        self.assertTrue(track.steps[3].transition == Transition.snapped)

    def test_should_snap_further_away_after_tracker_failure(self):
        bbox1 = mkbox(0, 0, 50, 50)
        bbox2 = mkbox(20, 0, 50, 50)
        bbox3 = mkbox(50, 0, 50, 50)
        bboxes_per_frame = [
            (None, []),
            (None, [bbox1]),
            (None, [bbox2]),
            (None, [bbox3])
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 20,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 30,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 0,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 0,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(1), params)

        self.assertEqual(len(track), 3)
        self.assertTrue(track.steps[0].bbox == bbox1)
        self.assertTrue(track.steps[0].transition == Transition.first)
        self.assertTrue(track.steps[1].bbox == bbox2)
        self.assertTrue(track.steps[1].transition == Transition.snapped)
        self.assertTrue(track.steps[2].bbox == bbox3)
        self.assertTrue(track.steps[2].transition == Transition.patched)

    def test_should_find_track_with_large_gap(self):
        bbox1 = mkbox(0, 0, 50, 50)
        bbox2 = mkbox(20, 0, 50, 50)
        bbox3 = mkbox(40, 0, 50, 50)
        bbox4 = mkbox(120, 0, 50, 50)
        bboxes_per_frame = [
            (None, []),
            (None, [bbox1]),
            (None, [bbox2]),
            (None, [bbox3]),
            (None, []),
            (None, []),
            (None, []),
            (None, [bbox4])
        ]
        params = {
            'MAX_INTERSEC_AREA_PERC': 0.0,
            'OPENCV_OBJ_TRACKER_TYPE': '',
            'TRACKER_SUCCESS_MAX_SNAP_DISTANCE': 20,
            'TRACKER_FAIL_MAX_SNAP_DISTANCE': 30,
            'AVG_BBOX_VEL_MAX_BACK_HOPS': 3,
            'LOOK_AHEAD_MAX_FRONT_HOPS': 3,
        }

        track = find_some_track(bboxes_per_frame, FakeObjectTracker(2), params)

        self.assertEqual(len(track), 7)
        self.assertEqual(track.steps[0].bbox, bbox1)
        self.assertEqual(track.steps[1].bbox, bbox2)
        self.assertEqual(track.steps[1].transition, Transition.snapped)
        self.assertEqual(track.steps[2].bbox, bbox3)
        self.assertEqual(track.steps[2].transition, Transition.snapped)
        self.assertEqual(track.steps[3].bbox.origin.x, 60)
        self.assertEqual(track.steps[3].transition, Transition.interpolated)
        self.assertEqual(track.steps[4].bbox.origin.x, 80)
        self.assertEqual(track.steps[4].transition, Transition.interpolated)
        self.assertEqual(track.steps[5].bbox.origin.x, 100)
        self.assertEqual(track.steps[5].transition, Transition.interpolated)
        self.assertEqual(track.steps[6].bbox, bbox4)
        self.assertEqual(track.steps[6].transition, Transition.patched)

class TestFilterBboxes(unittest.TestCase):
    def test_filter_bboxes(self):
        bbox1 = BBox(Point(0, 0), 50, 50, 0.5, 'person')
        bbox2 = BBox(Point(5, 4), 50, 50, 0.93, 'person')
        bbox3 = BBox(Point(90, 15), 50, 50, 0.85, 'bicycle')
        bbox4 = BBox(Point(20, 30), 50, 50, 0.96, 'person')
        bbox5 = BBox(Point(60, 10), 500, 500, 0.97, 'person')
        bbox6 = BBox(Point(100, 33), 5, 5, 0.98, 'person')
        orig_bboxes_per_frame = [
            (None, [
                bbox1,
                bbox2,
            ]),
            (None, [
                bbox3,
                bbox4,
                bbox5,
            ]),
            (None, [
                bbox6,
            ])
        ]
        min_det_score = 0.95
        min_bbox_area = 25 * 25
        max_bbox_area = 100 * 100

        bboxes_per_frame = filter_bboxes(orig_bboxes_per_frame, min_det_score, min_bbox_area, max_bbox_area)

        self.assertEqual(len(bboxes_per_frame), 3)
        self.assertEqual(len(bboxes_per_frame[0][1]), 0)
        self.assertEqual(len(bboxes_per_frame[1][1]), 1)
        self.assertIs(bboxes_per_frame[1][1][0], bbox4)
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

class TestParseTrack(unittest.TestCase):
    def test_parse_json(self):
        track_json = [ # TODO Move this into fixtures
            {"frame_index": 28, "bbox": {"id": 1, "origin": [0, 84], "width": 107, "height": 92, "score": 0.81, "obj_class": "person"}, "transition": "first"}, 
            {"frame_index": 29, "bbox": {"id": 2, "origin": [0, 96], "width": 122, "height": 81, "score": 0.98, "obj_class": "person"}, "transition": "snapped"}
        ]
        track = Track.parse(track_json)
        self.assertEqual(len(track), 2)
        fr_idx1, bbox1, trans1 = track.get_step(0)
        self.assertEqual(fr_idx1, 28)
        # self.assertEqual(bbox1.id, 1) TODO what about this?
        self.assertEqual(bbox1.origin, Point(0, 84))
        self.assertEqual(bbox1.width, 107)
        self.assertEqual(bbox1.height, 92)
        self.assertAlmostEqual(bbox1.score, 0.81, places=2)
        self.assertEqual(bbox1.obj_class, 'person')
        self.assertEqual(trans1, Transition.first)
        fr_idx2, bbox2, trans2 = track.get_step(1)
        self.assertEqual(fr_idx2, 29)
        # self.assertEqual(bbox2.id, 2) TODO what about this?
        self.assertEqual(bbox2.origin, Point(0, 96))
        self.assertEqual(bbox2.width, 122)
        self.assertEqual(bbox2.height, 81)
        self.assertAlmostEqual(bbox2.score, 0.98, places=2)
        self.assertEqual(bbox2.obj_class, 'person')
        self.assertEqual(trans2, Transition.snapped)

if __name__ == '__main__':
    unittest.main()
