# FP4 final mesh builder (graph-driven, modifier-independent).
# Rebuilds export-ready geometry directly from Layer 1 + Layer 2 data.

import math

import bpy
import bmesh

from .sync import _compute_room_inner_polygon
from .junction_solver import compute_wall_quad as _compute_wall_quad
from .junction_solver import junction_polygon_corners as _junction_polygon_corners


_EPS = 1e-6


def _signed_area(poly):
    n = len(poly)
    if n < 3:
        return 0.0
    return 0.5 * sum(
        poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
        for i in range(n)
    )


def _pt_key(x, y, z):
    return (round(x, 6), round(y, 6), round(z, 6))


def _get_or_add_vert(bm, cache, x, y, z):
    key = _pt_key(x, y, z)
    v = cache.get(key)
    if v is None:
        v = bm.verts.new((x, y, z))
        cache[key] = v
    return v


def _add_face_safe(bm, verts):
    if len(verts) < 3:
        return
    if len(set(verts)) < 3:
        return
    try:
        bm.faces.new(verts)
    except ValueError:
        pass


def _face_normal_from_verts(verts):
    if len(verts) < 3:
        return (0.0, 0.0, 0.0)
    a = verts[0].co
    b = verts[1].co
    c = verts[2].co
    abx, aby, abz = b.x - a.x, b.y - a.y, b.z - a.z
    acx, acy, acz = c.x - a.x, c.y - a.y, c.z - a.z
    return (
        aby * acz - abz * acy,
        abz * acx - abx * acz,
        abx * acy - aby * acx,
    )


def _add_face_oriented(bm, verts, expected_normal):
    nx, ny, nz = _face_normal_from_verts(verts)
    ex, ey, ez = expected_normal
    if nx * ex + ny * ey + nz * ez < 0.0:
        verts = list(reversed(verts))
    _add_face_safe(bm, verts)


def _segment_breaks(start, end, openings):
    a = min(start, end)
    b = max(start, end)
    vals = [a, b]
    for t1, t2, _z1, _z2 in openings:
        if t1 > a + _EPS and t1 < b - _EPS:
            vals.append(t1)
        if t2 > a + _EPS and t2 < b - _EPS:
            vals.append(t2)
    vals = sorted(set(round(v, 8) for v in vals))
    return vals


def _z_breaks(height, openings):
    vals = [0.0, height]
    for _t1, _t2, z1, z2 in openings:
        if z1 > _EPS and z1 < height - _EPS:
            vals.append(z1)
        if z2 > _EPS and z2 < height - _EPS:
            vals.append(z2)
    vals = sorted(set(round(v, 8) for v in vals))
    return vals


def _inside_any_opening(t, z, openings):
    for t1, t2, z1, z2 in openings:
        if t > t1 + _EPS and t < t2 - _EPS and z > z1 + _EPS and z < z2 - _EPS:
            return True
    return False


def _build_junction_fill(bm, vcache, junction, sg, junctions_by_id):
    # Emit a prism that fills the junction gap for T and X joints.
    # Bottom face is omitted (floor mesh covers Z=0); top cap seals the ceiling.
    corners = _junction_polygon_corners(junction, junctions_by_id, sg)
    if not corners:
        return

    walls = sg.get_walls_for_junction(junction.id)
    if not walls:
        return
    h = min(w.height for w in walls)
    if h <= _EPS:
        return

    N = len(corners)
    top = [_get_or_add_vert(bm, vcache, cx, cy, h) for cx, cy in corners]

    # Top cap only — the walls' side surfaces already enclose the vertical
    # faces of the junction area.  Adding vertical sides here would create
    # interior faces embedded inside solid wall material.
    _add_face_safe(bm, top)


