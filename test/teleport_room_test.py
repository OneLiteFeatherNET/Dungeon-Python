import unittest

from rooms.teleport_room import TeleportRoom
from utils.globals import DoorFace


class TeleportRoomTest(unittest.TestCase):
    def setUp(self) -> None:
        self._t_room = TeleportRoom(1, 2, 3, 4)

    def test_get_connected_room(self):
        self.assertEqual(4, self._t_room.get_connected_room_id())

    def test_to_dict_contains_the_connected_room_id(self):
        self.assertEqual(4, self._t_room.to_dict()["_connected_room_id"])

    def test_from_dict_restores_the_teleport_room(self):
        self._t_room.add_door(DoorFace.EAST)

        restored = TeleportRoom.from_dict(self._t_room.to_dict())

        self.assertEqual(self._t_room, restored)
        self.assertEqual(4, restored.get_connected_room_id())
        self.assertEqual([DoorFace.EAST], restored.get_doors())


if __name__ == "__main__":
    unittest.main()
