import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import json
import cv2
import cvutil
import tnt
from colorize import yellow

import pdb

def load_json(path):
  with open(path) as json_file:
    return json.loads(json_file.read())

def search_index_bbox_track_set(already_tracked_index_bbox_track_sets, searching_index, searching_bbox):
    for index, bbox, track in already_tracked_index_bbox_track_sets:
        if searching_index == index and searching_bbox == bbox:
            return (index, bbox, track)
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", help="path to the video")
    parser.add_argument("tags_path", help="path to a tags JSON file")
    parser.add_argument("tracks_path", help="path to a tracks JSON file")
    parser.add_argument("output_dir", help="path to output directory")
    args = parser.parse_args()

    tags = load_json(args.tags_path)
    tracks = load_json(args.tracks_path)
    print(yellow("{0} tracks".format(str(len(tracks)))) + " found in JSON file.")

    already_tracked_index_bbox_track_sets = []
    for track_index in range(len(tracks)):
        print("Loading video...") # TODO load only once, I'm doing this bc frames cannot be re-used as it is
        video = cv2.VideoCapture(args.video_path)
        # Exit if video not opened.
        if not video.isOpened():
            print("ERROR: could not open video")
            sys.exit()
        width = video.get(3)
        height = video.get(4)
        frames = cvutil.read_frames_from_video(video)
        print("Exporting track " + yellow("#{0}".format(str(track_index))))
        track = tracks[track_index]
        track_first_index = track[0]["index"]
        track_last_index = track[len(track) - 1]["index"]

        track_folder_path = os.path.join(args.output_dir, "track-{0}".format(track_index))
        try:
            os.mkdir(track_folder_path)
        except FileExistsError as err:
            print(yellow("ERROR: could not create directory at {0}".format(track_folder_path)))
            print(err)

        for i in range(len(frames)):
            if i >= track_first_index and i <= track_last_index:
                frame = frames[i]
                for obj_detected_bbox in tags["frames"][i]["boxes"]:
                    # index_bbox_track_set = (i, obj_detected_bbox, track_index)
                    found_index_bbox_track_set = search_index_bbox_track_set(already_tracked_index_bbox_track_sets, i, obj_detected_bbox)
                    if found_index_bbox_track_set is not None:
                        _, _, belongs_to_track_index = found_index_bbox_track_set
                        cvutil.draw_label_on_frame(frame, "t#{0}".format(belongs_to_track_index), obj_detected_bbox[1], obj_detected_bbox[0])
                        cvutil.draw_bbox_on_frame(frame, obj_detected_bbox, rect_color=(0,0,0), text_color=(55,55,55))
                    else:
                        cvutil.draw_bbox_on_frame(frame, obj_detected_bbox, rect_color=(255,255,255), text_color=(255,255,255))

                cvutil.draw_bbox_on_frame(frame, track[i - track_first_index]["bbox"], rect_color=(255, 155, 0), text_color=(0,155,255))
                already_tracked_index_bbox_track_sets.append((i, track[i - track_first_index]["bbox"], track_index))
                cvutil.save_image(frame, "track-{0}-frame-{1}.png".format(track_index, i), track_folder_path)
