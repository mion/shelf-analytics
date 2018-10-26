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
        self.x += p.x 
        self.y += p.y
