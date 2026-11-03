"""
Colors and sizes used to draw the floors in the tkinter UI.
"""

from dataclasses import dataclass
from typing import Dict

from utils.room_type import RoomType

# Space between the border of a cell and the room drawn in it
ROOM_PADDING_X = 10
ROOM_PADDING_Y = 8
# Radius of the rounded room corners
ROOM_CORNER_RADIUS = 8
# Width of the door connectors between two rooms
DOOR_WIDTH = 14
ICON_SIZE = 28


@dataclass(frozen=True)
class Palette:
    """
    Colors of one theme.
    """

    name: str
    window: str
    panel: str
    canvas: str
    grid: str
    room_outline: str
    door: str
    teleport_link: str
    text: str
    muted_text: str
    button: str
    button_active: str
    entry: str
    rooms: Dict[RoomType, str]


LIGHT = Palette(
    name="light",
    window="#e5e9f0",
    panel="#e5e9f0",
    canvas="#f4f6f9",
    grid="#dde2ea",
    room_outline="#4c566a",
    door="#4c566a",
    teleport_link="#8e6bb8",
    text="#2e3440",
    muted_text="#5e6779",
    button="#ffffff",
    button_active="#d8dee9",
    entry="#ffffff",
    rooms={
        RoomType.NORMAL_ROOM: "#cdd5e1",
        RoomType.DEAD_END: "#b7c1d1",
        RoomType.ITEM_ROOM: "#92c47f",
        RoomType.SHOP_ROOM: "#ebcb6e",
        RoomType.START_ROOM: "#ee9d5e",
        RoomType.TELEPORT_ROOM: "#b28fd8",
        RoomType.BOSS_ROOM: "#d9665f",
        RoomType.SECRET_ROOM: "#7393cf",
        RoomType.SUPER_SECRET_ROOM: "#5fb3b0",
    },
)

DARK = Palette(
    name="dark",
    window="#1b1e24",
    panel="#1b1e24",
    canvas="#232730",
    grid="#2c313c",
    room_outline="#11131a",
    door="#8d97a8",
    teleport_link="#b28fd8",
    text="#e5e9f0",
    muted_text="#a3abb9",
    button="#2e3440",
    button_active="#3b4252",
    entry="#2e3440",
    rooms={
        RoomType.NORMAL_ROOM: "#4c5669",
        RoomType.DEAD_END: "#3e4757",
        RoomType.ITEM_ROOM: "#5f9a55",
        RoomType.SHOP_ROOM: "#c4a446",
        RoomType.START_ROOM: "#cf7a3d",
        RoomType.TELEPORT_ROOM: "#8a64b5",
        RoomType.BOSS_ROOM: "#b84d47",
        RoomType.SECRET_ROOM: "#4f6fae",
        RoomType.SUPER_SECRET_ROOM: "#3f8f8b",
    },
)

_current = LIGHT


def get_palette() -> Palette:
    """
    Returns the palette of the current theme.
    @return: current palette
    """
    return _current


def set_palette(palette: Palette) -> None:
    """
    Sets the palette of the current theme.
    @param palette: palette to use
    """
    global _current  # pylint: disable=global-statement
    _current = palette
