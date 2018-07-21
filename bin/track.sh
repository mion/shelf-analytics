#!/bin/bash
set -o errexit

WS_PATH=~/shan
VIDEO_ID=$1
VIDEO_PATH=$WS_PATH/$VIDEO_ID
VIDEO_FILE_PATH=$VIDEO_PATH/videos/$VIDEO_ID-fps-10.mp4
CODE_PATH=~/dev/shelf-analytics
CALIB_PATH=$CODE_PATH/test/calib-configs/venue-11-shelf-1-fps-10.json
TAGS_PATH=$VIDEO_PATH/data/tags.json
OUTPUT_PATH=$VIDEO_PATH/data

if [ -z "$2" ]; then
    python scripts/track_objects2.py $VIDEO_FILE_PATH $CALIB_PATH $TAGS_PATH $OUTPUT_PATH
elif [ -n "$2" ]; then
    python -m pdb scripts/track_objects2.py $VIDEO_FILE_PATH $CALIB_PATH $TAGS_PATH $OUTPUT_PATH
fi
