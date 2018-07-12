#!/bin/bash
DIR_PATH=$1
FPS=$2
OUTPUT_NAME=$3
cd $DIR_PATH
ffmpeg -framerate $FPS -pattern_type glob -i "*.png" -c:v libx264 -r $FPS -pix_fmt yuv420p $OUTPUT_NAME