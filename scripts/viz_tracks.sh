#!/bin/bash
TARGET_DIR=/tmp
rm -rf $TARGET_DIR/tracks
mkdir $TARGET_DIR/tracks
python scripts/visualize_tracks2.py ~/shan/video-33-p_06/video-33-p_06-fps-10.mp4 ~/shan/video-33-p_06/frames_tagged/tags.json /tmp/tracks.json $TARGET_DIR/tracks