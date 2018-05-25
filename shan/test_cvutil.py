import sys
import os
import cv2
import cvutil
import numpy as np

def test_drawing():
    img = np.zeros((512, 512, 3), np.uint8)
    # cv2.line(img, (0,0), (511,511), (255,0,0), 5)
    cvutil.draw_label_on_frame(img, "Gondola Pet 2L (ESQUERDA)", 50, 25)
    cvutil.show_image(img)

def test_video_loading():
  print("Loading video...")
  video = cv2.VideoCapture("/Users/gvieira/temp/transcoded/video-01-d-fps-5.mp4")
  # Exit if video not opened.
  if not video.isOpened():
      print("ERROR: could not open video")
      sys.exit()

  frames = cvutil.read_frames_from_video(video)
  if frames == None:
      print('ERROR: could not read frames from video file')
      sys.exit()
  print("Done, loaded " + str(len(frames)) + " frames")

  frame = frames[0]
  width = video.get(3)
  height = video.get(4)
  print("Width: {0}\nHeight: {1}".format(str(width), str(height)))
  # frame_with_rect = cv2.rectangle(frame, (0, 0), (100, 125), (255, 50, 10), 2)
  new_frame = cvutil.draw_bbox_on_frame(frame, (10, 15, 60, 120))
  cv2.imshow('frame', new_frame)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

if __name__ == '__main__':
    test_drawing()