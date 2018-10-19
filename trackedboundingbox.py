from detectedboundingbox import DetectedBBox

class TrackedBBox(DetectedBBox):
    def __init__(self, origin, width, height, identifier, score, obj_class, filtering_results, parent_track_id):
        super().__init__(origin, width, height, identifier, score, obj_class, filtering_results)
        self.parent_track_ids = [parent_track_id]
