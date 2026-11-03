"""Unit tests for the TkinterGenerator class."""

import tempfile
import time
import unittest
from unittest import mock

from floor_test_support import teleport_seed
from ui_test_support import requires_display
from utils import globals as my_globals


@requires_display()
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

        with mock.patch.object(generator, "toggle_legend") as m:
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
        self._generator.generate(teleport_seed())
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

    def test_f1_shows_and_hides_the_legend(self):
        generator = self._generator
        generator.create_menu_bar()
        generator._content.pack()
        generator._apply_legend_visibility()

        self._press("<F1>")
        self.assertFalse(generator.show_legend.get())
        self.assertFalse(generator._legend.winfo_ismapped())

        self._press("<F1>")
        self.assertTrue(generator.show_legend.get())
        self.assertTrue(generator._legend.winfo_ismapped())

    def test_legend_counts_the_rooms_of_the_current_floor(self):
        # pylint: disable=import-outside-toplevel
        from collections import Counter

        generator = self._generator
        first = generator._floor
        generator.generate("2")

        def expected(floor):
            return Counter(room.get_type() for room in floor.get_rooms())

        for room_type, count in expected(generator._floor).items():
            self.assertEqual(count, generator._legend.get_count(room_type))

        generator._decrease_floor()
        for room_type, count in expected(first).items():
            self.assertEqual(count, generator._legend.get_count(room_type))

    def test_menu_bar_has_file_view_and_floor_menus(self):
        generator = self._generator
        generator.create_menu_bar()
        menu_bar = generator._tk.nametowidget(generator._tk["menu"])

        labels = [
            menu_bar.entrycget(index, "label")
            for index in range(menu_bar.index("end") + 1)
        ]

        self.assertEqual(["File", "View", "Floor"], labels)

    def test_dark_theme_check_mark_follows_the_shortcut(self):
        generator = self._generator
        generator.create_menu_bar()

        self._press("<Control-t>")
        self.assertTrue(generator._theme_handler.dark.get())

        self._press("<Control-t>")
        self.assertFalse(generator._theme_handler.dark.get())

    def _type_in_seed_field(self, key: str) -> None:
        tk = self._generator._tk
        entry = self._generator._next_seed_entry
        tk.update()
        entry.focus_force()
        tk.update()
        entry.event_generate(key, when="now")
        tk.update()

    def test_space_in_the_seed_field_does_not_generate_a_floor(self):
        generator = self._generator
        generator.add_buttons()
        generator._floor_manager.next_seed.set("my")
        generator._next_seed_entry.icursor("end")

        with mock.patch.object(generator, "_generate_and_draw_floor") as generate:
            self._type_in_seed_field("<space>")

        generate.assert_not_called()

    def test_arrow_keys_in_the_seed_field_do_not_switch_the_floor(self):
        generator = self._generator
        generator.add_buttons()
        generator.generate("2")
        current = generator._floor

        self._type_in_seed_field("<Left>")
        self._type_in_seed_field("<Right>")

        self.assertIs(current, generator._floor)

    def test_shortcuts_work_again_after_leaving_the_seed_field(self):
        generator = self._generator
        generator.add_buttons()
        for key in ("<Escape>", "<Return>"):
            with self.subTest(key=key), mock.patch(
                "floors.tkinter_floor.TkinterFloor.draw_step_by_step"
            ):
                self._type_in_seed_field(key)
                self.assertIs(generator._tk, generator._tk.focus_get())

                with mock.patch.object(
                    generator, "_generate_and_draw_floor"
                ) as generate:
                    self._press("<space>")
                generate.assert_called_once()

    def test_each_generation_adds_one_floor_to_the_history(self):
        # Some seeds need several attempts until a floor fits
        for seed in ("a", "b", "c", "d", "e"):
            self._generator.generate(seed)

        self.assertEqual(6, len(self._generator._floor_manager._floors))
        self.assertEqual("6 / 6", self._generator._floor_manager.position.get())

    def test_generate_uses_the_floor_id_from_the_floor_field(self):
        generator = self._generator
        generator.add_buttons()
        generator.next_floor_id.set("5")

        with mock.patch("floors.tkinter_floor.TkinterFloor.draw_step_by_step"):
            generator._generate_and_draw_floor()

        self.assertEqual(5, generator._floor.floor_id)
        self.assertEqual("5", generator._floor_manager.current_floor_id_var.get())
        self.assertEqual(5, generator.to_dict()["_floor_id"])

    def test_page_keys_change_the_floor_id(self):
        generator = self._generator
        generator.add_buttons()

        self._press("<Prior>")
        self._press("<Prior>")
        self.assertEqual("4", generator.next_floor_id.get())

        for _ in range(10):
            self._press("<Next>")
        self.assertEqual("0", generator.next_floor_id.get())

    def test_floor_field_only_accepts_floor_ids(self):
        # pylint: disable=import-outside-toplevel
        from generators.tkinter_generator import _is_floor_id_input

        self.assertTrue(_is_floor_id_input(""))
        self.assertTrue(_is_floor_id_input("12"))
        self.assertFalse(_is_floor_id_input("-1"))
        self.assertFalse(_is_floor_id_input("x"))
        self.assertFalse(_is_floor_id_input("100"))

    def test_empty_floor_field_keeps_the_last_floor_id(self):
        generator = self._generator
        generator.add_buttons()
        generator.next_floor_id.set("")

        with mock.patch("floors.tkinter_floor.TkinterFloor.draw_step_by_step"):
            generator._generate_and_draw_floor()

        self.assertEqual(2, generator._floor.floor_id)
        self.assertEqual("2", generator.next_floor_id.get())

    def test_going_back_shows_the_floor_id_of_the_previous_floor(self):
        generator = self._generator
        generator.add_buttons()
        generator.next_floor_id.set("7")
        with mock.patch("floors.tkinter_floor.TkinterFloor.draw_step_by_step"):
            generator._generate_and_draw_floor()

        self._press("<Left>")

        self.assertEqual("2", generator._floor_manager.current_floor_id_var.get())
        self.assertEqual("1 / 2", generator._floor_manager.position.get())


if __name__ == "__main__":
    unittest.main()
