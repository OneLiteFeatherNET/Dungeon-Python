# Python Dungeon Generator

A small generator for 2D dungeon floors.
The algorithm is based on the floor generation of the game "The Binding of Isaac",
which is described in this [article](https://www.boristhebrave.com/2020/09/12/dungeon-generation-in-binding-of-isaac/).

A floor is a grid of 9 × 8 cells with a start room, normal rooms, dead ends and a boss room.
Depending on the layout it also contains an item room, a shop and secret rooms.
The same seed and floor id always produce the same floor.

The generator can be used in three ways:

- as a [command line tool](#command-line) that writes the floor to a JSON file
- with a [Tkinter UI](#user-interface) that draws the floors
- as a [REST API](#rest-api) that returns the floor as JSON

## Installation

Requires Python 3.12 or newer. The UI additionally needs Tkinter
(on Debian/Ubuntu: `apt install python3-tk`).

```bash
pip install -r requirements.txt
```

## Command line

```bash
python src/main.py -s my-seed -f 3 -o my-floor
```

| Option | Description | Default |
|---|---|---|
| `-s`, `--seed` | Seed for the random number generator | random seed |
| `-f`, `--floor` | Floor id, must be 0 or greater. Higher floor ids get more rooms (at most 15) | `2` |
| `-o`, `--output` | Name of the output file | `floor` |
| `-u`, `--ui` | Opens the UI instead of writing a file | disabled |
| `-h`, `--help` | Shows the help | |

The floor is saved in the `generation` folder in the project root.
A number based on the current time is appended to the file name, e.g. `generation/my-floor123456.json`.

## User interface

```bash
python src/main.py --ui
```

The UI draws a generated floor room by room, including the doors between the rooms
and an arrow from a teleport room to its target. Every generated floor is kept,
so you can switch between them. A legend next to the floor shows the room types
and how often they appear on the current floor.
All actions are also available in the File, View and Floor menus.

| Key | Action |
|---|---|
| `Space` | Generate a new floor with the seed from the "Next seed" field |
| `Enter` in "Next seed" | Generate a new floor with the entered seed |
| `←` / `→` | Switch to the previous / next floor |
| `Ctrl+O` | Open a floor from a JSON file |
| `Ctrl+S` | Save the current floor |
| `Ctrl+Shift+S` | Save the current floor as a new file |
| `Ctrl+T` | Switch between light and dark theme |
| `F1` | Show or hide the legend |
| `Ctrl+Q` | Quit |

## REST API

```bash
pip install -r requirements.txt
python -m uvicorn controller:app --app-dir src --port 8000
```

Or with Docker:

```bash
docker build -t dungeon-python .
docker run -p 8000:8000 dungeon-python
```

| Endpoint | Description |
|---|---|
| `GET /gen` | Floor with id 0 and a random seed |
| `GET /gen/{floor_id}` | Floor with the given id and a random seed |
| `GET /gen/{floor_id}/{seed}` | Floor with the given id and seed |

All endpoints return the floor as `application/json` with the file name `floor.json`.
A negative floor id returns `422`.

## Floor format

```json
{
  "_width": 9,
  "_height": 8,
  "_floor": {
    "_seed": "2",
    "_rooms": [
      {
        "_doors": [2],
        "_id": 0,
        "_type": 4,
        "_x": 3,
        "_y": 0
      },
      {
        "_doors": [3, 2],
        "_id": 12,
        "_type": 5,
        "_x": 8,
        "_y": 1,
        "_connected_room_id": 3
      }
    ]
  },
  "_generated_by": "python"
}
```

| Field | Description |
|---|---|
| `_width`, `_height` | Size of the floor in rooms |
| `_floor._seed` | Seed the floor was generated with |
| `_floor._rooms` | List of all rooms |
| `_id` | Id of the room, unique within the floor |
| `_type` | [Room type](#room-types) |
| `_x`, `_y` | Position of the room. `0, 0` is the top left corner, `y` grows downwards |
| `_doors` | [Doors](#doors) of the room |
| `_connected_room_id` | Only for teleport rooms: id of the room the teleport leads to |

### Room types

| Value | Type |
|---|---|
| 0 | Normal room |
| 1 | Dead end |
| 2 | Item room |
| 3 | Shop |
| 4 | Start room |
| 5 | Teleport room |
| 6 | Boss room |
| 7 | Secret room |

A boss room can span up to 2 × 2 cells, every cell is stored as its own room.
On some floors the boss room is moved to a free cell away from the other rooms
and can only be reached through a teleport room.

### Doors

| Value | Door |
|---|---|
| 0 | Top |
| 1 | Right |
| 2 | Bottom |
| 3 | Left |

## Development

```bash
pip install -r requirements-dev.txt
```

| Check | Command |
|---|---|
| Tests | `pytest` |
| Formatting | `black --check src test` |
| Linting | `pylint src --rcfile=.pylintrc` and `flake8 src test` |
| Type checks | `mypy` |

The UI tests are skipped when no display is available. On Linux they can be run with `xvfb-run -a pytest`.

Pull requests target the `dev` branch.
