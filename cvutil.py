import cv2
import os

def read_frames_from_video(video):
    is_first_frame = True
    frames = []
    while True:
        ok, frame = video.read()
        if not ok and is_first_frame:
            return None
        elif not ok and not is_first_frame:
            break
        else:
            is_first_frame = False
            frames.append(frame)
    return frames

def draw_bbox_on_frame(frame, bbox, rect_color=(0,0,255), text_color=(255,255,255), text=None):
  y1, x1, y2, x2 = bbox
  new_frame = cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, 2)
  font = cv2.FONT_HERSHEY_SIMPLEX
  if text == None:
      text = "({0},{1},{2},{3})".format(x1, y1, x2, y2)
  return cv2.putText(new_frame, text, (x1, y2 + 15), font, 0.30, text_color, 1, cv2.LINE_AA)

def save_image(img, name, path):
  cv2.imwrite(os.path.join(path, name), img)