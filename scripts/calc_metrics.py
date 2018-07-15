import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))
sys.path.append(os.path.join(os.getcwd(), 'shan/mask_rcnn'))
import argparse
import json
from tnt import get_filenames_at, load_json, print_table
from colorize import green, yellow, red

def compare(video_id, bench, events):
    walked_count = 0
    pondered_count = 0
    interacted_count = 0
    for evt in events:
        if evt['type'] == 'walked':
            walked_count += 1
        elif evt['type'] == 'interacted':
            interacted_count += 1
        elif evt['type'] == 'pondered':
            pondered_count += 1
        else:
            raise RuntimeError('unknown event type: ' + evt['type'])
    walked_accuracy = (100 * (walked_count / bench['walked_count'])) if bench['walked_count'] > 0 else (100.0 if walked_count == 0 else 0.0)
    pondered_accuracy = (100 * (pondered_count / bench['pondered_count'])) if bench['pondered_count'] > 0 else (100.0 if pondered_count == 0 else 0.0)
    interacted_accuracy = (100 * (interacted_count / bench['interacted_count'])) if bench['interacted_count'] > 0 else (100.0 if interacted_count == 0 else 0.0)
    return [
        video_id,
        '{:d}/{:d} ({:.0f}%)'.format(walked_count, bench['walked_count'], walked_accuracy),
        '{:d}/{:d} ({:.0f}%)'.format(pondered_count, bench['pondered_count'], pondered_accuracy),
        '{:d}/{:d} ({:.0f}%)'.format(interacted_count, bench['interacted_count'], interacted_accuracy)
    ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_path", help="path to directory with benchmark data")
    parser.add_argument("workspace_path", help="path to directory with video")
    args = parser.parse_args()

    results_rows = []
    results_header = ['VIDEO', 'WALKED', 'PONDERED', 'INTERACTED']
    fnames = get_filenames_at(args.bench_path)
    for name in fnames:
        bench = load_json(os.path.join(args.bench_path, name))
        video_id, _ = name.split('.')
        try:
            events = load_json(os.path.join(args.workspace_path, video_id, 'data/events.json'))
            results_rows.append(compare(video_id, bench, events))
            print(green('Loaded events for {}'.format(video_id)))
        except Exception as e:
            print(red('Failed to open events.json for {}'.format(video_id)))
    
    # for row in results_rows:
    #     print("\t".join([str(v) for v in row]))
    print_table(results_rows, header=results_header)
        
