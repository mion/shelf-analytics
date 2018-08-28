import os
import sys
sys.path.append('/Users/gvieira/code/toneto/shan')

from shan.workers.calib_manager import CalibManager
from shan.workers.db_saver import DBSaver
from shan.workers.detector import Detector
from shan.workers.downloader import Downloader
from shan.workers.event_extractor import EventExtractor
from shan.workers.evented_video_maker import EventedVideoMaker
from shan.workers.frame_splitter import FrameSplitter
from shan.workers.recorder import Recorder
from shan.workers.tracker import Tracker
from shan.workers.transcoder import Transcoder
from shan.workers.uploader import Uploader

WORKERS = [CalibManager, DBSaver, Detector, Downloader, EventedVideoMaker, EventedVideoMaker, FrameSplitter, Recorder, Tracker, Transcoder, Uploader]
# WIP