# Last time I left this worker running, I got this error at the end of 2 jobs.

# Traceback (most recent call last):
#   File "workers/detector.py", line 64, in <module>
#     start_worker()
#   File "workers/detector.py", line 53, in start_worker
#     channel.start_consuming()
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 1780, in start_consuming
#     self.connection.process_data_events(time_limit=None)
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 716, in process_data_events
#     self._dispatch_channel_events()
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 518, in _dispatch_channel_events
#     impl_channel._get_cookie()._dispatch_events()
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 1403, in _dispatch_events
#     evt.body)
#   File "workers/detector.py", line 23, in process_job
#     channel.basic_ack(delivery_tag = method.delivery_tag)
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 1988, in basic_ack
#     self._flush_output()
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 1250, in _flush_output
#     *waiters)
#   File "/Users/gvieira/code/ai/lib/python3.6/site-packages/pika/adapters/blocking_connection.py", line 474, in _flush_output
#     result.reason_text)
# pika.exceptions.ConnectionClosed: (-1, "BrokenPipeError(32, 'Broken pipe')")
#
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import pika
import json
import argparse
from detection import detect_humans_in_every_image

DETECTOR_QUEUE_HOST = 'localhost'
DETECTOR_QUEUE_NAME = 'detection'
DETECTOR_QUEUE_DURABLE = True
DETECTOR_QUEUE_PREFETCH_COUNT = 1 # do not give more than one message to a worker at a time
DETECTOR_DELIVERY_MODE = 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html

def process_job(channel, method, properties, message):
    job = json.loads(message)
    print("Received job:")
    print(job)
    print("Processing...")
    detect_humans_in_every_image(job['input_dir_path'], job['output_file_path'], job['frames_dir_path'])
    channel.basic_ack(delivery_tag = method.delivery_tag)

def add_job(input_dir_path, output_file_path, frames_dir_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=DETECTOR_QUEUE_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=DETECTOR_QUEUE_NAME, durable=DETECTOR_QUEUE_DURABLE)
    job = {
        'input_dir_path': input_dir_path,
        'output_file_path': output_file_path,
        'frames_dir_path': frames_dir_path
    }
    message = json.dumps(job)
    channel.basic_publish(exchange='',
                        routing_key=DETECTOR_QUEUE_NAME,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode = DETECTOR_DELIVERY_MODE, 
                        ))
    print('Job added to queue:')
    print(job)
    connection.close()

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=DETECTOR_QUEUE_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=DETECTOR_QUEUE_NAME, durable=DETECTOR_QUEUE_DURABLE)
    channel.basic_qos(prefetch_count=DETECTOR_QUEUE_PREFETCH_COUNT) 
    channel.basic_consume(process_job,
                        queue=DETECTOR_QUEUE_NAME)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--input", help="input frames dir path")
    parser.add_argument("-o", "--output", help="output JSON file path")
    parser.add_argument("-d", "--frames_dir_path", help="where to save debug frames")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        start_worker()
    elif cmd == 'add':
        add_job(args.input, args.output, args.frames_dir_path)
