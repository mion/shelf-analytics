class DetectionResult:
    """
    The result of object detection.
    """
    def __init__(self, frames, dbboxes_by_frame_idx):
        self.frames = frames
        self.dbboxes_by_frame_idx = dbboxes_by_frame_idx
