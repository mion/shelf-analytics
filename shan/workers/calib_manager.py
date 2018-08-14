import argparse
import pika

import worker
import recorder
import transcoder
import uploader
import db_saver

def consume(self, channel, method, properties, message):
    print("[*] Received message:\n{}".format(message))

def start(self):
    conf = worker.Worker.DEFAULT_OUTPUT_CONF
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=conf['QUEUE_HOST']))
    channel = connection.channel()
    channel.queue_declare(queue=conf['QUEUE_NAME'], durable=conf['QUEUE_DURABLE'])
    channel.basic_qos(prefetch_count=conf['QUEUE_PREFETCH_COUNT']) 
    channel.basic_consume(consume, queue=conf['QUEUE_NAME'])
    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calibration Manager worker.')
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-s", "--shelf_id", type=int, help="db ID of the Shelf to record a calibration video")
    args = parser.parse_args()
