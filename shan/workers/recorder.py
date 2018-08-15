import argparse
import time
import cv2

from worker import Worker


class Recorder(Worker):
    def __init__(self):
        conf = {
            'QUEUE_HOST': 'localhost',
            'QUEUE_NAME': 'example_queue_1',
            'QUEUE_DURABLE': True,
            'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
            'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
        }
        super().__init__('recorder', conf)
    
    def process(self, job):
        keys = ['filename', 'duration', 'codec', 'size', 'fps']
        for key in keys:
            if key not in job:
                print("FAILURE: missing required key '{}' in job JSON".format(key))
                return False
        filename = job['filename']
        width = None
        height = None
        fps = None
        duration = float(job['duration'])
        codec = job['codec']
        cap = cv2.VideoCapture(0)
        if job['size'] == 'source':
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            width, height = map(int, job['size'].split('x'))
        if job['fps'] == 'source':
            fps = int(cap.get(cv2.CAP_PROP_FPS))
        else:
            fps = int(job['fps'])
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        start_time = time.perf_counter() # returns a float
        print('Recording started with FPS {} and {}x{} resolution...'.format(fps, width, height))
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                out.write(frame)
                elapsed = time.perf_counter() - start_time
                if elapsed > duration:
                    break
            else:
                break
        cap.release()
        out.release()
        print("SUCCESS: saved {:.2f}seg of video to file '{}' with codec {}".format(elapsed, filename, codec))
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recorder worker.')
    parser.add_argument("command", type=str, help="the worker command: 'add', 'start'")
    parser.add_argument("-f", "--filename", type=str, help="name of the output video file")
    parser.add_argument("-d", "--duration", type=int, help="duration in seconds to record")
    parser.add_argument("-c", "--codec", type=str, help="OpenCV codec: DIVX, XVID, MJPG, X264, WMV1, WMV2, etc. See http://www.fourcc.org/ for more.")
    parser.add_argument("-r", "--framerate", default="source", type=str, help="frames per second of the output video as an integer or 'source' to match video source features (default)")
    parser.add_argument("-s", "--size", default="source", type=str, help="width and height of video frame formatted as 'WIDTHxHEIGHT', or 'source' to match video source features (default)")
    args = parser.parse_args()
    cmd = args.command
    if cmd == 'start':
        recorder = Recorder()
        recorder.start()
    elif cmd == 'add':
        recorder = Recorder()
        recorder.add_job({
            'filename': args.filename, 
            'duration': args.duration, 
            'fps': args.framerate,
            'size': args.size,
            'codec': args.codec
        })
