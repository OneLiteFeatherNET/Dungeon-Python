"""
This module contains the Generator class.
A generator generates a floor with the given seed and saves it as a json file.
The generation is inspired by the floor generation of the game "The Binding of Isaac".
"""

import itertools
import json
import os
import random
from collections import deque
from datetime import datetime
from typing import List, Optional, Tuple

from floors.floor import Floor
from rooms.room import Room
from utils import util_functions, globals as my_globals, room_type
from utils.direction import Direction
from utils.room_type import RoomType


class Generator:
    """
    Objects of this class are representing generators.
    They generate a Floor object that contains all rooms.
    """

    def __init__(
        self,
        seed: str,
        output_file_name: str,
        output_file_path: str = "",
        stage_id: int = 2,
    ):
        """
        Creates a new generator with the given arguments.
        @param seed: seed for generating the floor
        @param output_file_name: name for the outputfile
        @param stage_id: id for the floor (must be 0 or greater)
        """
        if stage_id < 0:
            raise ValueError(f"stage_id must be 0 or greater, got {stage_id}")
        self._stage_id = stage_id
        self._seed = seed
        self._output_file_name = output_file_name
        self._output_file_path = output_file_path
        self._floor: Floor = Floor(
            my_globals.FLOOR_HEIGHT, my_globals.FLOOR_WIDTH, seed
        )
        self._random = random.Random()
        self._seed_random(seed)

    def to_dict(self) -> dict:
        """
        Creates a dictionary representation of the generator object.
        @return: dictionary with the size and the floor of the generator
        """
        return {
            "_width": my_globals.FLOOR_WIDTH,
            "_height": my_globals.FLOOR_HEIGHT,
            "_floor": self._floor.to_dict(),
            "_generated_by": "python",
        }

    def to_json(self, indent: int = 1) -> str:
        """
        Creates a string representation of the generator object.
        @param indent: Number of indentation levels per nesting level
        @return: json string of the generator
        """
        return json.dumps(self.to_dict(), indent=len(my_globals.BASE_INDENT) * indent)

    def _seed_random(self, seed: str) -> None:
        """
        Seeds the random number generator with the seed and the floor id,
        so the same seed produces different floors for different floor ids.
        @param seed: seed for generating the floor
        """
        self._random.seed(f"{seed}/{self._stage_id}")

    def _create_floor(self) -> None:
        """
        Creates a new floor.
        """
        self._floor = Floor(my_globals.FLOOR_HEIGHT, my_globals.FLOOR_WIDTH, self._seed)

    def _add_new_room(
        self, new_room_tuple: Tuple[int, int], room_tuple_queue: deque
    ) -> bool:
        """
        Checks if a room can be added at the new position
        and if possible adds it to the queue and floor grid.
        @param new_room_tuple: position for the new room
        @param room_tuple_queue: queue for the rooms
        @return: True if the position was added to the queue otherwise False
        """
        if (
            self._floor.is_within_border(new_room_tuple)
            and (not self._floor.contains_room(new_room_tuple))
            and (
                self._floor.count_neighbours(new_room_tuple[0], new_room_tuple[1]) <= 1
            )
            and util_functions.place_room(self._random)
        ):
            room_tuple_queue.append(new_room_tuple)
            self._floor.add_to_floor_grid(*new_room_tuple)
            return True
        return False

    def generate(self, new_seed=None) -> None:
        """
        Generates the rooms for the floor.
        Like in "The Binding of Isaac", a floor is generated again if it does not
        reach the room amount or has not enough dead ends for the special rooms.
        """
        if new_seed is not None:
            self._seed_random(new_seed)
            self._seed = new_seed
        for attempt in range(my_globals.MAX_GENERATION_ATTEMPTS):
            last_attempt = attempt == my_globals.MAX_GENERATION_ATTEMPTS - 1
            start_room, complete = self._place_rooms()
            dead_ends = self.mark_dead_ends()
            if last_attempt or (
                complete and len(dead_ends) >= my_globals.REQUIRED_DEAD_ENDS
            ):
                break
        self.add_boss_room(dead_ends, start_room)
        self.add_special_rooms(dead_ends)
        self.place_secret_room()
        self.place_super_secret_room()
        self._floor.add_doors_to_rooms()

    def _place_rooms(self) -> Tuple[Tuple[int, int], bool]:
        """
        Creates a new floor and places the start room and the normal rooms.
        @return: position of the start room and
            if the room amount for the floor has been reached
        """
        self._create_floor()
        floor = self._floor
        number_of_rooms = util_functions.calculate_room_amount(
            self._stage_id, self._random
        )

        # Add start room
        start_room: Tuple[int, int] = (
            self._random.randint(0, my_globals.FLOOR_WIDTH - 1),
            self._random.randint(0, my_globals.FLOOR_HEIGHT - 1),
        )
        floor.add_room(start_room[0], start_room[1], RoomType.START_ROOM)
        number_of_current_rooms = 1
        room_tuple_queue: deque = deque([start_room])  # Room coordinates
        room_tuple_list = []
        while number_of_current_rooms < number_of_rooms and len(room_tuple_queue) > 0:
            room_tuple = room_tuple_queue.pop()
            for direction in Direction.main_directions():
                if number_of_current_rooms >= number_of_rooms:
                    break
                new_room_tuple = util_functions.add_direction_to_coordinates(
                    direction, room_tuple
                )
                if self._add_new_room(new_room_tuple, room_tuple_queue):
                    number_of_current_rooms += 1
            room_tuple_list.append(room_tuple)

        while len(room_tuple_queue) > 0:
            room_tuple_list.append(room_tuple_queue.pop())
        room_tuple_list.remove(start_room)
        while len(room_tuple_list) > 0:
            room_tuple = room_tuple_list.pop()
            floor.add_room(room_tuple[0], room_tuple[1])
        return start_room, number_of_current_rooms >= number_of_rooms

    def mark_dead_ends(self) -> list:
        """
        Searches for dead ends in the floor and marks them ands returns their indices in a list.
        @return: indices of all dead ends
        """
        dead_end_indices: List[int] = []
        floor = self._floor
        for i in range(len(floor.get_rooms())):
            room = floor.get_rooms()[i]
            if (
                floor.is_dead_end(room[0], room[1])
                and room.get_type() == RoomType.NORMAL_ROOM
            ):
                room.set_type(RoomType.DEAD_END)
                dead_end_indices += (i,)
        return dead_end_indices

    def _add_rooms_next_to_room(self, room, directions) -> None:
        """
        Adds new boss rooms next to a given room.
        @param room: new rooms will be placed next to this room
        @param directions: directions in which the new boss rooms will be placed
        """
        floor = self._floor
        for direction in directions:
            floor.add_room_next_to(room, direction, RoomType.BOSS_ROOM)

    def add_boss_room(self, dead_end_indices: list, start_room: tuple) -> None:
        """
        Turns one of the dead ends farthest away from the start room into the boss room.
        A dead end with free space next to it is preferred, otherwise the boss room
        is moved away and connected to the floor with a teleport room.
        @param dead_end_indices: indices for all dead ends
        @param start_room: coordinates of the start room in a tuple
        """
        if len(dead_end_indices) == 0:
            return
        floor = self._floor
        rooms = floor.get_rooms()
        farthest_first = sorted(
            dead_end_indices,
            key=lambda index: -util_functions.calculate_distance(
                start_room, rooms[index]
            ),
        )
        candidates = farthest_first[: my_globals.BOSS_ROOM_CANDIDATES]
        boss_room_index = next(
            (index for index in candidates if self._free_boss_locations(rooms[index])),
            farthest_first[0],
        )
        boss_room = rooms[boss_room_index]
        possible_locations = self._free_boss_locations(boss_room)

        if len(possible_locations) == 0:
            # Place a teleport-room to the boss-room
            self._place_boss_with_teleport_room(boss_room)
        else:
            size_roll = self._random.random()
            placed = (
                len(possible_locations) >= 2
                and size_roll < my_globals.BIG_BOSS_ROOM_CHANCE
                and self._place_big_boss_room(possible_locations, boss_room)
            )
            if not placed and size_roll < (
                my_globals.BIG_BOSS_ROOM_CHANCE + my_globals.LONG_BOSS_ROOM_CHANCE
            ):
                # Create a 1 * 2 boss-room
                floor.add_room_next_to(
                    boss_room, possible_locations[0], RoomType.BOSS_ROOM
                )

        boss_room.set_type(RoomType.BOSS_ROOM)
        dead_end_indices.remove(boss_room_index)

    def _free_boss_locations(self, room: Room) -> List[Direction]:
        """
        Returns the directions in which the boss room could be extended.
        @param room: possible boss room
        @return: directions with a free cell that is only next to the room
        """
        floor = self._floor
        locations = []
        for direction in Direction.main_directions():
            cell = util_functions.add_direction_to_coordinates(
                direction, (room[0], room[1])
            )
            if (
                floor.is_within_border(cell)
                and not floor.contains_room(cell)
                and floor.count_neighbours(cell[0], cell[1]) == 1
            ):
                locations.append(direction)
        return locations

    def _place_big_boss_room(self, possible_locations: List, boss_room: Room) -> bool:
        """
        Searches a free location to add more boss rooms next to the existing boss room.
        @param possible_locations: possible positions for the other boss rooms
        @param boss_room: current boss room
        @return: True if more boss rooms are added otherwise False
        """
        directions = [
            (Direction.RIGHT, Direction.UP, Direction.UP_RIGHT),
            (Direction.RIGHT, Direction.DOWN, Direction.DOWN_RIGHT),
            (Direction.LEFT, Direction.UP, Direction.UP_LEFT),
            (Direction.LEFT, Direction.DOWN, Direction.DOWN_LEFT),
        ]
        for direction in directions:
            corner = util_functions.add_direction_to_coordinates(
                direction[2], (boss_room[0], boss_room[1])
            )
            if (
                direction[0] in possible_locations
                and direction[1] in possible_locations
                and self._floor.has_no_neighbours(corner)
            ):
                self._add_rooms_next_to_room(boss_room, direction)
                return True

        return False

    def _place_boss_with_teleport_room(self, boss_room) -> None:
        """
        Moves the boss room to a free location without neighbours
        and places a teleport room at its old position.
        If no such location exists, the boss room stays where it is.
        @param boss_room: boss room to move
        """
        destination = self._find_teleport_destination()
        if destination is None:
            return
        floor = self._floor
        floor.add_teleport_room(boss_room)
        boss_room.set_cord(*destination)
        floor.add_to_floor_grid(*destination)

    def _find_teleport_destination(self) -> Optional[Tuple[int, int]]:
        """
        Searches for a free location without neighbours, preferring the corners.
        @return: coordinates of the location or None if there is none
        """
        floor = self._floor
        corners = (
            floor.top_left(),
            floor.top_right(),
            floor.bottom_left(),
            floor.bottom_right(),
        )
        all_points = (
            (x, y)
            for y in range(my_globals.FLOOR_HEIGHT)
            for x in range(my_globals.FLOOR_WIDTH)
        )
        for point in itertools.chain(corners, all_points):
            if self._check_if_not_contains_room_and_has_no_neighbours(point):
                return point
        return None

    def _check_if_not_contains_room_and_has_no_neighbours(
        self, point: Tuple[int, int]
    ) -> bool:
        floor = self._floor
        return not floor.contains_room(
            (point[0], point[1])
        ) and floor.has_no_neighbours(point)

    def add_special_rooms(self, dead_ends: list) -> None:
        """
        Places the special rooms on the dead ends of the floor.
        @param dead_ends: indices of all dead ends
        """
        floor = self._floor
        i = 0
        while i < len(room_type.SPECIAL_ROOMS) and i < len(dead_ends):
            floor.get_rooms()[dead_ends[i]].set_type(room_type.SPECIAL_ROOMS[i])
            i += 1

    def place_super_secret_room(self) -> None:
        """
        Places a super secret room on the floor.
        The super secret room should be as close as possible to the boss room
        but should not be adjacent to the boss room.
        It should only have one adjacent room.
        """
        floor = self._floor
        distance_to_boss = float("inf")
        candidate = None
        boss_room = floor.get_boss_room()
        for room in floor.get_rooms():
            for direction in Direction.main_directions():
                neighbour = util_functions.add_direction_to_coordinates(
                    direction, (room[0], room[1])
                )
                if (
                    floor.is_within_border(neighbour)
                    and not floor.contains_room(neighbour)
                    and not floor.has_boss_room_as_neighbour(neighbour)
                    and floor.count_neighbours(neighbour[0], neighbour[1]) == 1
                ):
                    distance = util_functions.calculate_distance(boss_room, neighbour)
                    if distance < distance_to_boss:
                        distance_to_boss = distance
                        candidate = neighbour
        if candidate is not None:
            floor.add_room(candidate[0], candidate[1], RoomType.SUPER_SECRET_ROOM)

    def place_secret_room(self) -> None:
        """
        Places a secret room on the floor.
        If no valid position exists, no secret room is placed.
        """
        floor = self._floor
        neighbour_rooms = 3
        while neighbour_rooms > 0:
            for room in reversed(floor.get_rooms()):
                # Check all neighbours of the room
                if self._check_directions_for_secret_room(room, neighbour_rooms):
                    return
            neighbour_rooms -= 1

    def _check_directions_for_secret_room(
        self, room: Room, neighbour_rooms: int
    ) -> bool:
        """
        Checks if a secret room can be placed next to a given room.
        @param room: room to check
        @param neighbour_rooms: number of minimum neighbours
        @return: True if a secret room was placed otherwise False
        """
        floor = self._floor
        for direction in Direction.main_directions():
            neighbour = util_functions.add_direction_to_coordinates(
                direction, (room[0], room[1])
            )
            if not floor.is_within_border(neighbour) or floor.contains_room(neighbour):
                continue
            if floor.has_special_room_as_neighbour(neighbour):
                continue
            current_neighbour = floor.count_neighbours(neighbour[0], neighbour[1])
            if (
                current_neighbour >= neighbour_rooms
                and not floor.has_boss_room_as_neighbour(neighbour)
            ):
                floor.add_room(neighbour[0], neighbour[1], RoomType.SECRET_ROOM)
                return True
        return False

    def save(self, path: str = "") -> str:
        """
        Writes the generated floor in the output file.
        """
        if len(path) > 0:
            output = path
        else:
            time = str(datetime.now().microsecond)
            n = self._output_file_name + time + my_globals.JSON_SUFFIX
            output = os.path.join(self._output_file_path, n)

        with open(output, "w", encoding="utf-8") as file:
            file.write(self.to_json(1))
        return output
