import os, sys, inspect, argparse, json
from shan.common.colorize import header, yellow, red, green
from shan.common.util import load_json

def get_currendir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def is_dir_empty(path):
    return next(os.scandir(path), None) is None

def test_all(ws_path):
    pass

def test_detection(ws_path):
    import uuid
    from shan.core.detection import detect_humans_in_every_image
    test_id = uuid.uuid4().hex
    input_dir_path = os.path.join(get_currendir(), 'test/fixture/detection')
    output_file_path = os.path.join(ws_path, 'detection_test_tags_{}.json'.format(test_id))
    frames_dir_path = os.path.join(ws_path, 'detection_test_tagged_frames_{}'.format(test_id))
    os.mkdir(frames_dir_path)
    print(yellow('[*] Input dir path: ') + input_dir_path)
    print(yellow('[*] Output file path: ') + output_file_path)
    print(yellow('[*] Frames dir path: ') + frames_dir_path)

    error = detect_humans_in_every_image(input_dir_path, output_file_path, frames_dir_path)

    if error is None and os.path.exists(output_file_path) and not is_dir_empty(frames_dir_path):
        print(green('[*] TEST SUCCESSFUL'))
    else:
        print(red('[!] TEST FAILED'))

def test_event_extraction(ws_path):
    pass

def test_frame_splitting(ws_path):
    import uuid
    from shan.core.frame_splitting import split_frames
    EXT = 'png'
    input_video_path = os.path.join(get_currendir(), 'test/fixture/frame_splitting/walked-single-fps-10.mp4')
    output_dir_path = os.path.join(ws_path, 'frame_splitting_test_{}'.format(uuid.uuid4().hex))
    os.mkdir(output_dir_path)
    print(yellow('[*] Input video path: ') + input_video_path)
    print(yellow('[*] Output dir path: ') + output_dir_path)
    print(yellow('[*] Extension: ') + EXT)

    success = split_frames(input_video_path, output_dir_path, EXT)

    if success and os.path.exists(os.path.join(output_dir_path, 'frame-56.png')):
        print(green('[*] TEST SUCCESSFUL'))
    else:
        print(red('[!] TEST FAILED'))

def test_iaot(ws_path):
    from shan.core.iaot import extract_intersection_area_over_time
    tracks_path = os.path.join(get_currendir(), 'test/fixture/iaot/tracks.json')
    rois_path = os.path.join(get_currendir(), 'test/fixture/iaot/venue-11-shelf-1.json')
    tracks = load_json(tracks_path)
    rois = load_json(rois_path)
    print(yellow('[*] Tracks path: ') + tracks_path)
    print(yellow('[*] Rois path: ') + rois_path)
    iaot = extract_intersection_area_over_time(tracks, rois)
    if len(iaot) > 0:
        print(green('[*] TEST SUCCESSFUL'))
    else:
        print(red('[!] TEST FAILED'))

def test_tracking(ws_path):
    import uuid
    from shan.core.frame_bundle import load_frame_bundles
    from shan.core.tracking import track_humans

    test_id = uuid.uuid4().hex
    MAX_TRACKS = 40

    calib_config_path = os.path.join(get_currendir(), 'test/calib-configs/venue-11-shelf-1-fps-10.json')
    tags_path = os.path.join(get_currendir(), 'test/fixture/tracking/tags.json')
    video_path = os.path.join(get_currendir(), 'test/fixture/tracking/video-33-p_06-fps-10.mp4')
    output_dir_path = os.path.join(ws_path, 'tracking_test_{}'.format(test_id))
    os.mkdir(output_dir_path)
    output_file_path = os.path.join(output_dir_path, 'tracks.json')
    tr_file_path = os.path.join(output_dir_path, 'tracking-result.json')

    print(yellow('[*] Calib config path: ') + calib_config_path)
    print(yellow('[*] Tags path: ') + tags_path)
    print(yellow('[*] Video path: ') + video_path)
    print(yellow('[*] Output dir path: ') + output_dir_path)

    calib_config = load_json(calib_config_path)
    tags = load_json(tags_path)
    frame_bundles = load_frame_bundles(video_path, tags)
    tracks, tracking_result = track_humans(calib_config, frame_bundles, MAX_TRACKS)
    with open(output_file_path, 'w') as output_file:
        json.dump(tracks, output_file)
    tracking_result.save_as_json(tr_file_path)

    if os.path.exists(output_file_path) and os.path.exists(tr_file_path):
        print(green('[*] TEST SUCCESSFUL'))
    else:
        print(red('[!] TEST FAILED'))

def test_transcoding(ws_path):
    from shan.core.transcoding import transcode
    FPS = 10
    test_videos_path = os.path.join(get_currendir(), 'test/videos')
    test_video_name = 'walked-single.mp4'
    input_video_path = os.path.join(test_videos_path, test_video_name)
    output_video_path = os.path.join(ws_path, 'walked-single-fps-{}.mp4'.format(FPS))
    print(yellow('[*] Input video path: ') + input_video_path)
    print(yellow('[*] Output video path: ') + output_video_path)
    print(yellow('[*] FPS: ') + str(FPS))

    success = transcode(input_video_path, output_video_path, FPS)

    if success and os.path.exists(output_video_path):
        print(green('[*] TEST SUCCESSFUL'))
    else:
        print(red('[!] TEST FAILED'))

if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description='A very simple and rudimentary integration test for all the code.')
    argparse.add_argument('name', type=str, help="Name of the module to test: 'all', 'detection', 'event_extraction', 'frame_splitting', 'iaot', 'tracking' or 'transcoding'")
    argparse.add_argument('-p', '--path', type=str, help="Path to the temporary directory where files will be created.")
    args = argparse.parse_args()

    func_for_name = {
        'all': test_all,
        'detection': test_detection,
        'event_extraction': test_event_extraction,
        'frame_splitting': test_frame_splitting,
        'iaot': test_iaot,
        'tracking': test_tracking,
        'transcoding': test_transcoding
    }

    if args.name not in func_for_name:
        print(red('[!] ERROR: invalid name:')+ args.name)
        sys.exit(1)

    print(yellow('[*] Module: ') + header(args.name))
    print(yellow('[*] Workspace: ') + args.path)
    func_for_name[args.name](args.path)
