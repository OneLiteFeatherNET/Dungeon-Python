"""
Tooltips for widgets and for the rooms on the floor canvas.
"""

import tkinter as tk
from typing import Callable, Optional, Tuple, Union

from floors.floor import Floor
from rooms.room_description import describe_room
from rooms.tkinter import style
from utils import globals as my_globals

# Time the mouse has to rest on an element before its tooltip is shown
TOOLTIP_DELAY_MS = 400
# Distance between the mouse pointer and the tooltip
_OFFSET = 14


class _TooltipWindow:
    """
    Small borderless window that shows a text next to the mouse pointer
    in the colors of the current theme.
    """

    def __init__(self, master: tk.Misc) -> None:
        self._master = master
        self._window: Optional[tk.Toplevel] = None
        self._label: Optional[tk.Label] = None

    def is_shown(self) -> bool:
        """
        Returns if the tooltip is currently shown.
        """
        return self._window is not None

    def get_text(self) -> str:
        """
        Returns the shown text or an empty text if the tooltip is hidden.
        """
        return "" if self._label is None else str(self._label.cget("text"))

    def show(self, text: str, x_root: int, y_root: int) -> None:
        """
        Shows the text next to the given screen position.
        """
        palette = style.get_palette()
        if self._window is None:
            self._window = tk.Toplevel(self._master)
            self._window.wm_overrideredirect(True)
            self._label = tk.Label(self._window, justify=tk.LEFT, padx=8, pady=4)
            self._label.pack()
        assert self._label is not None
        self._window.configure(background=palette.grid)
        self._label.configure(
            text=text,
            background=palette.button,
            foreground=palette.text,
            font=("DejaVu Sans", 9),
        )
        # The label is surrounded by a 1 pixel border in the grid color
        self._label.pack_configure(padx=1, pady=1)
        self.move(x_root, y_root)

    def move(self, x_root: int, y_root: int) -> None:
        """
        Moves the tooltip next to the given screen position,
        above the pointer if there is no space below it.
        """
        if self._window is None:
            return
        self._window.update_idletasks()
        height = self._window.winfo_reqheight()
        y = y_root + _OFFSET
        if y + height > self._window.winfo_screenheight():
            y = y_root - _OFFSET - height
        self._window.wm_geometry(f"+{x_root + _OFFSET}+{y}")

    def hide(self) -> None:
        """
        Hides the tooltip.
        """
        if self._window is not None:
            self._window.destroy()
            self._window = None
            self._label = None


class ToolTip:
    """
    Shows a text after the mouse rested on a widget for a moment.
    """

    def __init__(
        self, widget: tk.Widget, text: Union[str, tk.StringVar, Callable[[], str]]
    ) -> None:
        """
        @param widget: widget that shows the tooltip
        @param text: fixed text, variable or function that returns the text
        """
        self.widget = widget
        self._text = text
        self._window = _TooltipWindow(widget)
        self._after_id: Optional[str] = None
        self._pointer = (0, 0)
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Motion>", self._remember_pointer, add="+")
        widget.bind("<Leave>", lambda event: self.hide(), add="+")
        widget.bind("<ButtonPress>", lambda event: self.hide(), add="+")

    def get_text(self) -> str:
        """
        Returns the current text of the tooltip.
        """
        if isinstance(self._text, str):
            return self._text
        if isinstance(self._text, tk.StringVar):
            return self._text.get()
        return self._text()

    def get_shown_text(self) -> str:
        """
        Returns the text that is shown right now, empty if the tooltip is hidden.
        """
        return self._window.get_text()

    def _remember_pointer(self, event: tk.Event) -> None:
        self._pointer = (event.x_root, event.y_root)

    def _schedule(self, event: tk.Event) -> None:
        self._remember_pointer(event)
        self._cancel()
        self._after_id = self.widget.after(TOOLTIP_DELAY_MS, self.show)

    def show(self) -> None:
        """
        Shows the tooltip next to the mouse pointer.
        """
        self._after_id = None
        text = self.get_text()
        if text:
            self._window.show(text, *self._pointer)

    def hide(self) -> None:
        """
        Hides the tooltip and cancels a scheduled tooltip.
        """
        self._cancel()
        self._window.hide()

    def _cancel(self) -> None:
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None


class RoomToolTip:
    """
    Shows the details of the room below the mouse pointer on the floor canvas.
    """

    def __init__(
        self, canvas: tk.Canvas, get_floor: Callable[[], Optional[Floor]]
    ) -> None:
        """
        @param canvas: canvas the floor is drawn on
        @param get_floor: returns the floor that is currently drawn
        """
        self._canvas = canvas
        self._get_floor = get_floor
        self._window = _TooltipWindow(canvas)
        self._after_id: Optional[str] = None
        self._cell: Optional[Tuple[int, int]] = None
        self._pointer = (0, 0)
        canvas.bind("<Motion>", self.on_motion, add="+")
        canvas.bind("<Leave>", lambda event: self.hide(), add="+")

    def get_shown_text(self) -> str:
        """
        Returns the text that is shown right now, empty if the tooltip is hidden.
        """
        return self._window.get_text()

    def on_motion(self, event: tk.Event) -> None:
        """
        Shows the details of the room below the pointer after a short delay
        and follows the pointer while it stays in the same room.
        """
        self._pointer = (event.x_root, event.y_root)
        cell = (event.x // my_globals.ROOM_WIDTH, event.y // my_globals.ROOM_HEIGHT)
        if cell == self._cell:
            self._window.move(*self._pointer)
            return
        self.hide()
        self._cell = cell
        self._after_id = self._canvas.after(TOOLTIP_DELAY_MS, self.show)

    def show(self) -> None:
        """
        Shows the details of the room in the cell below the pointer, if there is one.
        """
        self._after_id = None
        floor = self._get_floor()
        if floor is None or self._cell is None:
            return
        room = floor.get_room(self._cell)
        if room is not None:
            self._window.show(describe_room(floor, room), *self._pointer)

    def hide(self) -> None:
        """
        Hides the tooltip and cancels a scheduled tooltip.
        """
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None
        self._cell = None
        self._window.hide()
