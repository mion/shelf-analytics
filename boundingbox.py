from enum import Enum
from point import Point

class Format(Enum):
    y1_x1_y2_x2 = "(y1, x1, y2, x2)"
    x1_y1_w_h = "(x1, y1, w, h)"

class BBox:
    next_id = 1
    def __init__(self, origin, width, height):
        self.id = BBox.next_id
        BBox.next_id += 1
        self.parent_track_id = None
        self.origin = origin
        self.width = width
        self.height = height
        self.center = Point(origin.x + int(width / 2), origin.y + int(height / 2))
        self.area = width * height
        # for backward comp
        self.x1 = origin.x
        self.y1 = origin.y
        self.x2 = origin.x + width
        self.y2 = origin.y + height

    def __str__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.origin.x, self.origin.y, self.width, self.height)

    def __repr__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.origin.x, self.origin.y, self.width, self.height)

    def is_similar(self, bbox):
        return self.origin == bbox.origin and self.width == bbox.width and self.height == bbox.height

    def distance_to(self, bbox):
        return self.center.distance_to(bbox.center)

    def has_intersection_with(self, bbox):
        return self.intersection_area(bbox) > 0

    def intersection_area(self, bbox):
        x1 = max(self.x1, bbox.x1)
        y1 = max(self.y1, bbox.y1)
        x2 = min(self.x2, bbox.x2)
        y2 = min(self.y2, bbox.y2)
        return (x2 - x1) * (y2 - y1) if ((x1 < x2) and (y1 < y2)) else 0

    def to_tuple(self, fmt):
        if fmt == Format.x1_y1_w_h:
            return (self.x1, self.y1, self.width, self.height)
        else: # fmt == Format.y1_x1_y2_x2:
            return (self.y1, self.x1, self.y2, self.x2)

    @staticmethod
    def parse(raw_bbox, fmt):
        # IMPORTANT: OpenCV expects tuples, not lists.
        #            Also, tuples will be used as indexes so
        #            ints are necessary.
        # TODO: rewrite the above comment?
        args = tuple([int(n) for n in raw_bbox])
        if fmt == Format.x1_y1_w_h:
            x1 = args[0]
            y1 = args[1]
            width = args[2]
            height = args[3]
            return BBox(Point(x1, y1), width, height)
        else: # fmt == Format.y1_x1_y2_x2
            y1, x1, y2, x2 = args
            width = x2 - x1
            height = y2 - y1
            return BBox(Point(x1, y1), width, height)

class DetectedBBox(BBox):
    """
    A bbox that was outputted from object detection.
    """
    def __init__(self, origin, width, height, score, obj_class):
        super().__init__(origin, width, height)
        self.score = score
        self.obj_class = obj_class

    def __repr__(self):
        return "<DBBox#{:d} ({:d}, {:d}) {:d}x{:d} {}~{:.2f}>".format(self.id, self.origin.x, self.origin.y, self.width, self.height, self.obj_class, self.score)

# These deserialization functions are nasty but let's avoid introducing
# a dependency for the moment. If we need to do more of this, then we
# can use `marshmallow` for proper deserialization.
# See: https://marshmallow.readthedocs.io/en/3.0/index.html

class ValidationError(Exception):
    """The JSON data is invalid."""

def load_detected_bbox(bbox_json):
    if not isinstance(bbox_json, dict):
        raise ValidationError
    for required_field in ('origin', 'width', 'height', 'score', 'obj_class'):
        if required_field not in bbox_json:
            raise ValidationError
    if not isinstance(bbox_json['origin'], list):
        raise ValidationError
    if len(bbox_json['origin']) != 2:
        raise ValidationError
    x, y = bbox_json['origin']
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValidationError
    origin = Point(x, y)
    if not isinstance(bbox_json['width'], int):
        raise ValidationError
    width = bbox_json['width']
    if not isinstance(bbox_json['height'], int):
        raise ValidationError
    height = bbox_json['height']
    if not isinstance(bbox_json['score'], float):
        raise ValidationError
    score = bbox_json['score']
    if not isinstance(bbox_json['obj_class'], str):
        raise ValidationError
    obj_class = bbox_json['obj_class']
    if width < 0 or height < 0 or score < 0.0:
        raise ValidationError
    return DetectedBBox(origin=origin, width=width, height=height, score=score, obj_class=obj_class)

def load_detected_bboxes_per_frame(raw_json):
    det_bboxes_per_frame = []
    if not isinstance(raw_json, dict):
        raise ValidationError
    if 'bboxes_per_frame' not in raw_json:
        raise ValidationError
    if not isinstance(raw_json['bboxes_per_frame'], list):
        raise ValidationError
    for bboxes_json in raw_json['bboxes_per_frame']:
        if not isinstance(bboxes_json, list):
            raise ValidationError
        det_bboxes = [load_detected_bbox(bbox_json) for bbox_json in bboxes_json]
        det_bboxes_per_frame.append(det_bboxes)
    return det_bboxes_per_frame
