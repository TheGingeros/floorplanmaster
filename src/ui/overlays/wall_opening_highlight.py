# pyright: reportMissingImports=false
# GPU overlay — always-visible wall/opening edge highlights.
# Draws geometry-matching wall edges for every visible FloorPlan object.
# Openings are highlighted by type: doors (cyan), windows (purple).

import gpu
import math
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ... import _graph_store, is_floorplan_obj, is_floorplan_obj_visible
from ...core.sync import _compute_wall_quad


_WALL_COLOR = (0.0, 0.0, 0.0, 0.95)
_DOOR_COLOR = (0.0, 0.85, 1.0, 0.95)
_WINDOW_COLOR = (0.62, 0.22, 0.95, 0.95)
_LINE_WIDTH = 3.0


def _append_box_edges(lines, p0, p1, p2, p3, z_min, z_max):
    b0 = Vector((p0[0], p0[1], z_min))
    b1 = Vector((p1[0], p1[1], z_min))
    b2 = Vector((p2[0], p2[1], z_min))
    b3 = Vector((p3[0], p3[1], z_min))
    t0 = Vector((p0[0], p0[1], z_max))
    t1 = Vector((p1[0], p1[1], z_max))
    t2 = Vector((p2[0], p2[1], z_max))
    t3 = Vector((p3[0], p3[1], z_max))

    # Bottom ring.
    lines.extend([b0, b1, b1, b2, b2, b3, b3, b0])
    # Top ring.
    lines.extend([t0, t1, t1, t2, t2, t3, t3, t0])
    # Vertical edges.
    lines.extend([b0, t0, b1, t1, b2, t2, b3, t3])


def _draw_lines(shader, lines, color):
    if not lines:
        return
    batch = batch_for_shader(shader, 'LINES', {"pos": lines})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _collect_lines_for_object(sg):
    wall_lines = []
    door_lines = []
    window_lines = []

    walls = sg.get_all_walls()
    junctions_by_id = {j.id: j for j in sg.get_all_junctions()}

    for wall in walls:
        quad = _compute_wall_quad(wall, junctions_by_id, sg)
        if quad is not None:
            p0, p1, p2, p3 = quad
            _append_box_edges(wall_lines, p0, p1, p2, p3, 0.0, wall.height)

        j_start = junctions_by_id.get(wall.junction_start)
        j_end = junctions_by_id.get(wall.junction_end)
        if j_start is None or j_end is None:
            continue
        sx, sy = j_start.position
        ex, ey = j_end.position
        dx = ex - sx
        dy = ey - sy
        length = math.hypot(dx, dy)
        if length < 1e-9:
            continue
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux

        for opening in getattr(wall, "openings", []):
            cx = sx + opening.position * dx
            cy = sy + opening.position * dy
            half_w = opening.width / 2.0
            half_d = wall.thickness / 2.0

            op0 = (cx - half_w * ux + half_d * nx, cy - half_w * uy + half_d * ny)
            op1 = (cx + half_w * ux + half_d * nx, cy + half_w * uy + half_d * ny)
            op2 = (cx + half_w * ux - half_d * nx, cy + half_w * uy - half_d * ny)
            op3 = (cx - half_w * ux - half_d * nx, cy - half_w * uy - half_d * ny)

            z = opening.sill_height
            z_max = opening.sill_height + opening.height
            target = door_lines if opening.opening_type == 'DOOR' else window_lines
            _append_box_edges(target, op0, op1, op2, op3, z, z_max)

    return wall_lines, door_lines, window_lines


def draw_wall_opening_highlight(context):
    settings = getattr(getattr(context, "scene", None), "floorplan", None)
    if settings is None or not settings.show_wall_highlight:
        return

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.line_width_set(_LINE_WIDTH)

    for obj in context.scene.objects:
        if not is_floorplan_obj(obj):
            continue
        if not is_floorplan_obj_visible(context, obj):
            continue
        if obj.name not in _graph_store:
            continue

        sg, _rg, _mapper = _graph_store[obj.name]
        wall_lines, door_lines, window_lines = _collect_lines_for_object(sg)
        _draw_lines(shader, wall_lines, _WALL_COLOR)
        _draw_lines(shader, door_lines, _DOOR_COLOR)
        _draw_lines(shader, window_lines, _WINDOW_COLOR)

    gpu.state.depth_test_set('NONE')
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
