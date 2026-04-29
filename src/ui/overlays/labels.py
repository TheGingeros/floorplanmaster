# pyright: reportMissingImports=false
# GPU overlay — viewport labels for rooms, walls, doors and windows.
# Runs as a persistent POST_PIXEL layer via overlay_manager (one per scene).
# Each element type has an independent toggle; a master switch gates all of them.
#
# Projection: 3D world positions → 2D screen pixels via
# bpy_extras.view3d_utils.location_3d_to_region_2d.  Returns None when a
# point is behind the camera; those labels are silently skipped.
#
# Extension points (future overlays such as dimensions):
#   - Add new per-type colour / size constants at the top of this file.
#   - Add a new _draw_<type>_labels() helper with the same (context, sg, rg,
#     mapper, region, rv3d, settings) signature.
#   - Call it from draw_labels() under a new show_<type>_labels guard.

import math
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from ... import _graph_store, is_floorplan_obj, is_floorplan_obj_visible

# Font sizes (Blender font_id=0 is the built-in proportional font).
_FONT_ID = 0
_ROOM_FONT_SIZE  = 14
_WALL_FONT_SIZE  = 11
_DOOR_FONT_SIZE  = 11
_WINDOW_FONT_SIZE = 11

# RGBA colours.
_ROOM_COLOR   = (1.0, 1.0, 1.0, 0.95)
_WALL_COLOR   = (0.7, 0.85, 1.0, 0.90)
_DOOR_COLOR   = (0.0, 0.85, 1.0, 0.90)
_WINDOW_COLOR = (0.78, 0.55, 1.0, 0.90)

# Vertical line spacing for multi-line wall label (pixels).
_LINE_SPACING = 14

# Room labels should sit close to floor plane, not at mid-height.
_ROOM_LABEL_Z_OFFSET = 0.08

# Wall/opening center-collision avoidance in screen space.
_CENTER_OPENING_THRESHOLD = 0.18
_CENTER_COLLISION_SHIFT_PX = 18


def _project(pos3d, region, rv3d):
    """Project a (x, y, z) world-space point to region pixel coords.

    Returns a Vector((px, py)) or None if behind the camera.
    """
    return location_3d_to_region_2d(region, rv3d, Vector(pos3d))


def _draw_text(text, px, py, font_size, color):
    """Draw *text* at pixel position (px, py) with given size and colour."""
    blf.size(_FONT_ID, font_size)
    blf.color(_FONT_ID, *color)
    blf.position(_FONT_ID, px, py, 0.0)
    blf.draw(_FONT_ID, text)


def _is_opening_label_visible(opening, settings):
    if opening.opening_type == 'DOOR':
        return settings.show_door_labels
    return settings.show_window_labels


def _has_center_opening_label(wall, settings):
    for opening in getattr(wall, "openings", []):
        if not _is_opening_label_visible(opening, settings):
            continue
        if abs(opening.position - 0.5) <= _CENTER_OPENING_THRESHOLD:
            return True
    return False


def _draw_room_labels(context, sg, rg, mapper, region, rv3d, settings):
    if not settings.show_room_labels:
        return
    for room in rg.get_all_rooms():
        cx, cy = room.centroid
        if len(room.cycle) < 3:
            continue
        label_z = min(room.height * 0.25, _ROOM_LABEL_Z_OFFSET)
        pos = _project((cx, cy, label_z), region, rv3d)
        if pos is None:
            continue
        label = room.name
        blf.size(_FONT_ID, _ROOM_FONT_SIZE)
        w, _h = blf.dimensions(_FONT_ID, label)
        _draw_text(label, pos.x - w * 0.5, pos.y - _ROOM_FONT_SIZE * 0.5, _ROOM_FONT_SIZE, _ROOM_COLOR)


