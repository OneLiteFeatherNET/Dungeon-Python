"""
Main file for the dungeon generator.
Parses the command line arguments and calls the generator.
"""

import os.path
import secrets
import sys

from utils import globals as my_globals
from generators.generator import Generator
from generators.tkinter_generator import TkinterGenerator

HELP_MESSAGE = """Creates a dungeon floor and saves it to a json file.
Options:
    -h, --help: Prints this message.
    -s, --seed: Sets the seed for the random number generator.
    -o, --output: Sets the output file name, default is output.json.
    -u, --ui: Enables the UI, default is disabled.
    -f --floor: Sets the id for the floor, default is 0. (Must be 0 or greater)
    """


def main(seed: str, output: str, ui: bool, floor_id):
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
        os.mkdir(output_folder)
        print("No output folder found. Creating specific folder")

    if ui:
        TkinterGenerator(
            seed, my_globals.DEFAULT_FLOOR_NAME, output_folder, floor_id
        ).run()
    else:
        generator = Generator(seed=seed, output_file_name=output, stage_id=floor_id)
        generator.generate()
        generator.save()
        print("Floor saved to " + output)


if __name__ == "__main__":
    _seed: str = ""
    _output: str = "floor"
    _show_ui: bool = False
    _floor_id: int = 2
    i: int = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-s" or sys.argv[i] == "--seed":
            if i + 1 < len(sys.argv):
                _seed = sys.argv[i + 1]
                i += 1
        elif sys.argv[i] == "-u" or sys.argv[i] == "--ui":
            _show_ui = True
        elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
            print(HELP_MESSAGE)
            sys.exit(0)
        elif sys.argv[i] == "-o" or sys.argv[i] == "--output":
            if i + 1 < len(sys.argv):
                _output = sys.argv[i + 1]
                i += 1
        elif sys.argv[i] == "-f" or sys.argv[i] == "--floor":
            if i + 1 < len(sys.argv):
                try:
                    _floor_id = int(sys.argv[i + 1])
                    i += 1
                    if _floor_id < 0:
                        print("The floor id must be greater than 0!")
                        sys.exit(-1)
                except ValueError:
                    print(sys.argv[i + 1] + " is not a valid number!")
                    sys.exit(-1)
        else:
            print(sys.argv[i] + " is not a valid argument!")
            sys.exit(-1)
        i += 1

    if _seed == "":
        _seed = secrets.token_hex(16)

    main(_seed, _output, _show_ui, _floor_id)
