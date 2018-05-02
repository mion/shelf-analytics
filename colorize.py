#  Copyright 2018 Toneto Labs. All Rights Reserved.
#
"""Toneto terminal colors helper module."""


class Colors: # from Blender build script
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def header(string):
    return Colors.HEADER + string + Colors.ENDC


def yellow(string):
    return Colors.WARNING + string + Colors.ENDC


def red(string):
    return Colors.FAIL + string + Colors.ENDC


def green(string):
    return Colors.OKGREEN + string + Colors.ENDC

