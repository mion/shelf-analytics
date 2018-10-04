import os
import sys
sys.path.append(os.environ['SHANPATH'])
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/common'))
sys.path.append(os.path.join(os.environ['SHANPATH'], 'shan/core'))

import argparse
from util import load_json, load_frames, make_events_per_frame
from bounding_box import BoundingBox as BBox, BoundingBoxFormat as BBoxFormat
from tracking import TrackingResult
from cvutil import save_image
from drawing import draw_bbox_with_title, draw_sidebar_right, draw_text, get_text_size, draw_bbox_outline

def render_frame_with_events(frame, index, rois, bboxes_in_frame, events_in_frame, past_events):
    for roi in rois:
        triggered_event = False
        for evt in events_in_frame:
            if evt['roi_name'] == roi['name']:
                triggered_event = True
        if triggered_event:
            frame = draw_bbox_with_title(frame, BBox(roi['bbox'], BBoxFormat.y1_x1_y2_x2), roi['name'], text_color=(0, 255, 0), outline_color=(0, 255, 0), thickness=3)
        else:
            frame = draw_bbox_with_title(frame, BBox(roi['bbox'], BBoxFormat.y1_x1_y2_x2), roi['name'], text_color=(255, 255, 255), outline_color=(255, 255, 255), thickness=1)
    for bbox in bboxes_in_frame:
        if len(bbox.parent_track_ids) > 0:
            frame = draw_bbox_with_title(frame, bbox, ('Customer #' + ''.join([str(i) for i in bbox.parent_track_ids])), text_color=(255, 125, 0), outline_color=(255, 50, 0), title_bg_color=(50, 0, 0), thickness=2)
        else:
            frame = draw_bbox_outline(frame, bbox)
    # draw events
    LINE_SPACE = 10
    PADDING = 15
    _, frame_width, _ = frame.shape
    start_x = frame_width + PADDING
    curr_y = PADDING
    frame = draw_sidebar_right(frame, 400)
    events = past_events + events_in_frame
    events.reverse() # show later events first
    for evt in events:
        text = 'frame {} ({}): "{}" by customer #{}'.format(str(evt['index']), evt['roi_name'], evt['type'], evt['track'] + 1)
        frame = draw_text(frame, text, (start_x, curr_y), color=(0, 255, 0))
        _, text_height = get_text_size(text)
        curr_y += text_height + LINE_SPACE
    return frame

def print_frames(video_path, rois_path, tr_path, events_path, output_path):
    frames = load_frames(video_path)
    rois = load_json(rois_path)
    tracking_result = TrackingResult()
    tracking_result.load_from_json(frames, tr_path)
    events = load_json(events_path)

    bboxes_by_frame_index = {}
    bboxes_by_id = {}
    for index in range(len(frames)):
        bboxes_by_frame_index[index] = []
        for bbox in tracking_result.frame_bundles[index].bboxes:
            bboxes_by_id[bbox.id] = bbox
            bboxes_by_frame_index[index].append(bbox)
    for track in tracking_result.tracks:
        for frame_index, bbox, transition in track.steps:
            if bbox.id not in bboxes_by_id:
                bboxes_by_frame_index[frame_index].append(bbox)
                bboxes_by_id[bbox.id] = bbox

    n_digits = len(str(len(frames)))
    events_per_frame = make_events_per_frame(events)

    past_events = []
    for idx in range(len(frames)):
        events_in_frame = events_per_frame[idx] if idx in events_per_frame else []
        frame = render_frame_with_events(frames[idx], idx, rois, bboxes_by_frame_index[idx], events_in_frame, past_events)
        past_events += events_in_frame
        filename = 'frame-{}.png'.format(str(idx).zfill(n_digits))
        save_image(frame, filename, output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', help='path to the video file')
    parser.add_argument('rois_path', help='path to the rois JSON file')
    parser.add_argument('tracking_result_path', help='path to a tracking result JSON file')
    parser.add_argument('events_path', help='path to the events JSON file')
    parser.add_argument("output_path", help="path to the output directory where frames will be saved")
    args = parser.parse_args()

    print_frames(args.video_path, args.rois_path, args.tracking_result_path, args.events_path, args.output_path)

    # frames = load_frames(args.video_path)
    # rois = load_json(args.rois_path)
    # tracking_result = TrackingResult()
    # tracking_result.load_from_json(frames, args.tracking_result_path)
    # events = load_json(args.events_path)

    # bboxes_by_frame_index = {}
    # bboxes_by_id = {}
    # for index in range(len(frames)):
    #     bboxes_by_frame_index[index] = []
    #     for bbox in tracking_result.frame_bundles[index].bboxes:
    #         bboxes_by_id[bbox.id] = bbox
    #         bboxes_by_frame_index[index].append(bbox)
    # for track in tracking_result.tracks:
    #     for frame_index, bbox, transition in track.steps:
    #         if bbox.id not in bboxes_by_id:
    #             bboxes_by_frame_index[frame_index].append(bbox)
    #             bboxes_by_id[bbox.id] = bbox

    # n_digits = len(str(len(frames)))
    # events_per_frame = make_events_per_frame(events)

    # past_events = []
    # for idx in range(len(frames)):
    #     events_in_frame = events_per_frame[idx] if idx in events_per_frame else []
    #     frame = render_frame_with_events(frames[idx], idx, rois, bboxes_by_frame_index[idx], events_in_frame, past_events)
    #     past_events += events_in_frame
    #     filename = 'frame-{}.png'.format(str(idx).zfill(n_digits))
    #     save_image(frame, filename, args.output_path)

