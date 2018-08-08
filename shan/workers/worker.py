import json
import argparse

import pika


class Worker:
    def __init__(self, conf, verbose=True):
        self.conf = conf
        self.verbose = verbose
    
    def process(self, job):
        raise NotImplementedError()
    
    def process_job(self, channel, method, properties, message):
        job = json.loads(message)
        if self.verbose:
            print("[*] Received job:", job)
            print("[*] Processing...")
        self.process(job)
        if self.verbose:
            print("[*] Processing done, acknowledging.")
        channel.basic_ack(delivery_tag = method.delivery_tag)

    def add_job(self, job):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['QUEUE_HOST']))
        channel = connection.channel()
        channel.queue_declare(queue=self.conf['QUEUE_NAME'], durable=self.conf['QUEUE_DURABLE'])
        message = json.dumps(job)
        channel.basic_publish(exchange='',
                            routing_key=self.conf['QUEUE_NAME'],
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode = self.conf['DELIVERY_MODE'], 
                            ))
        if self.verbose:
            print('[*] Job added to queue:', job)
        connection.close()

    def start(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['QUEUE_HOST']))
        channel = connection.channel()
        channel.queue_declare(queue=self.conf['QUEUE_NAME'], durable=self.conf['QUEUE_DURABLE'])
        channel.basic_qos(prefetch_count=self.conf['QUEUE_PREFETCH_COUNT']) 
        channel.basic_consume(self.process_job, queue=self.conf['QUEUE_NAME'])
        if self.verbose:
            print('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

if __name__ == '__main__':
    import time
    import random

    EXAMPLE_CONF = {
        'QUEUE_HOST': 'localhost',
        'QUEUE_NAME': 'example_queue_1',
        'QUEUE_DURABLE': True,
        'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
    }

    class SampleWorker(Worker):
        def __init__(self):
            super().__init__(conf=EXAMPLE_CONF, verbose=True)
        
        def process(self, job):
            secs = job['seconds']
            prob = job['probability_of_failure']
            print("Sleeping {:d} seconds...".format(secs))
            for _ in range(secs):
                if random.random() < prob:
                    print("\tFAILED!")
                    raise RuntimeError("sample failure")
                else:
                    print("\tSlept 1 second.")
                    time.sleep(1)

    parser = argparse.ArgumentParser(description='Sample worker.')
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-s", "--seconds", type=int, default=3, help="number of seconds to sleep")
    parser.add_argument("-p", "--probability_of_failure", type=float, default=0.0, help="prob of raising an error after waiting 1 second")
    args = parser.parse_args()
    cmd = args.command
    worker = SampleWorker()
    if cmd == 'start':
        worker.start()
    elif cmd == 'add':
        worker.add_job({'seconds': args.seconds, 'probability_of_failure': args.probability_of_failure})
