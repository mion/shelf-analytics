import argparse
import json
import requests

from worker import Worker

API_BASE_URL = 'http://localhost:8000/shancms' 

class DBSaver(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'db_saver_dev_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('db_saver', conf)
    
    def save_events(self, shelf_id, events):
        url = API_BASE_URL + '/shelves/{}/events'.format(shelf_id)
        r = requests.post(url, json={'events': events})
        r.raise_for_status()
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['data'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return
        data = job['data']
        if ('shelf_id' in data) and ('events' in data):
            self.save_events(data['shelf_id'], data['events'])
        else:
            print("FAILURE: invalid data to be saved:\n{}".format(json.dumps(data)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-j", "--json_string", type=str, help="the JSON data to be saved")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = DBSaver()
        worker.start()
    elif cmd == 'add':
        worker = DBSaver()
        worker.add_job({
            'data': json.loads(args.json_string),
        })
