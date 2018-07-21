import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import argparse
from tnt import load_json, save_json

ap = argparse.ArgumentParser()
ap.add_argument('input_tags_path', help='path to broken tags.json')
ap.add_argument('output_tags_path', help='path to correct tags.json')
args = ap.parse_args()

tags = load_json(args.input_tags_path)
for frame in tags['frames']:
    img_path = frame['tagged_frame_image_path']
    _, filename = os.path.split(img_path)
    name, _ = os.path.splitext(filename)
    parts = name.split('-')
    correct_frame_index = int(parts[len(parts) -1]) - 1
    frame['frame_index'] = correct_frame_index

tags['frames'] = sorted(tags['frames'], key=lambda fr: fr['frame_index'])

save_json(tags, args.output_tags_path)
