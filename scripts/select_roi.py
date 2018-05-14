import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import cv2
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video')
    args = parser.parse_args()

    video = cv2.VideoCapture(args.video_path)
    if not video.isOpened():
        print('ERROR: could not open video.')
        sys.exit(1)
    
    ok, frame = video.read()
    if not ok:
        print('ERROR: Cannot read first frame from video file.')
        sys.exit()
    
    bbox = cv2.selectROI(frame, False)
    y1, x1, y2, x2 = bbox
    print(json.dumps({
        'bbox': [y1, x1, y2, x2]
    }))