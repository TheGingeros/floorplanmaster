# Operators module — classes registered by addon __init__.py

from .pencil_tool import (
    FLOORPLAN_OT_pencil_tool,
    register_pencil_keymap,
    unregister_pencil_keymap,
)
from .insert_room import FLOORPLAN_OT_insert_room
from .select_wall import FLOORPLAN_OT_select_wall, FLOORPLAN_OT_deselect_wall


def get_classes():
    return [
        FLOORPLAN_OT_pencil_tool,
        FLOORPLAN_OT_insert_room,
        FLOORPLAN_OT_select_wall,
        FLOORPLAN_OT_deselect_wall,
    ]
