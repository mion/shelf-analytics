from boundingbox import BBox

class DetectedBBox(BBox):
    """
    A bbox that was outputted from object detection.
    """
    def __init__(self, origin, width, height, identifier, score, obj_class, filtering_results=None):
        super().__init__(origin, width, height)
        self.identifier = identifier
        self.score = score
        self.obj_class = obj_class
        self.filtering_results = [] if filtering_results is None else filtering_results
