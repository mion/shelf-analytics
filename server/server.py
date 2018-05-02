from flask import Flask
from flask import jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/videos")
def hello():
  resp = {
    "videos": [
      {
        "id": "123",
        "name": "video-01-d-fps-5"
      }
    ]
  }
  return jsonify(resp)
