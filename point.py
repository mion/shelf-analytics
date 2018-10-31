from math import sqrt

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "({:d},{:d})".format(self.x, self.y)

    def __repr__(self):
        return "<Point ({:d},{:d})>".format(self.x, self.y)

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

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

    def multiply(self, k):
        return Point(self.x * k, self.y * k)

    def normalized_direction(self, p):
        direction = self.subtract(p)
        return direction.normalize()
