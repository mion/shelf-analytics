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
  else:
      print("Done, loaded " + str(len(frames)) + " frames")
