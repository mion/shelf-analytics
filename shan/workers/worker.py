import json
import argparse

import pika


class Worker:
    DEFAULT_OUTPUT_CONF = {
        'QUEUE_HOST': 'localhost',
        'QUEUE_NAME': 'output_dev_11',
        'QUEUE_DURABLE': True,
        'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
    }
    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
        self.output_conf = Worker.DEFAULT_OUTPUT_CONF
    
    def print_json(self, obj):
        print(json.dumps(obj, indent=3, sort_keys=True))
    
    def missing_keys(self, job, required_keys):
        missing = []
        for key in required_keys:
            if key not in job:
                missing.append(key)
        return missing
    
    def process(self, job):
        raise NotImplementedError()
    
    def process_job(self, channel, method, properties, message):
        job = json.loads(message)
        print("[*] Received job:")
        self.print_json(job)
        print("[*] Processing...")
        success = self.process(job)
        print("[*] Processing done, acknowledging...")
        channel.basic_ack(delivery_tag = method.delivery_tag)

        if self.output_conf is not None:
            print("[*] Adding to output queue...")
            result = {
                'worker': self.name,
                'success': success,
                'job': job
            }
            self._add_message(result, self.output_conf['QUEUE_NAME'], self.output_conf['QUEUE_HOST'], self.output_conf['QUEUE_DURABLE'], self.output_conf['DELIVERY_MODE'])
            print("[*] Done!")
        else:
            print("[*] Output queue is NULL, all done.")

    def _add_message(self, msg, queue_name, queue_host, durable, delivery_mode):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=queue_host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=durable)
        message = json.dumps(msg)
        channel.basic_publish(exchange='',
                            routing_key=queue_name,
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode = delivery_mode, 
                            ))
        connection.close()

    def add_job(self, job):
        self._add_message(job, self.conf['QUEUE_NAME'], self.conf['QUEUE_HOST'], self.conf['QUEUE_DURABLE'], self.conf['DELIVERY_MODE'])
        print('[*] Job added to queue:', job)

    def start(self):
        params = pika.ConnectionParameters(host=self.conf['QUEUE_HOST'])
        self.connection = pika.BlockingConnection(params)
        channel = self.connection.channel()
        channel.queue_declare(queue=self.conf['QUEUE_NAME'], durable=self.conf['QUEUE_DURABLE'])
        channel.basic_qos(prefetch_count=self.conf['QUEUE_PREFETCH_COUNT']) 
        channel.basic_consume(self.process_job, queue=self.conf['QUEUE_NAME'])
        print('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

if __name__ == '__main__':
    import time
    import random

    EXAMPLE_CONF = {
        'QUEUE_HOST': 'localhost',
        'QUEUE_NAME': 'example_queue_2',
        'QUEUE_DURABLE': True,
        'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
    }

    class SampleWorker(Worker):
        def __init__(self):
            super().__init__('sample', conf=EXAMPLE_CONF)
        
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
                    self.connection.process_data_events()

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
