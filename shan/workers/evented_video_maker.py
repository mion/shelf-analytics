import os
import sys
import subprocess
import argparse
import json
import shutil

from configuration import configuration

from worker import Worker
from shan.scripts.print_events import print_frames
from shan.common.util import load_json

def make_video(video_filename, evented_frames_dir_path, videos_path):
    fps = 10
    output_video_name = 'evented-' + video_filename
    cmd_tmpl = 'cd {}; ffmpeg -framerate {} -pattern_type glob -i "*.png" -c:v libx264 -r {} -pix_fmt yuv420p {}'
    cmd = cmd_tmpl.format(evented_frames_dir_path, fps, fps, output_video_name)
    # WARNING shell=True is dangerous
    result = subprocess.call(cmd, shell=True)
    if result != 0:
        raise RuntimeError('Command "{}" returned non-zero'.format(cmd))
    shutil.move(os.path.join(evented_frames_dir_path, output_video_name), videos_path)

class EventedVideoMaker(Worker):
    def __init__(self):
        # conf = {
        #     'QUEUE_HOST': 'localhost',
        #     'QUEUE_NAME': 'evented_video_maker_1',
        #     'QUEUE_DURABLE': True,
        #     'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        #     'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        # }
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
