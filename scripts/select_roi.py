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
    
    cv_bbox = cv2.selectROI(frame, False)
    x1 = int(cv_bbox[0])
    y1 = int(cv_bbox[1])
    x2 = int(cv_bbox[0] + cv_bbox[2])
    y2 = int(cv_bbox[1] + cv_bbox[3])
    print(json.dumps({
        'bbox': [y1, x1, y2, x2]
    }))