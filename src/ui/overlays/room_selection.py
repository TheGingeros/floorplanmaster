"""GPU overlay — room selection highlight.

Draws a semi-transparent orange floor fill and orange wireframe OBB lines
for each boundary wall of the currently selected room.
Registered as a persistent POST_VIEW layer via :mod:`~ui.overlay_manager`.
"""
# GPU overlay — room selection highlight.
# Draws a semi-transparent orange floor fill and orange wireframe OBB lines
# for each boundary wall of the currently selected room.
# Registered as a persistent POST_VIEW layer via overlay_manager.

import gpu
import math
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..selection_state import _selection
from ... import _graph_store, get_floorplan_obj_by_name, is_floorplan_mode_active, is_floorplan_obj_visible

# Small Z lift to avoid z-fighting with the mesh floor face at Z=0.
_FLOOR_Z = 0.005
# Expand for wall OBB wireframe — matches wall_selection.py constant.
_EXPAND = 0.03


def _build_wall_obb(wall, sg, all_walls):
    # Return (b, t) — each a list of 4 Vectors (base / top corners of the OBB).
    # Returns None if the wall is degenerate.
    j1 = sg.get_junction(wall.junction_start)
    j2 = sg.get_junction(wall.junction_end)
    if j1 is None or j2 is None:
        return None
    ax, ay = j1.position
    bx, by = j2.position
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return None
    dx, dy = (bx - ax) / length, (by - ay) / length
    nx, ny = -dy, dx
    hw = wall.thickness / 2.0 + _EXPAND
    h = wall.height

    def _max_half_t(junction_id):
        return max(
            (w.thickness / 2.0 for w in all_walls
             if w.id != wall.id and junction_id in (w.junction_start, w.junction_end)),
            default=0.0,
        )

    start_ext = _max_half_t(j1.id) + _EXPAND
    end_ext   = _max_half_t(j2.id) + _EXPAND

    s0x, s0y = ax - dx * start_ext, ay - dy * start_ext
    e0x, e0y = bx + dx * end_ext,   by + dy * end_ext

    b0 = Vector((s0x + nx * hw, s0y + ny * hw, -_EXPAND))
    b1 = Vector((e0x + nx * hw, e0y + ny * hw, -_EXPAND))
    b2 = Vector((e0x - nx * hw, e0y - ny * hw, -_EXPAND))
    b3 = Vector((s0x - nx * hw, s0y - ny * hw, -_EXPAND))
    base = [b0, b1, b2, b3]
    top  = [Vector((v.x, v.y, h + _EXPAND)) for v in base]
    return base, top


def draw_room_selection(context):
    # Draws an orange semi-transparent floor fill + orange OBB wireframe for
    # each boundary wall of the currently selected room.
    if not is_floorplan_mode_active(context):
        return
    room_uuid = _selection.room_id
    if not room_uuid:
        return
    if not context or not getattr(context, 'scene', None):
        return
    obj = get_floorplan_obj_by_name(context, _selection.object_name)
    if obj is None or not is_floorplan_obj_visible(context, obj) or obj.name not in _graph_store:
        return
    sg, rg, _ = _graph_store[obj.name]
    room = rg.get_room(room_uuid)
    if room is None:
        return

    # Gather ordered floor vertices from the room cycle.
    verts_2d = sg.get_cycle_vertices(room.cycle)  # list of (x, y)
    if len(verts_2d) < 3:
        return

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.face_culling_set('NONE')

    # Floor fill — fan triangulation at Z = _FLOOR_Z.
    floor_verts = [Vector((x, y, _FLOOR_Z)) for x, y in verts_2d]
    tris = []
    for i in range(1, len(floor_verts) - 1):
        tris += [floor_verts[0], floor_verts[i], floor_verts[i + 1]]

    gpu.state.depth_test_set('LESS_EQUAL')
    batch_floor = batch_for_shader(shader, 'TRIS', {"pos": tris})
    shader.bind()
    shader.uniform_float("color", (1.0, 0.55, 0.1, 0.25))
    batch_floor.draw(shader)

    # Boundary wall OBB wireframes — 12 edges per wall (4 bottom + 4 top + 4 vertical).
    all_walls = sg.get_all_walls()
    n = len(room.cycle)
    lines = []
    for i in range(n):
        ja = room.cycle[i]
        jb = room.cycle[(i + 1) % n]
        wall = sg.get_wall_between(ja, jb)
        if wall is None:
            continue
        obb = _build_wall_obb(wall, sg, all_walls)
        if obb is None:
            continue
        b, t = obb
        # Bottom ring
        for k in range(4):
            lines += [b[k], b[(k + 1) % 4]]
        # Top ring
        for k in range(4):
            lines += [t[k], t[(k + 1) % 4]]
        # Vertical pillars
        for k in range(4):
            lines += [b[k], t[k]]

    if lines:
        gpu.state.depth_test_set('LESS_EQUAL')
        batch_lines = batch_for_shader(shader, 'LINES', {"pos": lines})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.55, 0.1, 0.9))
        batch_lines.draw(shader)

    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')
