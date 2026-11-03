"""
This file contains the RoomType enum.
"""

from enum import Enum
from typing import List


class RoomType(Enum):
    """
    Enum for the room types.
    """

    @classmethod
    def list(cls) -> List[int]:
        """
        Returns a list of all the room types.
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_all(cls) -> List:
        """
        Returns a list of all the room types.
        """
        return list(cls)

    def is_special(self) -> bool:
        """
        Checks if the room type is special.
        Special rooms are rooms that have a special function.
        Special rooms are:
        - Item room
        - Shop room
        - Boss room
        - Secret room
        @return: True if special otherwise False
        """
        return self in (
            RoomType.ITEM_ROOM,
            RoomType.SHOP_ROOM,
            RoomType.BOSS_ROOM,
            RoomType.SECRET_ROOM,
            RoomType.SUPER_SECRET_ROOM,
        )

    NORMAL_ROOM = 0
    DEAD_END = 1
    ITEM_ROOM = 2
    SHOP_ROOM = 3
    START_ROOM = 4
    TELEPORT_ROOM = 5
    BOSS_ROOM = 6
    SECRET_ROOM = 7
    SUPER_SECRET_ROOM = 8


room_names = {
    RoomType.NORMAL_ROOM: "Normal Room",
    RoomType.DEAD_END: "Dead End",
    RoomType.ITEM_ROOM: "Item Room",
    RoomType.SHOP_ROOM: "Shop Room",
    RoomType.START_ROOM: "Start Room",
    RoomType.TELEPORT_ROOM: "Teleport Room",
    RoomType.BOSS_ROOM: "Boss Room",
    RoomType.SECRET_ROOM: "Secret Room",
    RoomType.SUPER_SECRET_ROOM: "Super Secret Room",
}

SPECIAL_ROOMS = (RoomType.ITEM_ROOM, RoomType.SHOP_ROOM)
