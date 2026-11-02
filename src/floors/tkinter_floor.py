"""
Module for the TkinterFloor class.
"""

import threading
import time
from typing import List, cast

from floors.floor import Floor
from rooms.room import Room
from rooms.teleport_room import TeleportRoom

from rooms.tkinter.tkinter_room import TkinterRoom
from rooms.tkinter.tkinter_teleport_room import TkinterTeleportRoom
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
        self._first_draw = True
        self.name = name
        self._is_drawing = False

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
        self._canvas.delete("all")
        for room in self._tkinter_rooms():
            room.draw(self._canvas)

    def draw_thread(self) -> None:
        """
        Starts a new thread to draw the floor step by step.
        """
        thread = threading.Thread(target=self.draw_step_by_step)
        thread.start()

    def stop_drawing(self) -> None:
        """
        Stops the drawing of the floor.
        """
        self._is_drawing = False

    def draw_step_by_step(self) -> None:
        """
        Draws the floor step by step.
        """
        self._canvas.delete("all")
        sorted_rooms = sorted(self._tkinter_rooms(), key=lambda r: r.get_id())
        self._is_drawing = True
        for room in sorted_rooms:
            if not self._is_drawing:
                sorted_rooms.clear()
                return
            room.draw(self._canvas)
            time.sleep(0.5)
