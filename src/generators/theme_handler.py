"""
Module to handle the theme of the application.
"""

from typing import Callable, List, Optional
from tkinter import BooleanVar, Menu, Tk, Canvas, ttk

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
        self._menus: List[Menu] = []
        # Shown as check mark in the view menu
        self.dark = BooleanVar(tk, value=False)
        self.apply_theme()

    def switch_theme(self) -> None:
        """
        Switches the theme of the application.
        """
        self.set_dark(self._palette is style.LIGHT)

    def set_dark(self, dark: bool) -> None:
        """
        Switches to the dark or the light theme.
        @param dark: True for the dark theme, False for the light theme
        """
        self._palette = style.DARK if dark else style.LIGHT
        self.dark.set(dark)
        self.apply_theme()
        if self._on_change is not None:
            self._on_change()

    def register_menu(self, menu: Menu) -> None:
        """
        Colors the menu in the current theme and whenever the theme changes.
        @param menu: menu to color
        """
        self._menus.append(menu)
        self._apply_to_menu(menu)

    def _apply_to_menu(self, menu: Menu) -> None:
        palette = self._palette
        menu.configure(
            background=palette.panel,
            foreground=palette.text,
            activebackground=palette.button_active,
            activeforeground=palette.text,
            selectcolor=palette.text,
            borderwidth=0,
            relief="flat",
        )

    def apply_theme(self) -> None:
        """
        Applies the current theme to the application.
        """
        palette = self._palette
        style.set_palette(palette)
        self._tk.configure(background=palette.window)
        for menu in self._menus:
            self._apply_to_menu(menu)
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
