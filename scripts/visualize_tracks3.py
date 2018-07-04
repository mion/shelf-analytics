import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("frames_path", help="path to the video")
    parser.add_argument("tags_path", help="path to a tags JSON file")
    parser.add_argument("tracks_path", help="path to a tracks JSON file")
    args = parser.parse_args()
