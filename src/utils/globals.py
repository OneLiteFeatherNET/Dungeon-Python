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


class Color(Enum):
    """
    Enum for the colors.
    """

    ORANGE = (255, 140, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 100, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)
    YELLOW = (250, 250, 55)
    VIOLET = (148, 0, 211)
    BLUE = (0, 0, 255)


DOOR_COLOR = Color.BLACK

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
MAX_ROOMS: int = 15
# Distance between start and boss room
X_OFFSET = (FLOOR_WIDTH * ROOM_WIDTH) / 2
Y_OFFSET = 0

# Window
WINDOW_MULTIPLIER: float = 2
WINDOW_HEIGHT = FLOOR_HEIGHT * ROOM_HEIGHT * WINDOW_MULTIPLIER
WINDOW_WIDTH = FLOOR_WIDTH * ROOM_WIDTH * WINDOW_MULTIPLIER

LINE_THICKNESS = 5
