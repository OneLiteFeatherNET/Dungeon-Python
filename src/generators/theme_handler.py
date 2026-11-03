"""
Module to handle the theme of the application.
"""

from typing import Callable, Optional
from tkinter import Tk, Canvas, ttk

from rooms.tkinter import style


class ThemeHandler:
    """
    Class to handle the theme of the application.
    """

    def __init__(
        self, tk: Tk, canvas: Canvas, on_change: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Creates a new theme handler.
        @param tk: Root of the application
        @param canvas: Canvas of the application
        @param on_change: Called after the theme has changed, e.g. to redraw the floor
        """
        self._tk = tk
        self._canvas = canvas
        self._on_change = on_change
        self._palette = style.LIGHT
        self.apply_theme()

    def switch_theme(self) -> None:
        """
        Switches the theme of the application.
        """
        self._palette = style.DARK if self._palette is style.LIGHT else style.LIGHT
        self.apply_theme()
        if self._on_change is not None:
            self._on_change()

    def apply_theme(self) -> None:
        """
        Applies the current theme to the application.
        """
        palette = self._palette
        style.set_palette(palette)
        self._tk.configure(background=palette.window)
        self._canvas.configure(
            background=palette.canvas, highlightthickness=0, borderwidth=0
        )
        ttk_style = ttk.Style(self._tk)
        ttk_style.theme_use("clam")
        ttk_style.configure(
            ".",
            background=palette.panel,
            foreground=palette.text,
            fieldbackground=palette.entry,
            bordercolor=palette.grid,
            lightcolor=palette.panel,
            darkcolor=palette.panel,
            insertcolor=palette.text,
            font=("DejaVu Sans", 10),
        )
        ttk_style.configure("TFrame", background=palette.panel)
        ttk_style.configure("TLabel", background=palette.panel, foreground=palette.text)
        ttk_style.configure(
            "Muted.TLabel", background=palette.panel, foreground=palette.muted_text
        )
        ttk_style.configure(
            "TButton",
            background=palette.button,
            foreground=palette.text,
            bordercolor=palette.grid,
            focuscolor=palette.button,
            padding=(12, 4),
        )
        ttk_style.map(
            "TButton",
            background=[("pressed", palette.grid), ("active", palette.button_active)],
        )
        ttk_style.configure(
            "TEntry",
            fieldbackground=palette.entry,
            foreground=palette.text,
            bordercolor=palette.grid,
            padding=(6, 3),
        )
