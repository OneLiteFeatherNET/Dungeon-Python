"""
Makes sure that a seed and floor id always produce the same floor.

The expected floors are stored as hashes in resources/floor_hashes.json.
If a change to the generation is intended, regenerate them with:
    python test/seed_stability_test.py --update
"""

import hashlib
import json
import os
import sys
import unittest
from typing import Dict

_HASH_FILE = os.path.join(os.path.dirname(__file__), "resources", "floor_hashes.json")
_SEEDS = [str(number) for number in range(50)] + [
    "abc",
    "test-seed",
    'a"b',
    "ä🙂",
    "78d11f0d5a8bd74e510194e16e4b352a",
]
_FLOOR_IDS = range(6)


def _floor_hash(seed: str, floor_id: int) -> str:
    # pylint: disable=import-outside-toplevel
    from generators.generator import Generator

    generator = Generator(seed, "floor", stage_id=floor_id)
    generator.generate()
    # Only the floor itself is pinned, so new metadata does not change the hashes
    canonical = json.dumps(
        generator.to_dict()["_floor"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _current_hashes() -> Dict[str, str]:
    return {
        f"{floor_id}/{seed}": _floor_hash(seed, floor_id)
        for floor_id in _FLOOR_IDS
        for seed in _SEEDS
    }


class SeedStabilityTest(unittest.TestCase):
    def test_seeds_produce_the_same_floors(self):
        with open(_HASH_FILE, encoding="utf-8") as file:
            expected = json.load(file)

        current = _current_hashes()

        changed = sorted(key for key in expected if current.get(key) != expected[key])
        self.assertEqual(
            [],
            changed,
            f"{len(changed)} of {len(expected)} floors changed (floor id/seed). "
            "Existing seeds must keep producing the same floors.",
        )
        self.assertEqual(sorted(expected), sorted(current))


if __name__ == "__main__":
    if "--update" in sys.argv:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        with open(_HASH_FILE, "w", encoding="utf-8") as hash_file:
            json.dump(_current_hashes(), hash_file, indent=2, ensure_ascii=False)
            hash_file.write("\n")
        print(f"Updated {_HASH_FILE}")
    else:
        unittest.main()
