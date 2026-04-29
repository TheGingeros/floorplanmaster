# GPU overlay — active FloorPlan object hint (POST_PIXEL).
# Shows a bottom-left text cue when a FloorPlan object is active.

import blf


def draw_active_floorplan_hint(context):
    from ... import find_floorplan_obj
    from ...operators import pencil_tool

    obj = find_floorplan_obj(context)
    if obj is None:
        return
    if pencil_tool._pencil_state is not None:
        return

    font_id = 0
    blf.size(font_id, 16)
    blf.color(font_id, 1.0, 1.0, 1.0, 0.8)
    blf.position(font_id, 20, 40, 0)
    blf.draw(font_id, f"FloorPlanMaster - FloorPlan MODE: {obj.name}")
