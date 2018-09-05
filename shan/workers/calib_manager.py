import os
import sys
import json
import argparse
import time
import shutil

import pika

from configuration import configuration
from shan.common.util import add_suffix_to_basename, current_local_time_isostring
from worker import Worker
from detector import Detector
from tracker import Tracker
from recorder import Recorder
from transcoder import Transcoder
from uploader import Uploader
from db_saver import DBSaver
from downloader import Downloader
from frame_splitter import FrameSplitter
from event_extractor import EventExtractor
from evented_video_maker import EventedVideoMaker

class CalibManager(Worker):
    def __init__(self):
        super().__init__('calib_manager', configuration['dev']['workers']['default'])
        self.output_conf = None

    def process(self, msg):
        # TODO check for 'success' status
        if 'job' not in msg:
            print("[!] FAILURE: missing 'job' key in msg dict")
            return True
        if 'flow' not in msg['job']:
            print("[!] FAILURE: missing 'flow' key in msg dict")
            return True
        if 'worker' not in msg:
            print("[!] FAILURE: missing 'worker' key in msg dict")
            return True
        if msg['worker'] == 'db_saver':
            print("[*] Ignoring 'db_saver' message")
            return True
        if msg['job']['flow'] == 'calibration':
            if msg['worker'] == 'recorder':
                print('[*] Adding output of Recorder to Transcoder...')
                shelf_id = msg['job']['shelf_id']
                filename = msg['job']['filename']
                flow = msg['job']['flow']
                recording_date = msg['job']['recording_date']
                t = Transcoder() 
                fps = 10
                final_ext = 'mp4'
                filename_without_ext, _ = os.path.splitext(filename)
                filename_with_new_ext = filename_without_ext + '.' + final_ext
                t.add_job({
                    'shelf_id': shelf_id,
                    'flow': flow,
                    'input_video_path': filename,
                    'output_video_path': add_suffix_to_basename(filename_with_new_ext, '-fps-{:d}'.format(fps)),
                    'fps': fps,
                    'recording_date': recording_date
                })
            elif msg['worker'] == 'transcoder':
                print('[*] Adding output of Transcoder to Uploader...')
                flow = msg['job']['flow']
                transcoded_video_path = msg['job']['output_video_path']
                shelf_id = msg['job']['shelf_id']
                recording_date = msg['job']['recording_date']
                u = Uploader()
                _, basename = os.path.split(transcoded_video_path)
                u.add_job({
                    'shelf_id': shelf_id,
                    'flow': flow,
                    'input_file_path': transcoded_video_path,
                    's3_bucket': configuration['dev']['s3_bucket'],
                    's3_key': basename,
                    'recording_date': recording_date
                })
            elif msg['worker'] == 'uploader':
                print('[*] Adding output of Uploader to DBSaver...')
                flow = msg['job']['flow']
                shelf_id = msg['job']['shelf_id']
                s3_key = msg['job']['s3_key']
                recording_date = msg['job']['recording_date']
                d = DBSaver()
                d.add_job({
                    'type': 'calib',
                    'flow': flow,
                    'data': {
                        'shelf_id': shelf_id,
                        's3_key': s3_key,
                        'recording_date': recording_date
                    }
                })
            else:
                print("[!] FAILURE: unknown worker '{}'".format(msg['worker']))
        elif msg['job']['flow'] == 'experiment':
            if msg['worker'] == 'downloader':
                print('[*] Downloader -> Frame Splitter')
                _, fname = os.path.split(msg['job']['output_file_path'])
                name, _ = os.path.splitext(fname)
                main_path = os.path.join(configuration['dev']['workspace_path'], name)
                videos_path = os.path.join(main_path, 'videos')
                os.mkdir(main_path)
                os.mkdir(videos_path)
                os.mkdir(os.path.join(main_path, 'data'))
                os.mkdir(os.path.join(main_path, 'frames'))
                os.mkdir(os.path.join(main_path, 'frames/tagged'))
                os.mkdir(os.path.join(main_path, 'frames/raw'))
                os.mkdir(os.path.join(main_path, 'frames/events'))
                orig_input_video_path = msg['job']['output_file_path']
                shutil.move(orig_input_video_path, videos_path)
                _, video_filename = os.path.split(orig_input_video_path)
                input_video_path = os.path.join(videos_path, video_filename)
                w = FrameSplitter()
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'main_path': main_path,
                    'input_video_path': input_video_path,
                    'output_dir_path': os.path.join(main_path, 'frames/raw'),
                    'ext': 'png',
                })
            elif msg['worker'] == 'frame_splitter':
                print("[*] Frame Splitter -> Detector")
                raw_frames_dir_path = msg['job']['output_dir_path']
                main_path = msg['job']['main_path']
                output_file_path = os.path.join(main_path, 'data/tags.json')
                output_frames_dir_path = os.path.join(main_path, 'frames/tagged')
                w = Detector()
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'main_path': main_path,
                    'video_path': msg['job']['input_video_path'],
                    'raw_frames_dir_path': raw_frames_dir_path,
                    'output_file_path': output_file_path,
                    'output_frames_dir_path': output_frames_dir_path
                })
            elif msg['worker'] == 'detector':
                print('[*] Detector -> Tracker')
                main_path = msg['job']['main_path']
                video_path = msg['job']['video_path']
                calib_path = '/Users/gvieira/code/toneto/shan/test/calib-configs/venue-11-shelf-1-fps-10.json'
                tags_path = os.path.join(main_path, 'data/tags.json')
                output_file_path = os.path.join(main_path, 'data/tracks.json')
                w = Tracker()
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'main_path': main_path,
                    'video_path': video_path,
                    'calib_path': calib_path,
                    'tags_path': tags_path,
                    'output_file_path': output_file_path
                })
            elif msg['worker'] == 'tracker':
                print('[*] Tracker -> EventExtractor')
                main_path = msg['job']['main_path']
                video_path = msg['job']['video_path']
                w = EventExtractor()
                tracks_path = msg['job']['output_file_path']
                rois_path = '/Users/gvieira/code/toneto/shan/test/rois/v11s1.json'
                output_path = os.path.join(main_path, 'data/events.json')
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'main_path': main_path,
                    'video_path': video_path,
                    'tracks_path': tracks_path,
                    'rois_path': rois_path,
                    'output_path': output_path
                })
            elif msg['worker'] == 'event_extractor':
                print('[*] EventExtractor -> EventedVideoMaker')
                w = EventedVideoMaker()
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'video_path': msg['job']['video_path'],
                    'rois_path': msg['job']['rois_path'],
                    'tr_path': os.path.join(msg['job']['main_path'], 'data/tracking-result.json'),
                    'events_path': msg['job']['output_path'],
                    'output_frames_path': os.path.join(msg['job']['main_path'], 'frames/events'),
                    'output_videos_path': os.path.join(msg['job']['main_path'], 'videos')
                })
            elif msg['worker'] == 'evented_video_maker':
                print('[*] EventedVideoMaker -> Uploader')
                w = Uploader()
                _, orig_video_filename = os.path.split(msg['job']['video_path'])
                evented_video_filename = 'evented-' + orig_video_filename
                evented_video_path = os.path.join(msg['job']['output_videos_path'], evented_video_filename)
                w.add_job({
                    'flow': 'experiment',
                    'shelf_id': msg['job']['shelf_id'],
                    'input_file_path': evented_video_path,
                    's3_bucket': configuration['dev']['s3_bucket'],
                    's3_key': evented_video_filename
                })
            elif msg['worker'] == 'uploader':
                print('[*] Uploader -> DBSaver')
                d = DBSaver()
                d.add_job({
                    'type': 'experiment',
                    'flow': 'experiment',
                    'data': {
                        'shelf_id': msg['job']['shelf_id'],
                        's3_key': msg['job']['s3_key']
                    }
                }) 
        else:
            print("[!] FAILURE: unknown flow '{}'".format(msg['flow']))
        return True

