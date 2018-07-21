"""
In order to debug or calibrate the segmenter, run this:

    $ python scripts/segment.py ~/shan-lab/v3.mp4 -f 10 -s 15 -d 200 --verbose > segment.log

Then read the 'segment.log' while keeping the PNG file open so you can visualize what's going on.
"""
import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))
from tnt import get_name_without_ext

from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import matplotlib.pyplot as plt

DEFAULT_FPS = 10
DEFAULT_STATIC_THRESH_SECS = 15
DEFAULT_DIFF_THRESH = 200

def blur_frame(frame):
    res_frame = imutils.resize(frame, width=500)
    gray_frame = cv2.cvtColor(res_frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray_frame, (21, 21), 0)

def calc_area_delta(frame1, frame2):
    delta = cv2.absdiff(frame1, frame2)
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    return sum([cv2.contourArea(c) for c in cnts])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('video', help='path to the video file')
    ap.add_argument('-f', '--fps', default=DEFAULT_FPS, type=int, help='framerate of the video (default: {:d})'.format(DEFAULT_FPS))
    ap.add_argument('-s', '--static_thresh_secs', default=DEFAULT_STATIC_THRESH_SECS, type=int, help='number of seconds the video must be approximately static before cutting out a segment (default: {:d})'.format(DEFAULT_STATIC_THRESH_SECS))
    ap.add_argument('-d', '--diff_thresh', default=DEFAULT_DIFF_THRESH, type=int, help='area delta diff threshold to consider two frames equal, thus being static (default: {:d})'.format(DEFAULT_DIFF_THRESH))
    ap.add_argument('-v', '--verbose', action='store_true', help='print area delta and area delta diff for each frame; also print a plot of the area delta over time')
    args = vars(ap.parse_args())
    # pdb.set_trace()
    verbose = args.get('verbose')
    video_path = args.get('video')
    fps = args.get('fps')
    static_thresh_secs = args.get('static_thresh_secs')
    diff_thresh = args.get('diff_thresh')

    video = cv2.VideoCapture(video_path)

    area_delta_over_time = []

    frame_counter = 0
    below_thresh_fr_counter = 0
    last_area_delta = None
    last_blurred_frame = None
    is_static = False
    while True:
        curr_frame = video.read()[1]
        if curr_frame is None:
            break
        frame_counter += 1
        curr_blurred_frame = blur_frame(curr_frame)
        if last_blurred_frame is None:
            last_blurred_frame = curr_blurred_frame
            continue
        area_delta = calc_area_delta(last_blurred_frame, curr_blurred_frame)
        area_delta_over_time.append(area_delta)
        if last_area_delta is None:
            last_area_delta = area_delta
        abs_area_delta_diff = abs(area_delta - last_area_delta)
        last_area_delta = area_delta
        if verbose:
            print("Frame #{:09d}\t{}\t{}".format(frame_counter, area_delta, abs_area_delta_diff))
        if not is_static:
            if abs_area_delta_diff < diff_thresh:
                below_thresh_fr_counter += 1
                secs_below_thresh = below_thresh_fr_counter / fps
                if secs_below_thresh > static_thresh_secs:
                    is_static = True
                    time_secs = int((frame_counter - below_thresh_fr_counter) / fps)
                    print("START cutting at\t{:02d}:{:02d}".format(int(time_secs / 60), time_secs % 60))
            else:
                below_thresh_fr_counter = 0
        else:
            if abs_area_delta_diff > diff_thresh:
                below_thresh_fr_counter = 0
                is_static = False
                time_secs = int(frame_counter / fps)
                print("STOP cutting at\t{:02d}:{:02d}".format(int(time_secs / 60), time_secs % 60))
    
    if verbose:
        plt.plot(area_delta_over_time)
        plt.ylabel('Area delta')
        plt.xlabel('Frame index')
        # plt.show()
        plt.savefig('{}-area-delta-over-time.png'.format(get_name_without_ext(video_path)))
    
    video.release()
    cv2.destroyAllWindows()
