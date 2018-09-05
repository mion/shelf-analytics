import os
import sys
import argparse
import json

from configuration import configuration

from worker import Worker
from shan.core.event_extraction import extract_all_events
from shan.core.iaot import extract_intersection_area_over_time
from shan.common.util import load_json

class EventExtractor(Worker):
    def __init__(self):
        name = 'event_extractor'
        super().__init__(name, configuration['dev']['workers'][name])
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['tracks_path', 'rois_path', 'output_path'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        rois = load_json(job['rois_path'])
        tracks = load_json(job['tracks_path'])
        _iaot = extract_intersection_area_over_time(tracks, rois)
        events = extract_all_events(_iaot, tracks, rois)
        with open(job['output_path'], 'w') as output_file:
            json.dump(events, output_file)
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument('-t', '--tracks_path', help='path to the tracks JSON file')
    parser.add_argument('-r', '--rois_path', help='path to the rois JSON file')
    parser.add_argument('-o', '--output_path', help='path to the output events JSON file')
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = EventExtractor()
        worker.start()
    elif cmd == 'add':
        worker = EventExtractor()
        worker.add_job({
            'tracks_path': args.tracks_path,
            'rois_path': args.rois_path,
            'output_path': args.output_path,
        })
