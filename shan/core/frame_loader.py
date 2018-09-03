#
# NOTE: I implemented this but didn't test it.
#       It is intended to speed up the frame loading time in the track 
#       inspection tool.
#
import skimage.io
import os

class FrameLoader:
    def __init__(self, images_path):
        self.images_path = images_path
        self._frames_count = 0 # cache
    
    def frames_count(self):
        if self._frames_count is None:
            image_filenames = next(os.walk(self.images_path))[2]
            self._frames_count = len(image_filenames)
        return self._frames_count

    def get_frame_at(self, index):
        image_filenames = next(os.walk(self.images_path))[2]
        if self._frames_count is None:
            self._frames_count = len(image_filenames)
        file_path = image_filenames[index]
        return skimage.io.imread(file_path)
