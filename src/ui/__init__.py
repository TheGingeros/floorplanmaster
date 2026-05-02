# UI module — classes registered by addon __init__.py

try:
    import bpy
    _HAS_BPY = True
except ImportError:
    _HAS_BPY = False

if _HAS_BPY:
    from .panels import (
        FLOORPLAN_OT_toggle_room,
        FLOORPLAN_OT_toggle_room_walls,
        FLOORPLAN_OT_toggle_wall_details,
        FLOORPLAN_OT_toggle_wall_openings,
        FLOORPLAN_OT_toggle_wall_position,
        FLOORPLAN_OT_toggle_room_wall_opening,
        FLOORPLAN_OT_select_wall_from_room,
        FLOORPLAN_PT_wall_properties,
        FLOORPLAN_PT_room_properties,
        FLOORPLAN_PT_main,
        FLOORPLAN_PT_tools,
        FLOORPLAN_PT_rooms,
        FLOORPLAN_PT_settings,
    )

    def get_classes():
        return [
            FLOORPLAN_OT_toggle_room,
            FLOORPLAN_OT_toggle_room_walls,
            FLOORPLAN_OT_toggle_wall_details,
            FLOORPLAN_OT_toggle_wall_openings,
            FLOORPLAN_OT_toggle_wall_position,
            FLOORPLAN_OT_toggle_room_wall_opening,
            FLOORPLAN_OT_select_wall_from_room,
            FLOORPLAN_PT_wall_properties,
            FLOORPLAN_PT_room_properties,
            FLOORPLAN_PT_main,
            FLOORPLAN_PT_tools,
            FLOORPLAN_PT_rooms,
            FLOORPLAN_PT_settings,
        ]
else:
    def get_classes():
        return []
