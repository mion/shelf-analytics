import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))
from tnt import load_json
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
import shutil
import argparse

DEFAULT_MIN_AREA_PERSON = 4500
DEFAULT_MAX_AREA_PERSON = 14000
DEFAULT_MIN_SCORE = 0.9

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

def find_detection_failure_frame_indexes(bboxes_per_frame, min_area_person, max_area_person, min_score):
    """
    Returns an array of indexes of frames containing at least one of these:
        - A large bbox with high score (two people were detected as one)
        - A bbox with low score but sufficient area
        - Two or more bboxes are intersecting
    """
    indexes = []
    for idx in range(len(bboxes_per_frame)):
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
                        # TODO intersection area percentage is larger than P
                        if bbox.has_intersection_with(other_bbox):
                            indexes.append(idx)
    return indexes

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tags_path', help='path to the tags JSON file')
    ap.add_argument('-a', '--area_range', default='{},{}'.format(DEFAULT_MIN_AREA_PERSON, DEFAULT_MAX_AREA_PERSON), help='an area range in pixels of a person bbox (default: "{:d},{:d}")'.format(DEFAULT_MIN_AREA_PERSON, DEFAULT_MAX_AREA_PERSON))
    ap.add_argument('-s', '--min_score', default=DEFAULT_MIN_SCORE, type=float, help='minimum score to be considered a succesful detection (default: {:2f})'.format(DEFAULT_MIN_SCORE))
    ap.add_argument('output_path', help='path to output directory where frames to be tagged will be saved')
    args = ap.parse_args()
    tags = load_json(args.tags_path)
    min_area, max_area = [int(s) for s in vars(args).get('area_range').split(',')]
    min_score = vars(args).get('min_score')
    bboxes_per_frame = load_bboxes_per_frame(tags['frames'])
    indexes = find_detection_failure_frame_indexes(bboxes_per_frame, min_area, max_area, min_score)
    for idx in indexes:
        img_path = tags['frames'][idx]['tagged_frame_image_path']
        shutil.copy(img_path, args.output_path)
