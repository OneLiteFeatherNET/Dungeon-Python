"""
This module contains the function to display the legend on the canvas.
"""

import tkinter as tk

import utils.globals as my_globals
from utils import util_functions
from utils.room_type import RoomType, room_colors, room_names


def display_legend():
    """
    Displays the legend on the canvas.
    """
    legend_window = tk.Toplevel()
    legend_window.title("Room Type Legend")
    legend_canvas = tk.Canvas(legend_window)
    legend_canvas.pack()
    y_offset = 10
    room_type: RoomType
    for room_type in RoomType.get_all():
        color: my_globals.Color = room_colors[room_type]
        legend_canvas.create_rectangle(
            10, y_offset, 30, y_offset + 20, fill=util_functions.rgb2hex(*color.value)
        )
        legend_canvas.create_text(
            40, y_offset + 10, anchor=tk.W, text=room_names[room_type]
        )
        y_offset += 30
