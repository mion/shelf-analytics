import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'shan'))
import argparse
import subprocess
import time
import cv2

from configuration import configuration
from worker import Worker

SHAN_WORKSPACE_PATH = '/Users/gvieira/shan'

class Detector(Worker):
    def __init__(self):
        # conf = {
        #     'QUEUE_HOST': 'localhost',
        #     'QUEUE_NAME': 'detector_dev_6',
        #     'QUEUE_DURABLE': True,
        #     'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        #     'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        # }
        name = 'detector'
        super().__init__(name, configuration['dev']['workers'][name])
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['raw_frames_dir_path', 'output_file_path', 'output_frames_dir_path'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        # NOTE: Something I have not figure out yet in the MaskRCNN code currently starts TensorFlow upon import. 
        # Keeping TF running for too long seems clog the CPU/RAM so for now we want it to get restarted everytime.
        from detection import detect_humans_in_every_image
        raw_frames_dir_path = job['raw_frames_dir_path']
        output_file_path = job['output_file_path']
        output_frames_dir_path = job['output_frames_dir_path']
        error = detect_humans_in_every_image(raw_frames_dir_path, output_file_path, output_frames_dir_path, pika_connection=self.connection)
        if error is None:
            return True
        else:
            print("FAILURE: detect_humans_in_every_image returned an error:\n{}".format(error))
            return False
        # cmd = 'python scripts/detect_objects2.py {} {} --frames_dir_path {}'.format(raw_frames_dir_path, output_file_path, output_frames_dir_path)
        # # FIXME shell=True is NOT SECURE
        # # NOTE check=True will raise an exception if exit status is not 0
        # subprocess.run(cmd, shell=True, check=True)
        # return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Object detection worker.')
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--raw_frames_dir_path", type=str, help="path to the directory with each frame as an image")
    parser.add_argument("-o", "--output_file_path", type=str, help="path to the output JSON file")
    parser.add_argument("-f", "--output_frames_dir_path", type=str, help="path to the directory where each detected frame should be saved")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        detector = Detector()
        detector.start()
    elif cmd == 'add':
        detector = Detector()
        detector.add_job({
            'raw_frames_dir_path': args.raw_frames_dir_path,
            'output_file_path': args.output_file_path,
            'output_frames_dir_path': args.output_frames_dir_path,
        })
