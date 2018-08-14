import argparse
import boto3

from worker import Worker


class Uploader(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'uploader_dev_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('uploader', conf)
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['input_file_path', 's3_bucket', 's3_key'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        input_file_path = job['input_file_path']
        bucket = job['s3_bucket']
        key = job['s3_key']
        s3 = boto3.client('s3')
        s3.upload_file(input_file_path, bucket, key)
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-i", "--input_file_path", type=str, help="path to the file to be uploader")
    parser.add_argument("-b", "--s3_bucket", type=str, help="name of the bucket in S3")
    parser.add_argument("-k", "--s3_key", type=str, help="key (the 'filename') that the file will have in the bucket")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = Uploader()
        worker.start()
    elif cmd == 'add':
        worker = Uploader()
        worker.add_job({
            'input_file_path': args.input_file_path,
            's3_bucket': args.s3_bucket,
            's3_key': args.s3_key,
        })
