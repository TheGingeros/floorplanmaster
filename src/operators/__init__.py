# Operators module — classes registered by addon __init__.py

from .pencil_tool import (
    FLOORPLAN_OT_pencil_tool
)
from .insert_room import FLOORPLAN_OT_insert_room
from .select_wall import FLOORPLAN_OT_select_wall
from .floorplan_mode import FLOORPLAN_OT_floorplan_modal, FLOORPLAN_OT_toggle_mode
from .add_opening import FLOORPLAN_OT_add_opening, FLOORPLAN_OT_remove_opening
from .remove_room import FLOORPLAN_OT_remove_room
from .remove_wall import FLOORPLAN_OT_remove_selected_wall
from .edit_mode_detach import (
    FLOORPLAN_OT_edit_mode_detach_bake,
    FLOORPLAN_OT_edit_mode_detach_cancel,
    FLOORPLAN_OT_edit_mode_detach_lose_data,
    FLOORPLAN_OT_edit_mode_with_detach,
)
from .finalize import FLOORPLAN_OT_finalize


def get_classes():
    return [
        FLOORPLAN_OT_pencil_tool,
        FLOORPLAN_OT_insert_room,
        FLOORPLAN_OT_select_wall,
        FLOORPLAN_OT_floorplan_modal,
        FLOORPLAN_OT_toggle_mode,
        FLOORPLAN_OT_add_opening,
        FLOORPLAN_OT_remove_opening,
        FLOORPLAN_OT_remove_room,
        FLOORPLAN_OT_remove_selected_wall,
        FLOORPLAN_OT_edit_mode_detach_cancel,
        FLOORPLAN_OT_edit_mode_detach_bake,
        FLOORPLAN_OT_edit_mode_detach_lose_data,
        FLOORPLAN_OT_edit_mode_with_detach,
        FLOORPLAN_OT_finalize,
    ]
