#!/bin/bash
WS_PATH=~/shan
OUTPUT_PATH=~/shan-debug

for video_path in $WS_PATH/*; do
    video_id=$(basename $video_path)
    cp $video_path/videos/evented-$video_id-fps-10.mp4 $OUTPUT_PATH
    echo "Created evented video for $video_id"
done