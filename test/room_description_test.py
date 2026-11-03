"""Unit tests for the room descriptions."""

import unittest

from floor_test_support import teleport_seed
from floors.floor import Floor
from generators.generator import Generator
from rooms.room_description import describe_room
from rooms.teleport_room import TeleportRoom
from utils.globals import DoorFace
from utils.room_type import RoomType


class DescribeRoomTest(unittest.TestCase):
    def test_describes_type_id_position_and_doors(self):
        floor = Floor(8, 9, "1")
        floor.add_room(2, 3, RoomType.SHOP_ROOM)
        room = floor.get_rooms()[0]
        room.add_door(DoorFace.WEST)
        room.add_door(DoorFace.TOP)

        self.assertEqual(
            "Shop Room · #0\nPosition 2, 3\nDoors: top, left",
            describe_room(floor, room),
        )

    def test_room_without_doors(self):
        floor = Floor(8, 9, "1")
        floor.add_room(0, 0)

        self.assertIn("Doors: none", describe_room(floor, floor.get_rooms()[0]))

    def test_teleport_and_boss_room_name_each_other(self):
        generator = Generator(teleport_seed(), "test", "", 2)
        generator.generate()
        floor = generator._floor
        teleport = next(r for r in floor.get_rooms() if isinstance(r, TeleportRoom))
        boss = next(
            r
            for r in floor.get_rooms()
            if r.get_id() == teleport.get_connected_room_id()
        )

        self.assertIn(
            f"Teleports to #{boss.get_id()} (Boss Room)", describe_room(floor, teleport)
        )
        self.assertIn(
            f"Reached through teleport #{teleport.get_id()}", describe_room(floor, boss)
        )

    def test_big_boss_room_names_its_shape(self):
        floor = Floor(8, 9, "1")
        for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
            floor.add_room(x, y, RoomType.BOSS_ROOM)

        self.assertIn(
            "Part of a 2 × 2 boss room", describe_room(floor, floor.get_rooms()[0])
        )


if __name__ == "__main__":
    unittest.main()
