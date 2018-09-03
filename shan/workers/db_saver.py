import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))

import argparse
import json
import requests

from configuration import configuration
from worker import Worker

API_BASE_URL = 'http://localhost:8000/shancms' 

class DBSaver(Worker):
    def __init__(self):
        # conf = {
        #     'QUEUE_HOST': 'localhost',
        #     'QUEUE_NAME': 'db_saver_dev_2',
        #     'QUEUE_DURABLE': True,
        #     'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
        #     'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        # }
        name = 'db_saver'
        super().__init__(name, configuration['dev']['workers'][name])
    
    def save_events(self, shelf_id, events):
        url = API_BASE_URL + '/shelves/{}/events'.format(shelf_id)
        r = requests.post(url, json={'events': events})
        r.raise_for_status()
    
    def save_calib(self, shelf_id, s3_key, recording_date):
        url = API_BASE_URL + '/shelves/{}/calibration_videos'.format(shelf_id)
        r = requests.post(url, json={'s3_key': s3_key, 'recording_date': recording_date})
        r.raise_for_status()
    
    def save_experiment(self, shelf_id, s3_key):
        url = API_BASE_URL + '/shelves/{}/experiments/save'.format(shelf_id)
        r = requests.post(url, json={'s3_key': s3_key})
        r.raise_for_status()
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['data', 'type'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        if job['type'] == 'events':
            data = job['data']
            self.save_events(data['shelf_id'], data['events'])
            return True
        elif job['type'] == 'calib':
            data = job['data']
            self.save_calib(data['shelf_id'], data['s3_key'], data['recording_date'])
            return True
        elif job['type'] == 'experiment':
            data = job['data']
            self.save_experiment(data['shelf_id'], data['s3_key'])
        else:
            print("FAILURE: invalid data type: {}".format(job['type']))
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-j", "--json_string", type=str, help="the JSON data to be saved")
    parser.add_argument("-t", "--data_type", type=str, help="this is used to determine how the data should be saved")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = DBSaver()
        worker.start()
    elif cmd == 'add':
        worker = DBSaver()
        worker.add_job({
            'data': json.loads(args.json_string),
            'type': args.data_type
        })
