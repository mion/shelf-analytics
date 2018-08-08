#!/bin/bash
set -o errexit

WS_PATH=~/shan
CODE_PATH=~/code/toneto/shan
SPLIT_FRAMES_SCRIPT_PATH=$CODE_PATH/scripts/split_frames.py
TRANSCODE_SCRIPT_PATH=$CODE_PATH/scripts/transcode.py
OUTPUT_VIDEO_EXT="mp4"
OUTPUT_FRAMES_EXT="png"

if [ -z $1 ]; then
    echo "ERROR: missing input video path as 1st argument"
    exit 1
fi
INPUT_VIDEO_PATH=$1

if [ -z $2 ]; then
    echo "ERROR: missing desired FPS as 2nd argument"
    exit 1
fi
FPS=$2

FILENAME=$(basename -- "$INPUT_VIDEO_PATH")
INPUT_VIDEO_EXT="${FILENAME##*.}"
VIDEO_ID="${FILENAME%.*}"
OUTPUT_DIR_PATH=$WS_PATH/$VIDEO_ID
OUTPUT_VIDEO_PATH=$OUTPUT_DIR_PATH/videos/$VIDEO_ID-fps-$FPS.$OUTPUT_VIDEO_EXT

if [ -e $OUTPUT_DIR_PATH ]; then
    echo "ERROR: there is a directory at that path already."
    exit 1
fi

# Create basic dir structure
mkdir $OUTPUT_DIR_PATH
mkdir $OUTPUT_DIR_PATH/videos
mkdir $OUTPUT_DIR_PATH/data
mkdir $OUTPUT_DIR_PATH/frames
mkdir $OUTPUT_DIR_PATH/frames/raw

# Transcode, then split frames
python $TRANSCODE_SCRIPT_PATH --fps $FPS $INPUT_VIDEO_PATH $OUTPUT_VIDEO_PATH
python $SPLIT_FRAMES_SCRIPT_PATH --ext $OUTPUT_FRAMES_EXT $OUTPUT_VIDEO_PATH $OUTPUT_DIR_PATH/frames/raw

# (ai) ➜  shan git:(master) ✗ python scripts/split_frames.py -h
# usage: split_frames.py [-h] [--ext EXT] input_video_path output_dir_path

# positional arguments:
#   input_video_path  input video file path
#   output_dir_path   output directory

# optional arguments:
#   -h, --help        show this help message and exit
#   --ext EXT         frame image file extension: 'png' (default) or 'jpg'

# (ai) ➜  shan git:(master) ✗ python scripts/transcode.py -h
# usage: transcode.py [-h] [--fps FPS] input_video_path output_video_path

# positional arguments:
#   input_video_path   input video file path
#   output_video_path  output video file path

# optional arguments:
#   -h, --help         show this help message and exit
#   --fps FPS          frames per second for output video (default is 10)
# (ai) ➜  shan git:(master) ✗ bin/transplit.sh ./test/videos/video-01-p.mp4

# CODE_PATH=~/code/toneto/shan
# CALIB_PATH=$CODE_PATH/test/calib-configs/venue-11-shelf-1-fps-10.json
# TAGS_PATH=$VIDEO_PATH/data/tags.json
# OUTPUT_PATH=$VIDEO_PATH/data

# if [ -z "$2" ]; then
#     python scripts/track_objects2.py $VIDEO_FILE_PATH $CALIB_PATH $TAGS_PATH $OUTPUT_PATH
# elif [ -n "$2" ]; then
#     python -m pdb scripts/track_objects2.py $VIDEO_FILE_PATH $CALIB_PATH $TAGS_PATH $OUTPUT_PATH
# fi
