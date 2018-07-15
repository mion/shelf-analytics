VIDEO_ID=$1
BASE_PATH=/home/mion/shan
VIDEO_PATH=$BASE_PATH/$VIDEO_ID
RAW_VIDEOS_PATH=/home/mion/dev/shelf-analytics/test/videos

echo "Creating dirs..."
mkdir $VIDEO_PATH
mkdir $VIDEO_PATH/data
mkdir $VIDEO_PATH/videos
mkdir $VIDEO_PATH/frames
mkdir $VIDEO_PATH/frames/raw
mkdir $VIDEO_PATH/frames/tagged
echo "Transcoding video at $RAW_VIDEOS_PATH/$VIDEO_ID.mp4"
python scripts/transcode.py $RAW_VIDEOS_PATH/$VIDEO_ID.mp4 $VIDEO_PATH/videos/$VIDEO_ID-fps-10.mp4 --fps 10
echo "Splitting frames..."
python scripts/split_frames.py $VIDEO_PATH/videos/$VIDEO_ID-fps-10.mp4 $VIDEO_PATH/frames/raw
