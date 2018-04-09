import unittest
from tracking import *


class TestTracking(unittest.TestCase):
  def test_empty_frames(self):
    frames = [
      {'boxes': []},
      {'boxes': []},
      {'boxes': []}
    ]
    tracker = Tracker(frames)
    self.assertEqual(len(tracker.tracks), 0)
    self.assertEqual(len(tracker.humans), 0)
  
  def test_single_frame(self):
    frames = [
      {'boxes': [], 'humans': []},
      {'boxes': []},
      {'boxes': [
        [5, 10, 25, 40]
      ]}
      tracker = Tracker(frames)
      self.assertEqual(len(tracker.tracks), 1)
      self.assertEqual(len(tracker.humans), 1)
    ]
  

if __name__ == '__main__':
  unittest.main()
