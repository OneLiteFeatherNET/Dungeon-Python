import random
import unittest
from utils import globals, util_functions


class UtilsTest(unittest.TestCase):
    def test_calculate_room_amount(self):
        rooms = util_functions.calculate_room_amount(2, random.Random(1))
        self.assertTrue(0 < rooms <= globals.MAX_ROOMS)

    def test_calculate_room_amount_follows_the_isaac_formula(self):
        # random(2) + 5 + level * 2.6 with level 1 for the first floor
        expected = {0: {7, 8}, 1: {10, 11}, 2: {12, 13}, 3: {15, 16}, 4: {18, 19}}
        for stage_id, amounts in expected.items():
            with self.subTest(stage_id=stage_id):
                results = {
                    util_functions.calculate_room_amount(stage_id, random.Random(seed))
                    for seed in range(50)
                }
                self.assertEqual(amounts, results)

    def test_place_room(self):
        util_functions.place_room(random.Random(1))


if __name__ == "__main__":
    unittest.main()
