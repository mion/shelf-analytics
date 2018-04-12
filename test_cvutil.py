import sys
import os
import cv2
import cvutil

if __name__ == '__main__':
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
