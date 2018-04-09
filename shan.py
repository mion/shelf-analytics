import os
import json

def load_tagged_bundle(path):
  tags_file_path = os.path.join(path, "tags.json")
  with open(tags_file_path, "r") as tags_file:
    return json.loads(tags_file.read())
