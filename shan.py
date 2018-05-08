#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Main Shelf Analytics script."""
import os
import argparse
import json

from colorize import red, green, yellow, header


def load_json(path):
    with open(path, "r") as tags_file:
      return json.loads(tags_file.read())


if __name__ == '__main__':
    print("Hello")