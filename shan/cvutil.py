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
  font = cv2.FONT_HERSHEY_DUPLEX
  if text == None:
      text = "({0},{1},{2},{3})".format(x1, y1, x2, y2)
  return cv2.putText(new_frame, text, (x1, y2 + 15), font, 0.50, text_color, 1, cv2.LINE_AA)

def draw_subtitled_bbox_on_frame(frame, bbox, text, rect_color=(255, 255, 255)):
    y1, x1, y2, x2 = bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, 2) 
    draw_label_on_frame(frame, text, x1, y2 + 15)
    return frame

def draw_text_on_frame(frame, text, x, y, color):
  return cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.50, color, 1, cv2.LINE_AA)

def save_image(img, name, path):
  cv2.imwrite(os.path.join(path, name), img)

def show_image(img, window_title='Image'):
    cv2.imshow(window_title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def draw_label_on_frame(frame, text, x, y):
    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1.0
    font_thickness = 1
    size = cv2.getTextSize(text, font, font_scale, font_thickness)
    width, height = size[0]
    PADDING = 5
    cv2.rectangle(frame, 
                  (x, y), 
                  (x + width + (2 * PADDING), y + height + (2 * PADDING)), 
                  (50, 50, 50), 
                  cv2.FILLED, 
                  cv2.LINE_AA)
    cv2.putText(frame, 
                text, 
                (x + PADDING, y + height + PADDING), 
                font, 
                font_scale, 
                (255,255,255), 
                thickness=font_thickness, 
                lineType=cv2.LINE_AA)
    return frame
