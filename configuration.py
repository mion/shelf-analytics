DEV_QUEUE_HOST = 'localhost'

configuration = {
    'dev': {
        'API_base_url': 'http://localhost:8000/shancms',
        'workspace_path': '/Users/gvieira/shan-develop',
        's3_bucket': 'shan-develop',
        'default_calib_config_path': '/Users/gvieira/code/toneto/shan/test/calib-configs/venue-11-shelf-1-fps-10.json',
        'default_rois_path': '/Users/gvieira/code/toneto/shan/test/rois/v11s1.json',
        'workers': {
            'default': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'default2',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'db_saver': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'db_saver1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'detector': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'detector2',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'downloader': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'downloader1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'event_extractor': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'event_extractor1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'evented_video_maker': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'evented_video_maker1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'frame_splitter': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'frame_splitter1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'recorder': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'recorder1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'tracker': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'tracker1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'transcoder': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'transcoder1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
            'uploader': {
                'USER': 'admin',
                'PASSWORD': 'shan',
                'QUEUE_HOST': DEV_QUEUE_HOST,
                'QUEUE_NAME': 'uploader1',
                'QUEUE_DURABLE': True,
                'QUEUE_PREFETCH_COUNT': 1, # do not give more than one message to a worker at a time
                'DELIVERY_MODE': 2 # make message persistent, for stronger guarantee of persistance see: https://www.rabbitmq.com/confirms.html
            },
        }
    }
}