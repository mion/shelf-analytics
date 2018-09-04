import os, sys, inspect, argparse

from shan.common.colorize import header, yellow, red, green

def get_currendir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def test_all(ws_path):
    pass

def test_detection(ws_path):
    pass

def test_event_extraction(ws_path):
    pass

def test_frame_splitter(ws_path):
    pass

def test_iaot(ws_path):
    pass

def test_tracking(ws_path):
    pass

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
        print(green('[*] TEST SUCCESFUL'))
    else:
        print(red('[!] TEST FAILED'))

if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description='A very simple and rudimentary integration test for all the code.')
    argparse.add_argument('name', type=str, help="Name of the module to test: 'all', 'detection', 'event_extraction', 'frame_splitter', 'iaot', 'tracking' or 'transcoding'")
    argparse.add_argument('-p', '--path', type=str, help="Path to the temporary directory where files will be created.")
    args = argparse.parse_args()

    func_for_name = {
        'all': test_all,
        'detection': test_detection,
        'event_extraction': test_event_extraction,
        'frame_splitter': test_frame_splitter,
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
