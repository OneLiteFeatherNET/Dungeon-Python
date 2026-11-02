import random
import unittest
from utils import globals, util_functions


class UtilsTest(unittest.TestCase):
    def test_calculate_room_amount(self):
        rooms = util_functions.calculate_room_amount(2, random.Random(1))
        self.assertTrue(0 < rooms <= globals.MAX_ROOMS)

    def test_place_room(self):
        util_functions.place_room(random.Random(1))


if __name__ == "__main__":
    unittest.main()
