"""
Module for the TkinterGenerator class.
"""

import os
import secrets
import tkinter as tk
from typing import Optional
from tkinter import filedialog, messagebox
from tkinter import ttk

from floors.floor import Floor
from floors.tkinter_floor import TkinterFloor
from generators.floor_manager import FloorManager
from generators.generator import Generator
from generators.theme_handler import ThemeHandler
from rooms.tkinter import legend_window
from utils import util_functions, globals as my_globals


class TkinterGenerator(Generator):
    """
    Tkinter version of the generator.
    """

    _floor: TkinterFloor

    def __init__(
        self, seed: str, output_file_name: str, output_file_path: str, stage_id: int = 2
    ):
        """
        Creates a new generator.
        @param output_file_name: Name for the output file
        @param output_file_path: Path for the output file
        @param stage_id: ID for the stage
        @param seed: seed for the random generator

        """
        super().__init__(seed, output_file_name, output_file_path, stage_id)
        self._tk = tk.Tk()
        self._canvas = tk.Canvas(
            self._tk,
            height=my_globals.FLOOR_HEIGHT * my_globals.ROOM_HEIGHT,
            width=my_globals.FLOOR_WIDTH * my_globals.ROOM_WIDTH,
        )
        self._bottom_bar: Optional[ttk.Frame] = None
        self._path = tk.StringVar()
        self._path.set(self._output_file_path)
        self._theme_handler = ThemeHandler(
            self._tk, self._canvas, on_change=self._redraw_floor
        )
        self._floor_manager = FloorManager(output_file_name)
        self._tk.protocol("WM_DELETE_WINDOW", self.quit)

    def _create_floor(self) -> None:
        """
        Creates a new TkinterFloor and appends it to the floor queue.
        """
        self._floor = TkinterFloor(
            my_globals.FLOOR_HEIGHT,
            my_globals.FLOOR_WIDTH,
            self._canvas,
            my_globals.DEFAULT_FLOOR_NAME + my_globals.JSON_SUFFIX,
            self._seed,
        )
        self._floor_manager.add_floor(self._floor)

    def _generate_and_draw_floor(self) -> None:
        """
        Calls the generate method and the draw method of the floor.
        """
        self._floor.stop_drawing()
        self.generate(self._floor_manager.next_seed.get())
        self._floor_manager.next_seed.set(secrets.token_hex(16))
        self._floor_manager.get_current_floor().draw_step_by_step()
        self._floor = self._floor_manager.get_current_floor()

    def open(self) -> None:
        """
        Shows a dialog for opening a file.
        Stores the path and the name of the file.
        """
        options = util_functions.json_file_options.copy()
        options["initialdir"] = self._output_file_path
        options["title"] = util_functions.open_file_text
        path = filedialog.askopenfilename(**options)
        if len(path) > 0:
            self._output_file_path = os.path.dirname(path)
            self._output_file_name = os.path.basename(path)
            self._floor_manager.current_floor_name.set(self._output_file_name)
            self._path.set(self._output_file_path)
            encoding = "utf-8"
            with open(path, "r", encoding=encoding) as file:
                json_string = file.read()
                self._floor.stop_drawing()
                self._floor = TkinterFloor.from_floor(
                    Floor.from_json(json_string), self._canvas, self._output_file_name
                )
                self._floor_manager.add_floor(self._floor)
                self._floor.draw()

    def save(self, path: str = "") -> str:
        """
        Shows a dialog for saving the floor to a file.
        @param path: Optional path
        @return: Path the floor has been saved to
        """
        if len(path) > 0:
            if not path.endswith(my_globals.JSON_SUFFIX):
                path += my_globals.JSON_SUFFIX
            save_file = False
            # Check if the file already exists
            if os.path.exists(path):
                # Show dialog for overwriting the file
                if messagebox.askyesno(
                    "File already exists", "Do you want to overwrite the file?"
                ):
                    save_file = True
            else:
                save_file = True
            if save_file:
                # Save the file to the given path
                path = super().save(path)
                # Show dialog for saving the file
                messagebox.showinfo("Save", "File saved successfully!")

            return path
        options = util_functions.json_file_options.copy()
        options["initialdir"] = self._output_file_path
        options["initialfile"] = self._output_file_name
        options["title"] = util_functions.save_file_text
        file_path = filedialog.asksaveasfilename(**options)
        if len(file_path) > 0:
            self._output_file_path = os.path.dirname(file_path)
            self._output_file_name = os.path.basename(file_path)
            self._path.set(self._output_file_path)
            self._floor_manager.set_current_floor_name(self._output_file_name)

        return super().save(file_path)

    def run(self) -> None:
        """
        Sets up the ui elements and starts the main loop of the application.
        """
        self._tk.title(util_functions.window_title)
        self._tk.resizable(False, False)
        self.generate()
        self._floor_manager.get_current_floor().draw()
        self._canvas.pack(padx=16, pady=(16, 8))
        self.add_information_frame()
        self.add_buttons()
        self.create_menu_bar()
        self._tk.mainloop()

    def quit(self) -> None:
        """
        Shows a dialog for quitting the application.
        """
        if messagebox.askyesno("Quit", "Do you really want to quit?"):
            self._tk.quit()

    def _redraw_floor(self) -> None:
        """
        Draws the current floor again, e.g. after the theme has changed.
        """
        self._floor_manager.get_current_floor().draw()

    def _get_bottom_bar(self) -> ttk.Frame:
        """
        Returns the bar below the floor that contains the status and the controls.
        """
        if self._bottom_bar is None:
            self._bottom_bar = ttk.Frame(self._tk, padding=(16, 0, 16, 14))
            self._bottom_bar.pack(fill=tk.X)
        return self._bottom_bar

    def add_information_frame(self) -> None:
        """
        Adds the status of the current floor below the floor.
        """
        status = ttk.Frame(self._get_bottom_bar())
        status.pack(side=tk.LEFT)
        name_label = ttk.Label(
            status,
            textvariable=self._floor_manager.current_floor_name,
            font=("DejaVu Sans", 10, "bold"),
        )
        name_label.pack(side=tk.LEFT)
        _ToolTip(name_label, self._path)
        ttk.Label(status, text="  ·  Seed ", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            status,
            textvariable=self._floor_manager.current_floor_seed_var,
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Label(status, text="  ·  ", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            status, textvariable=self._floor_manager.position, style="Muted.TLabel"
        ).pack(side=tk.LEFT)

    def _increase_floor(self) -> None:
        """
        Increases the current floor index.
        """
        self._floor_manager.increase_floor()
        self._floor = self._floor_manager.get_current_floor()

    def _decrease_floor(self) -> None:
        """
        Decreases the current floor index.
        """
        self._floor_manager.decrease_floor()
        self._floor = self._floor_manager.get_current_floor()

    def add_buttons(self) -> None:
        """
        Adds buttons to the application.
        """
        button_frame = ttk.Frame(self._get_bottom_bar())
        button_frame.pack(side=tk.RIGHT)
        button_pre = ttk.Button(
            button_frame, text="◀", width=3, command=self._decrease_floor
        )
        button_pre.pack(side=tk.LEFT)
        # Left arrow to decrease
        self._tk.bind("<Left>", lambda event: self._decrease_floor())
        button_gen = ttk.Button(
            button_frame, text="Generate", command=self._generate_and_draw_floor
        )
        button_gen.pack(side=tk.LEFT, padx=6)
        # Space to generate
        self._tk.bind("<space>", lambda event: self._generate_and_draw_floor())
        button_next = ttk.Button(
            button_frame, text="▶", width=3, command=self._increase_floor
        )
        button_next.pack(side=tk.LEFT)
        # Right arrow to increase
        self._tk.bind("<Right>", lambda event: self._increase_floor())
        # Next seed entry
        next_seed_label = ttk.Label(
            button_frame, text="Next seed", style="Muted.TLabel"
        )
        next_seed_label.pack(side=tk.LEFT, padx=(20, 6))
        self._next_seed_entry = ttk.Entry(
            button_frame, textvariable=self._floor_manager.next_seed, width=34
        )
        # Enter generates a floor with the entered seed
        self._next_seed_entry.bind(
            "<Return>", lambda event: self._generate_and_draw_floor()
        )
        self._next_seed_entry.pack(side=tk.LEFT)

    def create_menu_bar(self) -> None:
        """
        Creates a menu bar for the application.
        """
        # Create a menu bar
        menu_bar = tk.Menu(self._tk)
        self._tk.config(menu=menu_bar)
        menu_bar.add_command(label="Open", command=self.open, accelerator="Ctrl+o")
        menu_bar.add_command(
            label="Save",
            command=self._save_current_floor,
            accelerator="Ctrl+s",
        )
        menu_bar.add_command(
            label="Save As", command=self.save, accelerator="Ctrl+Shift+s"
        )
        menu_bar.add_command(
            label="Switch Theme",
            command=self._theme_handler.switch_theme,
            accelerator="Ctrl+t",
        )
        menu_bar.add_command(
            label="Legend", command=legend_window.display_legend, accelerator="F1"
        )
        menu_bar.add_command(label="Exit", command=self.quit, accelerator="Ctrl+q")
        self._tk.bind("<Control-o>", lambda event: self.open())
        self._tk.bind("<Control-s>", lambda event: self._save_current_floor())
        self._tk.bind("<Control-S>", lambda event: self.save())
        self._tk.bind("<Control-t>", lambda event: self._theme_handler.switch_theme())
        self._tk.bind("<F1>", lambda event: legend_window.display_legend())
        self._tk.bind("<Control-q>", lambda event: self.quit())

    def _save_current_floor(self) -> None:
        """
        Saves the current floor to the current output file.
        """
        self.save(os.path.join(self._output_file_path, self._output_file_name))


class _ToolTip:
    """
    Shows the value of a variable in a small window while the mouse is over a widget.
    """

    def __init__(self, widget: tk.Widget, text: tk.StringVar) -> None:
        self._widget = widget
        self._text = text
        self._window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", lambda event: self._show())
        widget.bind("<Leave>", lambda event: self._hide())

    def _show(self) -> None:
        if self._window is not None or not self._text.get():
            return
        self._window = tk.Toplevel(self._widget)
        self._window.wm_overrideredirect(True)
        x = self._widget.winfo_rootx()
        y = self._widget.winfo_rooty() - 28
        self._window.wm_geometry(f"+{x}+{y}")
        ttk.Label(
            self._window, textvariable=self._text, padding=(6, 2), relief=tk.SOLID
        ).pack()

    def _hide(self) -> None:
        if self._window is not None:
            self._window.destroy()
            self._window = None
