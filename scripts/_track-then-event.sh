#!/bin/bash
set -o errexit

WS_PATH=~/shan
CODE_PATH=~/dev/shelf-analytics

ROIS_PATH=$CODE_PATH/test/rois/v11s1.json
CALIB_PATH=$CODE_PATH/test/calib-configs/venue-11-shelf-1-fps-10.json
VIDEO_PATH=$WS_PATH/$1/videos/$1-fps-10.mp4
DATA_PATH=$WS_PATH/$1/data
TAGS_PATH=$WS_PATH/$1/frames/tagged/tags.json
TR_PATH=$DATA_PATH/tracking-result.json
TRACKS_PATH=$WS_PATH/$1/data/tracks.json
IAOT_PATH=$DATA_PATH/iaot.json
EVENTS_PATH=$DATA_PATH/events.json
EVT_OUTPUT_PATH=$WS_PATH/$1/frames/events
EVT_VIDEO_NAME=evented-$1-fps-10.mp4
DEBUG_PATH=~/shan-debug

echo "Tracking..."
python scripts/track_objects2.py $VIDEO_PATH $CALIB_PATH $TAGS_PATH $DATA_PATH
echo "Extracting IAOT..."
python scripts/extract_intersection_area_over_time.py $TRACKS_PATH $ROIS_PATH > $IAOT_PATH
echo "Extracting events..."
python scripts/extract_events2.py $IAOT_PATH $TRACKS_PATH $ROIS_PATH $EVENTS_PATH
echo "Printing events..."
mkdir $EVT_OUTPUT_PATH
python scripts/print_events.py $VIDEO_PATH $ROIS_PATH $TR_PATH $EVENTS_PATH $EVT_OUTPUT_PATH
echo "Creating final video..."
scripts/_makevideo.sh $WS_PATH/$1/frames/events 10 $EVT_VIDEO_NAME
echo "Moving final video to output dir..."
mv $WS_PATH/$1/frames/events/$EVT_VIDEO_NAME $WS_PATH/$1/videos
cp $WS_PATH/$1/videos/$EVT_VIDEO_NAME $DEBUG_PATH
