import pdb
import sys
import json
import cv2
import math
import os


def save_track_as_images(frames, track, folder_name, path):
  # create output dir
  try:
    folder_path = os.path.join(path, folder_name)
    os.mkdir(folder_path)
  except Exception as err:
    print("ERROR - Could not create folder '{0}' at path '{1}':\n{2}".format(folder_name, path, str(err)))
  # draw each bbox in the track on the frame and then save it
  for i in range(len(frames)):
    # TODO stopped here
    pass


# TODO add this to a shared json file
DEFAULT_MIN_SNAPPING_DISTANCE = 25
TRACKER_FAILED_MIN_SNAPPING_DISTANCE = 50

# TODO do not accept a bbox if it belongs to some other track
def find_nearest_available_bbox(orig_bbox, other_bboxes_in_frame, frame_index, tracks_list, max_allowed_distance):
  nearest_available = {
    "bbox": None,
    "distance": 999999999 # FIXME use Infinity or something
  }

  for bbox in other_bboxes_in_frame:
    if orig_bbox == bbox:
      continue # just in case, make sure it's not the same bbox
    distance = bbox_distance(orig_bbox, bbox)
    is_available = not tracks_list.belongs_to_some_track(frame_index, bbox)
    if is_available and distance < max_allowed_distance:
      if distance < nearest_available["distance"]:
        nearest_available["bbox"] = bbox
        nearest_available["distance"] = distance

  return nearest_available["bbox"]

# DEPRECATED in favor of the method above.
def find_closest_bbox_to_snap_on(bboxes_list, tracker_bbox, min_snapping_distance):
  closest_bbox = None
  min_distance = 99999999 # FIXME
  for bbox in bboxes_list:
    dist = bbox_distance(tracker_bbox, bbox)
    if dist < min_distance:
      min_distance = dist
      closest_bbox = bbox
  if min_distance < min_snapping_distance:
    return closest_bbox
  else:
    return None


def bbox_distance(bbox_orig, bbox_dest):
  y1_orig, x1_orig, y2_orig, x2_orig = bbox_orig
  y1_dest, x1_dest, y2_dest, x2_dest = bbox_dest
  center_orig = ((x1_orig + x2_orig) / 2, (y1_orig + y2_orig) / 2)
  center_dest = ((x1_dest + x2_dest) / 2, (y1_dest + y2_dest) / 2)
  dx = center_dest[0] - center_orig[0]
  dy = center_dest[1] - center_orig[1]
  return math.sqrt((dx * dx) + (dy * dy))


class Track:
  def __init__(self):
    self.index_bbox_transition_sets = []
    self.contained_index_bbox = {}
  
  def add(self, index, bbox, transition):
    """
    `bbox` format is [y1, x1, y2, x2]
    `transition` is an object like this:
    {
      "type": "snapped", (can be "snapped", "tracked", "retaken" or "first")
      "from_bbox": [1, 2, 3, 4],
      "distance": 321.5
    }
    """
    self.index_bbox_transition_sets.append((index, bbox, transition))
    self.contained_index_bbox[self.to_key(index, bbox)] = True
  
  def to_key(self, index, bbox):
    """
    Transforms `index` and `bbox` into a string key to 
    be used in the `contained_index_bbox` dictionary.
    """
    return str(index) + "_" + ",".join([str(n) for n in bbox])

  def last_bbox(self):
    count = len(self.index_bbox_transition_sets)
    if count == 0:
      return None
    else:
      _, bbox, _ = self.index_bbox_transition_sets[count - 1]
      return bbox
  
  def contains(self, index, bbox):
    # [!] TODO: Here we are looking for an absolute match.
    # Should we look for an approximate match instead?
    return self.to_key(index, bbox) in self.contained_index_bbox
  
  def to_json(self):
    return [{"index": i, "bbox": [int(n) for n in b], "transition": t} for i, b, t in self.index_bbox_transition_sets]


class TracksList:
  def __init__(self):
    self.tracks = []
  
  def add(self, track):
    self.tracks.append(track)
  
  def belongs_to_some_track(self, index, bbox):
    for track in self.tracks:
      if track.contains(index, bbox):
        return True
    return False
  
  def get_tracks(self):
    return [track.to_json() for track in self.tracks]
  
  def dump_json_string(self):
    return json.dumps([track.to_json() for track in self.tracks])


