#!/bin/bash
set -o errexit
ROIS_PATH=/Users/gvieira/code/toneto/shan/test/rois/venue-11-shelf-1.json
DATA_PATH=/Users/gvieira/shan/$1/data
TAGS_PATH=/Users/gvieira/shan/$1/data/tags.json
CALIB_PATH=/Users/gvieira/code/toneto/shan/test/calib-configs/venue-11-shelf-1-fps-10.json
VIDEO_PATH=/Users/gvieira/shan/$1/videos/$1-fps-10.mp4
TR_PATH=/Users/gvieira/shan/$1/data/tracking-result.json
TRACKS_PATH=/Users/gvieira/shan/$1/data/tracks.json
EVENTS_PATH=/Users/gvieira/shan/$1/data/events.json
OUTPUT_PATH=/Users/gvieira/shan/$1/frames/events

echo "Cleaning up..."
rm -rf ~/shan/$1/data/tracks.json
rm -rf ~/shan/$1/data/tracking-result.json
rm -rf ~/shan/$1/data/iaot.json
rm -rf ~/shan/$1/data/events.json
rm -rf ~/shan/$1/frames/events/*
if [ -z "$2" ]; then
  echo "Tracking..."
  python scripts/track_objects2.py $VIDEO_PATH $CALIB_PATH $TAGS_PATH $DATA_PATH
  echo "Extracting IAOT..."
  python scripts/extract_intersection_area_over_time.py $TRACKS_PATH $ROIS_PATH > $DATA_PATH/iaot.json
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
