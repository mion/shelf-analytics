LOCAL_IP = '192.168.0.2'
DEV_QUEUE_HOST = LOCAL_IP
configuration = {
    'dev': {
        'API_base_url': 'http://'+LOCAL_IP+':8000/shancms',
        'workspace_path': '/home/mion/shanws',
        's3_bucket': 'shan-develop',
        'default_calib_config_path': '/home/mion/dev/shelf-analytics/test/calib-configs/venue-11-shelf-1-fps-10.json',
        'default_rois_path': '/home/mion/dev/shelf-analytics/test/rois/v11s1.json',
        'workers': {
            'default': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'default2',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'db_saver': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'db_saver1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'detector': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'detector2',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'downloader': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'downloader1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'event_extractor': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'event_extractor1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'evented_video_maker': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'evented_video_maker1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'frame_splitter': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'frame_splitter1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'recorder': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'recorder1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'tracker': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'tracker1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'transcoder': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'transcoder1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'uploader': {
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'uploader1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
        }
    }
}