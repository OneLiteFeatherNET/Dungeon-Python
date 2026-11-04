# Python Dungeon Generator

A small generator for 2D dungeon floors.
The algorithm is based on the floor generation of the game "The Binding of Isaac",
which is described in this [article](https://www.boristhebrave.com/2020/09/12/dungeon-generation-in-binding-of-isaac/).

A floor is a grid of 9 × 8 cells with a start room, normal rooms, dead ends, a boss room,
an item room, a shop, a secret room and a super secret room.
Like in the game, a floor is generated again until it has enough rooms
and dead ends for the special rooms.
The same seed and floor id always produce the same floor,
and every floor id produces a different floor for the same seed.

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
| `-f`, `--floor` | Floor id, must be 0 or greater. Higher floor ids get more rooms (7 to 8 on floor 0, up to 20) | `2` |
| `-o`, `--output` | Name of the output file | `floor` |
| `-u`, `--ui` | Opens the UI instead of writing a file | disabled |
| `-h`, `--help` | Shows the help | |

The floor is saved in the `generation` folder in the project root.
A number based on the current time is appended to the file name, e.g. `generation/my-floor123456.json`.

## User interface

```bash
python src/main.py --ui
```

The UI draws a generated floor step by step, spreading from the start room through the doors
and revealing the secret rooms last. It shows the doors between the rooms
and an arrow from a teleport room to its target. Every generated floor is kept,
so you can switch between them. A legend next to the floor shows the room types
and how often they appear on the current floor.
The status bar shows the seed and floor id of the shown floor
and its position in the history.
Resting the mouse on a room shows its type, id, position, doors and teleport connection,
and the controls show what they do and their keyboard shortcut.
All actions are also available in the File, View and Floor menus.

| Key | Action |
|---|---|
| `Space` | Generate a new floor with the seed from the "Next seed" field and the floor id from the "Floor" field |
| `Enter` in "Next seed" or "Floor" | Generate a new floor with the entered values |
| `Page Up` / `Page Down` | Increase / decrease the floor id in the "Floor" field |
| `←` / `→` | Go back / forward in the history of generated floors |
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

## How floors are generated

The floor plan follows the algorithm of the original "The Binding of Isaac"
as described in the [article](https://www.boristhebrave.com/2020/09/12/dungeon-generation-in-binding-of-isaac/):

1. The floor needs `random(2) + 5 + level * 2.6` rooms, where floor id 0 is level 1.
2. The start room is placed at cell 35, the middle of the 9 × 8 grid.
3. The floor grows breadth first from the start room. A neighbour cell only gets a room
   if it is empty, has at most one filled neighbour, the floor still needs rooms
   and a random 50 % check passes. Floors with more than 16 rooms grow again from the
   start room. Rooms that do not add a neighbour are dead ends.
4. A floor is generated again if it misses its room amount, if the boss room would be
   next to the start room or if there are not enough dead ends for the special rooms.
5. The boss room is placed on the farthest dead end, the item room and shop on random
   dead ends.
6. The secret room is placed on a random empty cell next to as many rooms as possible
   and not next to a dead end.

On top of that, this generator adds some features that are not part of the original game:

- a super secret room next to exactly one room, close to the boss room
- boss rooms that span 1 × 2 or 2 × 2 cells
- a teleport room to the boss room when the boss room has no space next to it
- item room and shop are never placed directly next to the start room

## Floor format

```json
{
  "_width": 9,
  "_height": 8,
  "_floor_id": 2,
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
| `_floor_id` | Floor id the floor was generated for. Together with the seed it reproduces the floor |
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
| 8 | Super secret room, connected to only one room and placed close to the boss room |

Most boss rooms are a single cell, some span 1 × 2 or 2 × 2 cells
and every cell is stored as its own room.
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
CI sets `REQUIRE_UI_TESTS=1`, which makes them fail instead of being skipped.

Pull requests target the `dev` branch.