def _draw_wall_labels(context, sg, rg, mapper, region, rv3d, settings):
    if not settings.show_wall_labels:
        return
    for wall in sg.get_all_walls():
        j_start = sg.get_junction(wall.junction_start)
        j_end   = sg.get_junction(wall.junction_end)
        if j_start is None or j_end is None:
            continue
        sx, sy = j_start.position
        ex, ey = j_end.position
        mx, my = (sx + ex) * 0.5, (sy + ey) * 0.5
        mid_z  = wall.height * 0.5
        pos = _project((mx, my, mid_z), region, rv3d)
        if pos is None:
            continue
        wall_num = mapper.get(wall.id)
        length   = math.hypot(ex - sx, ey - sy)
        line1 = f"Wall #{wall_num}"
        line2 = f"{length:.2f} m"
        blf.size(_FONT_ID, _WALL_FONT_SIZE)
        w1, _ = blf.dimensions(_FONT_ID, line1)
        w2, _ = blf.dimensions(_FONT_ID, line2)
        y_shift = _CENTER_COLLISION_SHIFT_PX if _has_center_opening_label(wall, settings) else 0.0
        _draw_text(line1, pos.x - w1 * 0.5, pos.y + _LINE_SPACING * 0.5 + y_shift, _WALL_FONT_SIZE, _WALL_COLOR)
        _draw_text(line2, pos.x - w2 * 0.5, pos.y - _LINE_SPACING * 0.5 + y_shift, _WALL_FONT_SIZE, _WALL_COLOR)


def _draw_opening_labels(context, sg, rg, mapper, region, rv3d, settings):
    show_doors   = settings.show_door_labels
    show_windows = settings.show_window_labels
    if not show_doors and not show_windows:
        return
    for wall in sg.get_all_walls():
        j_start = sg.get_junction(wall.junction_start)
        j_end   = sg.get_junction(wall.junction_end)
        if j_start is None or j_end is None:
            continue
        sx, sy = j_start.position
        dx = j_end.position[0] - sx
        dy = j_end.position[1] - sy
        for opening in getattr(wall, "openings", []):
            is_door   = opening.opening_type == 'DOOR'
            is_window = opening.opening_type == 'WINDOW'
            if is_door and not show_doors:
                continue
            if is_window and not show_windows:
                continue
            cx = sx + opening.position * dx
            cy = sy + opening.position * dy
            cz = opening.sill_height + opening.height * 0.5
            pos = _project((cx, cy, cz), region, rv3d)
            if pos is None:
                continue
            op_num = mapper.get(opening.id)
            if is_door:
                label = f"Door #{op_num}"
                color = _DOOR_COLOR
                font_size = _DOOR_FONT_SIZE
            else:
                label = f"Window #{op_num}"
                color = _WINDOW_COLOR
                font_size = _WINDOW_FONT_SIZE
            blf.size(_FONT_ID, font_size)
            w, _ = blf.dimensions(_FONT_ID, label)
            y_shift = -_CENTER_COLLISION_SHIFT_PX if abs(opening.position - 0.5) <= _CENTER_OPENING_THRESHOLD else 0.0
            _draw_text(label, pos.x - w * 0.5, pos.y - font_size * 0.5 + y_shift, font_size, color)


def draw_labels(context):
    """Main entry point — called by overlay_manager POST_PIXEL handler."""
    settings = getattr(getattr(context, "scene", None), "floorplan", None)
    if settings is None or not settings.show_labels:
        return

    region  = getattr(context, "region", None)
    rv3d    = getattr(context, "region_data", None)
    if region is None or rv3d is None:
        return

    for obj in context.scene.objects:
        if not is_floorplan_obj(obj):
            continue
        if not is_floorplan_obj_visible(context, obj):
            continue
        if obj.name not in _graph_store:
            continue
        sg, rg, mapper = _graph_store[obj.name]
        _draw_room_labels(context, sg, rg, mapper, region, rv3d, settings)
        _draw_wall_labels(context, sg, rg, mapper, region, rv3d, settings)
        _draw_opening_labels(context, sg, rg, mapper, region, rv3d, settings)
