#!/bin/bash
set -o errexit

WS_PATH=~/shan
VIDEO_ID=$1
VIDEO_PATH=$WS_PATH/$VIDEO_ID
EVENTED_VIDEO_FILENAME=evented-$1-fps-10.mp4

rm $VIDEO_PATH/data/iaot.json
echo "Removed $VIDEO_PATH/iaot.json"

rm $VIDEO_PATH/data/events.json
echo "Removed $VIDEO_PATH/events.json"

rm $VIDEO_PATH/data/tracking-result.json
echo "Removed $VIDEO_PATH/tracking-result.json"

rm $VIDEO_PATH/data/tracks.json
echo "Removed $VIDEO_PATH/tracks.json"

rm $VIDEO_PATH/frames/events/*
echo "Removed every file in $VIDEO_PATH/frames/events"

rm $VIDEO_PATH/videos/$EVENTED_VIDEO_FILENAME
echo "Removed $VIDEO_PATH/videos/$EVENTED_VIDEO_FILENAME"

echo "Video $VIDEO_ID is clean"