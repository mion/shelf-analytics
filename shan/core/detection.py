"""
This module handles detection of human beings in images.
"""
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))

from tnt import load_images, load_json
import json

# Mask RCNN stuff
import random
import numpy as np
from skimage.measure import find_contours
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import coco
import utils
import model as modellib
import visualize

DEFAULT_FRAME_IMAGE_EXTENSION = 'png'
COCO_CLASS_NAMES = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                    'bus', 'train', 'truck', 'boat', 'traffic light',
                    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                    'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                    'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                    'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                    'kite', 'baseball bat', 'baseball glove', 'skateboard',
                    'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                    'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                    'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                    'teddy bear', 'hair drier', 'toothbrush']

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

def apply_mask(image, mask, color, alpha=0.5):
    """Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(mask == 1,
                                  image[:, :, c] *
                                  (1 - alpha) + alpha * color[c] * 255,
                                  image[:, :, c])
    return image

def print_detected_result(image, output_image_path, boxes, masks, class_ids, scores):
    N = boxes.shape[0]
    fig, ax = plt.subplots(1, figsize=(16, 16))
    # Remove white margin:
    # https://stackoverflow.com/a/27227718
    ax.set_axis_off()
    ax.set_title("")
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    ax.get_xaxis().set_major_locator(plt.NullLocator())
    ax.get_yaxis().set_major_locator(plt.NullLocator())
    # Always use red
    color = (0.9, 0.1, 0.0)
    # Print mask and box
    masked_image = image.astype(np.uint32).copy()
    for i in range(N):
        # Skip objects that are not people
        if COCO_CLASS_NAMES.index('person') != class_ids[i]:
            continue
        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        y1, x1, y2, x2 = boxes[i] # CAREFUL WITH THE ORDERING
        p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                              alpha=0.7, linestyle="dashed",
                              edgecolor=color, facecolor='none')
        ax.add_patch(p)
        # Label
        class_id = class_ids[i]
        score = scores[i] if scores is not None else None
        label = COCO_CLASS_NAMES[class_id]
        x = random.randint(x1, (x1 + x2) // 2)
        caption = "{} {:.3f} at [{},{},{},{}]".format(label, score, x1, y1, x2, y2) if score else label
        ax.text(x1, y1 + 8, caption,
                color='w', size=11, backgroundcolor="none")
        # Mask
        mask = masks[:, :, i]
        masked_image = apply_mask(masked_image, mask, color)
        # Mask Polygon
        # Pad to ensure proper polygons for masks that touch image edges.
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            p = Polygon(verts, facecolor="none", edgecolor=color)
            ax.add_patch(p)
    ax.imshow(masked_image.astype(np.uint8))
    plt.savefig(output_image_path, bbox_inches="tight", pad_inches=0, Transparent=True)
    plt.close(fig)

def detect_humans(model, image, debug_output_path):
    """
    Runs the image through the object detection system and returns an
    object with bounding boxes and their scores.
    If `debug_output_path` is not None, save tagged image in this dir.
    """
    all_results = model.detect([image], verbose=1)
    result = all_results[0]
    boxes = result['rois']
    masks = result['masks']
    class_ids = result['class_ids']
    scores = result['scores']

    N = boxes.shape[0]

    if not N:
        print('Warning: boxes.shape[0] was None')
        return {'boxes': [], 'scores': []}
    
    if debug_output_path is not None:
        print_detected_result(image, debug_output_path, boxes, masks, class_ids, scores)
    
    simple_boxes = []
    simple_scores = []
    for i in range(N):
        # ignore objects that are not humans
        if COCO_CLASS_NAMES.index('person') != class_ids[i]:
            continue
        box = []
        for coord in range(0, len(boxes[i])):
            # convert to normal int so it can be JSON dumped
            box.append(int(boxes[i][coord]))
        simple_boxes.append(box)
        if scores[i] is not None:
            simple_scores.append(float(scores[i]))
        else:
            simple_scores.append(0.0)
    
    return {'boxes': simple_boxes, 'scores': simple_scores}

# NOTE: This code assumes that the frames will be read in
# the right order, which may not be the case. We should add a
# 'last_processed_frame_filename' value to the output object 
# and handle it accordingly.
def detect_humans_in_every_image(input_dir_path, output_file_path, frames_dir_path, pika_connection=None):
    """
    This is ugly but we need the `pika_connection` to call `.process_data_events()` so it won't be closed by RabbitMQ.
    """
    ### Load images and last json
    images = load_images(input_dir_path, DEFAULT_FRAME_IMAGE_EXTENSION)
    output = None
    if os.path.exists(output_file_path):
        print("Found older output JSON, loading it")
        output = load_json(output_file_path)
    else:
        print("No JSON found at path, starting fresh")
        output = {
            "last_detected_frame_index": 0,
            "frames": []
        }
    ### Setup MaskRCNN
    config = InferenceConfig()
    config.display()
    ROOT_DIR = os.getcwd()
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "shan/mask_rcnn/mask_rcnn_coco.h5")
    # Create model object in inference mode.
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)
    ### Run object detection on every image
    return_error = None
    for index in range(output['last_detected_frame_index'], len(images)):
        print('Detecting objects in frame {} of {}'.format(str(index), str(len(images))))
        if pika_connection is not None:
            pika_connection.process_data_events()
        try:
            img = images[index]
            n_digits = len(str(len(images)))
            frame_image_name = 'detected-{}.png'.format(str(index).zfill(n_digits))
            tagged_frame_obj = detect_humans(model, img, os.path.join(frames_dir_path, frame_image_name))
            tagged_frame_obj.update({
                'frame_index': index
            })
            output['frames'].append(tagged_frame_obj)
            output['last_detected_frame_index'] = index
        except Exception as exc:
            print('Detection failed, stopping. ERROR: ' + str(exc))
            return_error = exc
            break
    # save work done so far
    with open(output_file_path, 'w') as output_file:
        json.dump(output, output_file)

    return return_error
