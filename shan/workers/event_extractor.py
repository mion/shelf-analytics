import os
import sys
sys.path.append('/Users/gvieira/code/toneto/shan')
import argparse
import json

from shan.workers.worker import Worker
from shan.event_extraction import extract_all_events
from shan.iaot import extract_intersection_area_over_time
from shan.tnt import load_json

class EventExtractor(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'event_extractor_dev_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('event_extractor', conf)
    
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
