import json
import os

import skimage.io
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import tnt

def main():
  _, ax = plt.subplots(1, figsize=(16, 16))

  image = skimage.io.imread("/Users/gvieira/Pictures/c3po.jpg")

  # Remove white margin:
  # https://stackoverflow.com/a/27227718
  ax.set_axis_off()
  ax.set_title("")
  plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
  plt.margins(0, 0)
  ax.get_xaxis().set_major_locator(plt.NullLocator())
  ax.get_yaxis().set_major_locator(plt.NullLocator())

  x1, y1, x2, y2 = [10, 10, 50, 75]

  p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                        alpha=0.7, linestyle="dashed",
                        edgecolor=(1.0, 0.0, 0.0), facecolor='none')
  ax.add_patch(p)

  ax.imshow(image)
  plt.savefig("foobar.jpg", bbox_inches="tight", pad_inches=0.0)

if __name__ == '__main__':
  main()