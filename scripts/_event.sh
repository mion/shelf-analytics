#!/bin/bash
ROIS_PATH=/Users/gvieira/code/toneto/shan/test/rois/venue-11-shelf-1.json
VIDEO_PATH=/Users/gvieira/shan/$1/videos/transcoded-fps-10.mp4
TR_PATH=/Users/gvieira/shan/$1/data/tracking-result.json
EVENTS_PATH=/Users/gvieira/shan/$1/data/events.json
OUTPUT_PATH=/Users/gvieira/shan/$1/frames/events

echo "Cleaning up..."
rm -rf ~/shan/$1/events.json
rm -rf ~/shan/$1/frames/events/*
echo "Extracting events..."
python scripts/extract_events2.py $1 $ROIS_PATH
echo "Printing events..."
python scripts/print_events.py $VIDEO_PATH $ROIS_PATH $TR_PATH $EVENTS_PATH $OUTPUT_PATH
echo "DONE!"
