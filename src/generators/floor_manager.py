"""
Module for managing the floors of the tkinter generator.
"""

import secrets
import tkinter as tk
from collections import deque
from typing import Deque

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
        # Floor id of the shown floor, "?" for files without a floor id
        self.current_floor_id_var = tk.StringVar()
        # Position of the shown floor in the history, e.g. "2 / 3"
        self.position = tk.StringVar()
        self.next_seed = tk.StringVar()
        self.next_seed.set(secrets.token_hex(16))

    def add_floor(self, floor: TkinterFloor) -> None:
        """
        Adds a floor to the floor manager and shows it.
        @param floor: floor to add
        """
        self._floors.append(floor)
        self.current_floor_index = len(self._floors) - 1
        self._show_current_floor_info()

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
        Shows the previous floor of the history.
        """
        if self.current_floor_index > 0:
            self._show_floor_at(self.current_floor_index - 1)

    def increase_floor(self) -> None:
        """
        Shows the next floor of the history.
        """
        if self.current_floor_index < len(self._floors) - 1:
            self._show_floor_at(self.current_floor_index + 1)

    def _show_floor_at(self, index: int) -> None:
        """
        Stops drawing the current floor and draws the floor at the given index.
        @param index: index of the floor in the history
        """
        self.get_current_floor().stop_drawing()
        self.current_floor_index = index
        self.get_current_floor().draw()
        self._show_current_floor_info()

    def _show_current_floor_info(self) -> None:
        """
        Updates the texts that describe the current floor.
        """
        floor = self.get_current_floor()
        self.current_floor_name.set(floor.name)
        self.current_floor_seed_var.set(floor.seed)
        self.current_floor_id_var.set(
            "?" if floor.floor_id is None else str(floor.floor_id)
        )
        self.position.set(f"{self.current_floor_index + 1} / {len(self._floors)}")
