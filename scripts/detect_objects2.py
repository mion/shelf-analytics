import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

import argparse

try:
    from detection import detect_humans_in_every_image

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir_path", help="input directory with many images inside")
    parser.add_argument("output_file_path", help="path to a JSON file where the data will be saved")
    parser.add_argument("--frames_dir_path", help="if specified, save frames after detection in this directory")
    args = parser.parse_args()

    error = detect_humans_in_every_image(args.input_dir_path, args.output_file_path, args.frames_dir_path)
    if error is None:
        print("SUCCESS: detection completed")
        sys.exit(0)
    else:
        print("FAILURE: detection failed for one of the frames:\n{}".format(error))
        sys.exit(1)
except Exception as err:
    print("FAILURE: something unexpected went wrong during object detection:\n{}".format(err))
    sys.exit(1)
