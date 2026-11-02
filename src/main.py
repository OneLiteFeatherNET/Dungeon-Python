"""
Main file for the dungeon generator.
Parses the command line arguments and calls the generator.
"""

import argparse
import os.path
import secrets
from typing import List, Optional

from utils import globals as my_globals
from generators.generator import Generator


def _floor_id(value: str) -> int:
    """
    Parses a floor id from the command line.
    @param value: value to parse
    @return: floor id
    """
    try:
        floor_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{value} is not a valid number") from error
    if floor_id < 0:
        raise argparse.ArgumentTypeError("the floor id must be 0 or greater")
    return floor_id


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses the command line arguments.
    @param argv: arguments to parse, defaults to the command line arguments
    @return: parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Creates a dungeon floor and saves it to a json file."
    )
    parser.add_argument(
        "-s",
        "--seed",
        default="",
        help="seed for the random number generator, default is a random seed",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=my_globals.DEFAULT_FLOOR_NAME,
        help="output file name, default is %(default)s",
    )
    parser.add_argument(
        "-u", "--ui", action="store_true", help="enables the UI, default is disabled"
    )
    parser.add_argument(
        "-f",
        "--floor",
        type=_floor_id,
        default=2,
        help="id for the floor, must be 0 or greater, default is %(default)s",
    )
    return parser.parse_args(argv)


def main(seed: str, output: str, ui: bool, floor_id: int) -> None:
    """
    Main function for the dungeon generator.
    @param seed: Seed for the random number generator.
    @param output: Output file name.
    @param ui: Enable the UI.
    @param floor_id: Id for the floor.
    """
    output_folder = os.path.join(my_globals.APPLICATION_PATH, "generation")
    output = os.path.join(output_folder, output)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print("No output folder found. Creating specific folder")

    if ui:
        # Imported here so the command line works without tkinter
        # pylint: disable=import-outside-toplevel
        from generators.tkinter_generator import TkinterGenerator

        TkinterGenerator(
            seed, my_globals.DEFAULT_FLOOR_NAME, output_folder, floor_id
        ).run()
    else:
        generator = Generator(seed=seed, output_file_name=output, stage_id=floor_id)
        generator.generate()
        path = generator.save()
        print("Floor saved to " + path)


if __name__ == "__main__":
    arguments = parse_arguments()
    main(
        arguments.seed or secrets.token_hex(16),
        arguments.output,
        arguments.ui,
        arguments.floor,
    )
