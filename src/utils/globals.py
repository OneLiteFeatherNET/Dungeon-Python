"""
This file contains all the global constants used in the project.
"""

import os
from enum import Enum


class DoorFace(Enum):
    """
    Enum for the door faces.
    """

    @classmethod
    def list(cls):
        """
        Returns a list of all the door faces.
        """
        return list(map(lambda c: c.value, cls))

    TOP = 0
    EAST = 1
    BOTTOM = 2
    WEST = 3


# Room constants
MAX_DOOR_AMOUNT: int = 4
ROOM_WIDTH: int = 120
ROOM_HEIGHT: int = 60

# Json
BASE_INDENT = "  "
JSON_SUFFIX = ".json"
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APPLICATION_PATH = os.path.dirname(os.path.dirname(_CURRENT_DIR))
DEFAULT_FLOOR_NAME = "floor"
DEFAULT_FLOOR_DIRECTORY = "generation"

# Floor
# Width and height in number of rooms
FLOOR_WIDTH: int = 9
FLOOR_HEIGHT: int = 8
MAX_ROOMS: int = 20
# The super secret room is only placed closer than this to the boss room
# (squared distance, 25 means a distance below 5 rooms)
MAX_SUPER_SECRET_ROOM_DISTANCE_SQUARED: int = 25
# Distance between start and boss room
X_OFFSET = (FLOOR_WIDTH * ROOM_WIDTH) / 2
Y_OFFSET = 0

# Window
WINDOW_MULTIPLIER: float = 2
WINDOW_HEIGHT = FLOOR_HEIGHT * ROOM_HEIGHT * WINDOW_MULTIPLIER
WINDOW_WIDTH = FLOOR_WIDTH * ROOM_WIDTH * WINDOW_MULTIPLIER

LINE_THICKNESS = 5
