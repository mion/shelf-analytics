# -*- coding: utf-8 -*-
import pdb

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import cv2
import argparse

import cvutil

from tracking import HumanTracker
from bounding_box import BoundingBox

def load_tags(path):
  with open(path, "r") as tags_file:
    return json.loads(tags_file.read())

DEFAULT_MIN_SCORE = 0.95 # TODO visualize this for calibration
DEFAULT_MIN_BBOX_AREA = 7500 # TODO visualize this for claibration
DEFAULT_MAX_BBOX_AREA = 15000 # TODO visualize this for calibration

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", help="path to the video")
    parser.add_argument("tags_path", help="path to a tags JSON file")
    parser.add_argument("output_dir_path", help="path to the output directory where a JSON file with the tracks will be saved")
    args = parser.parse_args()

    print("Loading video...")
    video = cv2.VideoCapture(args.video_path)
    # Exit if video not opened.
    if not video.isOpened():
        print("ERROR: could not open video")
        sys.exit()
    frames = cvutil.read_frames_from_video(video)
    if frames == None:
        print('ERROR: could not read frames from video file')
        sys.exit()
    else:
        print("Done, loaded " + str(len(frames)) + " frames")

    print("Loading tags...") 
    tags = load_tags(args.tags_path)
    list_of_bboxes_lists = []
    for i in range(len(tags["frames"])):
        bboxes_list = []
        for j in range(len(tags["frames"][i]["boxes"])): 
            score = tags["frames"][i]["scores"][j]
            bbox = tags["frames"][i]["boxes"][j] # should be same length as tags["frames"][i]["scores"]
            # detected objs with p < .95 should not be considered people
            # remove bboxes that are too small to be a person
            bounding_box = BoundingBox(bbox, BoundingBox.FORMAT_Y1_X1_Y2_X2)
            if score > DEFAULT_MIN_SCORE and bounding_box.area > DEFAULT_MIN_BBOX_AREA and bounding_box.area < DEFAULT_MAX_BBOX_AREA:
                # IMPORTANT opencv expects tuples, not lists;
                #           tuples are used as index so ints are necessary;
                bboxes_list.append(tuple([int(n) for n in bbox])) 
        list_of_bboxes_lists.append(bboxes_list)

    print("Tracking humans...")
    human_tracker = HumanTracker(frames=frames,
                                 list_of_bboxes_lists=list_of_bboxes_lists,
                                 obj_tracker_type="KCF")
    has_untracked_humans = True
    tracks_count = 0
    max_tracks_count = 100
    while tracks_count < max_tracks_count and has_untracked_humans:
        has_untracked_humans = human_tracker.track_someone_once()
        tracks_count += 1
    # tracks_json_string = human_tracker.dump_tracks_json_string()
    # print(tracks_json_string)
    tracks = human_tracker.get_tracks()

    output_file_path = os.path.join(args.output_dir_path, "tracks.json")
    with open(output_file_path, "w") as tracks_file:
        json.dump(tracks, tracks_file)
