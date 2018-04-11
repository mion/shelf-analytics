# -*- coding: utf-8 -*-
import pdb
import json
import cv2
import sys
import argparse

from shan import load_tagged_bundle
import tnt

major_ver, minor_ver, subminor_ver = cv2.__version__.split(".")


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


def has_humans(tag):
    return len(tag['boxes']) > 0


def box_to_str(box):
    return ",".join(str(n) for n in box)


def str_to_box(str):
    return [int(s) for s in str.split(",")]


# EXAMPLES
#
# boxstr_by_frame_by_human_id = {
#   "h0": {
#       1: "5,5,15,35",
#       2: "7,6,17,36",
#       ...
#   },
#   "h1": {
#       2: "90,100,190,200"
#   }
# }
#
# human_id_by_boxstr_by_frame_index = {
#   0: {
#
#   },
#   1: {
#       "5,5,15,35": "h0"
#   },
#   2: {
#       "7,6,17,36": "h0",
#       "90,100,190,200": "h1"
#   }
# }


def available_untracked_boxes(current_frame_index, tag, human_id_by_boxstr_by_frame_index):
    available_boxes = []
    for i in range(len(tag["boxes"])):
        box = tag["boxes"][i]
        boxstr = box_to_str(box)
        if (current_frame_index not in human_id_by_boxstr_by_frame_index) or (boxstr not in human_id_by_boxstr_by_frame_index[current_frame_index]):
            available_boxes.append(box)
    return available_boxes


def choose_box(boxes):
    return boxes[0] # for now let's use the first


def create_track(box,
                 frame_index,
                 next_human_id,
                 boxstr_by_frame_by_human_id,
                 human_id_by_boxstr_by_frame_index):
    h_id = "h" + str(next_human_id)
    boxstr = box_to_str(box)

    if h_id in boxstr_by_frame_by_human_id:
        boxstr_by_frame_by_human_id[h_id][frame_index] = boxstr
    else:
        boxstr_by_frame_by_human_id[h_id] = {
            frame_index: boxstr
        }
    
    if frame_index in human_id_by_boxstr_by_frame_index:
        human_id_by_boxstr_by_frame_index[frame_index][boxstr] = h_id
    else:
        human_id_by_boxstr_by_frame_index[frame_index] = {
            boxstr: h_id
        }

    return h_id


def update_track(human_id, box, frame_index, boxstr_by_frame_by_human_id, human_id_by_boxstr_by_frame_index):
    boxstr_by_frame_by_human_id[human_id][frame_index] = box_to_str(box)
    if frame_index not in human_id_by_boxstr_by_frame_index:
        human_id_by_boxstr_by_frame_index[frame_index] = {}
    human_id_by_boxstr_by_frame_index[frame_index][box_to_str(box)] = human_id


def track_first_frame_index(h_id, boxstr_by_frame_by_human_id):
    boxstr_by_frame = boxstr_by_frame_by_human_id[h_id]
    return sorted(boxstr_by_frame.keys())[0]


def _track_objects(tracker_type,
                   frames, 
                   tags, 
                   index_beginning, 
                   index_of_first_frame_with_humans,
                   next_human_id,
                   boxstr_by_frame_by_human_id,
                   human_id_by_boxstr_by_frame_index):

    tracker = cv2.TrackerKCF_create()

    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()

    current_human_id = None

    for i in range(index_beginning, len(frames)):
        print("Processing frame: " + tnt.color_warn(i))
        # skip frames without people
        if index_of_first_frame_with_humans == None:
            if has_humans(tags[i]):
                print("Found first frame with humans: " + tnt.color_warn(i))
                index_of_first_frame_with_humans = i
            else:
                continue
        # actual tracking
        if current_human_id == None:
            available_boxes = available_untracked_boxes(i, tags[i], human_id_by_boxstr_by_frame_index)
            if len(available_boxes) == 0:
                print("Nothing to new track in this frame")
                continue # we tracked everything in this frame
            else:
                some_box = choose_box(available_boxes)
                current_human_id = create_track(some_box, i, next_human_id, boxstr_by_frame_by_human_id, human_id_by_boxstr_by_frame_index)
                next_human_id += 1
                print("Tracking new human with ID = " + str(current_human_id))
                ok = tracker.init(frames[i], tuple(some_box)) # why tuple? see https://stackoverflow.com/questions/13225525/system-error-new-style-getargs-format-but-argument-is-not-a-tuple-when-using
                if not ok:
                    print(tnt.color_fail("ERROR: ") + "failed to initialize tracker")
                    sys.exit()
        else:
            print("Updating tracker with next frame...")
            ok, box = tracker.update(frames[i])
            if ok: # let's add another frame/box to the track
                print("Tracked human "+tnt.color_warn(current_human_id)+" updated on frame " + tnt.color_warn(i))
                update_track(current_human_id, box, i, boxstr_by_frame_by_human_id, human_id_by_boxstr_by_frame_index)
            else: # lost the tracked human, save the track and rewind
                print("Lost tracked human "+tnt.color_warn(current_human_id)+" on frame " + tnt.color_warn(i))
                index_beg = track_first_frame_index(current_human_id, boxstr_by_frame_by_human_id)
                _track_objects(tracker_type, frames, tags, index_beg, index_of_first_frame_with_humans, next_human_id, boxstr_by_frame_by_human_id, human_id_by_boxstr_by_frame_index)


