class Video:
    """
    A video is a list of Frames, each representing an image, that was loaded
    with OpenCV. It also contain properties such as the framerate (FPS), the
    format (e.g.: mp4), the name of the file, etc.
    """
    def __init__(self, frames=None):
        self.frames = [] if frames is None else frames
