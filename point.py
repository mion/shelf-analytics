from math import sqrt

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, p):
        dx = p.x - self.x
        dy = p.y - self.y
        return sqrt((dx * dx) + (dy * dy))

    def copy(self):
        return Point(self.x, self.y)

    def add(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def normalize(self):
        length = self.distance_to(Point(0, 0))
        return Point(self.x / length, self.y / length)

    def subtract(self, p):
        return Point(p.x - self.x, p.y - self.y)

    def normalized_direction(self, p):
        direction = self.subtract(p)
        return direction.normalize()
