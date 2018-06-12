import os
import sys
import json
import math
import cv2

DEFAULT_MIN_SNAPPING_DISTANCE = 150.0
TRACKER_FAILED_MIN_SNAPPING_DISTANCE = 300.0


class BoundingBox:
    """A bounding box is just a rectangle. This class helps handling the
    different formats that some libraries use.
    """
    FORMAT_Y1_X1_Y2_X2 = "FORMAT_Y1X1Y2X2"
    FORMAT_X1_Y1_W_H = "FORMAT_X1_Y1_W_H"

    def __init__(self, args, args_format):
        if args_format == self.FORMAT_Y1_X1_Y2_X2:
            self.y1 = args[0]
            self.x1 = args[1]
            self.y2 = args[2]
            self.x2 = args[3]
            self.width = self.x2 - self.x1
            self.height = self.y2 - self.y1
        elif args_format == self.FORMAT_X1_Y1_W_H:
            self.x1 = args[0]
            self.y1 = args[1]
            self.width = args[2]
            self.height = args[3]
            self.x2 = self.x1 + self.width
            self.y2 = self.y1 + self.height
        else:
            raise ValueError("invalid bounding box format: {0}".format(args_format))
        self.topLeft = (self.x1, self.y1)
        self.topRight = (self.x2, self.y1)
        self.bottomLeft = (self.x1, self.y2)
        self.bottomRight = (self.x2, self.y2)
        self.center = (self.x1 + self.width / 2, self.y1 + self.height / 2)
    
    def distance_to(self, bbox):
        dest_x, dest_y = bbox.center
        orig_x, orig_y = self.center
        dx = dest_x - orig_x
        dy = dest_y - orig_y
        return math.sqrt((dx * dx) + (dy * dy))


class HumanTracker:
    """A track represents a bounding box that was identified as being the
    same across a sequence of frames.

    Args:
        key (int): The index of this track.
    
    Attributes:
        index_bbox_pairs (list): A list of (index, bbox) tuples, 
        where `index` represents the frame index and `bbox` is an 
        instance of the `BoundingBox` class.
    """

    def __init__(self, key):
        self.key = key
        self.index_bbox_pairs = []

    def add(self, index, bbox):
        self.index_bbox_pairs.append((index, bbox))


# class TripProc:
#     def __init__(self, mechanic):
#         self.bicycles = []
#         for bike in self.bicycles:
#             mechanic.clean(bike)
#             mechanic.pump(bike)
#             mechanic.lump(bike)

# class TripOk:
#     def __init__(self, mechanic):
#         self.bicycles = []
#         for bike in self.bicycles:
#             mechanic.prepare(bike)
    
# class Trip:
#     def __init__(self, mechanic):
#         self.bicycles = []
#         mechanic.prepare_trip(self)

# class Mechanic:
#     def __init__(self):
#         pass
    
#     def prepare_trip(self, trip):
#         for bike in trip.bicycles:
#             self.prepare_bicycle(bike)
    
#     def prepare_bicycle(self, bike):
#         pass