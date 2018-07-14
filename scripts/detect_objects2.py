import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
from detection import detect_humans_in_every_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir_path", help="input directory with many images inside")
    parser.add_argument("output_file_path", help="path to a JSON file where the data will be saved")
    parser.add_argument("--frames_dir_path", help="if specified, save frames after detection in this directory")
    args = parser.parse_args()

    detect_humans_in_every_image(args.input_dir_path, args.output_file_path, args.frames_dir_path)
