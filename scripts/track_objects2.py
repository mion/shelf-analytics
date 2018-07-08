import pdb

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import argparse
from tnt import load_json, load_frames, load_bboxes_per_frame
from frame_bundle import load_frame_bundles
from bounding_box_filter import BoundingBoxFilter as BBoxFilter
from tracking2 import compute_tracking_result

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
    
    print('Analyzing tracks...')
    # tracks = extract_tracks(frame_bundles, cfg['MAX_TRACKS'])
    tracking_result = compute_tracking_result(frame_bundles, cfg['MAX_TRACKS'])

    print('Exporting tracking result...')
    output_file_path = os.path.join(args.output_dir_path, 'tracking-result.json')
    tracking_result.save_as_json(output_file_path)
    # print('Exporting tracks...')
    # output_file_path = os.path.join(args.output_dir_path, "tracks.json")
    # with open(output_file_path, "w") as tracks_file:
    #     json.dump(tracks, tracks_file)
    