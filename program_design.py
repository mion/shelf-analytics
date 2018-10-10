"""
This module is a blueprint for the design of the full program.
"""

###############################################################################
# Data definitions
###############################################################################
class CalibrationParameters(dict):
    """
    The tracking algorithm needs some arbitrary values to function (eg.: how
    small can the bounding box of a detected object be so it is still
    considered a human being). This class is simply a dictionary containing
    such values.
    """
    pass

###############################################################################
# Function wishlist
###############################################################################

