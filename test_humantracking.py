import unittest
from point import Point
from boundingbox import BBox
from humantracking import find_bbox_to_snap

class TestFindBBoxToSnap(unittest.TestCase):
    def test_should_find_closest(self):
        b1 = BBox(Point(25, 25), 200, 150)
        b2 = BBox(Point(25, 100), 200, 150)
        b3 = BBox(Point(25, 175), 200, 150)
        bboxes = [b1, b2, b3]

        closest_bbox_idx, closest_dist = find_bbox_to_snap(bboxes, 0, 1000)

        self.assertEqual(closest_bbox_idx, 1)
        self.assertEqual(closest_dist, 75)

if __name__ == '__main__':
    unittest.main()
