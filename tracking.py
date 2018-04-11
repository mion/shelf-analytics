import pdb
import sys
import json
import cv2


class Track:
  def __init__(self):
    self.index_bbox_pairs = []
  
  def add(self, index, bbox):
    self.index_bbox_pairs.append((index, bbox))
  
  def contains(self, index, bbox):
    try:
      return (True, self.index_bbox_pairs.index((index,bbox)))
    except ValueError:
      return (False, None)
  
  def to_json(self):
    return [{"index": i, "bbox": b} for i, b in self.index_bbox_pairs]


class TracksList:
  def __init__(self):
    self.tracks = []
  
  def add(self, track):
    self.tracks.append(track)
  
  def belongs_to_some_track(self, index, bbox):
    for track in self.tracks:
      ok, _ = track.contains(index, bbox)
      if ok:
        return True
    return False
  
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
    ok = obj_tracker.init(start_frame, start_bbox)
    if not ok:
      raise "failed to init obj tracker" # FIXME
    curr_track = Track()
    curr_track.add(start_index, start_bbox)
    # FIXME 1 frame videos?
    print("tracking human:")
    for idx in range(start_index + 1, len(self.frames)):
      frame = self.frames[idx]
      ok, bbox = obj_tracker.update(frame)
      if ok:
        # FIXME bbox should be floats perhaps
        int_bbox = tuple([int(n) for n in bbox])
        curr_track.add(idx, int_bbox)
        print("\tat frame {0} moved to bbox {1}".format(idx, int_bbox))
      else:
        break
    self.tracks_list.add(curr_track)
    print("done tracking human, tracks found: {0}".format(str(len(self.tracks_list.tracks))))
    # print(self.tracks_list.dump_json_string())
    return True

  def dump_tracks_json_string(self):
    return self.tracks_list.dump_json_string()
