"""
This file contains the floor class.
A floor is a collection of rooms.
The floor manages the creation of rooms and contains them.
It also provides methods to save and load the floor as a json file
and contains the seed it was created with.
"""

import json
from typing import List, Tuple, Optional

import numpy as np

import utils.util_functions
from utils import globals as my_globals
from utils.globals import DoorFace
from utils.room_type import RoomType
from utils.direction import Direction
from rooms.room import Room
from rooms.teleport_room import TeleportRoom


class Floor:
    """
    Objects of this class are representing floors.
    A floor manges the creation of rooms and contains them.
    """

    def __init__(self, height: int, width: int, seed: str):
        """
        Creates a new floor with the given width and height.
        @param height: height for the floor
        @param width: width for the floor
        """
        self._rooms: List[Room] = []
        self._floor_grid = np.zeros((height, width))
        self._width: int = width
        self._height: int = height
        self._room_id: int = 0
        self.seed: str = seed

    def top_left(self) -> Tuple[int, int]:
        """
        Returns the top left corner of the floor.
        """
        return 0, 0

    def top_right(self) -> Tuple[int, int]:
        """
        Returns the top right corner of the floor.
        """
        return self._width - 1, 0

    def bottom_left(self) -> Tuple[int, int]:
        """
        Returns the bottom left corner of the floor.
        """
        return 0, self._height - 1

    def bottom_right(self) -> Tuple[int, int]:
        """
        Returns the bottom right corner of the floor.
        """
        return self._width - 1, self._height - 1

    def to_dict(self) -> dict:
        """
        Creates a dictionary representation of the floor object.
        @return: dictionary with the seed and the rooms of the floor
        """
        return {
            "_seed": self.seed,
            "_rooms": [room.to_dict() for room in self._rooms],
        }

    def to_json(self, indent: int = 1) -> str:
        """
        Creates a json string for the current floor object.
        @param indent: Number of indentation levels per nesting level
        @return: json string
        """
        return json.dumps(self.to_dict(), indent=len(my_globals.BASE_INDENT) * indent)

    @classmethod
    def from_json(cls, json_string: str):
        """
        Creates a floor object from a json string.
        """
        json_dict = json.loads(json_string)
        floor = Floor(
            json_dict["_height"], json_dict["_width"], json_dict["_floor"]["_seed"]
        )
        for room_dict in json_dict["_floor"]["_rooms"]:
            room = (
                TeleportRoom.from_dict(room_dict)
                if "_connected_room_id" in room_dict
                else Room.from_dict(room_dict)
            )
            floor._rooms.append(room)
            floor.add_to_floor_grid(room[0], room[1])
        floor._room_id = max((room.get_id() for room in floor._rooms), default=-1) + 1
        return floor

    def add_to_floor_grid(self, x: int, y: int) -> None:
        """
        Adds a room to the floor grid at the given location.
        @param x: x coordinate of the room
        @param y: y coordinate of the room
        """
        self._floor_grid[y][x] = 1

    def add_room(
        self, x: int, y: int, room_type: RoomType = RoomType.NORMAL_ROOM
    ) -> None:
        """
        Creates and adds a room to the floor.
        @param x: x coordinate of the room
        @param y: y coordinate of the room
        @param room_type: type of the room (default = normal room)
        """
        self.add_to_floor_grid(x, y)
        self._rooms.append(Room(x=x, y=y, room_type=room_type, room_id=self._room_id))
        self._room_id += 1

    def add_room_next_to(
        self, room: Room, direction: Direction, room_type: RoomType
    ) -> None:
        """
        Creates and adds a room next to a given room.
        @param room: room where the new room is placed next to
        @param direction: direction in which the new room is placed
        @param room_type: type for the room
        """
        x, y = utils.util_functions.add_direction_to_coordinates(
            direction, (room[0], room[1])
        )
        self.add_room(x, y, room_type)

    def add_teleport_room(self, room: Room) -> None:
        """
        Creates and adds a new Teleport room to the floor.
        The new teleport room is placed at the position from the given room.
        @param room: Room which is connected to the teleport room.
        """
        t_room = TeleportRoom(
            x=room[0], y=room[1], room_id=self._room_id, connected_room_id=room.get_id()
        )
        self._rooms.append(t_room)
        self._room_id += 1

    def get_rooms(self) -> List[Room]:
        """
        Returns a list containing all the rooms of the floor.
        @return: rooms
        """
        return self._rooms

    def get_floor_grid(self) -> np.ndarray:
        """
        Returns the floor grid of the floor.
        @return: floor grid
        """
        return self._floor_grid

    def contains_room(self, coordinates: Tuple[int, int]) -> bool:
        """
        Checks if there is a room at the given coordinates.
        @param coordinates: coordinates to check
        @return: true if a there is a room otherwise false
        """
        return self._floor_grid[coordinates[1]][coordinates[0]] == 1

    def add_doors_to_rooms(self) -> None:
        """
        Adds doors to all rooms on the floor.
        """
        for room in self._rooms:
            x = room[0]
            y = room[1]
            if x + 1 < len(self._floor_grid[y]) and self._floor_grid[y][x + 1] == 1:
                room.add_door(DoorFace.EAST)
            if x - 1 >= 0 and self._floor_grid[y][x - 1] == 1:
                room.add_door(DoorFace.WEST)
            if y - 1 >= 0 and self._floor_grid[y - 1][x] == 1:
                room.add_door(DoorFace.TOP)
            if y + 1 < len(self._floor_grid) and self._floor_grid[y + 1][x] == 1:
                room.add_door(DoorFace.BOTTOM)

    def count_neighbours(self, x: int, y: int) -> int:
        """
        Counts how many rooms are next to the room.
        @param x: x coordinate  of the room
        @param y: y coordinate of the room
        @return: number of neighbour rooms
        """
        neighbours = 0
        if y + 1 < len(self._floor_grid):
            neighbours += self._floor_grid[y + 1][x]
        if y - 1 >= 0:
            neighbours += self._floor_grid[y - 1][x]
        if x + 1 < len(self._floor_grid[y]):
            neighbours += self._floor_grid[y][x + 1]
        if x - 1 >= 0:
            neighbours += self._floor_grid[y][x - 1]
        return neighbours

    def is_dead_end(self, x: int, y: int) -> bool:
        """
        Returns if the room at the given coordinates is a dead end.
        @param x: x coordinate
        @param y: y coordinate
        @return: true if the room is a dead end otherwise false
        """
        return self.count_neighbours(x, y) == 1

    def has_no_neighbours(self, coordinates: Tuple[int, int]) -> bool:
        """
        Checks if they are zero neighbours at the given location.
        @param coordinates: coordinates to check
        @return: True if the location has zero neighbours otherwise False
        """
        return self.count_neighbours(coordinates[0], coordinates[1]) == 0

    def is_within_border(self, coordinates: Tuple[int, int]) -> bool:
        """
        Checks if the given coordinates are within the floor.
        @param coordinates: coordinates to check
        @return: True if the coordinates are within the floor otherwise False
        """
        return 0 <= coordinates[0] < self._width and 0 <= coordinates[1] < self._height

    def _get_room(self, coordinates: Tuple[int, int]) -> Optional[Room]:
        """
        Returns the room at the given coordinates.
        @param coordinates: coordinates of the room
        @return: room
        """
        for room in self._rooms:
            if room[0] == coordinates[0] and room[1] == coordinates[1]:
                return room
        return None

    def has_boss_room_as_neighbour(self, coordinates: Tuple[int, int]) -> bool:
        """
        Checks if the given coordinates have a boss room as neighbour.
        @param coordinates: coordinates to check
        @return: True if the coordinates have a boss room as neighbour otherwise False
        """
        for direction in Direction.main_directions():
            new_coordinates = utils.util_functions.add_direction_to_coordinates(
                direction, coordinates
            )
            if self.is_within_border(new_coordinates) and self.contains_room(
                new_coordinates
            ):
                room = self._get_room(new_coordinates)
                if room is not None and room.get_type() == RoomType.BOSS_ROOM:
                    return True
        return False

    def has_special_room_as_neighbour(self, coordinates: Tuple[int, int]) -> bool:
        """
        Checks if the given coordinates have a special room as neighbour.
        Special rooms are rooms that have a special function.
        Special rooms are:
        - Item room
        - Shop room
        - Boss room
        - Secret room
        @param coordinates: coordinates to check
        @return: True if the coordinates have a special room as neighbour otherwise False
        """
        for direction in Direction.main_directions():
            new_coordinates = utils.util_functions.add_direction_to_coordinates(
                direction, coordinates
            )
            if self.is_within_border(new_coordinates) and self.contains_room(
                new_coordinates
            ):
                room = self._get_room(new_coordinates)
                if room is not None and room.get_type().is_special():
                    return True
        return False

    def get_boss_room(self) -> Optional[Room]:
        """
        Returns the boss room of the floor.
        @return: boss room
        """
        for room in self._rooms:
            if room.get_type() == RoomType.BOSS_ROOM:
                return room
        return None
