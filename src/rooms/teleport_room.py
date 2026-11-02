"""
Teleport room module.
"""

from rooms.room import Room
from utils.room_type import RoomType


class TeleportRoom(Room):
    """
    Teleport room class.
    This class represents a room that is connected to another room.
    A player can teleport from this room to the connected room.
    The room is represented by its coordinates, type and connected room id.
    """

    def __init__(self, x: int, y: int, room_id: int, connected_room_id: int):
        """
        Creates a new teleport room with the given values.
        @param x: x position for the room
        @param y: y position of the room
        @param room_id:
        @param connected_room_id: id of the room the teleport room is connected to
        """
        super().__init__(x, y, room_id, RoomType.TELEPORT_ROOM)
        self._connected_room = connected_room_id

    def get_connected_room_id(self) -> int:
        """
        Returns the id of the room the teleport room is connected to.
        @return: room id
        """
        return self._connected_room
