"""
Module for the TkinterGenerator class.
"""

import os
import secrets
import tkinter as tk
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
        color = my_globals.Color.LIGHT_GRAY.value
        hex_color = util_functions.rgb2hex(color[0], color[1], color[2])
        self._canvas = tk.Canvas(
            height=my_globals.FLOOR_HEIGHT * my_globals.ROOM_HEIGHT,
            width=my_globals.FLOOR_WIDTH * my_globals.ROOM_WIDTH,
            background=hex_color,
        )
        self._path = tk.StringVar()
        self._path.set(self._output_file_path)
        self._menu_bar = tk.Menu(self._tk)
        self._theme_handler = ThemeHandler(self._tk, self._canvas)
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
        self._floor_manager.add_new_floor(self._floor, self._canvas)
        self._floor = self._floor_manager.get_current_floor()

    def _generate_and_draw_floor(self) -> None:
        """
        Cals the generate method and the draw method of the floor.
        """
        self.generate(self._floor_manager.next_seed.get())
        self._floor_manager.next_seed.set(self._floor_manager.next_seed.get())
        self._floor_manager.next_seed.set(secrets.token_hex(16))
        # self._floors[self._current_floor].draw(tk)
        self._floor_manager.get_current_floor().draw_thread()
        self._floor = self._floor_manager.get_current_floor()

    def open(self) -> None:
        """
        Shows a dialog for opening a file.
        Stores the path and the name of the file.
        """
        options = util_functions.json_file_options.copy()
        options["initialdir"] = self._output_file_path
        options["title"] = "Open File"
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
        options["title"] = "Save File"
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
        self._tk.geometry(util_functions.window_size)
        self._tk.resizable(False, False)
        self.generate()
        self._floor_manager.get_current_floor().draw()
        self._canvas.pack(anchor=tk.NW, expand=True)
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

    def add_information_frame(self) -> None:
        """
        Adds a frame to the application which shows information about the current floor.
        """
        information_frame = ttk.Frame()
        # Create information frame
        information_frame.pack(pady=(0, 10))
        name_text = ttk.Label(information_frame, text="Floor name: ")
        name_text.pack(side=tk.LEFT)
        name_label = ttk.Label(
            information_frame, textvariable=self._floor_manager.current_floor_name
        )
        name_label.pack(side=tk.LEFT)
        path_text = ttk.Label(information_frame, text="Current path: ")
        path_text.pack(side=tk.LEFT, padx=(25, 0))
        path_label = ttk.Label(information_frame, textvariable=self._path)
        path_label.pack(side=tk.LEFT)
        seed_text = ttk.Label(information_frame, text="Seed: ")
        seed_text.pack(side=tk.LEFT, padx=(25, 0))
        seed_label = ttk.Label(
            information_frame, textvariable=self._floor_manager.current_floor_seed_var
        )
        seed_label.pack(side=tk.LEFT)

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
        # Create button frame
        button_frame = ttk.Frame(self._tk)
        button_frame.pack(pady=(0, 10))
        button_pre = ttk.Button(button_frame, text="<-", command=self._decrease_floor)
        button_pre.pack(side=tk.LEFT, padx=10)
        # Left arrow to decrease
        self._tk.bind("<Left>", lambda event: self._decrease_floor())
        button_gen = ttk.Button(
            button_frame, text="Generate", command=self._generate_and_draw_floor
        )
        button_gen.pack(side=tk.LEFT, padx=10)
        # Space to generate
        self._tk.bind("<space>", lambda event: self._generate_and_draw_floor())
        button_next = ttk.Button(button_frame, text="->", command=self._increase_floor)
        button_next.pack(side=tk.LEFT, padx=10)
        # Right arrow to increase
        self._tk.bind("<Right>", lambda event: self._floor_manager.increase_floor())
        # Next seed entry
        next_seed_label = ttk.Label(button_frame, text="Next seed: ")
        next_seed_label.pack(side=tk.LEFT, padx=10)
        next_seed_entry = ttk.Entry(
            button_frame, textvariable=self._floor_manager.next_seed
        )
        next_seed_entry.bind(
            "<Return>", lambda event: self._floor_manager.set_next_seed()
        )
        next_seed_entry.pack(side=tk.LEFT, padx=10)

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
            command=lambda: self.save(
                os.path.join(self._output_file_path, self._output_file_name)
            ),
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
