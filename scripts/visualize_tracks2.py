import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import json
import cv2
import cvutil
import tnt
import numpy as np
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

def draw_transition_line(frame, orig_bbox, dest_bbox, distance):
    if distance > 0:
        # y1 x1 y2 x2
        orig_width = orig_bbox[3] - orig_bbox[1]
        orig_height = orig_bbox[2] - orig_bbox[0]
        orig_center = (int(orig_bbox[1] + orig_width / 2), int(orig_bbox[0] + orig_height / 2))
        dest_width = dest_bbox[3] - dest_bbox[1]
        dest_height = dest_bbox[2] - dest_bbox[0]
        dest_center = (int(dest_bbox[1] + dest_width / 2), int(dest_bbox[0] + dest_height / 2))
        return cv2.line(frame, orig_center, dest_center, (0, 155, 255), 1)
    else:
        return None

# TODO add this to a shared json file
DISTANCES = {
    "SNAPPING": 25,
    "RETAKING": 50
}

def draw_calibration_footer(frame):
    height, width, channels = frame.shape
    FOOTER_HEIGHT = 200
    # create larger black img 
    frame_with_footer = np.zeros((height + FOOTER_HEIGHT, width, channels), np.uint8)
    # copy everything over
    frame_with_footer[0:(height - 1), 0:(width - 1)] = frame[0:(height - 1), 0:(width - 1)]
    # draw lines and labels
    PADDING = 50
    LINE_HEIGHT = 75
    frame_with_footer = cv2.line(frame_with_footer, 
            (PADDING, height + PADDING), 
            (PADDING + DISTANCES["SNAPPING"], height + PADDING),
            (0, 255, 255), 3)
    frame_with_footer = cvutil.draw_text_on_frame(frame_with_footer, 
                            "SNAPPING",
                            PADDING,
                            height + PADDING - 10,
                            (0, 255, 255))

    frame_with_footer = cv2.line(frame_with_footer, 
            (PADDING, height + PADDING + LINE_HEIGHT), 
            (PADDING + DISTANCES["RETAKING"], height + PADDING + LINE_HEIGHT),
            (0, 255, 255), 3)
    frame_with_footer = cvutil.draw_text_on_frame(frame_with_footer, 
                            "RETAKING",
                            PADDING,
                            height + PADDING - 10 + LINE_HEIGHT,
                            (0, 255, 255))

    return frame_with_footer

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
                transition = track[i - track_first_index]["transition"]
                
                for obj_detected_bbox in tags["frames"][i]["boxes"]:
                    found_index_bbox_track_set = search_index_bbox_track_set(already_tracked_index_bbox_track_sets, i, obj_detected_bbox)
                    if found_index_bbox_track_set is not None:
                        _, _, belongs_to_track_index = found_index_bbox_track_set
                        cvutil.draw_label_on_frame(frame, "#{0}".format(belongs_to_track_index), obj_detected_bbox[1], obj_detected_bbox[0])
                        cvutil.draw_bbox_on_frame(frame, obj_detected_bbox, rect_color=(0,0,0), text_color=(105,105,105))
                    else:
                        cvutil.draw_bbox_on_frame(frame, obj_detected_bbox, rect_color=(205,205,205), text_color=(255,255,255))

                curr_bbox = track[i - track_first_index]["bbox"]
                cvutil.draw_rect_on_frame(frame, transition["from_bbox"], rect_color=(255,200,200))
                draw_transition_line(frame, transition["from_bbox"], curr_bbox, transition["distance"])
                cvutil.draw_bbox_on_frame(frame, curr_bbox, rect_color=(255, 155, 0), text_color=(0,155,255))
                cvutil.draw_label_on_frame(frame, transition["type"], curr_bbox[1], curr_bbox[0], bg_color=(255,0,0))
                already_tracked_index_bbox_track_sets.append((i, track[i - track_first_index]["bbox"], track_index))

                # draw lines for calibration
                frame_with_footer = draw_calibration_footer(frame)

                cvutil.save_image(frame_with_footer, "track-{0}-frame-{1}.png".format(track_index, i), track_folder_path)
