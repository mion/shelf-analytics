import os
import sys
import argparse
import cv2
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/workers'))

from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from util import load_json
from drawing import draw_bbox_with_title

def test_drawing(img, bboxes):
    for bbox in bboxes:
        img = draw_bbox_with_title(img, bbox, title_text="Test", text_color=(255, 255, 255))
    cv2.imshow('image', img)
    k = cv2.waitKey(0) & 0xFF
    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image', help='path to image file')
    parser.add_argument('-t', '--tags', help='path to tags JSON')
    parser.add_argument('-f', '--frame', help='index of the frame in the tags JSON')
    args = parser.parse_args()

    tags = load_json(args.tags)
    raw_bboxes = tags[args.frame]
    test_drawing(cv2.imread(args.image, 0), bboxes=[BBox(b, BBoxFormat.y1_x1_y2_x2) for b in raw_bboxes])

if __name__ == '__main__':
    main()
