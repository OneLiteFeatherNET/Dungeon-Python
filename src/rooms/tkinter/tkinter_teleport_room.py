"""
Module for the TkinterTeleportRoom class.
"""

from utils import globals as my_globals
from rooms.teleport_room import TeleportRoom
from rooms.tkinter.tkinter_room import TkinterRoom


class TkinterTeleportRoom(TeleportRoom, TkinterRoom):
    """
    Tkinter version of teleport room.
    """

    def __init__(
        self,
        x: int,
        y: int,
        room_id: int,
        teleport_room_id: int,
        width=my_globals.ROOM_WIDTH,
        height=my_globals.ROOM_HEIGHT,
    ):
        """
        Creates a new teleport room with the given values.
        @param teleport_room_id: id of the room the teleport room is connected to
        """
        super().__init__(x, y, room_id, teleport_room_id)
        self._width = width
        self._height = height
