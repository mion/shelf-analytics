import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import subprocess
import argparse
import numpy as np
import cv2

from tnt import load_json, load_frames, get_name_without_ext
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from drawing import draw_bbox_outline
from cvutil import save_image

BBOX_OUTLINE_COLOR = (255, 0, 255)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    parser.add_argument('annotation_path', help='path to the annotation JSON file')
    parser.add_argument('output_dir_path', help='path to the output directory')
    args = parser.parse_args()

    frames = load_frames(args.video_path)
    annotation = load_json(args.annotation_path)

    for idx in range(len(frames)):
        frame = frames[idx]
        for track in annotation['tracks']:
            if track[idx] is not None:
                raw_bbox = [track[idx]['x'], track[idx]['y'], track[idx]['w'], track[idx]['h']]
                bbox = BBox(raw_bbox, BBoxFormat.x1_y1_w_h)
                frame = draw_bbox_outline(frame, bbox, BBOX_OUTLINE_COLOR, 1)
        save_image(frame, 'annotated-frame-{:09}.png'.format(idx), args.output_dir_path)

    # for roi in rois:
    #     bbox = BBox(roi['bbox'], BBoxFormat.y1_x1_y2_x2)
    #     sample_frame = draw_bbox_outline(sample_frame, bbox, ROI_BBOX_OUTLINE_COLOR)
    #     sample_frame = draw_text(sample_frame, roi['name'], bbox.topLeft, ROI_BBOX_PROPS_COLOR)
    
    # video_filename = get_name_without_ext(args.video_path)
    # rois_filename = get_name_without_ext(args.rois_path)
    # img_filename = '-'.join([video_filename, rois_filename]) + '.png'
    # save_image(sample_frame, img_filename, args.output_dir_path)