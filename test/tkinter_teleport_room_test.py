"""Unit tests for the TkinterTeleportRoom class."""

import unittest

from ui_test_support import requires_tkinter
from utils.room_type import RoomType


@requires_tkinter()
class TkinterTeleportRoomTest(unittest.TestCase):
    def setUp(self) -> None:
        # pylint: disable=import-outside-toplevel
        from rooms.tkinter.tkinter_teleport_room import TkinterTeleportRoom

        self._t_room = TkinterTeleportRoom(1, 2, room_id=3, teleport_room_id=4)

    def test_get_connected_room_id(self):
        self.assertEqual(4, self._t_room.get_connected_room_id())

    def test_room_values(self):
        self.assertEqual((1, 2), (self._t_room[0], self._t_room[1]))
        self.assertEqual(3, self._t_room.get_id())
        self.assertEqual(RoomType.TELEPORT_ROOM, self._t_room.get_type())


if __name__ == "__main__":
    unittest.main()
