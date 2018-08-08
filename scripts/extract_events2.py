import pdb
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse
import matplotlib.pyplot as plt
import json
import numpy
from scipy.signal import find_peaks, peak_widths, lfilter, lfilter_zi, filtfilt, butter
from tnt import load_json

VIDEO_FPS = 10
DEFAULT_CONFIG = {
    "BUTTER_CRIT_FREQ": 0.05,
    "BUTTER_ORDER": 1,
    "PEAK_MIN_HEIGHT": 300,
    "PEAK_WIDTH": 7,
    "INTERACTED_MIN_DURATION_MS": 1800,
    "INTERACTED_MIN_AREA": 1300,
    "WALKED_MIN_DURATION_MS": 1000,
    "WALKED_MIN_AREA": 2500,
    "PONDERED_MIN_DURATION_MS": 5000,
    "PONDERED_MIN_AREA": 2500
}

def smooth_without_delay(xn, order, crit_freq):
    # Butterworth filter
    b, a = butter(order, crit_freq)
    # Apply the filter to xn.  Use lfilter_zi to choose the initial condition
    # of the filter.
    zi = lfilter_zi(b, a)
    z, _ = lfilter(b, a, xn, zi=zi*xn[0])
    # Apply the filter again, to have a result filtered at an order
    # the same as filtfilt.
    z2, _ = lfilter(b, a, z, zi=zi*z[0])
    # Use filtfilt to apply the filter.
    return filtfilt(b, a, xn)

def extract_peaks(iaot, fps, b_ord, b_crit_freq, peak_height, peak_width):
    x = []
    area_over_time = []
    for i in range(len(iaot)):
        x.append(iaot[i]["index"])
        area_over_time.append(iaot[i]["area"])
    x = numpy.array(x)
    area_over_time = numpy.array(area_over_time)
    try:
        smooth_y = smooth_without_delay(area_over_time, b_ord, b_crit_freq)
        indexes, props = find_peaks(smooth_y, height=peak_height, width=peak_width)
        peaks = []
        for i in range(len(indexes)):
            frame_index = iaot[indexes[i]]["index"]
            duration_in_frames = props["widths"][i]
            intersection_area_in_pixels = props["peak_heights"][i]
            duration_ms = int(1000 * (duration_in_frames / fps))
            peaks.append({
                'frame_index': frame_index,
                'duration_in_frames': duration_in_frames,
                'intersection_area_in_pixels': intersection_area_in_pixels,
                'duration_ms': duration_ms
            })
        return (peaks, None)
    except Exception as exc:
        return (None, str(exc))

def print_plots(dir_path, iaot, b_ord, b_crit_freq):
    x = []
    y = []
    for i in range(len(iaot)):
        x.append(iaot[i]["index"])
        y.append(iaot[i]["area"])
    x = numpy.array(x)
    y = numpy.array(y)
    # raw scatter plot
    plt.scatter(x, y)
    plt.savefig(dir_path + '/raw.png')
    print('Saved plot: ' + dir_path + '/raw.png')
    try:
        # smoothed out signal
        smooth_y = smooth_without_delay(x, b_ord, b_crit_freq)
        plt.plot(smooth_y)
        plt.plot(y)
        plt.savefig(dir_path + '/smooth.png')
        plt.clf()
        print('\t\t\tSaved plot: ' + dir_path + '/smooth.png')
    except Exception as exc:
        print('ERROR: failed to plot smooth graph. ({})'.format(str(exc)))

def extract_interacted_event(peaks, min_duration, min_area):
    for pk in peaks:
            frame_index = pk['frame_index']
            duration_ms = pk["duration_ms"]
            intersection_area_in_pixels = pk["intersection_area_in_pixels"]
            if duration_ms > min_duration and intersection_area_in_pixels > min_area:
                return {
                    "index": int(frame_index),
                    "type": "interacted"
                }
    return None

# also used for `pondered` events
def extract_walked_event(iaot, fps, min_duration, min_area):
    frame_indexes_over_time = []
    area_over_time = []
    for i in range(len(iaot)):
        frame_indexes_over_time.append(iaot[i]["index"])
        area_over_time.append(iaot[i]["area"])
    min_frames_t = int((min_duration / 1000) * fps)
    # min_frames_t = 2 sec x (10 fr / sec) = 20 frames
    for t in range(len(area_over_time)):
        if area_over_time[t] < min_area:
            continue
        small_area_found = False
        for p in range(t, t + min_frames_t):
            if p >= len(area_over_time):
                small_area_found = True # not enough distance...
                break
            if area_over_time[p] < min_area:
                small_area_found = True
                break
        if not small_area_found:
            return {
                "type": "walked",
                "index": frame_indexes_over_time[t]
            }
    return None

