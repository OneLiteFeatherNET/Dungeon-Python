"""Unit tests for the TkinterGenerator class."""

import importlib.util
import tempfile
import unittest
from unittest import mock

from utils import globals as my_globals

_HAS_TKINTER = importlib.util.find_spec("tkinter") is not None


def _has_display() -> bool:
    if not _HAS_TKINTER:
        return False
    # pylint: disable=import-outside-toplevel
    import tkinter

    try:
        tkinter.Tk().destroy()
    except tkinter.TclError:
        return False
    return True


@unittest.skipUnless(_has_display(), "tkinter or a display is not available")
class TkinterGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        # pylint: disable=import-outside-toplevel
        from generators.tkinter_generator import TkinterGenerator

        self._tmp_dir = tempfile.TemporaryDirectory()
        self._generator = TkinterGenerator("1", "floor", self._tmp_dir.name, 2)
        self._generator.generate()

    def tearDown(self) -> None:
        self._generator._tk.destroy()
        self._tmp_dir.cleanup()

    def test_canvas_fits_the_floor(self):
        canvas = self._generator._canvas
        self.assertEqual(
            my_globals.FLOOR_WIDTH * my_globals.ROOM_WIDTH, int(canvas.cget("width"))
        )
        self.assertEqual(
            my_globals.FLOOR_HEIGHT * my_globals.ROOM_HEIGHT, int(canvas.cget("height"))
        )

    def _press(self, key: str) -> None:
        tk = self._generator._tk
        tk.update()
        tk.focus_force()
        tk.event_generate(key, when="now")
        tk.update()

    def test_arrow_keys_switch_the_current_floor(self):
        self._generator.add_buttons()
        first = self._generator._floor
        self._generator.generate("2")
        second = self._generator._floor

        self._press("<Left>")
        self.assertIs(first, self._generator._floor)

        self._press("<Right>")
        self.assertIs(second, self._generator._floor)

    def test_menu_shortcuts_are_bound(self):
        generator = self._generator
        generator.create_menu_bar()
        shortcuts = {
            "<Control-o>": "open",
            "<Control-s>": "_save_current_floor",
            "<Control-S>": "save",
            "<Control-q>": "quit",
        }
        for key, method in shortcuts.items():
            with self.subTest(key=key), mock.patch.object(generator, method) as m:
                self._press(key)
                m.assert_called_once()

        with mock.patch.object(generator._theme_handler, "switch_theme") as m:
            self._press("<Control-t>")
            m.assert_called_once()

        with mock.patch("rooms.tkinter.legend_window.display_legend") as m:
            self._press("<F1>")
            m.assert_called_once()


if __name__ == "__main__":
    unittest.main()
