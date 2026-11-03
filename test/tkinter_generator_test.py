"""Unit tests for the TkinterGenerator class."""

import importlib.util
import tempfile
import time
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

    def test_enter_in_the_next_seed_entry_generates_a_floor_with_that_seed(self):
        generator = self._generator
        generator.add_buttons()
        generator._floor_manager.next_seed.set("entered-seed")
        entry = generator._next_seed_entry

        with mock.patch("floors.tkinter_floor.TkinterFloor.draw_step_by_step"):
            generator._tk.update()
            entry.focus_force()
            entry.event_generate("<Return>", when="now")
            generator._tk.update()

        self.assertEqual("entered-seed", generator._floor.seed)
        self.assertEqual(
            "entered-seed", generator._floor_manager.current_floor_seed_var.get()
        )

    def _pump(self, milliseconds: int) -> None:
        end = time.monotonic() + milliseconds / 1000
        while time.monotonic() < end:
            self._generator._tk.update()
            time.sleep(0.005)

    def _drawn_rooms(self) -> int:
        return len(self._generator._canvas.find_withtag("room"))

    def test_draw_step_by_step_draws_one_room_after_another(self):
        floor = self._generator._floor

        floor.draw_step_by_step(delay_ms=10)

        self.assertEqual(1, self._drawn_rooms())
        self._pump(10 * len(floor.get_rooms()) + 300)
        self.assertEqual(len(floor.get_rooms()), self._drawn_rooms())

    def test_stop_drawing_stops_the_step_by_step_drawing(self):
        floor = self._generator._floor
        floor.draw_step_by_step(delay_ms=10)

        floor.stop_drawing()
        self._pump(200)

        self.assertEqual(1, self._drawn_rooms())

    def test_generating_a_new_floor_stops_drawing_the_previous_one(self):
        self._generator._floor.draw_step_by_step(delay_ms=10)

        self._generator._generate_and_draw_floor()
        self._pump(200)

        # Only the first room of the new floor is drawn, the next one follows
        # after 500 ms. Rooms of the previous floor must not be drawn anymore.
        self.assertEqual(1, self._drawn_rooms())

    def test_draw_shows_every_door(self):
        floor = self._generator._floor

        floor.draw()

        doors = sum(len(room.get_doors()) for room in floor.get_rooms())
        self.assertEqual(doors, len(self._generator._canvas.find_withtag("door")))

    def test_draw_links_teleport_rooms_to_their_target(self):
        # Seed "2" on floor 2 has a boss room behind a teleport room
        self._generator.generate("2")
        floor = self._generator._floor

        floor.draw()

        self.assertEqual(1, len(self._generator._canvas.find_withtag("link")))

    def test_switching_the_theme_redraws_the_floor_in_the_new_colors(self):
        # pylint: disable=import-outside-toplevel
        from rooms.tkinter import style

        floor = self._generator._floor
        floor.draw()
        canvas = self._generator._canvas

        self._generator._theme_handler.switch_theme()

        self.assertIs(style.DARK, style.get_palette())
        self.assertEqual(style.DARK.canvas, canvas.cget("background"))
        start_room = canvas.find_withtag("room")[0]
        self.assertIn(canvas.itemcget(start_room, "fill"), style.DARK.rooms.values())

        self._generator._theme_handler.switch_theme()
        self.assertIs(style.LIGHT, style.get_palette())


if __name__ == "__main__":
    unittest.main()
