"""
Module for TkinterRoom class.
"""

import tkinter as tk
from rooms.room import Room
from utils import util_functions, globals as my_globals, room_type
from utils.room_type import RoomType


class TkinterRoom(Room):
    """
    Tkinter version of room.
    A room that can be drawn on a tkinter canvas.
    """

    def __init__(
        self,
        x: int,
        y: int,
        room_id: int,
        room_type: RoomType,
        width=my_globals.ROOM_WIDTH,
        height=my_globals.ROOM_HEIGHT,
    ):
        """
        Creates a new room with the given values.
        """
        super().__init__(x, y, room_id, room_type)
        self._width = width
        self._height = height
        self._image = None

    def draw(self, canvas: tk.Canvas):
        """
        Draws the room on the given canvas.
        """
        x0 = self._x * my_globals.ROOM_WIDTH
        y0 = self._y * my_globals.ROOM_HEIGHT
        x1 = x0 + self._width
        y1 = y0 + self._height
        color = room_type.room_colors[self._type].value
        hex_color = util_functions.rgb2hex(color[0], color[1], color[2])
        canvas.create_rectangle((x0, y0), (x1, y1), fill=hex_color)
        center_x = x0 + self._width / 2
        center_y = y0 + self._height / 2
        self._image = util_functions.get_picture_for_room_type(self._type)
        if self._image is not None:
            canvas.create_image(center_x, center_y, image=self._image, anchor="center")

    @classmethod
    def from_room(cls, room: Room):
        """
        Creates a new TkinterRoom from a room.
        """
        return TkinterRoom(
            room._x, room._y, room._id, room._type
        )  # pylint: disable=protected-access
