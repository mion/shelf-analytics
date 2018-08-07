import argparse
import time
import numpy as np
import cv2

parser = argparse.ArgumentParser(description='Record a video to test the camera.')
parser.add_argument('ext', help="file extension")
parser.add_argument('codec', help="fourcc codec")
parser.add_argument('fps', type=int, help="frames per second")
parser.add_argument('size', help="a string like 640x480 or default")
args = parser.parse_args()

cap = cv2.VideoCapture(0)
w = None
h = None
if args.size == 'default':
    w = int(cap.get(3))
    h = int(cap.get(4))
else:
    w, h = map(int, args.size.split('x'))
print('Extension: ', args.ext)
print('Resolution: {}x{}'.format(w, h))
print('Codec: ', args.codec)
print('FPS: ', args.fps)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestr = time.strftime('%Y-%m-%d-%H-%M-%S-Z%z', time.localtime())
out = cv2.VideoWriter('test-recording-{}.{}'.format(timestr, args.ext),fourcc, 24, (w,h), True)
# NOTE To write an image frame note that the imgFrame must be the same size as capSize above or updates will fail.
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        # frame = cv2.flip(frame,0)
        out.write(frame)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
cap = None
out.release()
out = None
cv2.destroyAllWindows()
