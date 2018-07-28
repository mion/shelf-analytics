from flask import Flask
from flask import jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/videos")
def get_videos():
  resp = {
    "videos": [
      {
        "id": "123",
        "name": "video-33-p_06"
      }
    ]
  }
  return jsonify(resp)

@app.route("/videos/<video_id>")
def get_video(video_id):
  resp = {
    "id": "123",
    "name": "video-33-p_06",
    "frames": [
      {
        "frame_index": 0
      }
    ]
  }
  return jsonify(resp)
