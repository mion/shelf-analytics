from data_definitions import *

def detect_humans(video, config, params):
    """Detect human beings that appear in the frames of a `Video` object.

    Applies object detection, filtering out objects that are not human
    beings.

    Parameters
    ----------
    video : Video
        The `Video` object containing the frames upon which object detection
        will be applied, one by one.
    config : dict
        A dictionary specifying options such as the detection engine to be used
        (e.g. `YOLO` or `MaskRCNN`).
    params : dict
        A dictionary specifying values that should be calibrated according to
        the placement of the camera, and also that could be iterated upon
        to increase overall accuracy.

    Returns
    -------
    pdvideo : PostDetectionVideo
        A `PostDetectionVideo` object that embodies the result of the
        application of object detection to its frames.
    """
    return None

def filter_detected_rectangles(pdvideo, filters, params):
    """Removes detected rectangles with unwanted properties (e.g. too small).

    For example, some detected rectangles have a high score (confidence) but are actually
    too small or too large to be a person. In this example the area has to be
    calibrated according to the placement of the camera.

    Parameters
    ----------
    pdvideo : PostDetectionVideo
        The `PostDetectionVideo` object containing the frames and the detected
        rectangles that will be filtered.
    filters : list
        A list of filters to be applied. A filter is a function with the
        following signature:
        `f(drect:DetectedRectangle, params:dict) -> should_be_removed:bool`
    params : dict
        A dictionary specifying values that should be calibrated according to
        the placement of the camera.

    Returns
    -------
    filtered_pdvideo : PostDetectionVideo
        A `PostDetectionVideo` object that had some of its detected rectangles
        filtered out.
    """
    return None

def track_humans(pdvideo, config, params):
    """Attempt to link one person to the most likely detected rectangles
    across various frames.

    Uses an `OpenCV` object tracker under the hood for basic object tracking,
    then applies ad-hoc heuristics to handle cases such as missing detected
    rectangles, two drects merging into one, using the drect velocity to guess
    its next position, etc.

    Parameters
    ----------
    pdvideo : PostDetectionVideo
        The `PostDetectionVideo` object containing the frames and the detected
        rectangles that will be used for tracking.
    config : dict
        A dictionary specifying options such as the object tracker algorithm to
        be used (e.g. `KCF`, `MIL`, etc).
    params : dict
        A dictionary specifying values that should be calibrated according to
        the placement of the camera.

    Returns
    -------
    tresult : TrackingResult
        A `TrackingResult` object that embodies the result of the application
        of this human tracking algorithm.
    """
    return []

def load_video(file_path):
    """Loads a video file in memory using ``OpenCV``.

    The video will be split into many frames, each a ``Numpy`` image, and they
    will ALL be loaded in RAM memory.

    Parameters
    ----------
    file_path : str
        The full path of the video file to load.

    Returns
    -------
    Video
        A `Video` object containing the loaded frames and some other
        properties.

    Raises
    ------
    ValueError
        If `file_path` is an empty string or `None`.
    """
    if not file_path:
        raise ValueError('file_path must not be empty')
    return Video()
