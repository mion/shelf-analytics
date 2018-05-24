#!/bin/bash
echo "Cleaning up..."
rm -rf ~/shan/$1/iaot.json
rm -rf ~/shan/$1/events.json
rm -rf ~/shan/$1/events-$1-fps-5.mp4
rm -rf ~/shan/$1/frames_events/*
rm -rf ~/shan/$1/tracks/*
echo "Tracking objects IAOT..."
python scripts/track_objects.py ~/shan/$1/$1-fps-5.mp4 ~/shan/$1/frames_tagged/tags.json ~/shan/$1/tracks
echo "Extracting IAOT..."
python scripts/extract_intersection_area_over_time.py ~/shan/$1/tracks/tracks.json ./test/rois/rois-aisle.json > ~/shan/$1/iaot.json
echo "Extracting events..."
python scripts/extract_events.py ./test/rois/rois-aisle.json ~/shan/$1/iaot.json > ~/shan/$1/events.json
echo "Generating events..."
python scripts/visualize_events.py ~/shan/$1/frames_events/ ~/shan/$1/$1-fps-5.mp4 ~/shan/$1/events.json ./test/rois/rois-aisle.json ~/shan/$1/tracks/tracks.json ~/shan/$1/iaot.json
echo "Stiching frames together..."
ffmpeg -framerate 5 -pattern_type glob -i "/Users/gvieira/shan/$1/frames_events/*.png" -c:v libx264 -r 5 -pix_fmt yuv420p /Users/gvieira/shan/$1/events-$1-fps-5.mp4
echo "DONE!"
