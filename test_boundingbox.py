import unittest
from point import Point
from boundingbox import BBox, Format, load_detected_bounding_boxes_per_frame, ValidationError

class BBoxTest(unittest.TestCase):
    def test_parse_x1_y1_w_h(self):
        bbox = BBox.parse([5, 10, 200, 300], Format.x1_y1_w_h)
        self.assertEqual(bbox.origin.x, 5)
        self.assertEqual(bbox.origin.y, 10)
        self.assertEqual(bbox.width, 200)
        self.assertEqual(bbox.height, 300)

    def test_parse_y1_x1_y2_x2(self):
        bbox = BBox.parse([50, 20, 150, 220], Format.y1_x1_y2_x2)
        self.assertEqual(bbox.origin.x, 20)
        self.assertEqual(bbox.origin.y, 50)
        self.assertEqual(bbox.width, 200)
        self.assertEqual(bbox.height, 100)
    
    def test_intersection(self):
        bbox1 = BBox(Point(0, 0), 100, 100)
        bbox2 = BBox(Point(50, 50), 100, 100)
        area = bbox1.intersection_area(bbox2)
        self.assertEqual(area, 2500)
    
    def test_to_tuple(self):
        bbox1 = BBox(Point(1, 2), 321, 123)
        self.assertEqual(bbox1.to_tuple(Format.x1_y1_w_h), (1, 2, 321, 123))
        self.assertEqual(bbox1.to_tuple(Format.y1_x1_y2_x2), (2, 1, 125, 322))

class LoadDetectedBoundingBoxesPerFrameTest(unittest.TestCase):
    def test_invalid(self):
        invalid_raw_jsons = [
            None,
            {},
            {'bboxes_per_frme': {}},
            {'bboxes_per_frame': [
                [{'origin': [0], 'width': 10, 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': ['0', '0'], 'width': 10, 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': '10', 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': '10', 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': 10, 'score': '1.0', 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': 10, 'score': 1.0, 'obj_class': 0}]
            ]},
            {'bboxes_per_frame': [
                [{'width': 10, 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': 10, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': 10, 'score': 1.0}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': -10, 'height': 10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'height': -10, 'score': 1.0, 'obj_class': 'foo'}]
            ]},
            {'bboxes_per_frame': [
                [{'origin': [0, 0], 'width': 10, 'hight': 10, 'score': -1.0, 'obj_class': 'foo'}]
            ]},
        ]

        for json in invalid_raw_jsons:
            with self.assertRaises(ValidationError):
                load_detected_bounding_boxes_per_frame(json)

if __name__ == '__main__':
    unittest.main()
