"""
This file contains the test cases for the generator class.
"""
import json
import os
import tempfile
import unittest
from collections import deque

from floors.floor import Floor
from generators.generator import Generator
from rooms.teleport_room import TeleportRoom
from utils.globals import FLOOR_HEIGHT, FLOOR_WIDTH
from utils.room_type import RoomType

_SAMPLE_SEEDS = ("1", "42", "abc", "test-seed", "zzz", "0")


def _reachable_coordinates(floor):
    """
    Returns which room coordinates are reachable from the start room by
    walking grid-adjacent rooms and following teleport-room connections,
    together with the set of all room coordinates on the floor.
    """
    rooms = floor.get_rooms()
    rooms_by_id = {room.get_id(): room for room in rooms}
    coordinates = {(room[0], room[1]) for room in rooms}
    start_room = next(room for room in rooms if room.get_type() == RoomType.START_ROOM)

    seen = {(start_room[0], start_room[1])}
    queue = deque([start_room])
    while queue:
        current = queue.popleft()
        neighbour_coordinates = [
            (current[0] + dx, current[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        ]
        if isinstance(current, TeleportRoom):
            connected_room = rooms_by_id[current.get_connected_room_id()]
            neighbour_coordinates.append((connected_room[0], connected_room[1]))
        for room in rooms:
            room_coordinates = (room[0], room[1])
            if room_coordinates in neighbour_coordinates and room_coordinates not in seen:
                seen.add(room_coordinates)
                queue.append(room)
    return seen, coordinates


class GeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self._generator = Generator("1", "test", "", 1)

    def test_generate_creates_exactly_one_start_room(self):
        self._generator.generate()
        start_rooms = [
            room
            for room in self._generator._floor.get_rooms()
            if room.get_type() == RoomType.START_ROOM
        ]
        self.assertEqual(1, len(start_rooms))

    def test_generate_creates_a_boss_room(self):
        self._generator.generate()
        self.assertIsNotNone(self._generator._floor.get_boss_room())

    def test_generate_rooms_are_within_floor_bounds(self):
        for seed in _SAMPLE_SEEDS:
            with self.subTest(seed=seed):
                generator = Generator(seed, "test", "", 1)
                generator.generate()
                for room in generator._floor.get_rooms():
                    self.assertTrue(0 <= room[0] < FLOOR_WIDTH)
                    self.assertTrue(0 <= room[1] < FLOOR_HEIGHT)

    def test_generate_does_not_place_two_rooms_on_the_same_tile(self):
        for seed in _SAMPLE_SEEDS:
            with self.subTest(seed=seed):
                generator = Generator(seed, "test", "", 1)
                generator.generate()
                coordinates = [
                    (room[0], room[1]) for room in generator._floor.get_rooms()
                ]
                self.assertEqual(len(coordinates), len(set(coordinates)))

    def test_generate_produces_a_fully_reachable_dungeon(self):
        # Reachability also has to follow teleport rooms: the boss room can be
        # placed in a corner with no direct neighbours and only be reachable
        # through its connected teleport room.
        for seed in _SAMPLE_SEEDS:
            with self.subTest(seed=seed):
                generator = Generator(seed, "test", "", 1)
                generator.generate()
                seen, coordinates = _reachable_coordinates(generator._floor)
                self.assertEqual(coordinates, seen)

    def test_generate_is_deterministic_for_the_same_seed(self):
        first = Generator("det-seed", "test", "", 1)
        first.generate()
        second = Generator("det-seed", "test", "", 1)
        second.generate()
        self.assertEqual(first._floor.get_rooms(), second._floor.get_rooms())

    def test_mark_dead_ends_finds_all_rooms_with_a_single_neighbour(self):
        floor = self._generator._floor
        floor.add_room(2, 2, RoomType.START_ROOM)
        floor.add_room(1, 2)  # only neighbour is (2, 2) -> dead end
        floor.add_room(3, 2)  # neighbours are (2, 2) and (4, 2) -> not a dead end
        floor.add_room(4, 2)  # only neighbour is (3, 2) -> dead end

        dead_end_indices = self._generator.mark_dead_ends()

        self.assertEqual([1, 3], dead_end_indices)
        for index in dead_end_indices:
            self.assertEqual(RoomType.DEAD_END, floor.get_rooms()[index].get_type())

    def test_add_special_rooms_assigns_item_and_shop_room(self):
        floor = self._generator._floor
        floor.add_room(2, 2, RoomType.START_ROOM)
        floor.add_room(1, 2, RoomType.DEAD_END)
        floor.add_room(3, 2, RoomType.DEAD_END)

        self._generator.add_special_rooms([1, 2])

        self.assertEqual(RoomType.ITEM_ROOM, floor.get_rooms()[1].get_type())
        self.assertEqual(RoomType.SHOP_ROOM, floor.get_rooms()[2].get_type())

    def test_add_special_rooms_stops_when_there_are_fewer_dead_ends_than_special_rooms(self):
        floor = self._generator._floor
        floor.add_room(2, 2, RoomType.START_ROOM)
        floor.add_room(1, 2, RoomType.DEAD_END)

        self._generator.add_special_rooms([1])

        self.assertEqual(RoomType.ITEM_ROOM, floor.get_rooms()[1].get_type())

    def test_to_json_matches_the_generated_floor(self):
        self._generator.generate()

        result = json.loads(self._generator.to_json(1))

        self.assertEqual(FLOOR_WIDTH, result["_width"])
        self.assertEqual(FLOOR_HEIGHT, result["_height"])
        self.assertEqual("python", result["_generated_by"])
        self.assertEqual("1", result["_floor"]["_seed"])
        self.assertEqual(
            len(self._generator._floor.get_rooms()), len(result["_floor"]["_rooms"])
        )

    def test_to_json_round_trips_through_floor_from_json(self):
        self._generator.generate()

        restored = Floor.from_json(self._generator.to_json(1))

        self.assertEqual(self._generator._floor.get_rooms(), restored.get_rooms())

    def test_generate_terminates_when_no_secret_room_position_exists(self):
        # Seed "9" on floor 0 used to loop forever in place_secret_room.
        generator = Generator(seed="9", output_file_name="floor", stage_id=0)

        generator.generate()

        self.assertGreater(len(generator._floor.get_rooms()), 0)

    def test_generate_terminates_for_many_seeds_on_small_floors(self):
        for stage_id in (0, 1):
            for seed in range(200):
                with self.subTest(stage_id=stage_id, seed=seed):
                    Generator(
                        seed=str(seed), output_file_name="floor", stage_id=stage_id
                    ).generate()

    def test_save_writes_the_generated_floor_to_the_given_path(self):
        self._generator.generate()
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "floor.json")

            result_path = self._generator.save(output_path)

            self.assertEqual(output_path, result_path)
            with open(output_path, encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(self._generator.to_json(1), content)


if __name__ == "__main__":
    unittest.main()
