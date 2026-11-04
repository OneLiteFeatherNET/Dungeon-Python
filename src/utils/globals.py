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
# Position of the start room, cell 35 in "The Binding of Isaac"
# where the column 0 of the grid is unused
START_ROOM_POSITION = (4, 3)
# A floor is generated again if it has less dead ends than the boss, item and shop room need
REQUIRED_DEAD_ENDS: int = 3
# Upper limit for generating a floor again, the last attempt is always kept
MAX_GENERATION_ATTEMPTS: int = 200
# Chances for a 2 * 2 and a 1 * 2 boss room, otherwise the boss room is a single room
BIG_BOSS_ROOM_CHANCE: float = 0.1
LONG_BOSS_ROOM_CHANCE: float = 0.2
# Number of farthest dead ends that are tried for the boss room before a teleport is used
BOSS_ROOM_CANDIDATES: int = 2
# Distance between start and boss room
X_OFFSET = (FLOOR_WIDTH * ROOM_WIDTH) / 2
Y_OFFSET = 0

# Window
WINDOW_MULTIPLIER: float = 2
WINDOW_HEIGHT = FLOOR_HEIGHT * ROOM_HEIGHT * WINDOW_MULTIPLIER
WINDOW_WIDTH = FLOOR_WIDTH * ROOM_WIDTH * WINDOW_MULTIPLIER

LINE_THICKNESS = 5
