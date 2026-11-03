"""
This module contains the legend that explains the room types.
"""

import tkinter as tk
from collections import Counter
from tkinter import ttk
from typing import List

from floors.floor import Floor
from rooms.tkinter import style
from rooms.tkinter.tkinter_room import TkinterRoom
from utils.room_type import RoomType, room_names

_ROW_HEIGHT = 44
_WIDTH = 230


class LegendPanel(ttk.Frame):
    """
    Panel next to the floor that shows the room types
    and how often they appear on the current floor.
    """

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        ttk.Label(self, text="Legend", font=("DejaVu Sans", 11, "bold")).pack(
            anchor=tk.W, pady=(0, 4)
        )
        self._canvas = tk.Canvas(
            self,
            width=_WIDTH,
            height=len(RoomType.get_all()) * _ROW_HEIGHT,
            highlightthickness=0,
        )
        self._canvas.pack()
        # Keep references to the drawn rooms, otherwise tkinter discards their icons
        self._rooms: List[TkinterRoom] = []
        self._counts: Counter = Counter()
        self.redraw()

    def update_counts(self, floor: Floor) -> None:
        """
        Counts the room types of the given floor and shows them in the legend.
        @param floor: floor to count the rooms of
        """
        self._counts = Counter(room.get_type() for room in floor.get_rooms())
        self.redraw()

    def get_count(self, room_type: RoomType) -> int:
        """
        Returns how often the room type appears on the current floor.
        """
        return self._counts[room_type]

    def redraw(self) -> None:
        """
        Draws the legend in the colors of the current theme.
        """
        palette = style.get_palette()
        canvas = self._canvas
        canvas.delete("all")
        canvas.configure(background=palette.panel)
        self._rooms = []
        for index, room_type in enumerate(RoomType.get_all()):
            top = index * _ROW_HEIGHT
            room = TkinterRoom(0, 0, index, room_type, width=72, height=_ROW_HEIGHT)
            self._rooms.append(room)
            _draw_at(canvas, room, 0, top)
            canvas.create_text(
                84,
                top + _ROW_HEIGHT / 2,
                anchor=tk.W,
                text=room_names[room_type],
                fill=palette.text,
                font=("DejaVu Sans", 10),
            )
            canvas.create_text(
                _WIDTH - 4,
                top + _ROW_HEIGHT / 2,
                anchor=tk.E,
                text=str(self._counts[room_type]),
                fill=palette.muted_text,
                font=("DejaVu Sans", 10),
                tags=("count",),
            )


def _draw_at(canvas: tk.Canvas, room: TkinterRoom, x: int, y: int) -> None:
    """
    Draws the room on the canvas and moves it to the given position.
    """
    tag = f"legend-{room.get_id()}"
    before = set(canvas.find_all())
    room.draw(canvas)
    for item in set(canvas.find_all()) - before:
        canvas.addtag_withtag(tag, item)
    canvas.move(tag, x, y)
