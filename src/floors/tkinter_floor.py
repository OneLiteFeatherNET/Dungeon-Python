"""
Module for the TkinterFloor class.
"""

from typing import List, Optional, cast

from floors.floor import Floor
from rooms.room import Room
from rooms.teleport_room import TeleportRoom

from rooms.tkinter import style
from rooms.tkinter.tkinter_room import TkinterRoom
from rooms.tkinter.tkinter_teleport_room import TkinterTeleportRoom
from utils import globals as my_globals
from utils.room_type import RoomType


class TkinterFloor(Floor):
    """
    A tkinter version of the floor.
    This version is used to draw the floor and the rooms on a canvas.
    """

    def __init__(self, height: int, width: int, canvas, name: str, seed: str):
        """
        Creates a new floor width the given width and height.
        @param height: height of the floor
        @param width: width of the floor
        """
        super().__init__(height, width, seed)
        self._canvas = canvas
        self.name = name
        self._after_id: Optional[str] = None

    def add_room(self, x: int, y: int, room_type=RoomType.NORMAL_ROOM):
        self.add_to_floor_grid(x, y)
        self._rooms.append(
            TkinterRoom(x=x, y=y, room_type=room_type, room_id=self._room_id)
        )
        self._room_id += 1

    def add_teleport_room(self, room: Room) -> None:
        t_room = TkinterTeleportRoom(
            x=room[0], y=room[1], room_id=self._room_id, teleport_room_id=room.get_id()
        )
        self._rooms.append(t_room)
        self._room_id += 1

    @classmethod
    def from_floor(cls, floor: Floor, canvas, name: str):
        """
        Creates a new TkinterFloor from a floor.
        @param canvas: Canvas to draw on
        @param floor: floor to copy
        @param name: name of the floor
        @return: new TkinterFloor
        """
        # pylint: disable=protected-access
        tkinter_floor = TkinterFloor(
            floor._height,
            floor._width,
            canvas,
            name,
            floor.seed,
        )
        tkinter_floor.floor_id = floor.floor_id
        for room in floor.get_rooms():
            tkinter_room: TkinterRoom
            if isinstance(room, TeleportRoom):
                tkinter_room = TkinterTeleportRoom(
                    room[0], room[1], room.get_id(), room.get_connected_room_id()
                )
                for door in room.get_doors():
                    tkinter_room.add_door(door)
            else:
                tkinter_room = TkinterRoom.from_room(room)
            tkinter_floor._rooms.append(tkinter_room)
        tkinter_floor._floor_grid = floor.get_floor_grid().copy()
        tkinter_floor._room_id = floor._room_id
        return tkinter_floor

    def _tkinter_rooms(self) -> List[TkinterRoom]:
        """
        Returns the rooms of the floor, which are all tkinter rooms.
        @return: rooms
        """
        return cast(List[TkinterRoom], self._rooms)

    def draw(self) -> None:
        """
        Draws the floor with all the rooms on the canvas.
        """
        self.stop_drawing()
        self._draw_background()
        for room in self._tkinter_rooms():
            room.draw(self._canvas)
        self._draw_teleport_links()

    def _draw_background(self) -> None:
        """
        Clears the canvas and draws the empty cells of the floor.
        """
        palette = style.get_palette()
        self._canvas.delete("all")
        self._canvas.configure(background=palette.canvas)
        for x in range(self._width):
            for y in range(self._height):
                x0 = x * my_globals.ROOM_WIDTH + style.ROOM_PADDING_X
                y0 = y * my_globals.ROOM_HEIGHT + style.ROOM_PADDING_Y
                self._canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + my_globals.ROOM_WIDTH - 2 * style.ROOM_PADDING_X,
                    y0 + my_globals.ROOM_HEIGHT - 2 * style.ROOM_PADDING_Y,
                    outline=palette.grid,
                    width=1,
                    tags=("grid",),
                )

    def _draw_teleport_links(self) -> None:
        """
        Draws a dashed line from every teleport room to its connected room.
        """
        rooms_by_id = {room.get_id(): room for room in self._rooms}
        for room in self._rooms:
            if not isinstance(room, TeleportRoom):
                continue
            target = rooms_by_id.get(room.get_connected_room_id())
            if target is None:
                continue
            start = self._cell_center(room)
            end = self._cell_center(target)
            self._canvas.create_line(
                *self._room_edge(start, end),
                *self._room_edge(end, start),
                fill=style.get_palette().teleport_link,
                width=2,
                dash=(6, 4),
                arrow="last",
                arrowshape=(10, 12, 5),
                tags=("link",),
            )

    @staticmethod
    def _room_edge(center, towards):
        """
        Returns the point where a line from the center of a room
        towards another point leaves the room.
        """
        delta_x = towards[0] - center[0]
        delta_y = towards[1] - center[1]
        half_width = my_globals.ROOM_WIDTH / 2 - style.ROOM_PADDING_X
        half_height = my_globals.ROOM_HEIGHT / 2 - style.ROOM_PADDING_Y
        scale = min(
            half_width / abs(delta_x) if delta_x else float("inf"),
            half_height / abs(delta_y) if delta_y else float("inf"),
        )
        return center[0] + delta_x * scale, center[1] + delta_y * scale

    @staticmethod
    def _cell_center(room: Room):
        return (
            room[0] * my_globals.ROOM_WIDTH + my_globals.ROOM_WIDTH / 2,
            room[1] * my_globals.ROOM_HEIGHT + my_globals.ROOM_HEIGHT / 2,
        )

    def stop_drawing(self) -> None:
        """
        Stops the step by step drawing of the floor.
        """
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None

    def draw_step_by_step(self, delay_ms: int = 500) -> None:
        """
        Draws the floor step by step using the tkinter event loop,
        starting with the start room and spreading through the doors.
        @param delay_ms: delay between two steps in milliseconds
        """
        self.stop_drawing()
        self._draw_background()
        rings = cast(List[List[TkinterRoom]], self.rooms_by_distance())
        self._draw_next_ring(rings, delay_ms)

    def _draw_next_ring(self, rings: List[List[TkinterRoom]], delay_ms: int) -> None:
        """
        Draws the first of the given rings of rooms and schedules the remaining rings.
        @param rings: rings of rooms that still have to be drawn
        @param delay_ms: delay between two rings in milliseconds
        """
        self._after_id = None
        if len(rings) == 0:
            self._draw_teleport_links()
            return
        for room in rings[0]:
            room.draw(self._canvas)
        self._after_id = self._canvas.after(
            delay_ms, self._draw_next_ring, rings[1:], delay_ms
        )
