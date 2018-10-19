class Frame:
    """
    A frame loaded from a video. This class is a wrapper on top of an image
    loaded with OpenCV. It also contains properties such as width, height,
    color channels, etc.
    """
    def __init__(self, image):
        self.image = image
