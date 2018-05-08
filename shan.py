#
#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Main Shelf Analytics script."""

import os
import argparse
import json

import pika

from colorize import red, green, yellow, header


def load_json(path):
    with open(path, 'r') as tags_file:
      return json.loads(tags_file.read())


def callback(ch, method, properties, body):
    print(" [*] Received %r" % body)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()
    if args.command == 'send':
        connection  = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
        print(' [*] Sent "Hello world!" message')
        connection.close()
    elif args.command == 'receive':
        connection  = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        channel.basic_consume(callback, queue='hello', no_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    else:
        print(' [!] Unknown command "{0}"'.format(args.command))
