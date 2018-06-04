#!/bin/bash
VIDEO_PATH=~/shan/$1/$1-fps-$2.mp4
TAGS_PATH=~/shan/$1/frames_tagged/tags.json 
TRACKS_PATH=~/shan/$1/tracks/tracks.json
TRACK_INDEX=$3
OUTPUT_DIR=~/shan/$1/tracks

python scripts/visualize_tracks.py $VIDEO_PATH $TAGS_PATH $TRACKS_PATH $TRACK_INDEX $OUTPUT_DIR
