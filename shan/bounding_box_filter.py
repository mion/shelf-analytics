from tnt import load_json

cfg = load_json('shan/calibration-config.json')

class BoundingBoxFilterPolicy:
    def __init__(self, bbox):
        self.bbox = bbox
    
    def apply(self):
        return {'type': 'default', 'filtered': False}

class MinScorePolicy(BoundingBoxFilterPolicy):
    def __init__(self, bbox):
        super().__init__(bbox)
    
    def apply(self):
        if self.bbox.score < cfg['MIN_SCORE']:
            return {'type': 'score', 'filtered': True, 'message': 'score too low ({})'.format(str(self.bbox.score))}
        else:
            return {'type': 'score', 'filtered': False}

class AreaPolicy(BoundingBoxFilterPolicy):
    def __init__(self, bbox):
        super().__init__(bbox)
    
    def apply(self):
        if self.bbox.area < cfg['MIN_BBOX_AREA']:
            return {'type': 'area', 'filtered': True, 'message': 'area too low ({})'.format(str(self.bbox.area))}
        elif self.bbox.area > cfg['MAX_BBOX_AREA']:
            return {'type': 'area', 'filtered': True, 'message': 'area too high ({})'.format(str(self.bbox.area))}
        else:
            return {'type': 'area', 'filtered': False}

class BoundingBoxFilter:
    """
    This class receives a FrameBundle and a number of policies to filter out
    bounding boxes according to these policies.

    If policies is None, then use all policies known.
    """
    def __init__(self, policy_classes=None):
        if policy_classes is None:
            self.policy_classes = [MinScorePolicy, AreaPolicy]
        else:
            self.policy_classes = policy_classes
    
    def filter_frame_bundle(self, frame_bundle):
        for bbox in frame_bundle.bboxes:
            for policy_class in self.policy_classes:
                policy = policy_class(bbox)
                bbox.filtering_results.append(policy.apply())