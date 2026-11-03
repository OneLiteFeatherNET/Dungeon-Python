"""Unit tests for the Floor class."""

import unittest

from floors.floor import Floor
from utils.globals import DoorFace
from rooms.room import Room
from utils.room_type import RoomType
from utils.direction import Direction


class FloorTest(unittest.TestCase):
    def setUp(self) -> None:
        self._floor = Floor(20, 30, "1")
        self._floor_with_rooms = Floor(30, 30, "2")
        self._floor_with_rooms.add_room(2, 2)
        self._floor_with_rooms.add_room(1, 2)
        self._floor_with_rooms.add_room(3, 2)
        self._floor_with_rooms.add_room(5, 5)

    def test_to_json(self):
        expected = '{\n  "_seed": "1",\n  "_rooms": []\n}'
        self.assertEqual(expected, self._floor.to_json(1))

    def test_contains_room(self):
        self.assertFalse(self._floor.contains_room((1, 1)))

    def test_add_to_floor_grid_error(self):
        with self.assertRaises(IndexError):
            self._floor.add_to_floor_grid(31, 0)

    def test_add_two_floor_grid(self):
        self._floor.add_to_floor_grid(2, 3)
        self.assertTrue(self._floor.contains_room((2, 3)))

    def test_add_room_next_to_places_the_room_in_the_given_direction(self):
        room = Room(5, 5, 0, RoomType.NORMAL_ROOM)
        for direction in Direction:
            with self.subTest(direction=direction):
                floor = Floor(20, 30, "1")

                floor.add_room_next_to(room, direction, RoomType.BOSS_ROOM)

                expected = (5 + direction.value[0], 5 + direction.value[1])
                added = floor.get_rooms()[0]
                self.assertEqual(expected, (added[0], added[1]))
                self.assertEqual(RoomType.BOSS_ROOM, added.get_type())

    def test_add_room(self):
        self._floor.add_room(1, 1)
        self.assertTrue(self._floor.contains_room((1, 1)))
        result = self._floor.get_rooms()[0]
        self.assertEqual(Room(1, 1, 0, RoomType.NORMAL_ROOM), result)

    def test_get_rooms(self):
        rooms = [
            Room(2, 2, 0, RoomType.NORMAL_ROOM),
            Room(1, 2, 1, RoomType.NORMAL_ROOM),
            Room(3, 2, 2, RoomType.NORMAL_ROOM),
            Room(5, 5, 3, RoomType.NORMAL_ROOM),
        ]
        self.assertEqual(rooms, self._floor_with_rooms.get_rooms())

    def test_get_rooms2(self):
        self.assertEqual([], self._floor.get_rooms())

    def test_add_doors(self):
        self._floor_with_rooms.add_doors_to_rooms()
        self.assertEqual(
            [DoorFace.EAST, DoorFace.WEST],
            self._floor_with_rooms.get_rooms()[0].get_doors(),
        )

    def test_add_doors2(self):
        self._floor_with_rooms.add_doors_to_rooms()
        self.assertEqual([], self._floor_with_rooms.get_rooms()[3].get_doors())

    def test_count_neighbours(self):
        self.assertEqual(2, self._floor_with_rooms.count_neighbours(2, 2))

    def test_count_neighbours2(self):
        self.assertEqual(0, self._floor_with_rooms.count_neighbours(5, 5))

    def test_is_dead_end(self):
        self.assertTrue(self._floor_with_rooms.is_dead_end(1, 2))

    def test_is_dead_end_false(self):
        self.assertFalse(self._floor_with_rooms.is_dead_end(2, 2))

    def test_rooms_by_distance_spreads_from_the_start_room(self):
        # pylint: disable=import-outside-toplevel
        from generators.generator import Generator
        from rooms.teleport_room import TeleportRoom

        hidden = (RoomType.SECRET_ROOM, RoomType.SUPER_SECRET_ROOM)
        for stage_id in (0, 2, 5):
            for seed in range(60):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    floor = generator._floor
                    rings = floor.rooms_by_distance()

                    ids = [room.get_id() for ring in rings for room in ring]
                    self.assertEqual(
                        sorted(r.get_id() for r in floor.get_rooms()), sorted(ids)
                    )
                    self.assertEqual(
                        [RoomType.START_ROOM], [r.get_type() for r in rings[0]]
                    )
                    self.assertTrue(all(r.get_type() in hidden for r in rings[-1]))
                    boss_rings = {
                        index
                        for index, ring in enumerate(rings)
                        for room in ring
                        if room.get_type() == RoomType.BOSS_ROOM
                    }
                    self.assertEqual(1, len(boss_rings))
                    # Every visible room is reached from the ring before it
                    for index in range(1, len(rings) - 1):
                        previous = rings[index - 1]
                        for room in rings[index]:
                            if room.get_type() == RoomType.BOSS_ROOM:
                                continue
                            reached = any(
                                abs(room[0] - other[0]) + abs(room[1] - other[1]) == 1
                                or (
                                    isinstance(other, TeleportRoom)
                                    and other.get_connected_room_id() == room.get_id()
                                )
                                for other in previous
                            )
                            self.assertTrue(reached)


if __name__ == "__main__":
    unittest.main()
