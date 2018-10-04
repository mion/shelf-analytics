"""
Split a video into many frames using a ffmpeg subprocess.

Copyright (c) 2018 TonetoLabs.
Author: Gabriel Luis Vieira (gluisvieira@gmail.com)
"""
import os
import sys
import subprocess
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))
from util import has_ffmpeg_installed, count_frames

def split_frames(input_video_path, output_dir_path, extension):
    if not has_ffmpeg_installed():
        raise RuntimeError('ffmpeg is not installed')
    frame_count = count_frames(input_video_path)
    n_digits = len(str(frame_count))
    frame_number_format = '%0' + str(n_digits) + 'd'
    final_output_path = os.path.join(output_dir_path, "frame-{0}.{1}".format(frame_number_format, extension))
    cmd_template = "ffmpeg -i {0} {1} -hide_banner"
    cmd = cmd_template.format(input_video_path, final_output_path)
    # FIXME: using 'subprocess.call' with shell=True is not secure, search Python 3 docs for explanation.
    result = subprocess.call(cmd, shell=True)
    return result == 0
