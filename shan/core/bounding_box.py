import math
from enum import Enum

class BoundingBoxFormat(Enum):
    y1_x1_y2_x2 = "(y1, x1, y2, x2)"
    x1_y1_w_h = "(x1, y1, w, h)"

class BoundingBox:
    """
    A bounding box is just a rectangle. This class helps handling the
    different formats that some libraries use and also adds some
    helper methods to handle bounding boxes.
    """
    next_bbox_id = 1
    def __init__(self, raw_bbox, bbox_format):
        self.id = BoundingBox.next_bbox_id
        BoundingBox.next_bbox_id += 1
        self.frame_index = None # currently being used in 'find_detection_failures' script only
        self.filtering_results = []
        self.score = 0.0
        self.parent_track_ids = []
        # IMPORTANT: OpenCV expects tuples, not lists.
        #            Also, tuples will be used as indexes so
        #            ints are necessary.
        args = tuple([int(n) for n in raw_bbox])
        # Check the format and load
        if bbox_format == BoundingBoxFormat.y1_x1_y2_x2:
            self.y1 = args[0]
            self.x1 = args[1]
            self.y2 = args[2]
            self.x2 = args[3]
            self.width = self.x2 - self.x1
            self.height = self.y2 - self.y1
        elif bbox_format == BoundingBoxFormat.x1_y1_w_h:
            self.x1 = args[0]
            self.y1 = args[1]
            self.width = args[2]
            self.height = args[3]
            self.x2 = self.x1 + self.width
            self.y2 = self.y1 + self.height
        else:
            raise ValueError("invalid bounding box format: {0}".format(bbox_format))
        self.topLeft = (self.x1, self.y1)
        self.topRight = (self.x2, self.y1)
        self.bottomLeft = (self.x1, self.y2)
        self.bottomRight = (self.x2, self.y2)
        self.center = (self.x1 + int(self.width / 2), self.y1 + int(self.height / 2))
        self.area = self.width * self.height

    def __str__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.x1, self.y1, self.width, self.height)

    def __repr__(self):
        return "<BBox ({0}, {1}) {2}x{3}>".format(self.x1, self.y1, self.width, self.height)

    def distance_to(self, bbox):
        dest_x, dest_y = bbox.center
        orig_x, orig_y = self.center
        dx = dest_x - orig_x
        dy = dest_y - orig_y
        return math.sqrt((dx * dx) + (dy * dy))
    
    def distance_to_point(self, point):
        dest_x, dest_y = point
        orig_x, orig_y = self.center
        dx = dest_x - orig_x
        dy = dest_y - orig_y
        return math.sqrt((dx * dx) + (dy * dy))
    
    def has_intersection_with(self, bbox):
        return self.intersection_area(bbox) is not None
    
    def intersection_area(self, bbox):
        x1 = max(self.x1, bbox.x1)
        y1 = max(self.y1, bbox.y1)
        x2 = min(self.x2, bbox.x2)
        y2 = min(self.y2, bbox.y2)
        if x1 < x2 and y1 < y2:
            return (x2 - x1) * (y2 - y1)
        else:
            return None

    def to_tuple(self, bbox_format):
        if bbox_format == BoundingBoxFormat.x1_y1_w_h:
            return (self.x1, self.y1, self.width, self.height)
        elif bbox_format == BoundingBoxFormat.y1_x1_y2_x2:
            return (self.y1, self.x1, self.y2, self.x2)
        else:
            raise RuntimeError('invalid bounding box format')
    
    def is_filtered(self):
        for result in self.filtering_results:
            if result['filtered'] is True:
                return True
        return False
    
    def get_filtering_results_label(self):
        label_parts = []
        for result in self.filtering_results:
            if result['filtered'] is True:
                label_parts.append(result['type'])
        return '/'.join(label_parts)
    
    def is_available(self):
        return len(self.parent_track_ids) == 0
    
    def is_child_of(self, track_id):
        return track_id in self.parent_track_ids
    
    def to_json(self):
        return {
            'id': self.id,
            'y1_x1_y2_x2': self.to_tuple(BoundingBoxFormat.y1_x1_y2_x2),
            'filtering_results': self.filtering_results,
            'score': self.score,
            'parent_track_ids': self.parent_track_ids
        }
    
    @staticmethod
    def from_json(json):
        bbox = BoundingBox(json['y1_x1_y2_x2'], BoundingBoxFormat.y1_x1_y2_x2)
        bbox.id = json['id']
        bbox.score = json['score']
        bbox.filtering_results = json['filtering_results']
        bbox.parent_track_ids = json['parent_track_ids']
        return bbox
    
    # @staticmethod
    # def moved_by(base_bbox, offset_x, offset_y):
