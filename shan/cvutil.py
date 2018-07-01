import cv2
import os

def create_object_tracker(obj_tracker_type):
    major_ver, minor_ver, subminor_ver = cv2.__version__.split(".")
    if int(minor_ver) < 3:
        return cv2.Tracker_create(obj_tracker_type)
    else:
        if obj_tracker_type == 'BOOSTING':
            return cv2.TrackerBoosting_create()
        elif obj_tracker_type == 'MIL':
            return cv2.TrackerMIL_create()
        elif obj_tracker_type == 'KCF':
            return cv2.TrackerKCF_create()
        elif obj_tracker_type == 'TLD':
            return cv2.TrackerTLD_create()
        elif obj_tracker_type == 'MEDIANFLOW':
            return cv2.TrackerMedianFlow_create()
        elif obj_tracker_type == 'GOTURN':
            return cv2.TrackerGOTURN_create()
        else:
            raise RuntimeError("invalid object tracker type")

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

def draw_rect_on_frame(frame, bbox, rect_color=(255,255,255)):
  y1, x1, y2, x2 = bbox
  return cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, 1)

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

def draw_label_on_frame(frame, text, x, y, bg_color=(50, 50, 50), text_color=(255, 255, 255)):
    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1.0
    font_thickness = 1
    size = cv2.getTextSize(text, font, font_scale, font_thickness)
    width, height = size[0]
    PADDING = 5
    cv2.rectangle(frame, 
                  (x, y), 
                  (x + width + (2 * PADDING), y + height + (2 * PADDING)), 
                  bg_color, 
                  cv2.FILLED, 
                  cv2.LINE_AA)
    cv2.putText(frame, 
                text, 
                (x + PADDING, y + height + PADDING), 
                font, 
                font_scale, 
                text_color, 
                thickness=font_thickness, 
                lineType=cv2.LINE_AA)
    return frame
