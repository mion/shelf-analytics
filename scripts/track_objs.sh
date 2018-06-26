#!/bin/bash
TARGET_DIR=/tmp
rm $TARGET_DIR/tracks.json
python scripts/track_objects.py ~/shan/video-33-p_06/video-33-p_06-fps-10.mp4 ~/shan/video-33-p_06/frames_retagged/tags.json $TARGET_DIR