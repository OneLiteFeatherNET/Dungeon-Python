"""
This module contains the function to display the legend of the room types.
"""

import tkinter as tk

from rooms.tkinter import style
from rooms.tkinter.tkinter_room import TkinterRoom
from utils.room_type import RoomType, room_names

_ROW_HEIGHT = 44


def display_legend():
    """
    Displays the legend of the room types in a new window.
    """
    palette = style.get_palette()
    legend_window = tk.Toplevel(background=palette.window)
    legend_window.title("Room Type Legend")
    legend_window.resizable(False, False)
    room_types = RoomType.get_all()
    legend_canvas = tk.Canvas(
        legend_window,
        width=260,
        height=len(room_types) * _ROW_HEIGHT + 16,
        background=palette.window,
        highlightthickness=0,
    )
    legend_canvas.pack(padx=8, pady=8)
    # Keep references to the room icons, otherwise tkinter discards them
    legend_canvas.rooms = []  # type: ignore[attr-defined]
    for index, room_type in enumerate(room_types):
        room = TkinterRoom(0, 0, index, room_type, width=72, height=_ROW_HEIGHT)
        legend_canvas.rooms.append(room)  # type: ignore[attr-defined]
        _draw_at(legend_canvas, room, 8, 8 + index * _ROW_HEIGHT)
        legend_canvas.create_text(
            92,
            8 + index * _ROW_HEIGHT + _ROW_HEIGHT / 2,
            anchor=tk.W,
            text=room_names[room_type],
            fill=palette.text,
            font=("DejaVu Sans", 10),
        )


def _draw_at(canvas: tk.Canvas, room: TkinterRoom, x: int, y: int) -> str:
    """
    Draws the room on the canvas and moves it to the given position.
    @return: tag of the drawn items
    """
    tag = f"legend-{room.get_id()}"
    before = set(canvas.find_all())
    room.draw(canvas)
    for item in set(canvas.find_all()) - before:
        canvas.addtag_withtag(tag, item)
    canvas.move(tag, x, y)
    return tag
