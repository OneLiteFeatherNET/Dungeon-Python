"""
This module contains utility functions for the floor generator.
"""

import os
import random
import math
from typing import Tuple

import utils.globals as my_globals
from utils.direction import Direction
from utils.room_type import RoomType


def get_picture_for_room_type(room_type: RoomType):
    """
    Gets the picture for the given room type.
    @param room_type: room type to get the picture for
    @return: picture for the given room type
    """
    from PIL import Image, ImageTk

    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to the project root directory
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # Define the relative path to the image file
    image_file = f"{room_type.name.lower()}.png"
    # Join the project root directory with the relative path to get the absolute path
    image_path = os.path.join(project_root, "resources", "room_icons", image_file)
    try:
        return ImageTk.PhotoImage(Image.open(image_path).resize((32, 32)))
    except FileNotFoundError:
        return None


def calculate_room_amount(stage_id: int, rng: random.Random) -> int:
    """
    Calculates the room amount.
    @param stage_id: id for the floor
    @param rng: random number generator to use
    :return: room amount
    """
    return min(
        my_globals.MAX_ROOMS,
        int(rng.randint(0, 1) + 5 + math.floor(stage_id * 10) / 3.0),
    )


def place_room(rng: random.Random) -> bool:
    """
    Checks if a new room should be placed.
    @param rng: random number generator to use
    :return: True when room should be placed otherwise False
    """
    return rng.randint(1, 50) >= 25


def rgb2hex(r, g, b):
    """
    Converts rgb to hex.
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def add_direction_to_coordinates(
    direction: Direction, coordinates: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Calculates the room according to the given room and direction
    @param direction: direction for the room to calculate
    @param coordinates: start point for the calculation
    @return: calculated point
    """
    delta_x, delta_y = direction.value
    return coordinates[0] + delta_x, coordinates[1] + delta_y


json_file_options: dict = {
    "defaultextension": my_globals.JSON_SUFFIX,
    "filetypes": [("Json", my_globals.JSON_SUFFIX)],
}

open_file_text: str = "Open File"
save_file_text: str = "Save File"

window_title: str = "Floor Generator"
window_size: str = "1200x550"


def calculate_distance(cord1, cord2) -> int:
    """
    Calculates the distance between two points.
    """
    return (cord1[0] - cord2[0]) * (cord1[0] - cord2[0]) + (cord1[1] - cord2[1]) * (
        cord1[1] - cord2[1]
    )
