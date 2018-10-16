"""
This module is a blueprint for the design of the full program.
"""

###############################################################################
# Data definitions
###############################################################################
class Video:
    """
    A video is a list of Frames, each representing an image, that was loaded
    with OpenCV. It also contain properties such as the framerate (FPS), the
    format (e.g.: mp4), the name of the file, etc.
    """
    def __init__(self, frames=None):
        self.frames = [] if frames is None else frames

class Frame:
    """
    A frame loaded from a video. This class is a wrapper on top of an image
    loaded with OpenCV. It also contains properties such as width, height,
    color channels, etc.
    """
    def __init__(self, image):
        self.image = image

class CalibrationParameters(dict):
    """
    The tracking algorithm needs some arbitrary values to function (eg.: how
    small can the bounding box of a detected object be so it is still
    considered a human being). This class is simply a dictionary containing
    such values.
    """
    pass

class Point:
    """
    A point in 2-dimensional space.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangle:
    """
    A rectangle in 2D with an origin (a Point representing the upper left
    corner), width and height.
    """
    def __init__(self, origin, width, height):
        self.origin = origin
        self.width = width
        self.height = height

class DetectedRectangle(Rectangle):
    """
    A rectangle that was outputted from object detection.
    """
    def __init__(self, score, obj_class):
        self.score = score
        self.obj_class = obj_class

class PostDetectionFrame(Frame):
    """
    A frame that was outputted from object detection, containing a list of
    detected rectangles.
    """
    def __init__(self, drects):
        self.detected_rectangles = drects

class Track:
    """
    A track identifies the same detected rectangle (representing a person)
    across many different frames. (By 'frame' we mean a PostDetectionFrame.)
    """
    def __init__(self):
        self.steps = []

class Step:
    """
    A step is a simple structure containing the index of the frame and the
    rectangle (identifying the same person across all frames) and the
    transition from last step. (By 'frame' we mean a PostDetectionFrame.)
    """
    def __init__(self, pdframe_index, drect_index, trans):
        self.post_detection_frame_index = pdframe_index
        self.detected_rectangle_index = drect_index
        self.transition = trans

from enum import Enum
class Transition(Enum):
    """
    An Enum representing how a detected rectangle inside a certain frame
    is connnected to (transitions to) to another detected rectangle in the
    following frame. (By 'frame' we mean a PostDetectionFrame.)
    """
    first = 1
    snapped = 2
    tracked = 3
    retaken = 4
    interpolated = 5

class Event:
    """
    An event that is captured whenever a detected rectangle (representing a
    person) interacts with a ROI (region of interest) that was previously
    defined.
    """
    def __init__(self, event_type):
        self.type = event_type

class WalkEvent(Event):
    """
    A walk event is captured whenever a detected rectangle (representing a
    person) goes through a ROI (region of interest) without stopping for a
    certain amount of time.
    """
    def __init__(self):
        super().__init__('walk')

class PonderEvent(Event):
    """
    A ponder event is captured whenever a detected rectangle (representing a
    person) arrives at a ROI (region of interest) and stays there for a certain
    amount of time.
    """
    def __init__(self):
        super().__init__('ponder')

class TouchEvent(Event):
    """
    A touch event is captured whenever a detected rectangle (representing a
    person) enters and then exits a ROI (region of interest) in a short span of
    time.
    """
    def __init__(self):
        super().__init__('touch')

rois = {
    'aisle_front': (rect_aisle_front, ['walk', 'ponder']),
    'shelf_main': (rect_shelf_main, ['touch'])
}

###############################################################################
# Function wishlist
###############################################################################

