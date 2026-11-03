"""
Simple dialogs in the style of the application.
Native message boxes use the language of the operating system for their buttons,
so they would mix English texts with e.g. German buttons and ignore the dark theme.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from rooms.tkinter import style


class Dialog:
    """
    Modal dialog with a message and one or two buttons.
    """

    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        message: str,
        confirm_text: str,
        cancel_text: Optional[str] = None,
    ) -> None:
        """
        Creates the dialog without showing it.
        @param parent: window the dialog belongs to
        @param title: title of the dialog window
        @param message: message to show
        @param confirm_text: text of the confirm button
        @param cancel_text: text of the cancel button, None for no cancel button
        """
        self.result = False
        palette = style.get_palette()
        self.window = tk.Toplevel(parent, background=palette.window)
        self.window.title(title)
        self.window.resizable(False, False)
        self.window.transient(parent.winfo_toplevel())

        content = ttk.Frame(self.window, padding=(20, 16, 20, 14))
        content.pack(fill=tk.BOTH)
        ttk.Label(content, text=message, wraplength=360).pack(anchor=tk.W)
        buttons = ttk.Frame(content)
        buttons.pack(anchor=tk.E, pady=(16, 0))
        self.confirm_button = ttk.Button(
            buttons, text=confirm_text, command=self.confirm
        )
        self.confirm_button.pack(side=tk.RIGHT)
        self.cancel_button: Optional[ttk.Button] = None
        if cancel_text is not None:
            self.cancel_button = ttk.Button(
                buttons, text=cancel_text, command=self.cancel
            )
            self.cancel_button.pack(side=tk.RIGHT, padx=(0, 8))

        self.window.bind("<Return>", lambda event: self.confirm())
        self.window.bind("<Escape>", lambda event: self.cancel())
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        self._center_over(parent.winfo_toplevel())

    def _center_over(self, parent: tk.Misc) -> None:
        self.window.update_idletasks()
        x = (
            parent.winfo_rootx()
            + (parent.winfo_width() - self.window.winfo_reqwidth()) // 2
        )
        y = (
            parent.winfo_rooty()
            + (parent.winfo_height() - self.window.winfo_reqheight()) // 3
        )
        self.window.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def confirm(self) -> None:
        """
        Closes the dialog with a positive result.
        """
        self.result = True
        self.window.destroy()

    def cancel(self) -> None:
        """
        Closes the dialog with a negative result.
        """
        self.result = False
        self.window.destroy()

    def show(self) -> bool:
        """
        Shows the dialog and waits until it is closed.
        @return: True if the dialog was confirmed
        """
        # Wait until the dialog is visible, then keep all input in the dialog
        self.window.wait_visibility()
        self.window.grab_set()
        self.confirm_button.focus_force()
        self.window.wait_window()
        return self.result


def ask(
    parent: tk.Misc, title: str, message: str, confirm_text: str, cancel_text: str
) -> bool:
    """
    Asks a question with a confirm and a cancel button.
    @return: True if the question was confirmed
    """
    return Dialog(parent, title, message, confirm_text, cancel_text).show()


def inform(parent: tk.Misc, title: str, message: str) -> None:
    """
    Shows a message with an OK button.
    """
    Dialog(parent, title, message, "OK").show()
