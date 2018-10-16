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
