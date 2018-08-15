import argparse
import boto3

from worker import Worker


class Downloader(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'downloader_dev_3',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('downloader', conf)
    
    def process(self, job):
        missing_keys = self.missing_keys(job, ['output_file_path', 's3_bucket', 's3_key'])
        if len(missing_keys) > 0:
            print("FAILURE: missing required keys '{}' in job JSON".format(missing_keys))
            return False
        output_file_path = job['output_file_path']
        bucket = job['s3_bucket']
        key = job['s3_key']
        s3 = boto3.client('s3')
        s3.download_file(bucket, key, output_file_path)
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-o", "--output_file_path", type=str, help="path to the file to be downloaded")
    parser.add_argument("-b", "--s3_bucket", type=str, help="name of the bucket in S3")
    parser.add_argument("-k", "--s3_key", type=str, help="key (the 'filename') of the file in the bucket")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        worker = Downloader()
        worker.start()
    elif cmd == 'add':
        worker = Downloader()
        worker.add_job({
            'output_file_path': args.output_file_path,
            's3_bucket': args.s3_bucket,
            's3_key': args.s3_key,
        })
