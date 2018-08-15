import argparse
import time
import numpy as np
import cv2

parser = argparse.ArgumentParser(description='Record a video to test the camera.')
parser.add_argument('ext', help="file extension")
parser.add_argument('codec', help="fourcc codec")
parser.add_argument('fps', help="frames per second or 'source' to match video source")
parser.add_argument('size', help="a string like 640x480 or 'source' to match video source (WARNING: if you get this wrong the recording will be empty)")
args = parser.parse_args()

cap = cv2.VideoCapture(0)
w = None
h = None
if args.size == 'source':
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
else:
    w, h = map(int, args.size.split('x'))

if args.fps == 'source':
    fps = int(cap.get(cv2.CAP_PROP_FPS))
else:
    fps = int(args.fps)

print('Extension: ', args.ext)
print('Resolution: {}x{}'.format(w, h))
print('Codec: ', args.codec)
print('FPS: ', fps)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestr = time.strftime('%Y-%m-%d-%H-%M-%S-Z%z', time.localtime())
out = cv2.VideoWriter('test-recording-{}.{}'.format(timestr, args.ext),fourcc, fps, (w,h), True)
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
