#!/bin/bash
set -o errexit
ROIS_PATH=/Users/gvieira/code/toneto/shan/test/rois/venue-11-shelf-1.json
VIDEO_PATH=/Users/gvieira/shan/$1/videos/transcoded-fps-10.mp4
TR_PATH=/Users/gvieira/shan/$1/data/tracking-result.json
EVENTS_PATH=/Users/gvieira/shan/$1/data/events.json
OUTPUT_PATH=/Users/gvieira/shan/$1/frames/events

echo "Cleaning up..."
rm -rf ~/shan/$1/events.json
rm -rf ~/shan/$1/frames/events/*
if [ -z "$2" ]; then
  echo "Extracting events..."
  python scripts/extract_events2.py $1 $ROIS_PATH
  echo "Printing events..."
  python scripts/print_events.py $VIDEO_PATH $ROIS_PATH $TR_PATH $EVENTS_PATH $OUTPUT_PATH
  echo "Creating final video..."
  scripts/_makevideo.sh /Users/gvieira/shan/$1/frames/events 10 evented-fps-10.mp4
  echo "Moving final video to output dir..."
  mv /Users/gvieira/shan/$1/frames/events/evented-fps-10.mp4 /Users/gvieira/shan/$1/videos
else
  echo "Debugging extraction of events..."
  python -m pdb scripts/extract_events2.py $1 $ROIS_PATH
fi
