"""
Describes rooms of a floor in a short text, e.g. for tooltips.
"""

from typing import List

from floors.floor import Floor
from rooms.room import Room
from rooms.teleport_room import TeleportRoom
from utils.globals import DoorFace
from utils.room_type import RoomType, room_names

_DOOR_NAMES = {
    DoorFace.TOP: "top",
    DoorFace.EAST: "right",
    DoorFace.BOTTOM: "bottom",
    DoorFace.WEST: "left",
}
_BOSS_ROOM_SHAPES = {2: "1 × 2", 4: "2 × 2"}


def describe_room(floor: Floor, room: Room) -> str:
    """
    Describes a room with its type, id, position, doors and connections.
    @param floor: floor that contains the room
    @param room: room to describe
    @return: description with one fact per line
    """
    lines: List[str] = [
        f"{room_names[room.get_type()]} · #{room.get_id()}",
        f"Position {room[0]}, {room[1]}",
    ]
    doors = sorted(room.get_doors(), key=lambda door: door.value)
    door_names = ", ".join(_DOOR_NAMES[door] for door in doors)
    lines.append(f"Doors: {door_names or 'none'}")

    rooms_by_id = {other.get_id(): other for other in floor.get_rooms()}
    if isinstance(room, TeleportRoom):
        target = rooms_by_id.get(room.get_connected_room_id())
        if target is not None:
            lines.append(
                f"Teleports to #{target.get_id()} ({room_names[target.get_type()]})"
            )
    if room.get_type() == RoomType.BOSS_ROOM:
        cells = sum(
            other.get_type() == RoomType.BOSS_ROOM for other in floor.get_rooms()
        )
        if cells in _BOSS_ROOM_SHAPES:
            lines.append(f"Part of a {_BOSS_ROOM_SHAPES[cells]} boss room")
    for other in floor.get_rooms():
        if (
            isinstance(other, TeleportRoom)
            and other.get_connected_room_id() == room.get_id()
        ):
            lines.append(f"Reached through teleport #{other.get_id()}")
    return "\n".join(lines)
