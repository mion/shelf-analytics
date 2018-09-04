import os
import sys
import argparse
import matplotlib.pyplot as plt
import json
import numpy
from scipy.signal import find_peaks, peak_widths, lfilter, lfilter_zi, filtfilt, butter
from shan.common.util import load_json
from shan.core.event_extraction import extract_all_events

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('iaot_path', help='path to the iaot JSON file')
    parser.add_argument('tracks_path', help='path to the tracks JSON file')
    parser.add_argument('rois_path', help='path to the rois JSON file')
    parser.add_argument('output_path', help='path to the output events JSON file')
    args = parser.parse_args()

    iaot = load_json(args.iaot_path)
    tracks = load_json(args.tracks_path)
    rois = load_json(args.rois_path)

    events = extract_all_events(iaot, tracks, rois)

    with open(args.output_path, "w") as events_file:
        json.dump(events, events_file)
