import os
import sys
import json
import math
import cv2

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
