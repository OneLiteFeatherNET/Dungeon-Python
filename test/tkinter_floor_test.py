"""Unit tests for the TkinterFloor class."""

import importlib.util
import unittest

import numpy

from floors.floor import Floor
from generators.generator import Generator
from rooms.teleport_room import TeleportRoom

_HAS_TKINTER = importlib.util.find_spec("tkinter") is not None


@unittest.skipUnless(_HAS_TKINTER, "tkinter is not available")
class TkinterFloorTest(unittest.TestCase):
    def setUp(self) -> None:
        # pylint: disable=import-outside-toplevel
        from floors.tkinter_floor import TkinterFloor

        generator = Generator("2", "test", "", 2)
        generator.generate()
        self._floor = Floor.from_json(generator.to_json(1))
        self._tkinter_floor = TkinterFloor.from_floor(self._floor, None, "floor.json")

    def test_from_floor_keeps_the_rooms(self):
        self.assertEqual(self._floor.get_rooms(), self._tkinter_floor.get_rooms())

    def test_from_floor_keeps_the_doors(self):
        for original, converted in zip(
            self._floor.get_rooms(), self._tkinter_floor.get_rooms()
        ):
            with self.subTest(room=original.get_id()):
                self.assertEqual(original.get_doors(), converted.get_doors())

    def test_from_floor_keeps_teleport_rooms(self):
        teleport_rooms = [
            room
            for room in self._tkinter_floor.get_rooms()
            if isinstance(room, TeleportRoom)
        ]
        self.assertEqual(1, len(teleport_rooms))
        boss_room_ids = [
            room.get_id()
            for room in self._floor.get_rooms()
            if room.get_id() == teleport_rooms[0].get_connected_room_id()
        ]
        self.assertEqual(1, len(boss_room_ids))

    def test_from_floor_keeps_the_floor_grid(self):
        self.assertTrue(
            numpy.array_equal(
                self._floor.get_floor_grid(), self._tkinter_floor.get_floor_grid()
            )
        )

    def test_from_floor_keeps_the_saved_json(self):
        self.assertEqual(self._floor.to_json(), self._tkinter_floor.to_json())


if __name__ == "__main__":
    unittest.main()
