# UI module — classes registered by addon __init__.py

from .panels import (
    FLOORPLAN_PT_main,
    FLOORPLAN_PT_tools,
    FLOORPLAN_PT_rooms,
    FLOORPLAN_PT_settings,
)


def get_classes():
    return [
        FLOORPLAN_PT_main,
        FLOORPLAN_PT_tools,
        FLOORPLAN_PT_rooms,
        FLOORPLAN_PT_settings,
    ]