def track_objects(frames, tags):
    # create the tracker
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
    tracker_type = tracker_types[2]
    # aux vars
    boxstr_by_frame_by_human_id = {}
    human_id_by_boxstr_by_frame_index = {}
    _track_objects(tracker_type, 
                   frames, 
                   tags, 
                   0,
                   None, 
                   0, 
                   boxstr_by_frame_by_human_id,
                   human_id_by_boxstr_by_frame_index)

    print(tnt.color_warn("BOXSTR by frame by human id:"))
    print(json.dumps(boxstr_by_frame_by_human_id, sort_keys=True, indent=3))
    print(tnt.color_warn("HUMAN ID by boxstr by frame index:"))


if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("tagged_bundle_path", help="path to a directory containing both a set of tagged frames and a tags JSON file")
    parser.add_argument("--output_path", default="same", help="path to a directory where the tracks JSON file will be saved")
    args = parser.parse_args()

    # FIXME
    video_path = "/Users/gvieira/temp/transcoded/video-01-d-fps-5.mp4"
    print(tnt.color_info("Loading input video: ") + video_path)

    video = cv2.VideoCapture(video_path)

    # Exit if video not opened.
    if not video.isOpened():
        print(tnt.color_fail("ERROR: ") + "could not open video")
        sys.exit()
    else:
        print(tnt.color_ok("Done!"))

    print(tnt.color_info("Loading frames into memory..."))
    frames = read_frames_from_video(video)
    if frames == None:
        print(tnt.color_fail("ERROR: ") + 'could not read frames from video file')
        sys.exit()
    else:
        print(tnt.color_ok("Done: ") + "loaded " + tnt.color_warn(str(len(frames))) + " frames.")
    

    print(tnt.color_info("Loading tagged bundle: ") + args.tagged_bundle_path)
    tagged_bundle = load_tagged_bundle(args.tagged_bundle_path)
    print(tnt.color_ok("Done!"))

    print(tnt.color_info("Tracking objects..."))
    track_objects(frames, tagged_bundle['frames'])
    print(tnt.color_ok("Done!"))

    # Define an initial bounding box
    # bbox = (287, 23, 86, 320)

    # # Uncomment the line below to select a different bounding box
    # bbox = cv2.selectROI(frame, False)

    # # Initialize tracker with first frame and bounding box
    # ok = tracker.init(frame, bbox)

    # while True:
    #     # Read a new frame
    #     ok, frame = video.read()
    #     if not ok:
    #         break
         
    #     # Start timer
    #     timer = cv2.getTickCount()

    #     # Update tracker
    #     ok, bbox = tracker.update(frame)

    #     # Calculate Frames per second (FPS)
    #     fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    #     # Draw bounding box
    #     if ok:
    #         # Tracking success
    #         p1 = (int(bbox[0]), int(bbox[1]))
    #         p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    #         cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    #     else :
    #         # Tracking failure
    #         cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    #     # Display tracker type on frame
    #     cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
     
    #     # Display FPS on frame
    #     cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)

    #     # Display result
    #     cv2.imshow("Tracking", frame)

    #     # Exit if ESC pressed
    #     k = cv2.waitKey(1) & 0xff
    #     if k == 27 : break