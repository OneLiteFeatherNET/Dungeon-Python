"""
Module for TkinterRoom class.
"""

import tkinter as tk
from typing import List

from rooms.room import Room
from rooms.tkinter import style
from utils import util_functions, globals as my_globals
from utils.globals import DoorFace
from utils.room_type import RoomType

_SECRET_ROOMS = (RoomType.SECRET_ROOM, RoomType.SUPER_SECRET_ROOM)


def _rounded_rectangle(x0, y0, x1, y1, radius) -> List[float]:
    """
    Returns the points of a rectangle with rounded corners
    for a smoothed canvas polygon.
    """
    return [
        x0 + radius, y0, x1 - radius, y0, x1, y0, x1, y0 + radius,
        x1, y1 - radius, x1, y1, x1 - radius, y1, x0 + radius, y1,
        x0, y1, x0, y1 - radius, x0, y0 + radius, x0, y0,
    ]  # fmt: skip


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
        Draws the room with its doors on the given canvas.
        """
        palette = style.get_palette()
        cell_x0 = self._x * my_globals.ROOM_WIDTH
        cell_y0 = self._y * my_globals.ROOM_HEIGHT
        x0 = cell_x0 + style.ROOM_PADDING_X
        y0 = cell_y0 + style.ROOM_PADDING_Y
        x1 = cell_x0 + self._width - style.ROOM_PADDING_X
        y1 = cell_y0 + self._height - style.ROOM_PADDING_Y
        center_x = cell_x0 + self._width / 2
        center_y = cell_y0 + self._height / 2

        self._draw_doors(canvas, cell_x0, cell_y0, (x0, y0, x1, y1))
        canvas.create_polygon(
            _rounded_rectangle(x0, y0, x1, y1, style.ROOM_CORNER_RADIUS),
            smooth=True,
            fill=palette.rooms[self._type],
            outline=palette.room_outline,
            width=2,
            dash=(4, 3) if self._type in _SECRET_ROOMS else (),
            tags=("room",),
        )
        if self._type == RoomType.TELEPORT_ROOM:
            for radius, width in ((14, 3), (7, 2)):
                canvas.create_oval(
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                    outline=palette.canvas,
                    width=width,
                    tags=("icon",),
                )
            return
        self._image = util_functions.get_picture_for_room_type(self._type)
        if self._image is not None:
            canvas.create_image(
                center_x, center_y, image=self._image, anchor="center", tags=("icon",)
            )

    def _draw_doors(self, canvas: tk.Canvas, cell_x0, cell_y0, room) -> None:
        """
        Draws a connector from the room to the border of its cell for every door.
        """
        x0, y0, x1, y1 = room
        cell_x1 = cell_x0 + self._width
        cell_y1 = cell_y0 + self._height
        center_x = cell_x0 + self._width / 2
        center_y = cell_y0 + self._height / 2
        half = style.DOOR_WIDTH / 2
        connectors = {
            DoorFace.TOP: (center_x - half, cell_y0, center_x + half, y0 + 2),
            DoorFace.BOTTOM: (center_x - half, y1 - 2, center_x + half, cell_y1),
            DoorFace.WEST: (cell_x0, center_y - half, x0 + 2, center_y + half),
            DoorFace.EAST: (x1 - 2, center_y - half, cell_x1, center_y + half),
        }
        for door in self._doors:
            canvas.create_rectangle(
                *connectors[door],
                fill=style.get_palette().door,
                width=0,
                tags=("door",),
            )

    @classmethod
    def from_room(cls, room: Room):
        """
        Creates a new TkinterRoom from a room.
        """
        tkinter_room = TkinterRoom(room[0], room[1], room.get_id(), room.get_type())
        for door in room.get_doors():
            tkinter_room.add_door(door)
        return tkinter_room
