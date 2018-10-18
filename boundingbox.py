from enum import Enum
from point import Point

class Format(Enum):
    y1_x1_y2_x2 = "(y1, x1, y2, x2)"
    x1_y1_w_h = "(x1, y1, w, h)"

class BBox:
    def __init__(self, origin, width, height):
        self.origin = origin
        self.width = width
        self.height = height
        self.center = (origin.x + int(width / 2), origin.y + int(height / 2))
        self.area = width * height

    def __str__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.origin.x, self.origin.y, self.width, self.height)

    def __repr__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.origin.x, self.origin.y, self.width, self.height)

    @staticmethod
    def parse(raw_bbox, fmt):
        # IMPORTANT: OpenCV expects tuples, not lists.
        #            Also, tuples will be used as indexes so
        #            ints are necessary.
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
