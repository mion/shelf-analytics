import os
import sys
import argparse
from shan.core.detection import detect_humans_in_every_image

parser = argparse.ArgumentParser()
parser.add_argument("input_dir_path", help="input directory with many images inside")
parser.add_argument("output_file_path", help="path to a JSON file where the data will be saved")
parser.add_argument("--frames_dir_path", help="if specified, save frames after detection in this directory")
args = parser.parse_args()

error = detect_humans_in_every_image(args.input_dir_path, args.output_file_path, args.frames_dir_path, image_ext='jpg')
if error is None:
    print("SUCCESS: detection completed")
    sys.exit(0)
else:
    print("FAILURE: detection failed for one of the frames:\n{}".format(error))
    sys.exit(1)
