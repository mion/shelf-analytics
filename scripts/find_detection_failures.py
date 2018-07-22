import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))
from tnt import load_json
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
import argparse

def load_bboxes_per_frame(frame_objs):
    bboxes_per_frame = []
    for idx in range(len(frame_objs)):
        bboxes_per_frame.append([])
        obj = frame_objs[idx]
        for i in range(len(obj['boxes'])):
            bbox = BBox(obj['boxes'][i], BBoxFormat.y1_x1_y2_x2)
            bbox.score = obj['scores'][i]
            bbox.frame_index = idx
            bboxes_per_frame[idx].append(bbox)
    return bboxes_per_frame

def find_detection_failure_frame_indexes(bboxes_per_frame, min_area_person, max_area_person, min_score, min_distance):
    """
    Returns an array of indexes of frames containing at least one of these:
        - A large bbox with high score (two people were detected as one)
        - A bbox with low score but sufficient area
        - Two or more bboxes very close to one another
    """
    indexes = []
    for idx in bboxes_per_frame:
        for bbox in bboxes_per_frame[idx]:
            if bbox.area > max_area_person:
                indexes.append(idx)
            elif bbox.area < max_area_person and bbox.area > min_area_person and bbox.score < min_score:
                indexes.append(idx)
            else:
                for other_bbox in bboxes_per_frame[idx]:
                    if bbox.id == other_bbox.id:
                        continue
                    else:
                        if bbox.distance_to(other_bbox) < min_distance:
                            indexes.append(idx)
    return indexes

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tags_path', 'path to the tags JSON file')
    ap.add_argument('output_path', help='path to output directory where frames to be tagged will be saved')
    args = ap.parse_args()
    tags = load_json(args.tags_path)
    bboxes_per_frame = load_bboxes_per_frame(tags['frames'])
    pdb.set_trace()
