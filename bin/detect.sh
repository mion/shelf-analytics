#!/bin/bash
set -o errexit

WS_PATH=~/shan
CODE_PATH=~/code/toneto/shan
DETECT_SCRIPT_PATH=$CODE_PATH/scripts/detect_objects2.py

if [ -z $1 ]; then
    echo "ERROR: missing input video ID as 1st argument"
    exit 1
fi
VIDEO_ID=$1

RAW_FRAMES_DIR_PATH=$WS_PATH/$VIDEO_ID/frames/raw
DETECTED_FRAMES_DIR_PATH=$WS_PATH/$VIDEO_ID/frames/tagged
DATA_PATH=$WS_PATH/$VIDEO_ID/data
DETECTED_DATA_FILEPATH=$DATA_PATH/tags.json

if [ -e $DETECTED_FRAMES_DIR_PATH ]; then
    echo "ERROR: there is a directory for detected frames at that path already."
    exit 1
fi

if [ -e $DETECTED_DATA_FILEPATH ]; then
    echo "ERROR: there is a JSON for detected data at that path already."
    exit 1
fi

mkdir $DETECTED_FRAMES_DIR_PATH
python $DETECT_SCRIPT_PATH $RAW_FRAMES_DIR_PATH $DETECTED_DATA_FILEPATH --frames_dir_path $DETECTED_FRAMES_DIR_PATH

# usage: detect_objects2.py [-h] [--frames_dir_path FRAMES_DIR_PATH]
#                           input_dir_path output_file_path

# positional arguments:
#   input_dir_path        input directory with many images inside
#   output_file_path      path to a JSON file where the data will be saved

# optional arguments:
#   -h, --help            show this help message and exit
#   --frames_dir_path FRAMES_DIR_PATH
#                         if specified, save frames after detection in this
#                         directory
