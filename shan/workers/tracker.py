import os
import sys
sys.path.append('/Users/gvieira/code/toneto/shan')
sys.path.append('/Users/gvieira/code/toneto/shan/shan')
import argparse
import json

from shan.workers.worker import Worker
from shan.tracking2 import track_humans
from shan.frame_bundle import load_frame_bundles
from shan.tnt import load_json

MAX_TRACKS = 40

class Tracker(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'tracker_dev_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('tracker', conf)
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['calib_path', 'tags_path', 'video_path', 'output_file_path'])
        if len(missing_keys) > 0:
            if self.verbose:
                print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return
        calib = load_json(job['calib_path'])
        tags = load_json(job['tags_path'])
        frame_bundles = load_frame_bundles(job['video_path'], tags)
        tracks = track_humans(calib, frame_bundles, MAX_TRACKS)
        with open(job['output_file_path'], 'w') as output_file:
            json.dump(tracks, output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument('-i', '--video_path', help='path to the video file')
    parser.add_argument('-c', '--calib_path', help='path to a calib-config JSON file')
    parser.add_argument('-t', '--tags_path', help='path to a tags JSON file')
    parser.add_argument('-o', '--output_file_path', help='path to the output JSON file where tracks will be saved')
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = Tracker()
        worker.start()
    elif cmd == 'add':
        worker = Tracker()
        worker.add_job({
            'video_path': args.video_path,
            'calib_path': args.calib_path,
            'tags_path': args.tags_path,
            'output_file_path': args.output_file_path,
        })
