"""
    $ worker_manager.py start recorder --config rabbit-mq-conf.json
    => started worker
    $ worker_manager.py add recorder "{\"job\": \"echo\"}" --config rabbit-mq-conf.json
    => created job 123
    $ worker_manager.py remove 123
    => removed job 123
"""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))

from workers.recorder import Recorder
import pika

class WorkerManager:
    def __init__(self, name):
        self.worker_name = name
        # TODO Use dynamic importing.
        # path = os.path.join(WORKERS_BASE_PATH, name)
        # worker_module = importlib.import_module('.' + name) #path)
        # worker_class = worker_module[name]
        # self.worker = worker_class()
        if name == 'recorder':
            self.worker = Recorder()
        else:
            raise RuntimeError('invalid name for worker "{}"'.format(name))
    
    # def process_job(self, channel, method, properties, message):
    def process_job(self):
        result = self.worker.process({})
        return result
    
    def connect(self, conf):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=conf['QUEUE_HOST']))
        channel = connection.channel()
        channel.queue_declare(queue=conf['QUEUE_NAME'], durable=conf['QUEUE_DURABLE'])
        channel.basic_qos(prefetch_count=conf['QUEUE_PREFETCH_COUNT'])
        channel.basic_consume(self.process_job,
                            queue=conf['QUEUE_NAME'])
        channel.start_consuming()

# wm = WorkerManager('recorder')
# print(wm.process_job())
# print('ok')
r = Recorder()