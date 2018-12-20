import unittest
import json
from point import Point
from boundingbox import BBox, Format, load_bboxes_per_frame, ValidationError

class BBoxTest(unittest.TestCase):
    def test_from_tuple_x1_y1_w_h(self):
        bbox = BBox.from_tuple([5, 10, 200, 300], Format.x1_y1_w_h)
        self.assertEqual(bbox.origin.x, 5)
        self.assertEqual(bbox.origin.y, 10)
        self.assertEqual(bbox.width, 200)
        self.assertEqual(bbox.height, 300)

    def test_from_tuple_y1_x1_y2_x2(self):
        bbox = BBox.from_tuple([50, 20, 150, 220], Format.y1_x1_y2_x2)
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

class LoadBoundingBoxesPerFrameTest(unittest.TestCase):
    def test_invalid(self):
        invalid_raw_jsons = [
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

        for raw_json in invalid_raw_jsons:
            with self.assertRaises(ValidationError, msg='this JSON is invalid: \n' + json.dumps(raw_json, indent=3)):
                load_bboxes_per_frame(raw_json)

    def test_valid(self):
        raw_json = {
            'bboxes_per_frame': [
                [{'origin': [1, 1], 'width': 10, 'height': 10, 'score': 0.1, 'obj_class': 'human'}],
                [
                    {'origin': [2, 2], 'width': 20, 'height': 20, 'score': 0.2, 'obj_class': 'cat'},
                    {'origin': [3, 3], 'width': 30, 'height': 30, 'score': 0.3, 'obj_class': 'dog'},
                    {'origin': [4, 4], 'width': 40, 'height': 40}
                ],
            ]
        }

        bboxes_per_frame = load_bboxes_per_frame(raw_json)

        self.assertEqual(len(bboxes_per_frame), 2)
        self.assertEqual(len(bboxes_per_frame[0]), 1)
        self.assertEqual(len(bboxes_per_frame[1]), 3)

        self.assertEqual(bboxes_per_frame[0][0].origin, Point(1, 1))
        self.assertEqual(bboxes_per_frame[0][0].height, 10)
        self.assertEqual(bboxes_per_frame[0][0].width, 10)
        self.assertEqual(bboxes_per_frame[0][0].score, 0.1)
        self.assertEqual(bboxes_per_frame[0][0].obj_class, 'human')

        self.assertEqual(bboxes_per_frame[1][0].origin, Point(2, 2))
        self.assertEqual(bboxes_per_frame[1][0].height, 20)
        self.assertEqual(bboxes_per_frame[1][0].width, 20)
        self.assertEqual(bboxes_per_frame[1][0].score, 0.2)
        self.assertEqual(bboxes_per_frame[1][0].obj_class, 'cat')

        self.assertEqual(bboxes_per_frame[1][1].origin, Point(3, 3))
        self.assertEqual(bboxes_per_frame[1][1].height, 30)
        self.assertEqual(bboxes_per_frame[1][1].width, 30)
        self.assertEqual(bboxes_per_frame[1][1].score, 0.3)
        self.assertEqual(bboxes_per_frame[1][1].obj_class, 'dog')

        self.assertEqual(bboxes_per_frame[1][2].origin, Point(4, 4))
        self.assertEqual(bboxes_per_frame[1][2].height, 40)
        self.assertEqual(bboxes_per_frame[1][2].width, 40)
        self.assertIsNone(bboxes_per_frame[1][2].score)
        self.assertIsNone(bboxes_per_frame[1][2].obj_class)

if __name__ == '__main__':
    unittest.main()
