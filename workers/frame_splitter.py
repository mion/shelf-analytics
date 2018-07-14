"""
The frame splitter worker takes transcoded videos and split them into many
separate frames.

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
from frame_splitting import split_frames

FRAME_SPLITTER_QUEUE_HOST = 'localhost'
FRAME_SPLITTER_QUEUE_NAME = 'frame_splitter'
FRAME_SPLITTER_QUEUE_DURABLE = True
FRAME_SPLITTER_QUEUE_PREFETCH_COUNT = 1 # do not give more than one message to a worker at a time
FRAME_SPLITTER_DELIVERY_MODE = 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html

def process_job(channel, method, properties, message):
    job = json.loads(message)
    print("Received job:")
    print(job)
    print("Processing...")
    success = split_frames(job['input_video_path'], job['output_dir_path'], job['ext'])
    if success:
        print("Success!")
    else:
        print("Failed to process job")
    channel.basic_ack(delivery_tag = method.delivery_tag)

def add_job(input_video_path, output_video_path, fps):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=FRAME_SPLITTER_QUEUE_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=FRAME_SPLITTER_QUEUE_NAME, durable=FRAME_SPLITTER_QUEUE_DURABLE)
    job = {
        'input_video_path': input_video_path,
        'output_dir_path': output_video_path,
        'ext': fps
    }
    message = json.dumps(job)
    channel.basic_publish(exchange='',
                        routing_key=FRAME_SPLITTER_QUEUE_NAME,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode = FRAME_SPLITTER_DELIVERY_MODE, 
                        ))
    print('Job added to queue:')
    print(job)
    connection.close()

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=FRAME_SPLITTER_QUEUE_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=FRAME_SPLITTER_QUEUE_NAME, durable=FRAME_SPLITTER_QUEUE_DURABLE)
    channel.basic_qos(prefetch_count=FRAME_SPLITTER_QUEUE_PREFETCH_COUNT) 
    channel.basic_consume(process_job,
                        queue=FRAME_SPLITTER_QUEUE_NAME)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Frame splitter worker.')
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--input", help="input video file path (to be used with 'add')")
    parser.add_argument("-o", "--output", help="output video file path (to be used with 'add')")
    parser.add_argument("-e", "--ext", help="image extension (to be used with 'add')")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        start_worker()
    elif cmd == 'add':
        add_job(args.input, args.output, args.ext)
