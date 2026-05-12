"""GPU overlay — wall selection highlight.

Draws a semi-transparent orange OBB box over the currently selected wall.
Registered as a persistent POST_VIEW layer via :mod:`~ui.overlay_manager`.
"""
# GPU overlay — wall selection highlight.
# Draws a semi-transparent orange OBB box over the currently selected wall.
# Registered as a persistent POST_VIEW layer via overlay_manager.

import gpu
import math
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..selection_state import _selection
from ... import _graph_store, get_floorplan_obj_by_name, is_floorplan_mode_active, is_floorplan_obj_visible


def draw_wall_selection(context):
    # Draws a semi-transparent orange OBB box over the currently selected wall.
    # Box is built directly from junction positions + wall.thickness — independent
    # of the mitered mesh geometry, so it is always accurate regardless of sync state.
    if not is_floorplan_mode_active(context):
        return
    wall_uuid = _selection.wall_id
    if not wall_uuid:
        return
    if not context or not getattr(context, 'scene', None):
        return
    obj = get_floorplan_obj_by_name(context, _selection.object_name)
    if obj is None or not is_floorplan_obj_visible(context, obj) or obj.name not in _graph_store:
        return
    sg, _rg, _ = _graph_store[obj.name]
    wall = sg.get_wall(wall_uuid)
    if wall is None:
        return
    j1 = sg.get_junction(wall.junction_start)
    j2 = sg.get_junction(wall.junction_end)
    if j1 is None or j2 is None:
        return
    ax, ay = j1.position
    bx, by = j2.position
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return
    # Unit direction along the wall and perpendicular.
    dx, dy = (bx - ax) / length, (by - ay) / length
    nx, ny = -dy, dx
    EXPAND = 0.03  # metres — extra clearance on top of neighbour insets
    hw = wall.thickness / 2.0 + EXPAND
    h = wall.height
    # Extend each end by the max half-thickness of walls connecting there
    # so the selection box covers the joint area at both junctions.
    all_walls = sg.get_all_walls()
    def _max_half_t(junction_id):
        return max(
            (w.thickness / 2.0 for w in all_walls
             if w.id != wall.id and junction_id in (w.junction_start, w.junction_end)),
            default=0.0,
        )
    start_ext = _max_half_t(j1.id) + EXPAND
    end_ext   = _max_half_t(j2.id) + EXPAND
    # 4 base corners: start and end extended along the wall axis.
    s0x, s0y = ax - dx * start_ext, ay - dy * start_ext
    e0x, e0y = bx + dx * end_ext,   by + dy * end_ext
    b0 = Vector((s0x + nx * hw, s0y + ny * hw, -EXPAND))
    b1 = Vector((e0x + nx * hw, e0y + ny * hw, -EXPAND))
    b2 = Vector((e0x - nx * hw, e0y - ny * hw, -EXPAND))
    b3 = Vector((s0x - nx * hw, s0y - ny * hw, -EXPAND))
    b = [b0, b1, b2, b3]
    t = [Vector((v.x, v.y, h + EXPAND)) for v in b]
    # 6 faces x 2 triangles = 12 tris; both sides rendered (no culling).
    tris = []
    # Bottom
    tris += [b[0], b[1], b[2],  b[0], b[2], b[3]]
    # Top
    tris += [t[0], t[2], t[1],  t[0], t[3], t[2]]
    # Sides
    for i in range(4):
        n = (i + 1) % 4
        tris += [b[i], b[n], t[n],  b[i], t[n], t[i]]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.face_culling_set('NONE')
    batch = batch_for_shader(shader, 'TRIS', {"pos": tris})
    shader.bind()
    shader.uniform_float("color", (1.0, 0.55, 0.1, 0.25))
    batch.draw(shader)
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')
