"""
The transcoder worker transforms a video in a given format and FPS, into
another video with other format and desired FPS.

Copyright (c) 2018 TonetoLabs.
Author: Gabriel Luis Vieira (gluisvieira@gmail.com)
"""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import json
import pika
import time
import argparse
from transcoding import transcode
from worker import Worker
from configuration import configuration


class Transcoder(Worker):
    def __init__(self):
        # conf = {
        #     'QUEUE_HOST': 'localhost',
        #     'QUEUE_NAME': 'transcoder_dev_2',
        #     'QUEUE_DURABLE': True,
        #     'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        #     'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        # }
        name = 'transcoder'
        super().__init__(name, configuration['workers'][name])
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['input_video_path', 'output_video_path', 'fps'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        success = transcode(job['input_video_path'], job['output_video_path'], job['fps'])
        if not success:
            print('FAILURE: could not transcode input video file')
            return False
        else:
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transcoder tool.')
    parser.add_argument("command", type=str, help="the transcoder command: 'add', 'start'")
    parser.add_argument("-i", "--input", type=str, help="input video file path (to be used with 'add')")
    parser.add_argument("-o", "--output", type=str, help="output video file path (to be used with 'add')")
    parser.add_argument("-f", "--fps", type=int, help="desired FPS framerate (to be used with 'add')")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = Transcoder()
        worker.start()
    elif cmd == 'add':
        worker = Transcoder()
        worker.add_job({
            'input_video_path': args.input, 
            'output_video_path': args.output, 
            'fps': args.fps
        })