def extract_event(roi_type, iaot, fps, config):
    if roi_type == 'shelf':
        # INTERACTED
        peaks, _ = extract_peaks(iaot, fps, config['BUTTER_ORDER'], config['BUTTER_CRIT_FREQ'], config['PEAK_MIN_HEIGHT'], config['PEAK_WIDTH'])
        if peaks is None or len(peaks) == 0:
            err = "peaks is null" if peaks is None else "peaks is empty"
            return (None, err)
        evt = extract_interacted_event(peaks, config['INTERACTED_MIN_DURATION_MS'], config['INTERACTED_MIN_AREA'])
        if evt is not None:
            return (evt, None)
        else:
            return (None, "had peaks but FAILED to extract interacted event")
    elif roi_type == 'aisle':
        # PONDERED
        pondered_evt = extract_walked_event(iaot, fps, config['PONDERED_MIN_DURATION_MS'], config['PONDERED_MIN_AREA'])
        if pondered_evt is not None:
            pondered_evt.update({"type": "pondered"})
            return (pondered_evt, None)
        # WALKED
        evt = extract_walked_event(iaot, fps, config['WALKED_MIN_DURATION_MS'], config['WALKED_MIN_AREA'])
        if evt is not None:
            return (evt, None)
        else:
            return (None, "no pondered nor walked event")

def extract_all_events(iaots_path, tracks_path, rois_path):
    rois = load_json(rois_path)
    iaots = load_json(iaots_path)
    tracks = load_json(tracks_path)
    events = []
    for roi in rois:
        roi_name = roi['name']
        print('Roi "{}" (type="{}")'.format(roi_name, roi['type']))
        for track_idx in range(len(tracks)):
            track = tracks[track_idx]
            event, err = extract_event(roi['type'], iaots[track_idx][roi_name], VIDEO_FPS, DEFAULT_CONFIG)
            if event is not None:
                print('\tTrack #{}: event "{}" at frame {}'.format(str(track_idx + 1), event['type'], str(event['index'])))
                event.update({
                    'roi_name': roi_name,
                    'track': track_idx
                })
                events.append(event)
            else:
                print('\tTrack #{}: error "{}"'.format(str(track_idx + 1), err))
    return events

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('video_id', help='a video id of the form "video-33-p_04"')
    parser.add_argument('iaot_path', help='path to the iaot JSON file')
    parser.add_argument('tracks_path', help='path to the tracks JSON file')
    parser.add_argument('rois_path', help='path to the rois JSON file')
    parser.add_argument('output_path', help='path to the output events JSON file')
    args = parser.parse_args()

    # video_id = args.video_id # "video-33-p_04"
    # iaot_path = "/Users/gvieira/shan/{}/data/iaot.json".format(video_id)
    # tracks_path = "/Users/gvieira/shan/{}/data/tracks.json".format(video_id)
    # output_events_path = "/Users/gvieira/shan/{}/data/events.json".format(video_id)
    # events = []
    # for roi in rois:
    #     roi_name = roi['name']
    #     print('Roi "{}" (type="{}")'.format(roi_name, roi['type']))
    #     for track_idx in range(len(tracks)):
    #         track = tracks[track_idx]
    #         event, err = extract_event(roi['type'], iaots[track_idx][roi_name], VIDEO_FPS, DEFAULT_CONFIG)
    #         if event is not None:
    #             print('\tTrack #{}: event "{}" at frame {}'.format(str(track_idx + 1), event['type'], str(event['index'])))
    #             event.update({
    #                 'roi_name': roi_name,
    #                 'track': track_idx
    #             })
    #             events.append(event)
    #         else:
    #             print('\tTrack #{}: error "{}"'.format(str(track_idx + 1), err))
    events = extract_all_events(args.iaots_path, args.tracks_path, args.rois_path)

    # output_file_path = os.path.join('/Users/gvieira/shan/{}/data'.format(video_id), "events.json")
    with open(args.output_path, "w") as events_file:
        json.dump(events, events_file)
