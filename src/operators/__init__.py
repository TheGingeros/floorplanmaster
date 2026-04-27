# Operators module — classes registered by addon __init__.py

from .pencil_tool import (
    FLOORPLAN_OT_pencil_tool,
    register_pencil_keymap,
    unregister_pencil_keymap,
)
from .insert_room import FLOORPLAN_OT_insert_room
from .select_wall import FLOORPLAN_OT_select_wall
from .add_opening import FLOORPLAN_OT_add_opening, FLOORPLAN_OT_remove_opening
from .remove_room import FLOORPLAN_OT_remove_room
from .remove_wall import FLOORPLAN_OT_remove_selected_wall
from .finalize import FLOORPLAN_OT_finalize


def get_classes():
    return [
        FLOORPLAN_OT_pencil_tool,
        FLOORPLAN_OT_insert_room,
        FLOORPLAN_OT_select_wall,
        FLOORPLAN_OT_add_opening,
        FLOORPLAN_OT_remove_opening,
        FLOORPLAN_OT_remove_room,
        FLOORPLAN_OT_remove_selected_wall,
        FLOORPLAN_OT_finalize,
    ]
