import sys
import argparse
import json
import cv2
import cvutil

def load_json(path):
  with open(path) as json_file:
    return json.loads(json_file.read())

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("video_path", help="path to the video")
  parser.add_argument("tags_path", help="path to a tags JSON file")
  parser.add_argument("tracks_path", help="path to a tracks JSON file")
  parser.add_argument("track_index", type=int, help="index of track to visualize")
  args = parser.parse_args()

  video = cv2.VideoCapture(args.video_path)
  # Exit if video not opened.
  if not video.isOpened():
      print("ERROR: could not open video")
      sys.exit()
  width = video.get(3)
  height = video.get(4)

  tags = load_json(args.tags_path)
  tracks = load_json(args.tracks_path)
  track = tracks[args.track_index]
  track_first_index = 0
  track_last_index = 18

  frames = cvutil.read_frames_from_video(video)
  for i in range(len(frames)):
    frame = frames[i]
    for obj_detected_bbox in tags["frames"][i]["boxes"]:
      cvutil.draw_bbox_on_frame(frame, obj_detected_bbox, rect_color=(0,0,255), text_color=(255,255,255))
    
    if i >= track_first_index and i <= track_last_index:
      cvutil.draw_bbox_on_frame(frame, track[i]["bbox"], rect_color=(255, 155, 0), text_color=(0,155,255))
      cvutil.save_image(frame, "track-{0}-frame-{1}.png".format(args.track_index, i), "/Users/gvieira/temp/tagged_frames/video-01-d-fps-5/tracks")