def _build_wall_geometry(bm, vcache, wall, sg, junctions_by_id):
    quad = _compute_wall_quad(wall, junctions_by_id, sg)
    if quad is None:
        return

    j_start = junctions_by_id.get(wall.junction_start)
    j_end = junctions_by_id.get(wall.junction_end)
    if j_start is None or j_end is None:
        return

    sx, sy = j_start.position
    ex, ey = j_end.position
    dx = ex - sx
    dy = ey - sy
    L = math.sqrt(dx * dx + dy * dy)
    if L < _EPS:
        return
    ux, uy = dx / L, dy / L
    out_left = (-uy, ux, 0.0)
    out_right = (uy, -ux, 0.0)

    def t_of(p):
        return (p[0] - sx) * ux + (p[1] - sy) * uy

    p0, p1, p2, p3 = quad
    tl0, tl1 = t_of(p0), t_of(p1)
    tr0, tr1 = t_of(p3), t_of(p2)

    # Side lines parameterized by centerline projection t.
    l0x, l0y = p0[0] - ux * tl0, p0[1] - uy * tl0
    r0x, r0y = p3[0] - ux * tr0, p3[1] - uy * tr0

    h = wall.height
    if h <= _EPS:
        return

    openings = []
    for op in sorted(wall.openings, key=lambda o: o.position):
        t1 = op.position * L - op.width / 2.0
        t2 = op.position * L + op.width / 2.0
        z1 = max(0.0, min(op.sill_height, h))
        z2 = max(z1 + _EPS, min(op.sill_height + op.height, h))
        if t2 <= t1 + _EPS:
            continue
        openings.append((t1, t2, z1, z2))

    def side_xy(side, t):
        if side == "L":
            return (l0x + ux * t, l0y + uy * t)
        return (r0x + ux * t, r0y + uy * t)

    # Left and right wall surfaces with analytic opening cutouts.
    for side, ts, te in (("L", tl0, tl1), ("R", tr0, tr1)):
        tvals = _segment_breaks(ts, te, openings)
        zvals = _z_breaks(h, openings)
        for i in range(len(tvals) - 1):
            ta = tvals[i]
            tb = tvals[i + 1]
            if tb - ta <= _EPS:
                continue
            tmid = 0.5 * (ta + tb)
            for j in range(len(zvals) - 1):
                za = zvals[j]
                zb = zvals[j + 1]
                if zb - za <= _EPS:
                    continue
                zmid = 0.5 * (za + zb)
                if _inside_any_opening(tmid, zmid, openings):
                    continue

                ax, ay = side_xy(side, ta)
                bx, by = side_xy(side, tb)
                v00 = _get_or_add_vert(bm, vcache, ax, ay, za)
                v10 = _get_or_add_vert(bm, vcache, bx, by, za)
                v11 = _get_or_add_vert(bm, vcache, bx, by, zb)
                v01 = _get_or_add_vert(bm, vcache, ax, ay, zb)

                if side == "L":
                    _add_face_oriented(bm, [v00, v10, v11, v01], out_left)
                else:
                    _add_face_oriented(bm, [v10, v00, v01, v11], out_right)

    # Top face (bottom omitted intentionally; floor mesh covers ground plane).
    v0t = _get_or_add_vert(bm, vcache, p0[0], p0[1], h)
    v1t = _get_or_add_vert(bm, vcache, p1[0], p1[1], h)
    v2t = _get_or_add_vert(bm, vcache, p2[0], p2[1], h)
    v3t = _get_or_add_vert(bm, vcache, p3[0], p3[1], h)
    _add_face_oriented(bm, [v0t, v1t, v2t, v3t], (0.0, 0.0, 1.0))

    # End caps only on free endpoints. Connected junctions would create
    # interior polygons at joints if capped per-wall.
    start_neighbors = [w for w in sg.get_walls_for_junction(wall.junction_start) if w.id != wall.id]
    end_neighbors = [w for w in sg.get_walls_for_junction(wall.junction_end) if w.id != wall.id]

    v0b = _get_or_add_vert(bm, vcache, p0[0], p0[1], 0.0)
    v1b = _get_or_add_vert(bm, vcache, p1[0], p1[1], 0.0)
    v2b = _get_or_add_vert(bm, vcache, p2[0], p2[1], 0.0)
    v3b = _get_or_add_vert(bm, vcache, p3[0], p3[1], 0.0)
    if not start_neighbors:
        _add_face_oriented(bm, [v0b, v3b, v3t, v0t], (-ux, -uy, 0.0))
    if not end_neighbors:
        _add_face_oriented(bm, [v2b, v1b, v1t, v2t], (ux, uy, 0.0))

    # Opening reveal faces (jambs/head/sill).
    for t1, t2, z1, z2 in openings:
        lx1, ly1 = side_xy("L", t1)
        rx1, ry1 = side_xy("R", t1)
        lx2, ly2 = side_xy("L", t2)
        rx2, ry2 = side_xy("R", t2)

        l1b = _get_or_add_vert(bm, vcache, lx1, ly1, z1)
        r1b = _get_or_add_vert(bm, vcache, rx1, ry1, z1)
        l1t = _get_or_add_vert(bm, vcache, lx1, ly1, z2)
        r1t = _get_or_add_vert(bm, vcache, rx1, ry1, z2)

        l2b = _get_or_add_vert(bm, vcache, lx2, ly2, z1)
        r2b = _get_or_add_vert(bm, vcache, rx2, ry2, z1)
        l2t = _get_or_add_vert(bm, vcache, lx2, ly2, z2)
        r2t = _get_or_add_vert(bm, vcache, rx2, ry2, z2)

        # Jamb at opening start/end and head.
        _add_face_oriented(bm, [l1b, r1b, r1t, l1t], (-ux, -uy, 0.0))
        _add_face_oriented(bm, [r2b, l2b, l2t, r2t], (ux, uy, 0.0))
        _add_face_oriented(bm, [l1t, l2t, r2t, r1t], (0.0, 0.0, -1.0))

        # Window sill only (doors stay open to floor).
        if z1 > _EPS:
            _add_face_oriented(bm, [r1b, r2b, l2b, l1b], (0.0, 0.0, 1.0))


def _build_room_surfaces(bm, vcache, room, sg, junctions_by_id):
    poly = _compute_room_inner_polygon(room, sg, junctions_by_id)
    if poly is None:
        poly = []
        for jid in room.cycle:
            j = junctions_by_id.get(jid)
            if j is not None:
                poly.append(j.position)

    if len(poly) < 3:
        return

    # Ensure CCW winding in XY.
    if _signed_area(poly) < 0.0:
        poly = list(reversed(poly))

    floor = [_get_or_add_vert(bm, vcache, x, y, 0.0) for x, y in poly]
    _add_face_oriented(bm, floor, (0.0, 0.0, 1.0))


def build_final_mesh_from_graph(sg, rg, mesh_name="FloorPlan_Baked"):
    # Build a clean static mesh from graph data only.
    rg.sync_from_structural_graph()
    junctions_by_id = {j.id: j for j in sg.get_all_junctions()}

    bm = bmesh.new()
    vcache = {}

    for wall in sg.get_all_walls():
        _build_wall_geometry(bm, vcache, wall, sg, junctions_by_id)

    for junction in sg.get_all_junctions():
        _build_junction_fill(bm, vcache, junction, sg, junctions_by_id)

    for room in rg.get_all_rooms():
        _build_room_surfaces(bm, vcache, room, sg, junctions_by_id)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    if bm.verts:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if bm.edges:
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)

    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.normal_update()

    mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh
