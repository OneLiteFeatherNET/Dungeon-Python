"""
Module for the TkinterGenerator class.
"""

import os
import secrets
import tkinter as tk
from typing import Callable, List, Optional, Union
from tkinter import filedialog, messagebox
from tkinter import ttk

from floors.floor import Floor
from floors.tkinter_floor import TkinterFloor
from generators.floor_manager import FloorManager
from generators.generator import Generator
from generators.theme_handler import ThemeHandler
from rooms.tkinter.legend_panel import LegendPanel
from rooms.tkinter.tooltip import RoomToolTip, ToolTip
from utils import util_functions, globals as my_globals

# Highest floor id that can be entered in the floor field
_MAX_FLOOR_ID = 99


def _is_floor_id_input(value: str) -> bool:
    """
    Checks if the text of the floor field is allowed while typing.
    @param value: new text of the floor field
    @return: True for an empty text or a number up to the highest floor id
    """
    return value == "" or (value.isdigit() and int(value) <= _MAX_FLOOR_ID)


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
        self._content = ttk.Frame(self._tk)
        self._canvas = tk.Canvas(
            self._content,
            height=my_globals.FLOOR_HEIGHT * my_globals.ROOM_HEIGHT,
            width=my_globals.FLOOR_WIDTH * my_globals.ROOM_WIDTH,
        )
        self._bottom_bar: Optional[ttk.Frame] = None
        self._path = tk.StringVar()
        self._path.set(self._output_file_path)
        self._theme_handler = ThemeHandler(
            self._tk, self._canvas, on_change=self._redraw_floor
        )
        self._legend = LegendPanel(self._content)
        self._room_tooltip = RoomToolTip(self._canvas, self._get_shown_floor)
        self._tooltips: List[ToolTip] = []
        self.show_legend = tk.BooleanVar(self._tk, value=True)
        self._floor_manager = FloorManager(output_file_name)
        # Floor id for the next generated floor, edited in the floor field
        self.next_floor_id = tk.StringVar(self._tk, value=str(stage_id))
        # The position changes whenever another floor is shown
        self._floor_manager.position.trace_add(
            "write", lambda *args: self._update_legend()
        )
        self._tk.protocol("WM_DELETE_WINDOW", self.quit)

    def _create_floor(self) -> None:
        """
        Creates a new TkinterFloor.
        The floor is added to the history once the generation has finished,
        because a generation can create several floors until one fits.
        """
        self._floor = TkinterFloor(
            my_globals.FLOOR_HEIGHT,
            my_globals.FLOOR_WIDTH,
            self._canvas,
            my_globals.DEFAULT_FLOOR_NAME + my_globals.JSON_SUFFIX,
            self._seed,
        )
        self._floor.floor_id = self._stage_id

    def _generate_and_draw_floor(self) -> None:
        """
        Calls the generate method and the draw method of the floor.
        """
        self._floor.stop_drawing()
        self.set_stage_id(self._read_next_floor_id())
        self.generate(self._floor_manager.next_seed.get())
        self._floor_manager.next_seed.set(secrets.token_hex(16))
        self._floor_manager.get_current_floor().draw_step_by_step()
        self._floor = self._floor_manager.get_current_floor()

    def _read_next_floor_id(self) -> int:
        """
        Returns the floor id from the floor field.
        An empty field is reset to the floor id of the last generation.
        @return: floor id for the next floor
        """
        try:
            return int(self.next_floor_id.get())
        except ValueError:
            self.next_floor_id.set(str(self._stage_id))
            return self._stage_id

    def change_floor_id(self, step: int) -> None:
        """
        Changes the floor id in the floor field.
        @param step: amount to add to the floor id, negative to lower it
        """
        floor_id = min(max(self._read_next_floor_id() + step, 0), _MAX_FLOOR_ID)
        self.next_floor_id.set(str(floor_id))

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
        self._content.pack(padx=16, pady=(16, 8))
        self._canvas.pack(side=tk.LEFT)
        self._apply_legend_visibility()
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
        Draws the current floor and the legend again, e.g. after the theme has changed.
        """
        self._legend.redraw()
        if self._floor_manager.current_floor_index >= 0:
            self._floor_manager.get_current_floor().draw()

    def generate(self, new_seed=None) -> None:
        """
        Generates a new floor, adds it to the history and updates the legend.
        """
        super().generate(new_seed)
        self._floor_manager.add_floor(self._floor)
        self._update_legend()

    def _add_tooltip(
        self, widget: tk.Widget, text: Union[str, tk.StringVar, Callable[[], str]]
    ) -> None:
        """
        Adds a tooltip to a widget and keeps a reference to it.
        @param widget: widget that shows the tooltip
        @param text: text, variable or function that returns the text
        """
        self._tooltips.append(ToolTip(widget, text))

    def _get_shown_floor(self) -> Optional[TkinterFloor]:
        """
        Returns the floor that is shown on the canvas or None before the first floor.
        """
        if self._floor_manager.current_floor_index < 0:
            return None
        return self._floor_manager.get_current_floor()

    def _update_legend(self) -> None:
        """
        Shows the room counts of the current floor in the legend
        and hides the room tooltip of the previous floor.
        """
        self._room_tooltip.hide()
        self._legend.update_counts(self._floor_manager.get_current_floor())

    def toggle_legend(self) -> None:
        """
        Shows or hides the legend next to the floor.
        """
        self.show_legend.set(not self.show_legend.get())
        self._apply_legend_visibility()

    def _apply_legend_visibility(self) -> None:
        """
        Shows or hides the legend depending on show_legend.
        """
        if self.show_legend.get():
            self._legend.pack(side=tk.LEFT, anchor=tk.N, padx=(20, 0))
        else:
            self._legend.pack_forget()

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
        self._add_tooltip(name_label, self._path)
        ttk.Label(status, text="  ·  Seed ", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            status,
            textvariable=self._floor_manager.current_floor_seed_var,
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Label(status, text="  ·  Floor ", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            status,
            textvariable=self._floor_manager.current_floor_id_var,
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Label(status, text="  ·  ", style="Muted.TLabel").pack(side=tk.LEFT)
        position_label = ttk.Label(
            status, textvariable=self._floor_manager.position, style="Muted.TLabel"
        )
        position_label.pack(side=tk.LEFT)
        self._add_tooltip(position_label, "Position in the history of generated floors")

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
        self._add_tooltip(button_pre, "Back to the previous floor (←)")
        # Left arrow to decrease
        self._tk.bind("<Left>", self._shortcut(lambda: self._decrease_floor()))
        button_gen = ttk.Button(
            button_frame, text="Generate", command=self._generate_and_draw_floor
        )
        button_gen.pack(side=tk.LEFT, padx=6)
        self._add_tooltip(button_gen, "Generate a new floor (Space)")
        # Space to generate
        self._tk.bind(
            "<space>", self._shortcut(lambda: self._generate_and_draw_floor())
        )
        button_next = ttk.Button(
            button_frame, text="▶", width=3, command=self._increase_floor
        )
        button_next.pack(side=tk.LEFT)
        self._add_tooltip(button_next, "Forward to the next floor (→)")
        # Right arrow to increase
        self._tk.bind("<Right>", self._shortcut(lambda: self._increase_floor()))
        # Floor id for the next floor
        ttk.Label(button_frame, text="Floor", style="Muted.TLabel").pack(
            side=tk.LEFT, padx=(20, 6)
        )
        self._floor_id_entry = ttk.Spinbox(
            button_frame,
            textvariable=self.next_floor_id,
            from_=0,
            to=_MAX_FLOOR_ID,
            width=4,
            validate="key",
            validatecommand=(self._tk.register(_is_floor_id_input), "%P"),
        )
        self._floor_id_entry.bind("<Return>", lambda event: self._submit_seed())
        self._floor_id_entry.bind("<Escape>", lambda event: self._tk.focus_set())
        self._floor_id_entry.pack(side=tk.LEFT)
        self._add_tooltip(
            self._floor_id_entry,
            "Floor id for the next floor, higher ids get more rooms\n"
            "(Page Up / Page Down)",
        )
        self._tk.bind("<Prior>", self._shortcut(lambda: self.change_floor_id(1)))
        self._tk.bind("<Next>", self._shortcut(lambda: self.change_floor_id(-1)))
        # Next seed entry
        next_seed_label = ttk.Label(
            button_frame, text="Next seed", style="Muted.TLabel"
        )
        next_seed_label.pack(side=tk.LEFT, padx=(16, 6))
        self._next_seed_entry = ttk.Entry(
            button_frame, textvariable=self._floor_manager.next_seed, width=30
        )
        # Enter generates a floor with the entered seed, Escape leaves the field.
        # Both give the focus back so that the shortcuts work again.
        self._next_seed_entry.bind("<Return>", lambda event: self._submit_seed())
        self._next_seed_entry.bind("<Escape>", lambda event: self._tk.focus_set())
        self._canvas.bind("<Button-1>", lambda event: self._tk.focus_set())
        self._next_seed_entry.pack(side=tk.LEFT)
        self._add_tooltip(
            self._next_seed_entry,
            "Seed for the next floor, press Enter to generate it",
        )

    def _submit_seed(self) -> None:
        """
        Generates a floor with the entered seed and leaves the seed field.
        """
        self._tk.focus_set()
        self._generate_and_draw_floor()

    @staticmethod
    def _shortcut(action: Callable[[], None]) -> Callable[[tk.Event], None]:
        """
        Creates a handler for a single key shortcut that is ignored while an
        entry or a button has the focus, so typing a seed or pressing a button
        with the keyboard does not trigger it.
        @param action: action of the shortcut
        @return: event handler
        """

        def handler(event: tk.Event) -> None:
            if isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Button, ttk.Button)):
                return
            action()

        return handler

    def create_menu_bar(self) -> None:
        """
        Creates the menu bar with the file, view and floor menus.
        """
        menu_bar = tk.Menu(self._tk, tearoff=False)
        self._tk.config(menu=menu_bar)
        self._theme_handler.register_menu(menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Open…", command=self.open, accelerator="Ctrl+O")
        file_menu.add_command(
            label="Save", command=self._save_current_floor, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="Save As…", command=self.save, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_checkbutton(
            label="Dark Theme",
            variable=self._theme_handler.dark,
            command=lambda: self._theme_handler.set_dark(
                self._theme_handler.dark.get()
            ),
            accelerator="Ctrl+T",
        )
        view_menu.add_checkbutton(
            label="Legend",
            variable=self.show_legend,
            command=self._apply_legend_visibility,
            accelerator="F1",
        )
        menu_bar.add_cascade(label="View", menu=view_menu)

        floor_menu = tk.Menu(menu_bar, tearoff=False)
        floor_menu.add_command(
            label="Generate", command=self._generate_and_draw_floor, accelerator="Space"
        )
        floor_menu.add_separator()
        floor_menu.add_command(
            label="Higher Floor ID",
            command=lambda: self.change_floor_id(1),
            accelerator="Page Up",
        )
        floor_menu.add_command(
            label="Lower Floor ID",
            command=lambda: self.change_floor_id(-1),
            accelerator="Page Down",
        )
        floor_menu.add_separator()
        floor_menu.add_command(
            label="Back", command=self._decrease_floor, accelerator="←"
        )
        floor_menu.add_command(
            label="Forward", command=self._increase_floor, accelerator="→"
        )
        menu_bar.add_cascade(label="Floor", menu=floor_menu)

        for menu in (file_menu, view_menu, floor_menu):
            self._theme_handler.register_menu(menu)

        self._tk.bind("<Control-o>", lambda event: self.open())
        self._tk.bind("<Control-s>", lambda event: self._save_current_floor())
        self._tk.bind("<Control-S>", lambda event: self.save())
        self._tk.bind("<Control-t>", lambda event: self._theme_handler.switch_theme())
        self._tk.bind("<F1>", lambda event: self.toggle_legend())
        self._tk.bind("<Control-q>", lambda event: self.quit())

    def _save_current_floor(self) -> None:
        """
        Saves the current floor to the current output file.
        """
        self.save(os.path.join(self._output_file_path, self._output_file_name))
