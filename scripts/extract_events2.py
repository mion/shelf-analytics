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

BUTTER_CRIT_FREQ = 0.05
BUTTER_ORDER = 1
PEAK_MIN_HEIGHT = 300
PEAK_WIDTH = 7
VIDEO_FPS = 10
INTERACTED_MIN_DURATION_MS = 1800
INTERACTED_MIN_AREA = 1300
WALKED_MIN_DURATION_MS = 1000
WALKED_MIN_AREA = 4500
PONDERED_MIN_DURATION_MS = 3000
PONDERED_MIN_AREA = 4000

def smooth_without_delay(xn, order, crit_freq):
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
    y = []
    for i in range(len(iaot)):
        x.append(iaot[i]["index"])
        y.append(iaot[i]["area"])
    x = numpy.array(x)
    y = numpy.array(y)
    try:
        smooth_y = smooth_without_delay(x, b_ord, b_crit_freq)
        indexes, props = find_peaks(smooth_y, height=peak_height, width=peak_width)
        peaks = []
        for i in range(len(indexes)):
            frame_index = indexes[i]
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
        print('Saved plot: ' + dir_path + '/smooth.png')
    except Exception as exc:
        print('ERROR: failed to plot smooth graph. ({})'.format(str(exc)))

def extract_interacted_event(peaks, min_duration, min_area):
    for peak in peaks:
            frame_index = peak['frame_index']
            duration_ms = peaks["duration_ms"]
            intersection_area_in_pixels = peak["intersection_area_in_pixels"]
            if duration_ms > min_duration and intersection_area_in_pixels > min_area:
                return {
                    "frame_index": frame_index,
                    "event_type": "interacted"
                }
    return None

def extract_walked_event(iaot, fps, min_duration, min_area):
    frame_indexe_over_time = []
    area_over_time = []
    for i in range(len(iaot)):
        frame_indexe_over_time.append(iaot[i]["index"])
        area_over_time.append(iaot[i]["area"])
    min_frames_t = int((min_duration / 1000) * fps)
    # min_frames_t = 2 sec x (10 fr / sec) = 20 frames
    for t in range(len(area_over_time)):
        if area_over_time[t] < min_area:
            continue
        small_area_found = False
        for p in range(t, len(area_over_time) - min_frames_t):
            if area_over_time[p] < min_area:
                small_area_found = True
                break
        if not small_area_found:
            return {
                "type": "walked",
                "frame_index": t + int(min_frames_t / 2)
            }
    return None

def extract_pondered_event(iaot, fps, min_duration, min_area):
    frame_indexe_over_time = []
    area_over_time = []
    for i in range(len(iaot)):
        frame_indexe_over_time.append(iaot[i]["index"])
        area_over_time.append(iaot[i]["area"])
    min_frames_t = int((min_duration / 1000) * fps)
    # min_frames_t = 2 sec x (10 fr / sec) = 20 frames
    for t in range(len(area_over_time)):
        if area_over_time[t] < min_area:
            continue
        small_area_found = False
        for p in range(t, len(area_over_time) - min_frames_t):
            if area_over_time[p] < min_area:
                small_area_found = True
                break
        if not small_area_found:
            return {
                "type": "walked",
                "frame_index": t + int(min_frames_t / 2)
            }
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_id', help='a video id of the form "video-33-p_04"')
    parser.add_argument('rois_path', help='path to the rois JSON file')
    args = parser.parse_args()

    rois = load_json(args.rois_path)
    video_id = args.video_id # "video-33-p_04"
    iaot_path = "/Users/gvieira/shan/{}/data/iaot.json".format(video_id)
    tracks_path = "/Users/gvieira/shan/{}/data/tracks.json".format(video_id)
    iaots = load_json(iaot_path)
    tracks = load_json(tracks_path)

    output_events_path = "/Users/gvieira/shan/{}/data/events.json".format(video_id)

    events = []
    os.mkdir('/Users/gvieira/shan/{}/events'.format(video_id))
    for roi in rois:
        roi_name = roi['name']
        print('- Roi "{}"'.format(roi_name))
        os.mkdir('/Users/gvieira/shan/{}/events/{}'.format(video_id, roi_name))
        for track_idx in range(len(tracks)):
            print('\t- Track #{}'.format(str(track_idx + 1)))
            track = tracks[track_idx]
            # INTERACTED
            print("\t\t- INTERACTED")
            if roi['type'] == 'shelf':
                track_dir_path = '/Users/gvieira/shan/{}/events/{}/track-{}'.format(video_id, roi["name"], str(track_idx + 1))
                os.mkdir(track_dir_path)
                print_plots(track_dir_path, iaots[track_idx][roi_name], BUTTER_ORDER, BUTTER_CRIT_FREQ)
                peaks, err = extract_peaks(iaots[track_idx][roi_name], VIDEO_FPS, BUTTER_ORDER, BUTTER_CRIT_FREQ, PEAK_MIN_HEIGHT, PEAK_WIDTH)
                if peaks is None:
                    print('\t\t\tFAILED to extract peaks')
                elif len(peaks) == 0:
                    print('\t\t\tZERO peaks were extracted')
                else:
                    print("\t\t\tExtracted {} peaks...".format(len(peaks))) 
                    evt = extract_interacted_event(peaks, INTERACTED_MIN_DURATION_MS, INTERACTED_MIN_AREA)
                    if evt is not None:
                        print("\t\t\tINTERACTED at frame {}".format(evt["frame_index"]))
                        evt.update({
                            'roi_name': roi_name,
                            'track': track_idx
                        })
                        events.append(evt)
                    else:
                        print("\t\t\tNO EVENT found")
            else:
                print("\t\tTYPE is not shelf")
            # WALKED
            print("\t\t- WALKED")
            if roi['type'] == 'aisle':
                evt2 = extract_walked_event(iaots[track_idx][roi_name], VIDEO_FPS, WALKED_MIN_DURATION_MS, WALKED_MIN_AREA)
                if evt2 is None:
                    print("\t\t\t NO EVENT found")
                else:
                    print("\t\t\tWALKED at frame {}".format(evt2["frame_index"]))
                    evt2.update({
                        'roi_name': roi_name,
                        'track': track_idx
                    })
                    events.append(evt2)
            else:
                print("\t\tTYPE is not aisle")
            # PONDERED
            # print("\t\t- PONDERED")
            # if roi['type'] == 'aisle':
            #     evt3 = extract_pondered_event(iaots[track_idx][roi_name], VIDEO_FPS, PONDERED_MIN_DURATION_MS, PONDERED_MIN_AREA)
            #     if evt2 is None:
            #         print("\t\t\t NO EVENT found")
            #     else:
            #         print("\t\t\tPONDERED for {} miliseconds starting at frame {}".format(evt["duration"], evt["frame_index"]))
            # else:
            #     print("\t\tTYPE is not aisle")
    output_file_path = os.path.join('/Users/gvieira/shan/{}/data'.format(video_id), "events.json")
    with open(output_file_path, "w") as events_file:
        json.dump(events, events_file)
