import unittest
from point import Point
from boundingbox import BBox
from humantracking import find_bbox_to_snap

class TestFindBBoxToSnap(unittest.TestCase):
    def test_should_find_first_in_line(self):
        bboxes = [
            BBox(Point(25, 25), 200, 150),
            BBox(Point(25, 100), 200, 150),
            BBox(Point(25, 175), 200, 150)
        ]

        closest_bbox_idx, closest_dist = find_bbox_to_snap(bboxes, 0, 1000)

        self.assertEqual(closest_bbox_idx, 1)
        self.assertEqual(closest_dist, 75)

    def test_should_not_find_beyond_max(self):
        bboxes = [
            BBox(Point(25, 25), 200, 150),
            BBox(Point(25, 175), 200, 150),
            BBox(Point(25, 325), 200, 150)
        ]

        closest_bbox_idx, closest_dist = find_bbox_to_snap(bboxes, 1, 149)

        self.assertEqual(closest_bbox_idx, None)
        self.assertEqual(closest_dist, None)

if __name__ == '__main__':
    unittest.main()
