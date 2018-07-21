#!/bin/bash
set -o errexit

WS_PATH=~/shan
VIDEO_ID=$1
VIDEO_PATH=$WS_PATH/$VIDEO_ID
VIDEO_FILE_PATH=$VIDEO_PATH/videos/$VIDEO_ID-fps-10.mp4
CODE_PATH=~/dev/shelf-analytics
CALIB_PATH=$CODE_PATH/test/calib-configs/venue-11-shelf-1-fps-10.json
TR_PATH=$VIDEO_PATH/data/tracking-result.json

python scripts/inspect_tracks.py $VIDEO_FILE_PATH $CALIB_PATH $TR_PATH
