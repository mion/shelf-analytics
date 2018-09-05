import os
import sys
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/workers'))
import subprocess
import argparse
import json
import shutil

from configuration import configuration

from worker import Worker
from print_events import print_frames
from util import load_json, make_video

class EventedVideoMaker(Worker):
    def __init__(self):
        name = 'evented_video_maker'
        super().__init__(name, configuration['dev']['workers'][name])
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['video_path', 'rois_path', 'tr_path', 'events_path', 'output_frames_path', 'output_videos_path'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        print_frames(job['video_path'], job['rois_path'], job['tr_path'], job['events_path'], job['output_frames_path'])
        _, video_filename = os.path.split(job['video_path'])
        make_video(video_filename, job['output_frames_path'], job['output_videos_path'])
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument('-v', '--video_path', help='')
    parser.add_argument('-r', '--rois_path', help='')
    parser.add_argument('-t', '--tr_path', help='')
    parser.add_argument('-e', '--events_path', help='')
    parser.add_argument('-f', '--output_frames_path', help='')
    parser.add_argument('-o', '--output_videos_path', help='')
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = EventedVideoMaker()
        worker.start()
    elif cmd == 'add':
        worker = EventedVideoMaker()
        worker.add_job({
            'video_path': args.video_path,
            'rois_path': args.rois_path,
            'tr_path': args.tr_path,
            'events_path': args.events_path,
            'output_frames_path': args.output_frames_path,
            'output_videos_path': args.output_videos_path,
        })
