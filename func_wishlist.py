from data_definitions import *

def detect_humans(video, config, params):
    """Detect human beings that appear in the frames of a `Video` object.

    Applies object detection using a deep learning framework such as MaskRCNN
    and then filters out objects that are not human beings or have unwanted
    properties. For example, some detected bboxes have a high score
    (confidence) but are actually too small or too large to be a person.
    In this example the area has to be calibrated according to the placement of the camera.

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

def track_humans(pdvideo, config, params):
    """Attempt to link one person to the most likely detected bboxes
    across various frames.

    Uses an `OpenCV` object tracker under the hood for basic object tracking,
    then applies ad-hoc heuristics to handle cases such as missing detected
    bboxes, two drects merging into one, using the drect velocity to guess
    its next position, etc.

    Parameters
    ----------
    pdvideo : PostDetectionVideo
        The `PostDetectionVideo` object containing the frames and the detected
        bboxes that will be used for tracking.
    config : dict
        A dictionary specifying options such as the object tracker algorithm to
        be used (e.g. `KCF`, `MIL`, etc).
    params : dict
        A dictionary specifying values that should be calibrated according to
        the placement of the camera.

    Returns
    -------
    tracking_result : TrackingResult
        A `TrackingResult` object that embodies the result of the application
        of this human tracking algorithm.
    """
    return []

def extract_events(tracking_result, rois, config, params):
    """Extracts events according to some regions of interest (ROIs).

    A ROI is simply a bbox accompanied by a list of events to be
    extracted from the intersection of a human bbox and this one.

    Parameters
    ----------
    tracking_result : TrackingResult
        A `TrackingResult` object that embodies the result of the application
        of this human tracking algorithm.
    rois : dict
        A dictionary specifying the desired ROIs (regions of interest). The
        dict must have this format:
            `name -> (bbox, ev_types)`
        Where `name` is a string representing the name of the ROI (e.g.
        "front_aisle"), `bbox` is the `BoundingBox` delimiting the actual region
        and `ev_types` is a list of strings defining the type of `Event` to be
        captured (e.g. "walk", "ponder" or "touch").
    config : dict
        A dictionary specifying options such as the object tracker algorithm to
        be used (e.g. `KCF`, `MIL`, etc).
    params : dict
        A dictionary specifying values that should be calibrated according to
        the placement of the camera.

    Returns
    -------
    events : list
        A list of `Event` objects that were extracted upon the interaction of
        a human with a region of interest. The `Event` object contains the
        name of ROI and also its type.
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
