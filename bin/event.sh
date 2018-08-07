#!/bin/bash
set -o errexit

WS_PATH=~/shan
VIDEO_ID=$1
VIDEO_PATH=$WS_PATH/$VIDEO_ID
VIDEO_FILE_PATH=$VIDEO_PATH/videos/$VIDEO_ID-fps-10.mp4
# CODE_PATH=~/dev/shelf-analytics
CODE_PATH=~/code/toneto/shan
CALIB_PATH=$CODE_PATH/test/calib-configs/venue-11-shelf-1-fps-10.json
ROIS_PATH=$CODE_PATH/test/rois/v11s2.json
TAGS_PATH=$VIDEO_PATH/data/tags.json
TRACKS_PATH=$VIDEO_PATH/data/tracks.json
TR_PATH=$VIDEO_PATH/data/tracking-result.json
IAOT_PATH=$VIDEO_PATH/data/iaot.json
EVENTS_PATH=$VIDEO_PATH/data/events.json
EVENTED_VIDEO_FILENAME=evented-$VIDEO_ID-fps-10.mp4

echo "Extracting IAOT..."
python scripts/extract_intersection_area_over_time.py $TRACKS_PATH $ROIS_PATH > $IAOT_PATH

echo "Extracting events..."
python scripts/extract_events2.py $IAOT_PATH $TRACKS_PATH $ROIS_PATH $EVENTS_PATH

echo "Printing events..."
python scripts/print_events.py $VIDEO_FILE_PATH $ROIS_PATH $TR_PATH $EVENTS_PATH $VIDEO_PATH/frames/events

echo "Creating final video..."
scripts/_makevideo.sh $VIDEO_PATH/frames/events 10 $EVENTED_VIDEO_FILENAME

echo "Moving final video to output dir..."
mv $VIDEO_PATH/frames/events/$EVENTED_VIDEO_FILENAME $VIDEO_PATH/videos
