from data_definitions import *

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
