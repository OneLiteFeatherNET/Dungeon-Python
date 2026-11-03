"""
Helpers to skip the UI tests when tkinter or a display is not available.

Set the environment variable REQUIRE_UI_TESTS=1 to make these tests fail
instead of being skipped, e.g. in CI where they must always run.
"""

import importlib.util
import os
import unittest
from typing import Callable, TypeVar

T = TypeVar("T")

_REQUIRED = os.environ.get("REQUIRE_UI_TESTS") == "1"


def has_tkinter() -> bool:
    """
    Returns if tkinter can be imported.
    """
    return importlib.util.find_spec("tkinter") is not None


def has_display() -> bool:
    """
    Returns if tkinter can open a window.
    """
    if not has_tkinter():
        return False
    # pylint: disable=import-outside-toplevel
    import tkinter

    try:
        tkinter.Tk().destroy()
    except tkinter.TclError:
        return False
    return True


def _require(available: bool, reason: str) -> Callable[[T], T]:
    if available:
        return lambda test: test
    if _REQUIRED:
        raise RuntimeError(f"UI tests are required but {reason}")
    return unittest.skip(reason)


def requires_tkinter() -> Callable[[T], T]:
    """
    Skips the decorated tests if tkinter is not available.
    """
    return _require(has_tkinter(), "tkinter is not available")


def requires_display() -> Callable[[T], T]:
    """
    Skips the decorated tests if tkinter cannot open a window.
    """
    return _require(has_display(), "tkinter or a display is not available")
