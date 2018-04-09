import unittest
from tracking import *


class TestTracking(unittest.TestCase):
  def test_empty_frames(self):
    frames = []
    tracker = Tracker(frames)
    self.assertEqual(len(tracker.tracks), 0)
    self.assertEqual(len(tracker.humans), 0)

if __name__ == '__main__':
  unittest.main()