def add_calibration_job(shelf_id):
    ext = '.mov'
    curr_time = time.localtime()
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', curr_time)
    r = Recorder()
    r.add_job({
        'flow': 'calibration',
        'shelf_id': shelf_id,
        'filename': os.path.join(configuration['dev']['workspace_path'], 'calib-{}'.format(time_str) + ext),
        'duration': 1,
        'fps': 'source',
        'size': 'source',
        'codec': 'mp4v',
        'recording_date': current_local_time_isostring()
    })

def add_experiment_job(s3_key, shelf_id, calibration_video_id, rois_conf, tracking_conf, events_conf):
    d = Downloader()
    s3_bucket = configuration['dev']['s3_bucket']
    d.add_job({
        'flow': 'experiment',
        'output_file_path': os.path.join(configuration['dev']['workspace_path'], s3_key),
        's3_key': s3_key,
        's3_bucket': s3_bucket,
        'shelf_id': shelf_id,
        'calibration_video_id': calibration_video_id,
        'rois_conf': rois_conf,
        'tracking_conf': tracking_conf,
        'events_conf': events_conf
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calibration Manager worker.')
    parser.add_argument("command", help="the worker command: 'add', 'start'")
    parser.add_argument("-s", "--shelf_id", type=int, help="db ID of the Shelf to record a calibration video")
    args = parser.parse_args()

    if args.command == 'start':
        calib_manager = CalibManager()
        calib_manager.start()
    elif args.command == 'add':
        if args.shelf_id is not None:
            add_calibration_job(args.shelf_id)
        else:
            print('ERROR: missing shelf ID')
