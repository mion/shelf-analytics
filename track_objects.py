# -*- coding: utf-8 -*-
import pdb
import json
import cv2
import sys
import argparse

from tracking import HumanTracker

def load_tags(path):
  with open(path, "r") as tags_file:
    return json.loads(tags_file.read())

def read_frames_from_video(video):
    is_first_frame = True
    frames = []
    while True:
        ok, frame = video.read()
        if not ok and is_first_frame:
            return None
        elif not ok and not is_first_frame:
            break
        else:
            is_first_frame = False
            frames.append(frame)
    return frames

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", help="path to the video")
    parser.add_argument("tags_path", help="path to a tags JSON file")
    args = parser.parse_args()

    print("Loading video...")
    video = cv2.VideoCapture(args.video_path)
    # Exit if video not opened.
    if not video.isOpened():
        print("ERROR: could not open video")
        sys.exit()
    frames = read_frames_from_video(video)
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
        for bbox in tags["frames"][i]["boxes"]:
            # IMPORTANT opencv expects tuples, not lists;
            #           tuples are used as index so ints are necessary;
            bboxes_list.append(tuple([int(n) for n in bbox])) 
        list_of_bboxes_lists.append(bboxes_list)

    print("Tracking humans...")
    human_tracker = HumanTracker(frames=frames,
                                 list_of_bboxes_lists=list_of_bboxes_lists,
                                 obj_tracker_type="KCF")
    has_untracked_humans = True
    while has_untracked_humans:
        has_untracked_humans = human_tracker.track_someone_once()
    tracks_json_string = human_tracker.dump_tracks_json_string()
    print(tracks_json_string)
