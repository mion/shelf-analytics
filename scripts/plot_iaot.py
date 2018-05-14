import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import matplotlib.pyplot as plt
import cv2
import json
import argparse
import numpy as np

def load_json(path):
  with open(path, "r") as json_file:
    return json.loads(json_file.read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('iaot_path', help='path to the intersection area over time JSON file')
    parser.add_argument('track_index', help='index of the track in root array of the iaot JSON file (0-based)')
    parser.add_argument('roi_name', help='name of the ROI as indexed in the objects found in the iaot JSON file')
    args = parser.parse_args()

    intersection_area_over_time = load_json(args.iaot_path)
    track_index = int(args.track_index)
    roi_name = args.roi_name
    # Example:
    #
    # [{                    -> track_index = 0
    #     "roi_1": [{       -> roi_name = "roi_1"
    #         "index": 4,   -> index of the frame in the video
    #         "area": 0,    -> intersection area
    #         "bbox": null  -> bbox of the intersection area
    #     }, {
    #         "index": 5,
    #         "area": 0,
    #         "bbox": null
    # ...
    #
    iaot = intersection_area_over_time[track_index][roi_name]

    X = []
    Y = []
    for i in range(len(iaot)):
        X.append(iaot[i]["index"])
        Y.append(iaot[i]["area"])
    
    # plt.scatter(X, Y, s=60, c='red')
    y = np.array(Y)
    dy = np.diff(y)
    dY = dy.tolist()

    X.pop()
    plt.scatter(X, dY, s=60, c='blue')

    # plt.xlim(0,1000)
    # plt.ylim(0,100)

    # plt.title('Intersection Area over Time - Track {0} / ROI "{1}"'.format(track_index, roi_name))
    plt.title('Diff -1 of Intersection Area over Time - Track {0} / ROI "{1}"'.format(track_index, roi_name))
    plt.xlabel('Frame Index (zero-based uint)')
    plt.ylabel('Intersection Area (pixels)')

    plt.show()