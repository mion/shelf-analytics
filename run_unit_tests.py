import unittest
from boundingbox import BBox, Format

class BBoxTest(unittest.TestCase):
    def test_parse_x1_y1_w_h(self):
        bbox = BBox.parse([5, 10, 200, 300], Format.x1_y1_w_h)
        self.assertEqual(bbox.origin.x, 5)
        self.assertEqual(bbox.origin.y, 10)
        self.assertEqual(bbox.width, 200)
        self.assertEqual(bbox.height, 300)

if __name__ == '__main__':
    unittest.main()
