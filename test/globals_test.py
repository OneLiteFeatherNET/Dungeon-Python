import os
import unittest
from utils import globals, room_type
from utils.direction import Direction
from utils.room_type import RoomType


class GlobalsTest(unittest.TestCase):
    def test_directions(self):
        expected = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
            (1, -1),
            (-1, -1),
            (1, 1),
            (-1, 1),
        ]
        self.assertEqual(expected, Direction.list())

    def test_up(self):
        self.assertEqual((0, -1), Direction.UP.value)

    def test_right(self):
        self.assertEqual((1, 0), Direction.RIGHT.value)

    def test_down(self):
        self.assertEqual((0, 1), Direction.DOWN.value)

    def test_left(self):
        self.assertEqual((-1, 0), Direction.LEFT.value)

    def test_up_right(self):
        self.assertEqual((1, -1), Direction.UP_RIGHT.value)

    def test_up_left(self):
        self.assertEqual((-1, -1), Direction.UP_LEFT.value)

    def test_down_right(self):
        self.assertEqual((1, 1), Direction.DOWN_RIGHT.value)

    def test_down_left(self):
        self.assertEqual((-1, 1), Direction.DOWN_LEFT.value)

    def test_door_faces(self):
        expected = [0, 1, 2, 3]
        self.assertEqual(expected, globals.DoorFace.list())

    def test_room_types(self):
        expected = [0, 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(expected, RoomType.list())

    def test_special_rooms(self):
        self.assertEqual(
            (RoomType.ITEM_ROOM, RoomType.SHOP_ROOM), room_type.SPECIAL_ROOMS
        )

    def test_room_width(self):
        self.assertEqual(120, globals.ROOM_WIDTH)

    def test_room_height(self):
        self.assertEqual(60, globals.ROOM_HEIGHT)

    def test_floor_height(self):
        self.assertEqual(8, globals.FLOOR_HEIGHT)

    def test_floor_width(self):
        self.assertEqual(9, globals.FLOOR_WIDTH)

    def test_base_indent(self):
        self.assertEqual("  ", globals.BASE_INDENT)

    def test_json_suffix(self):
        self.assertEqual(".json", globals.JSON_SUFFIX)

    def test_path(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(project_root, globals.APPLICATION_PATH)


if __name__ == "__main__":
    unittest.main()
