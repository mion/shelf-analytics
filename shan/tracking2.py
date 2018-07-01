import os
import sys
import json
import math
import cv2

class HumanTrackAnalyzer:
    """
    A track represents a bounding box that was identified as being the
    same person across a sequence of frames.
    """

    def __init__(self, frame_bundles):
        self.frame_bundles = frame_bundles

    def extract_tracks(self, max_number_of_tracks):
        return {
            "frames": []
        }