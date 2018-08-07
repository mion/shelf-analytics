import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'shan'))

# from worker import Worker

class Worker:
    def __init__(self, name):
        self.name = name
    
    def process(self, job):
        return False

class Recorder:
    def __init__(self):
        super().__init__('recorder')
    
    def process(self, job):
        return "Recording..."
