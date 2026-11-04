"""
This file contains the test cases for the generator class.
"""

import json
import os
import random
import tempfile
import unittest
from collections import deque

import numpy

from floor_test_support import teleport_seed
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
            (current[0] + dx, current[1] + dy)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        ]
        if isinstance(current, TeleportRoom):
            connected_room = rooms_by_id[current.get_connected_room_id()]
            neighbour_coordinates.append((connected_room[0], connected_room[1]))
        for room in rooms:
            room_coordinates = (room[0], room[1])
            if (
                room_coordinates in neighbour_coordinates
                and room_coordinates not in seen
            ):
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

        self.assertEqual(
            {RoomType.ITEM_ROOM, RoomType.SHOP_ROOM},
            {floor.get_rooms()[1].get_type(), floor.get_rooms()[2].get_type()},
        )

    def test_add_special_rooms_prefers_dead_ends_away_from_the_start(self):
        floor = self._generator._floor
        floor.add_room(2, 2, RoomType.START_ROOM)
        floor.add_room(1, 2, RoomType.DEAD_END)  # next to the start room
        floor.add_room(5, 5, RoomType.DEAD_END)
        floor.add_room(6, 6, RoomType.DEAD_END)

        self._generator.add_special_rooms([1, 2, 3])

        self.assertEqual(RoomType.DEAD_END, floor.get_rooms()[1].get_type())
        self.assertEqual(
            {RoomType.ITEM_ROOM, RoomType.SHOP_ROOM},
            {floor.get_rooms()[2].get_type(), floor.get_rooms()[3].get_type()},
        )

    def test_add_special_rooms_stops_when_there_are_fewer_dead_ends_than_special_rooms(
        self,
    ):
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

    def test_generate_is_not_affected_by_the_global_random_state(self):
        expected = Generator("rng-seed", "test", "", 1)
        expected.generate()
        generator = Generator("rng-seed", "test", "", 1)
        random.seed(999)
        random.random()

        generator.generate()

        self.assertEqual(expected._floor.get_rooms(), generator._floor.get_rooms())

    def test_initial_floor_has_the_floor_size(self):
        floor = Generator("1", "test")._floor

        self.assertEqual((FLOOR_WIDTH - 1, FLOOR_HEIGHT - 1), floor.bottom_right())
        self.assertEqual((FLOOR_HEIGHT, FLOOR_WIDTH), floor.get_floor_grid().shape)

    def test_negative_stage_id_is_rejected(self):
        with self.assertRaises(ValueError):
            Generator(seed="1", output_file_name="floor", stage_id=-1)

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

    def test_teleported_boss_room_is_moved_to_the_checked_corner(self):
        self._generator._create_floor()
        floor = self._generator._floor
        floor.add_room(1, 0)  # blocks the top left corner
        floor.add_room(4, 4)
        boss_room = floor.get_rooms()[1]

        self._generator._place_boss_with_teleport_room(boss_room)

        self.assertEqual((FLOOR_WIDTH - 1, 0), (boss_room[0], boss_room[1]))
        self.assertTrue(floor.contains_room((FLOOR_WIDTH - 1, 0)))
        teleport_room = floor.get_rooms()[-1]
        self.assertIsInstance(teleport_room, TeleportRoom)
        self.assertEqual((4, 4), (teleport_room[0], teleport_room[1]))
        self.assertEqual(boss_room.get_id(), teleport_room.get_connected_room_id())

    def test_boss_room_stays_when_there_is_no_free_location(self):
        self._generator._create_floor()
        floor = self._generator._floor
        for x in range(FLOOR_WIDTH):
            for y in range(FLOOR_HEIGHT):
                floor.add_to_floor_grid(x, y)
        floor.add_room(4, 4)
        boss_room = floor.get_rooms()[0]

        self._generator._place_boss_with_teleport_room(boss_room)

        self.assertEqual((4, 4), (boss_room[0], boss_room[1]))
        self.assertEqual(1, len(floor.get_rooms()))

    def test_teleported_boss_rooms_are_isolated_and_on_the_grid(self):
        for stage_id in (0, 1, 2, 3):
            for seed in range(200):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    floor = generator._floor
                    rooms = floor.get_rooms()
                    coordinates = [(room[0], room[1]) for room in rooms]
                    self.assertEqual(len(coordinates), len(set(coordinates)))
                    for point in coordinates:
                        self.assertTrue(floor.contains_room(point))
                    rooms_by_id = {room.get_id(): room for room in rooms}
                    for room in rooms:
                        if isinstance(room, TeleportRoom):
                            boss_room = rooms_by_id[room.get_connected_room_id()]
                            self.assertEqual(RoomType.BOSS_ROOM, boss_room.get_type())
                            self.assertEqual(
                                0, floor.count_neighbours(boss_room[0], boss_room[1])
                            )

    def test_from_json_restores_the_floor_grid(self):
        self._generator.generate()

        restored = Floor.from_json(self._generator.to_json(1))

        self.assertTrue(
            numpy.array_equal(
                self._generator._floor.get_floor_grid(), restored.get_floor_grid()
            )
        )

    def test_from_json_continues_the_room_ids(self):
        self._generator.generate()
        restored = Floor.from_json(self._generator.to_json(1))

        restored.add_room(0, 0)

        ids = [room.get_id() for room in restored.get_rooms()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_from_json_restores_teleport_rooms(self):
        generator = Generator(teleport_seed(), "test", "", 2)
        generator.generate()
        original = [
            room
            for room in generator._floor.get_rooms()
            if isinstance(room, TeleportRoom)
        ]
        self.assertEqual(1, len(original))

        restored = Floor.from_json(generator.to_json(1))

        teleport_rooms = [
            room for room in restored.get_rooms() if isinstance(room, TeleportRoom)
        ]
        self.assertEqual(1, len(teleport_rooms))
        self.assertEqual(
            original[0].get_connected_room_id(),
            teleport_rooms[0].get_connected_room_id(),
        )

    def test_to_json_escapes_special_characters_in_the_seed(self):
        for seed in ('a"b', "a\\b", "a\nb", "ä🙂"):
            with self.subTest(seed=seed):
                generator = Generator(seed, "test", "", 1)
                generator.generate()

                result = json.loads(generator.to_json(1))

                self.assertEqual(seed, result["_floor"]["_seed"])
                self.assertEqual(seed, Floor.from_json(generator.to_json(1)).seed)

    def test_every_floor_has_one_super_secret_room_next_to_a_single_room(self):
        for stage_id in range(6):
            for seed in range(100):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    floor = generator._floor
                    rooms = [
                        room
                        for room in floor.get_rooms()
                        if room.get_type() == RoomType.SUPER_SECRET_ROOM
                    ]
                    self.assertEqual(1, len(rooms))
                    position = (rooms[0][0], rooms[0][1])
                    self.assertEqual(1, floor.count_neighbours(*position))
                    self.assertFalse(floor.has_boss_room_as_neighbour(position))

    def test_to_json_contains_the_floor_id(self):
        generator = Generator("abc", "test", "", 3)
        generator.generate()

        result = json.loads(generator.to_json())

        self.assertEqual(3, result["_floor_id"])
        self.assertEqual(3, Floor.from_json(generator.to_json()).floor_id)

    def test_from_json_loads_files_without_a_floor_id(self):
        self._generator.generate()
        old_file = self._generator.to_dict()
        del old_file["_floor_id"]

        restored = Floor.from_json(json.dumps(old_file))

        self.assertIsNone(restored.floor_id)
        self.assertEqual(self._generator._floor.get_rooms(), restored.get_rooms())

    def test_set_stage_id_changes_the_generated_floor(self):
        self._generator.set_stage_id(4)
        self._generator.generate("abc")

        self.assertEqual(4, self._generator._floor.floor_id)
        expected = Generator("abc", "test", "", 4)
        expected.generate()
        self.assertEqual(expected.to_dict(), self._generator.to_dict())

    def test_set_stage_id_rejects_negative_ids(self):
        with self.assertRaises(ValueError):
            self._generator.set_stage_id(-1)

    def test_special_rooms_are_never_next_to_the_start(self):
        for stage_id in (0, 1, 2, 5):
            for seed in range(100):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    rooms = generator._floor.get_rooms()
                    start = next(
                        r for r in rooms if r.get_type() == RoomType.START_ROOM
                    )
                    for room in rooms:
                        if room.get_type() in (RoomType.ITEM_ROOM, RoomType.SHOP_ROOM):
                            distance = abs(room[0] - start[0]) + abs(room[1] - start[1])
                            self.assertGreater(distance, 1)

    def test_start_room_is_always_cell_35(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                generator = Generator(str(seed), "test", "", seed % 6)
                generator.generate()
                start = next(
                    room
                    for room in generator._floor.get_rooms()
                    if room.get_type() == RoomType.START_ROOM
                )
                self.assertEqual((4, 3), (start[0], start[1]))

    def test_boss_room_is_one_of_the_farthest_dead_ends(self):
        for stage_id in (0, 2, 5):
            for seed in range(100):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    floor = generator._floor
                    rooms = floor.get_rooms()
                    if any(isinstance(room, TeleportRoom) for room in rooms):
                        continue
                    steps = {
                        room.get_id(): ring
                        for ring, rooms_in_ring in enumerate(floor.rooms_by_distance())
                        for room in rooms_in_ring
                    }
                    boss = min(
                        steps[room.get_id()]
                        for room in rooms
                        if room.get_type() == RoomType.BOSS_ROOM
                    )
                    farther_dead_ends = [
                        room
                        for room in rooms
                        if room.get_type()
                        in (RoomType.DEAD_END, RoomType.ITEM_ROOM, RoomType.SHOP_ROOM)
                        and steps[room.get_id()] > boss
                    ]
                    # The farthest or, without space for the boss, the second farthest
                    self.assertLessEqual(len(farther_dead_ends), 1)

    def test_boss_room_is_never_next_to_the_start(self):
        for stage_id in (0, 1, 2):
            for seed in range(100):
                with self.subTest(stage_id=stage_id, seed=seed):
                    generator = Generator(str(seed), "test", "", stage_id)
                    generator.generate()
                    for room in generator._floor.get_rooms():
                        if room.get_type() == RoomType.BOSS_ROOM:
                            distance = abs(room[0] - 4) + abs(room[1] - 3)
                            self.assertGreater(distance, 1)

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
