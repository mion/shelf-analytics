"""
The frame splitter worker takes transcoded videos and split them into many
separate frames.

Copyright (c) 2018 TonetoLabs.
Author: Gabriel Luis Vieira (gluisvieira@gmail.com)
"""
import os
import sys
import json
import pika
import time
import argparse
from shan.core.frame_splitting import split_frames
from worker import Worker
from configuration import configuration

class FrameSplitter(Worker):
    def __init__(self):
        name = 'frame_splitter'
        super().__init__(name, configuration['dev']['workers'][name])
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['input_video_path', 'output_dir_path', 'ext'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        success = split_frames(job['input_video_path'], job['output_dir_path'], job['ext'])
        if not success:
            print('FAILURE: could not split frames from input video')
            return False
        else:
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Frame splitter worker.')
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--input", help="input video file path (to be used with 'add')")
    parser.add_argument("-o", "--output", help="output video file path (to be used with 'add')")
    parser.add_argument("-e", "--ext", help="image extension (to be used with 'add')")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = FrameSplitter()
        worker.start()
    elif cmd == 'add':
        worker = FrameSplitter()
        worker.add_job({
            'input_video_path': args.input, 
            'output_dir_path': args.output, 
            'ext': args.ext
        })
