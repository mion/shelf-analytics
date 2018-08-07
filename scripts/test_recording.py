import time
import numpy as np
import cv2

cap = cv2.VideoCapture(0)
w = int(cap.get(3))
h = int(cap.get(4))
print('Default resolution: {}x{}'.format(w, h))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestr = time.strftime('%Y-%m-%d-%H-%M-%S-Z%z', time.localtime())
out = cv2.VideoWriter('test-recording-{}.mov'.format(timestr),fourcc, 24, (w,h), True)
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
