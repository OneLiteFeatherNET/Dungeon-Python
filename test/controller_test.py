"""Unit tests for the FastAPI controller."""

import unittest

from fastapi.testclient import TestClient

import controller


class ControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._client = TestClient(controller.app)

    def test_negative_floor_id_is_rejected(self):
        response = self._client.get("/gen/-1")

        self.assertEqual(422, response.status_code)

    def test_negative_floor_id_with_seed_is_rejected(self):
        response = self._client.get("/gen/-1/abc")

        self.assertEqual(422, response.status_code)


if __name__ == "__main__":
    unittest.main()
