import argparse
import os
import subprocess
import time
import cv2

from worker import Worker


SHAN_WORKSPACE_PATH = '/Users/gvieira/shan'

class Detector(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'detector_dev_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('detector', conf)
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['video_id'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        video_id = job['video_id']
        video_dir_path = os.path.join(SHAN_WORKSPACE_PATH, video_id)
        raw_frames_dir_path = os.path.join(video_dir_path, 'frames/raw')
        output_file_path = os.path.join(video_dir_path, 'data/tags.json')
        output_frames_dir_path = os.path.join(video_dir_path, 'frames/tagged')
        cmd = 'python scripts/detect_objects2.py {} {} --frames_dir_path {}'.format(raw_frames_dir_path, output_file_path, output_frames_dir_path)
        # FIXME shell=True is NOT SECURE
        # NOTE check=True will raise an exception if exit status is not 0
        subprocess.run(cmd, shell=True, check=True)
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Object detection worker.')
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--video_id", type=str, help="the video ID that should be processed")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        detector = Detector()
        detector.start()
    elif cmd == 'add':
        detector = Detector()
        detector.add_job({
            'video_id': args.video_id
        })
