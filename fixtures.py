import math
iaot_signals = [
    ('smooth peak in the middle', 15, [math.pow(i, 3) for i in range(15)] + [math.pow(15 - i, 3) for i in range(15)], (100, 1)),
    ('accute peak in the middle', 5, [0, 1, 2, 30, 400, 5000, 600, 70, 8, 9, 10], (100, 1)),
    ('accute peak on the left', 2, [0, 100, 2000, 300, 40, 5, 0, 0], (100, 1)),
    ('accute peak on the right', 5, [0, 10, 20, 30, 400, 5000, 600, 70], (100, 1)),
    ('linear increasing sequence', None, [2*i for i in range(20)], (100, 1)),
    ('decreasing linear sequence', None, [2*i for i in range(20)], (100, 1)),
    ('increasing exp sequence', None, [math.pow(i, 3) for i in range(20)], (100, 1)),
    ('decreasing exp sequence', None, [math.pow(20 - i, 3) for i in range(20)], (100, 1)),
    ('mostly flat sequence', None, [10, 12, 9, 11, 10, 5, 10, 12, 8, 11], (100, 1))
]
