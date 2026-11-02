"""
This file contains the Room class.
The Room class is used to represent a room in the floor.
A room has a type, coordinates and doors.
"""

import json
from typing import List

from utils import globals as my_globals
from utils.globals import DoorFace, MAX_DOOR_AMOUNT
from utils.room_type import RoomType


class Room:
    """
    A room in the floor.
    A is represented by its coordinates, type and doors.
    """

    def __init__(self, x: int, y: int, room_id: int, room_type: RoomType):
        """
        Creates a new room with the given values.
        @param x: x coordinate of the room
        @param y: y coordinate of the room
        @param room_id: id of the room
        @param room_type: type of the room
        """
        self._x: int = x
        self._y: int = y
        self._id: int = room_id
        self._type = room_type
        self._doors: List[DoorFace] = []

    def __getitem__(self, index: int) -> int:
        """
        Provides an easier method to access the x and y coordinate of the room.
        If the index is not 0 or 1 the method raises an exception.
        @param index: 0 for x 1 for y
        @return: Returns x if index equals 0 and y if index equals 1
        """
        if index < 0 or index > 1:
            raise ValueError(str(index) + "is not a valid index")
        if index == 0:
            return self._x
        return self._y

    def to_dict(self) -> dict:
        """
        Creates a dictionary representation of the room object.
        @return: dictionary with the values of the room
        """
        return {
            "_doors": [door.value for door in self._doors],
            "_id": self._id,
            "_type": self._type.value,
            "_x": self._x,
            "_y": self._y,
        }

    def to_json(self, indent: int = 1) -> str:
        """
        Creates a json representation of the room object.
        @param indent: Number of indentation levels per nesting level
        @return: json string
        """
        return json.dumps(self.to_dict(), indent=len(my_globals.BASE_INDENT) * indent)

    @classmethod
    def from_dict(cls, json_dict: dict):
        """
        Creates a room object from a dictionary.
        """
        room = Room(
            json_dict["_x"],
            json_dict["_y"],
            json_dict["_id"],
            RoomType(json_dict["_type"]),
        )
        for door in json_dict["_doors"]:
            room._doors.append(DoorFace(door))
        return room

    def set_type(self, room_type: RoomType) -> None:
        """
        Sets the type of the room.
        @param room_type: type for the room
        """
        self._type = room_type

    def get_type(self) -> RoomType:
        """
        Returns the type of the room.
        @return: type
        """
        return self._type

    def get_id(self) -> int:
        """
        Returns the id of a room.
        @return: id
        """
        return self._id

    def set_cord(self, x: int, y: int) -> None:
        """
        Sets the coordinates of a room.
        @param x: new x coordinate
        @param y: new y coordinate
        """
        self._x = x
        self._y = y

    def get_doors(self) -> list:
        """
        Returns a list of all doors
        @return: list of doors
        """
        return self._doors

    def add_door(self, door_face: DoorFace) -> None:
        """
        Adds a door at the given location to the room.
        @param door_face: position to place the door
        """
        if len(self._doors) < MAX_DOOR_AMOUNT:
            self._doors.append(door_face)

    def __eq__(self, other) -> bool:
        """
        Compares two rooms which each other.
        Two rooms are equal if they are at the same coordinates and have the same type.
        @param other: Other object to compare
        @return: True if other is a room and they are equal otherwise false.
        """
        if isinstance(other, Room) is False:
            return False
        other_room: Room = other
        return (
            self._x == other_room._x
            and self._y == other_room._y
            and self._type == other_room._type
        )

    def __str__(self) -> str:
        """
        Returns a string representation of a room object.
        @return: String representation
        """
        return self.to_json()