class HumanTracker:
  def __init__(self, frames, list_of_bboxes_lists, obj_tracker_type):
    self.frames = frames
    self.list_of_bboxes_lists = list_of_bboxes_lists
    self.obj_tracker_type = obj_tracker_type
    self.tracks_list = TracksList()
  
  def create_obj_tracker(self):
    # load OpenCV object tracker
    major_ver, minor_ver, subminor_ver = cv2.__version__.split(".")
    if int(minor_ver) < 3:
      return cv2.Tracker_create(self.obj_tracker_type)
    else:
      if self.obj_tracker_type == 'BOOSTING':
        return cv2.TrackerBoosting_create()
      elif self.obj_tracker_type == 'MIL':
        return cv2.TrackerMIL_create()
      elif self.obj_tracker_type == 'KCF':
        return cv2.TrackerKCF_create()
      elif self.obj_tracker_type == 'TLD':
        return cv2.TrackerTLD_create()
      elif self.obj_tracker_type == 'MEDIANFLOW':
        return cv2.TrackerMedianFlow_create()
      elif self.obj_tracker_type == 'GOTURN':
        return cv2.TrackerGOTURN_create()
      else:
        raise "unknown obj tracker type" # FIXME

  def restart_obj_tracker(self, obj_tracker, frame, bbox):
    """
    Expected format of `bbox` is (y1, x1, y2, x2)
    """
    obj_tracker.clear()
    obj_tracker = self.create_obj_tracker()
    y1, x1, y2, x2 = bbox
    reinit_bbox = (x1, y1, x2 - x1, y2 - y1)
    if not obj_tracker.init(frame, reinit_bbox):
      raise "failed to re-init tracker after retake" # FIXME
    else:
      return obj_tracker

  def find_some_untracked_index_bbox_pair(self):
    for idx in range(len(self.frames)):
      bboxes_list = self.list_of_bboxes_lists[idx]
      for bbox in bboxes_list:
        if not self.tracks_list.belongs_to_some_track(idx, bbox):
          return (idx, bbox)
    return None

  def track_someone_once(self):
    print("searching untracked humans...")
    pair = self.find_some_untracked_index_bbox_pair()
    if pair == None:
      print("all humans have been tracked")
      return False
    start_index = pair[0]
    start_bbox = pair[1]
    print("found someone at frame {0} at bbox {1}".format(start_index, start_bbox))
    start_frame = self.frames[0] # FIXME check empty frames
    obj_tracker = self.create_obj_tracker()
    y1, x1, y2, x2 = start_bbox
    init_tracker_bbox = (x1, y1, x2 - x1, y2 - y1)
    ok = obj_tracker.init(start_frame, init_tracker_bbox)
    if not ok:
      raise "failed to init obj tracker" # FIXME
    curr_track = Track()
    curr_track.add(start_index, start_bbox, {"type": "first", "from_bbox": start_bbox, "distance": 0})

    # FIXME 1 frame videos?
    print("tracking human:")
    for idx in range(start_index + 1, len(self.frames)):
      frame = self.frames[idx]
      ok, xywh = obj_tracker.update(frame)
      if ok:
        # FIXME bbox should be floats perhaps
        x, y, w, h = xywh
        x1 = int(x)
        y1 = int(y)
        x2 = x1 + int(w)
        y2 = y1 + int(h)
        int_tracker_bbox = (y1, x1, y2, x2)
        bboxes_list = self.list_of_bboxes_lists[idx]
        # try to snap the bbox from tracker onto a detected bbox so we can compare it later on
        bbox = find_nearest_available_bbox(int_tracker_bbox, bboxes_list, idx, self.tracks_list, DEFAULT_MIN_SNAPPING_DISTANCE)
        # bbox = find_closest_bbox_to_snap_on(bboxes_list, int_tracker_bbox, min_snapping_distance=DEFAULT_MIN_SNAPPING_DISTANCE)
        if bbox != None:
          print("\t(snapped) at frame {0} moved to bbox {1}".format(idx, bbox))
          last_bbox = curr_track.last_bbox()
          curr_track.add(idx, bbox, {
            "type": "snapped",
            "from_bbox": last_bbox,
            "distance": bbox_distance(last_bbox, bbox)
          })
          # Let's update the tracker with the currently snapped bounding box
          obj_tracker = self.restart_obj_tracker(obj_tracker, frame, bbox)
        else: # the detection fails too, so we may have to go with whatever the tracker has
          print("\t(tracked) at frame {0} moved to bbox {1}".format(idx, int_tracker_bbox))
          last_bbox = curr_track.last_bbox()
          curr_track.add(idx, int_tracker_bbox, {
            "type": "tracked",
            "from_bbox": last_bbox,
            "distance": bbox_distance(last_bbox, int_tracker_bbox)
          })
      else:
        # when the tracker fails, also try to find the nearest detected bbox and snap onto it
        bboxes_list = self.list_of_bboxes_lists[idx]
        last_tracker_bbox = curr_track.last_bbox()
        # but in this case, its OK to look a bit further
        bbox = find_nearest_available_bbox(last_tracker_bbox, bboxes_list, idx, self.tracks_list, TRACKER_FAILED_MIN_SNAPPING_DISTANCE)
        # bbox = find_closest_bbox_to_snap_on(bboxes_list, last_tracker_bbox, min_snapping_distance=TRACKER_FAILED_MIN_SNAPPING_DISTANCE)
        if bbox != None:
          print("\t(retaken) at frame {0} moved to bbox {1}".format(idx, bbox))
          curr_track.add(idx, bbox, {
            "type": "retaken",
            "from_bbox": last_tracker_bbox,
            "distance": bbox_distance(last_tracker_bbox, bbox)
          })
          # If the tracker has failed, the `update` method cannot be called again.
          # Instead, we need to re-initialize it (the docs do not say this).
          # See: https://stackoverflow.com/questions/31432815/opencv-3-tracker-wont-work-after-reinitialization
          obj_tracker = self.restart_obj_tracker(obj_tracker, frame, bbox)
          # obj_tracker.clear()
          # obj_tracker = self.create_obj_tracker()
          # y1, x1, y2, x2 = bbox
          # reinit_bbox = (x1, y1, x2 - x1, y2 - y1)
          # if not obj_tracker.init(frame, reinit_bbox):
          #   raise "failed to re-init tracker after retake" # FIXME
        else:
          print("\ttrack lost at frame {0}".format(idx))
          break
    
    self.tracks_list.add(curr_track)
    print("done tracking human, tracks found: {0}".format(str(len(self.tracks_list.tracks))))
    # pdb.set_trace()
    # print(self.tracks_list.dump_json_string())
    return True

  def dump_tracks_json_string(self):
    return self.tracks_list.dump_json_string()
  
  def get_tracks(self):
    return self.tracks_list.get_tracks()
