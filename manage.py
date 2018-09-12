import sys, os, signal, argparse
from shan.common.colorize import header, yellow, green, red

workers = [
    'calib_manager',
    'db_saver',
    'detector',
    'downloader',
    'event_extractor',
    'evented_video_maker',
    'frame_splitter',
    'recorder',
    'tracker',
    'transcoder',
    'uploader'
]

def pid_for(name):
    lines = [l for l in os.popen('ps aux | grep {} | grep -v grep'.format(name))]
    if len(lines) == 0:
        return None
    elif len(lines) == 1:
        return lines[0].split()[1]
    else:
        raise RuntimeError('there is more than one proc with name "{}"'.format(name))

# https://gist.github.com/marcoagner/9926309
# def check_kill_process(pstring):
#     for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
#         fields = line.split()
#         pid = fields[0]
#         os.kill(int(pid), signal.SIGKILL)

def start_workers():
    pass

def stop_workers():
    print(header('[*] Killing workers...'))
    for name in workers:
        pid = pid_for(name)
        if pid is None:
            print('\t' + red('No running process found for {}'.format(name)))
        else:
            os.kill(int(pid), signal.SIGKILL)
            print('\t' + 'Killed process {} of {}'.format(yellow(pid), green(name)))

def list_workers():
    print(header('[*] Workers:'))
    for name in workers:
        pid = pid_for(name)
        status = green(pid) if pid is not None else red('stopped')
        print('\t{}\t{}'.format(status, yellow(name)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="One of: start_workers, list_workers, stop_workers")
    args = parser.parse_args()

    func_for_command = {
        'start_workers': start_workers,
        'stop_workers': stop_workers,
        'list_workers': list_workers
    }

    if args.command not in func_for_command:
        print('ERROR: unrecognized command "{}"'.format(args.command))
        sys.exit(1)
    else:
        func_for_command[args.command]()
