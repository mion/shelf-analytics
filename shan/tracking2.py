import os
import sys
import json
import math
import cv2

DEFAULT_MIN_SNAPPING_DISTANCE = 150.0
TRACKER_FAILED_MIN_SNAPPING_DISTANCE = 300.0

class BoundingBox:
    """A bounding box is just a rectangle. This class helps handling the
    different formats that some libs use.
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