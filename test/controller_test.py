"""Unit tests for the FastAPI controller."""

import json
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import controller


class ControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._client = TestClient(controller.app)

    def test_generate_returns_the_floor_as_json_file(self):
        response = self._client.get("/gen/2/abc")

        self.assertEqual(200, response.status_code)
        self.assertEqual("application/json", response.headers["content-type"])
        self.assertEqual(
            'attachment; filename="floor.json"',
            response.headers["content-disposition"],
        )
        self.assertEqual("abc", json.loads(response.text)["_floor"]["_seed"])

    def test_generate_does_not_write_files(self):
        working_directory = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            try:
                self._client.get("/gen")
                self._client.get("/gen/1")
                self._client.get("/gen/1/abc")
                self.assertEqual([], os.listdir(tmp_dir))
            finally:
                os.chdir(working_directory)

    def test_negative_floor_id_is_rejected(self):
        response = self._client.get("/gen/-1")

        self.assertEqual(422, response.status_code)

    def test_negative_floor_id_with_seed_is_rejected(self):
        response = self._client.get("/gen/-1/abc")

        self.assertEqual(422, response.status_code)


if __name__ == "__main__":
    unittest.main()
