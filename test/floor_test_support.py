"""
Helpers to find seeds with specific floor features for the tests.
"""

import functools

from generators.generator import Generator
from rooms.teleport_room import TeleportRoom


@functools.lru_cache(maxsize=None)
def teleport_seed(stage_id: int = 2) -> str:
    """
    Returns the first seed whose floor has a boss room behind a teleport room.
    @param stage_id: floor id to generate
    @return: seed
    """
    for number in range(10000):
        generator = Generator(str(number), "test", "", stage_id)
        generator.generate()
        if any(isinstance(room, TeleportRoom) for room in generator._floor.get_rooms()):
            return str(number)
    raise AssertionError("no seed with a teleport room found")
