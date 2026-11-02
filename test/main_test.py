"""Unit tests for the command line interface."""

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import main


class ParseArgumentsTest(unittest.TestCase):
    def test_defaults(self):
        arguments = main.parse_arguments([])

        self.assertEqual("", arguments.seed)
        self.assertEqual("floor", arguments.output)
        self.assertFalse(arguments.ui)
        self.assertEqual(2, arguments.floor)

    def test_all_options(self):
        arguments = main.parse_arguments(["-s", "abc", "-o", "out", "-u", "-f", "0"])

        self.assertEqual("abc", arguments.seed)
        self.assertEqual("out", arguments.output)
        self.assertTrue(arguments.ui)
        self.assertEqual(0, arguments.floor)

    def test_invalid_floor_ids_are_rejected(self):
        for value in ("-1", "x"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()):
                    main.parse_arguments(["-f", value])


class MainTest(unittest.TestCase):
    def test_main_saves_the_floor_in_the_generation_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir, mock.patch(
            "utils.globals.APPLICATION_PATH", tmp_dir
        ), contextlib.redirect_stdout(io.StringIO()):
            main.main("abc", "out", False, 1)

            files = os.listdir(os.path.join(tmp_dir, "generation"))
            self.assertEqual(1, len(files))
            with open(
                os.path.join(tmp_dir, "generation", files[0]), encoding="utf-8"
            ) as file:
                self.assertEqual("abc", json.load(file)["_floor"]["_seed"])


if __name__ == "__main__":
    unittest.main()
