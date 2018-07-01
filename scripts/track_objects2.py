import pdb

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import argparse
from tnt import load_json, load_frames, load_bboxes_per_frame
from tracking2 import HumanTracker
from frame_bundle import load_frame_bundles
from bounding_box_filter import BoundingBoxFilter as BBoxFilter

cfg = load_json('shan/calibration-config.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    parser.add_argument('tags_path', help='path to a tags JSON file')
    parser.add_argument('output_dir_path', help='path to the output directory where a JSON file with the tracks will be saved')
    args = parser.parse_args()
    
    print('Loading tags...')
    tags = load_json(args.tags_path)

    print('Loading frame bundles from video...')
    frame_bundles = load_frame_bundles(args.video_path, tags)

    print('Filtering bounding boxes inside frame bundles...')
    bbox_filter = BBoxFilter()
    for frame_bundle in frame_bundles:
        bbox_filter.filter_frame_bundle(frame_bundle)
    
    pdb.set_trace()
    
    