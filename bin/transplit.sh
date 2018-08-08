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
