SPATH=$(pwd)
if [ -d $SPATH/logs ]; then
  echo "Saving logs to: $SPATH/logs"
else
  mkdir $SPATH/logs
  echo "Creating dir and saving logs to: $SPATH/logs"
fi

echo "Starting calib_manager..."
SHANPATH=$SPATH nohup python shan/workers/calib_manager.py start >> $SPATH/logs/calib_manager.log 2>&1 &

echo "Starting db_saver..."
SHANPATH=$SPATH nohup python shan/workers/db_saver.py start >> $SPATH/logs/db_saver.log 2>&1 &

echo "Starting detector..."
SHANPATH=$SPATH nohup python shan/workers/detector.py start >> $SPATH/logs/detector.log 2>&1 &

echo "Starting downloader..."
SHANPATH=$SPATH nohup python shan/workers/downloader.py start >> $SPATH/logs/downloader.log 2>&1 &

echo "Starting event_extractor..."
SHANPATH=$SPATH nohup python shan/workers/event_extractor.py start >> $SPATH/logs/event_extractor.log 2>&1 &

echo "Starting evented_video_maker..."
SHANPATH=$SPATH nohup python shan/workers/evented_video_maker.py start >> $SPATH/logs/evented_video_maker.log 2>&1 &

echo "Starting frame_splitter..."
SHANPATH=$SPATH nohup python shan/workers/frame_splitter.py start >> $SPATH/logs/frame_splitter.log 2>&1 &

echo "Starting recorder..."
SHANPATH=$SPATH nohup python shan/workers/recorder.py start >> $SPATH/logs/recorder.log 2>&1 &

echo "Starting tracker..."
SHANPATH=$SPATH nohup python shan/workers/tracker.py start >> $SPATH/logs/tracker.log 2>&1 &

echo "Starting transcoder..."
SHANPATH=$SPATH nohup python shan/workers/transcoder.py start >> $SPATH/logs/transcoder.log 2>&1 &

echo "Starting uploader..."
SHANPATH=$SPATH nohup python shan/workers/uploader.py start >> $SPATH/logs/uploader.log 2>&1 &
