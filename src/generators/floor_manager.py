"""
Module for managing the floors of the tkinter generator.
"""

import secrets
import tkinter as tk
from collections import deque
from typing import Deque

from utils import globals as my_globals

from floors.tkinter_floor import TkinterFloor


class FloorManager:
    """
    Class to manage the floors of the tkinter generator.
    """

    def __init__(self, output_file_name: str) -> None:
        """
        Creates a new floor manager.
        @param output_file_name: name of the output file
        """
        self._floors: Deque[TkinterFloor] = deque()
        self.current_floor_index = -1
        self.current_floor_name = tk.StringVar()
        self.current_floor_name.set(output_file_name)
        self.current_floor_seed_var = tk.StringVar()
        self.next_seed = tk.StringVar()
        self.next_seed.set(secrets.token_hex(16))

    def add_new_floor(self, floor: TkinterFloor, canvas) -> None:
        """
        Adds a new floor to the floor manager.
        @param floor: floor to add
        @param canvas: canvas to draw on
        """
        self._floors.append(
            TkinterFloor(
                my_globals.FLOOR_HEIGHT,
                my_globals.FLOOR_WIDTH,
                canvas=canvas,
                name=my_globals.DEFAULT_FLOOR_NAME + my_globals.JSON_SUFFIX,
                seed=floor.seed,
            )
        )
        self.current_floor_index = len(self._floors) - 1
        current = self._floors[self.current_floor_index]
        self.current_floor_name.set(current.name)
        self.current_floor_seed_var.set(current.seed)

    def add_floor(self, floor: TkinterFloor) -> None:
        """
        Adds a floor to the floor manager.
        @param floor: floor to add
        """
        self._floors.append(floor)
        self.current_floor_index = len(self._floors) - 1
        self.current_floor_name.set(floor.name)
        self.current_floor_seed_var.set(floor.seed)

    def get_current_floor(self) -> TkinterFloor:
        """
        Returns the current floor.
        @return: the current floor
        """
        return self._floors[self.current_floor_index]

    def set_current_floor_name(self, name: str) -> None:
        """
        Sets the name of the current floor.
        @param name: name to set
        """
        self.get_current_floor().name = name
        self.current_floor_name.set(name)

    def decrease_floor(self) -> None:
        """
        Lowers the index of the current floor.
        """
        if self.current_floor_index > 0:
            self.get_current_floor().stop_drawing()
            self.current_floor_index -= 1
            self._floors[self.current_floor_index].draw()
            self.current_floor_name.set(self._floors[self.current_floor_index].name)
            self.current_floor_seed_var.set(self.get_current_floor().seed)

    def increase_floor(self) -> None:
        """
        Increases the index of the current floor.
        """
        last_floor = len(self._floors) - 1
        if self.current_floor_index < last_floor:
            self.get_current_floor().stop_drawing()
            self.current_floor_index += 1
            current_floor = self._floors[self.current_floor_index]
            current_floor.draw()
            self.current_floor_name.set(current_floor.name)
            self.current_floor_seed_var.set(self.get_current_floor().seed)
