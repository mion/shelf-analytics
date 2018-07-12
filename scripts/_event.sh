#!/bin/bash
ROIS_PATH=/Users/gvieira/code/toneto/shan/test/rois/venue-11-shelf-1.json
echo "Cleaning up..."
rm -rf ~/shan/$1/events.json
rm -rf ~/shan/$1/frames/events/*
rm -rf ~/shan/$1/events
echo "Running script..."
python scripts/extract_events2.py $1 $ROIS_PATH
echo "DONE!"
