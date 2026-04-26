# Layer 3 — Synchronisation bridge: Python graphs -> Blender mesh
# Two-phase sync:
#   Phase 1: topology — wall quad faces + room faces
#   Phase 2: attributes — named attributes on mesh face domain
#
# Strategy (Option C): each wall is represented as a 2D quad polygon (the
# actual wall outline computed from the centerline + half-thickness offsets,
# with corner intersections resolved per junction).  GN reads is_wall (INT,
# FACE) and wall_height (FLOAT, FACE) and simply extrudes each wall face by
# its height.  This produces geometrically correct joints at any angle without
# any instancing, trimming or shift logic.

import json
import math
import bpy
import bmesh

from .structural_graph import StructuralGraph, Opening
from .room_graph import RoomGraph


# UUID string -> stable integer ID for GPU-friendly named attributes.
class IdMapper:
    def __init__(self):
        self._map = {}
        self._reverse = {}
        self._next = 1

    def get(self, uuid_str):
        if uuid_str not in self._map:
            int_id = self._next
            self._map[uuid_str] = int_id
            self._reverse[int_id] = uuid_str
            self._next += 1
        return self._map[uuid_str]

    def lookup_uuid(self, int_id):
        return self._reverse.get(int_id)

    def clear(self):
        self._map.clear()
        self._reverse.clear()
        self._next = 1


# 2D wall outline helpers.

def _perp(dx, dy):
    # Unit perpendicular (left-hand normal) to (dx, dy).
    L = math.sqrt(dx * dx + dy * dy)
    if L < 1e-8:
        return (0.0, 1.0)
    return (-dy / L, dx / L)


def _line_intersect(p1, d1, p2, d2):
    # Intersect two infinite lines p1+t*d1 and p2+s*d2.
    # Returns the intersection point, or None if lines are parallel.
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-10:
        return None
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    t = (dx * d2[1] - dy * d2[0]) / cross
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def _wall_side_line(jx, jy, dx, dy, offset_x, offset_y):
    # A side line of a wall: starts at junction shifted by offset, runs along (dx,dy).
    p = (jx + offset_x, jy + offset_y)
    return p, (dx, dy)


def _junction_entries(junction, junctions_by_id, sg):
    # Build an angularly-sorted list of all walls at a junction.
    # Each entry: (angle, wall, out_ux, out_uy, out_nx, out_ny, half_thickness)
    # Angle is measured CCW from +X of the outgoing direction from junction.
    jx, jy = junction.position
    entries = []
    for w in sg.get_walls_for_junction(junction.id):
        other_jid = w.junction_end if w.junction_start == junction.id else w.junction_start
        other_j = junctions_by_id.get(other_jid)
        if other_j is None:
            continue
        odx = other_j.position[0] - jx
        ody = other_j.position[1] - jy
        L = math.sqrt(odx * odx + ody * ody)
        if L < 1e-8:
            continue
        out_ux, out_uy = odx / L, ody / L
        out_nx, out_ny = _perp(odx, ody)     # CCW (left) normal for outgoing direction
        angle = math.atan2(out_uy, out_ux)
        entries.append((angle, w, out_ux, out_uy, out_nx, out_ny, w.thickness / 2.0))
    entries.sort(key=lambda e: e[0])
    return entries


def _junction_polygon_corners(junction, junctions_by_id, sg):
    # Compute the N-gon that fills the gap at a junction with N>=3 walls.
    # Returns a list of (x, y) in CCW order, or [] when no fill is needed.
    #
    # Each corner is the intersection of two angularly-adjacent walls' inner
    # side-lines: corner[i] = wall[i].left ∩ wall[i+1].right (CCW order).
    # This matches exactly what _corner_at_junction produces for wall endpoints,
    # so the polygon tiles seamlessly with the surrounding wall quads.
    jx, jy = junction.position
    entries = _junction_entries(junction, junctions_by_id, sg)

    if len(entries) < 3:
        return []

    N = len(entries)
    corners = []
    for i in range(N):
        cur = entries[i]
        nxt = entries[(i + 1) % N]

        cur_left_off  = ( cur[4] * cur[6],  cur[5] * cur[6])
        nxt_right_off = (-nxt[4] * nxt[6], -nxt[5] * nxt[6])

        p1 = (jx + cur_left_off[0],  jy + cur_left_off[1])
        p2 = (jx + nxt_right_off[0], jy + nxt_right_off[1])

        pt = _line_intersect(p1, (cur[2], cur[3]), p2, (nxt[2], nxt[3]))
        if pt is None:
            pt = p1   # parallel / collinear — boundary is a shared edge

        corners.append(pt)

    # Remove consecutive duplicates (collinear wall pair collapses a corner).
    unique = []
    for c in corners:
        if unique and abs(c[0] - unique[-1][0]) < 1e-6 and abs(c[1] - unique[-1][1]) < 1e-6:
            continue
        unique.append(c)

    return unique if len(unique) >= 3 else []


def _corner_at_junction(junction, target_wall, is_start, ux, uy, nx, ny, ht,
                         side_off, junctions_by_id, sg):
    # Compute one corner of target_wall at the given junction using angular sort.
    #
    # The junction polygon is defined by intersecting adjacent walls' inner
    # side-lines in CCW angular order.  For the target wall at index i:
    #   left corner  = target's left side-line  ∩  CCW-next wall's right side-line
    #   right corner = target's right side-line ∩  CCW-prev wall's left side-line
    #
    # This guarantees each corner is the meeting point of exactly the two walls
    # that are angularly adjacent — works correctly for L, T, and X joints.
    jx, jy = junction.position
    raw = (jx + side_off[0], jy + side_off[1])
    wall_dir = (ux, uy) if is_start else (-ux, -uy)

    entries = _junction_entries(junction, junctions_by_id, sg)
    N = len(entries)

    if N < 2:
        return raw  # free end — perpendicular cap

    target_idx = next((i for i, e in enumerate(entries) if e[1].id == target_wall.id), None)
    if target_idx is None:
        return raw

    # For a straight-through (degree 2, nearly anti-parallel) junction: avoid
    # mitering.  Tiny angular errors after topology edits would create a visible
    # bevel on what should be a straight wall segment.
    if N == 2:
        adj_e = entries[(target_idx + 1) % N]
        dot = wall_dir[0] * adj_e[2] + wall_dir[1] * adj_e[3]
        cross = wall_dir[0] * adj_e[3] - wall_dir[1] * adj_e[2]
        if dot < -0.95 and abs(cross) < 0.05:
            return raw

    # is_left_side must be relative to the *outgoing* direction from the junction,
    # not the wall's start→end direction.  When the junction is the wall's END,
    # the outgoing direction is reversed, so left and right swap.
    _on_own_left = (side_off[0] * nx + side_off[1] * ny) > 0
    is_left_side = _on_own_left if is_start else not _on_own_left

    if is_left_side:
        # Left corner: intersect this wall's left side with the CCW-next wall's right side.
        adj_e = entries[(target_idx + 1) % N]
        adj_side_off = (-adj_e[4] * adj_e[6], -adj_e[5] * adj_e[6])  # right side of adj
    else:
        # Right corner: intersect this wall's right side with the CCW-prev wall's left side.
        adj_e = entries[(target_idx - 1) % N]
        adj_side_off = (adj_e[4] * adj_e[6], adj_e[5] * adj_e[6])    # left side of adj

    p_this = raw
    d_this = wall_dir
    p_adj = (jx + adj_side_off[0], jy + adj_side_off[1])
    d_adj = (adj_e[2], adj_e[3])

    pt = _line_intersect(p_this, d_this, p_adj, d_adj)
    if pt is None:
        return raw  # parallel / collinear — perpendicular cap

    t = (pt[0] - raw[0]) * wall_dir[0] + (pt[1] - raw[1]) * wall_dir[1]
    miter_limit = 2.0 * max(ht, adj_e[6])
    if abs(t) > miter_limit:
        return raw

    return pt


def _compute_wall_quad(wall, junctions_by_id, sg):
    # Returns (p0, p1, p2, p3) — the 4 2D corners of the wall outline, ordered
    # as a quad going around the wall:
    #   p0, p1 = left side (start -> end)
    #   p3, p2 = right side (start -> end)   (quad winds CCW when viewed from above)
    #
    # Corners at junctions are computed by angular sort: each corner is the
    # intersection of this wall's side-line with the angularly-adjacent
    # neighbour's opposing side-line.  Free endpoints get a perpendicular cap.
    j_start = junctions_by_id.get(wall.junction_start)
    j_end = junctions_by_id.get(wall.junction_end)
    if not (j_start and j_end):
        return None

    sx, sy = j_start.position
    ex, ey = j_end.position
    dx = ex - sx
    dy = ey - sy
    L = math.sqrt(dx * dx + dy * dy)
    if L < 1e-8:
        return None

    ux, uy = dx / L, dy / L
    nx, ny = _perp(dx, dy)
    ht = wall.thickness / 2.0

    left_off  = ( nx * ht,  ny * ht)
    right_off = (-nx * ht, -ny * ht)

    p0 = _corner_at_junction(j_start, wall, True,  ux, uy, nx, ny, ht, left_off,  junctions_by_id, sg)
    p1 = _corner_at_junction(j_end,   wall, False, ux, uy, nx, ny, ht, left_off,  junctions_by_id, sg)
    p2 = _corner_at_junction(j_end,   wall, False, ux, uy, nx, ny, ht, right_off, junctions_by_id, sg)
    p3 = _corner_at_junction(j_start, wall, True,  ux, uy, nx, ny, ht, right_off, junctions_by_id, sg)
    return (p0, p1, p2, p3)


def _compute_opening_cutter_quad(opening, wall, junctions_by_id):
    # Returns (p0, p1, p2, p3, z, effective_height) — 4 corners of the cutter
    # face + Z position + extrusion height.  The cutter extends well beyond
    # the wall on both sides to guarantee clean boolean, and overshoots
    # vertically to avoid coplanar faces with the wall top/bottom.
    from ..utils.constants import OPENING_CUTTER_OVERSHOOT, OPENING_CUTTER_Z_OVERSHOOT

    j_start = junctions_by_id.get(wall.junction_start)
    j_end = junctions_by_id.get(wall.junction_end)
    if not (j_start and j_end):
        return None

    sx, sy = j_start.position
    ex, ey = j_end.position
    dx = ex - sx
    dy = ey - sy
    L = math.sqrt(dx * dx + dy * dy)
    if L < 1e-8:
        return None

    ux, uy = dx / L, dy / L
    nx, ny = _perp(dx, dy)

    # Center of opening along wall centerline.
    cx = sx + opening.position * dx
    cy = sy + opening.position * dy

    half_w = opening.width / 2.0
    # Extend cutter slightly beyond the wall surface on each side.
    # wall.thickness/2 reaches the wall surface; OVERSHOOT adds a small
    # margin to guarantee penetration even after junction corner resolution.
    # Must NOT be too large — oversized cutters can reach adjacent walls at
    # junctions and cause the boolean solver to produce degenerate results.
    half_d = wall.thickness / 2.0 + OPENING_CUTTER_OVERSHOOT

    # Quad corners at Z position (will be extruded by effective_height in GN).
    p0 = (cx - half_w * ux + half_d * nx, cy - half_w * uy + half_d * ny)
    p1 = (cx + half_w * ux + half_d * nx, cy + half_w * uy + half_d * ny)
    p2 = (cx + half_w * ux - half_d * nx, cy + half_w * uy - half_d * ny)
    p3 = (cx - half_w * ux - half_d * nx, cy - half_w * uy - half_d * ny)

    # Doors (sill_height == 0): place cutter bottom just ABOVE Z=0 (+0.01 m).
    # This keeps the cutter entirely within the wall solid (Z=[0, wall_height]),
    # which is a simpler boolean operation than when the cutter extends below Z=0.
    # Extending below Z=0 requires the EXACT solver to intersect the cutter with
    # the wall's bottom face at exactly Z=0, which causes intermittent failures.
    # The resulting 1 cm gap at the very base of the door is imperceptible.
    # Windows (sill_height > 0): cutter is already above Z=0; keep original formula.
    if opening.sill_height == 0.0:
        z = OPENING_CUTTER_Z_OVERSHOOT  # +0.01 m above Z=0
        effective_height = opening.height + OPENING_CUTTER_Z_OVERSHOOT  # overshoot at top
    else:
        z = max(opening.sill_height - OPENING_CUTTER_Z_OVERSHOOT, -OPENING_CUTTER_Z_OVERSHOOT)
        effective_height = opening.height + 2 * OPENING_CUTTER_Z_OVERSHOOT

    return (p0, p1, p2, p3, z, effective_height)


def _compute_room_inner_polygon(room, sg, junctions_by_id):
    # Build a room floor polygon on the interior wall boundary.
    # Each edge is offset from its centerline toward the room centroid by
    # half wall thickness; corner points are intersections of neighboring
    # interior-side lines.
    cycle = room.cycle
    n = len(cycle)
    if n < 3:
        return None

    cx, cy = room.centroid
    edge_lines = []

    for i in range(n):
        jid_a = cycle[i]
        jid_b = cycle[(i + 1) % n]

        wall = sg.get_wall_between(jid_a, jid_b)
        j_a = junctions_by_id.get(jid_a)
        j_b = junctions_by_id.get(jid_b)
        if wall is None or j_a is None or j_b is None:
            return None

        sx, sy = j_a.position
        ex, ey = j_b.position
        dx = ex - sx
        dy = ey - sy
        L = math.sqrt(dx * dx + dy * dy)
        if L < 1e-8:
            return None

        ux, uy = dx / L, dy / L
        nx, ny = _perp(dx, dy)

        # Decide which side is interior by testing the room centroid against
        # the oriented centerline normal.
        signed = (cx - sx) * nx + (cy - sy) * ny
        side = 1.0 if signed >= 0.0 else -1.0
        ht = wall.thickness / 2.0
        offx, offy = nx * ht * side, ny * ht * side

        edge_lines.append(((sx + offx, sy + offy), (ux, uy), (offx, offy)))

    inner_pts = []
    for i in range(n):
        prev_line = edge_lines[(i - 1) % n]
        next_line = edge_lines[i]

        p1, d1, prev_off = prev_line
        p2, d2, next_off = next_line
        pt = _line_intersect(p1, d1, p2, d2)

        if pt is None:
            # Near-parallel neighbors (or numerical issues): fallback to a
            # stable shifted junction point using mean offset.
            j = junctions_by_id.get(cycle[i])
            if j is None:
                return None
            ox = (prev_off[0] + next_off[0]) * 0.5
            oy = (prev_off[1] + next_off[1]) * 0.5
            pt = (j.position[0] + ox, j.position[1] + oy)

        inner_pts.append(pt)

    return inner_pts


# Main sync class operating on one Blender object.
class AttributeSync:

    def __init__(self, obj, sg, rg, id_mapper=None):
        self.obj = obj
        self.sg = sg
        self.rg = rg
        self.id_mapper = id_mapper if id_mapper is not None else IdMapper()

    def full_sync(self):
        self._phase1_topology()
        self._phase2_attributes()

    # Phase 1: build mesh topology.
    # Wall outline quads are computed from L1 data.  Room centerline faces
    # (for floor geometry) are appended afterwards.
    def _phase1_topology(self):
        mesh = self.obj.data
        bm = bmesh.new()

        walls = self.sg.get_all_walls()
        self.rg.sync_from_structural_graph()
        rooms = self.rg.get_all_rooms()
        junctions = self.sg.get_all_junctions()
        junctions_by_id = {j.id: j for j in junctions}

        # Wall quad faces — one face per wall.
        wid_fidx = {}
        face_count = 0
        wall_vert_count = 0
        for w in walls:
            quad = _compute_wall_quad(w, junctions_by_id, self.sg)
            if quad is None:
                continue
            verts = [bm.verts.new((p[0], p[1], 0.0)) for p in quad]
            wall_vert_count += 4
            bm.verts.ensure_lookup_table()
            try:
                # Reverse winding so face normal points +Z (CCW from above).
                bm.faces.new(verts[::-1])
                wid_fidx[w.id] = face_count
                face_count += 1
            except ValueError:
                pass

        # Junction fill faces — one polygon per T/X joint (N>=3 walls).
        # GN extrudes these exactly like wall quads, sealing the top gap.
        jid_fidx = {}
        for junction in junctions:
            corners = _junction_polygon_corners(junction, junctions_by_id, self.sg)
            if not corners:
                continue
            verts = [bm.verts.new((cx, cy, 0.0)) for cx, cy in corners]
            bm.verts.ensure_lookup_table()
            # Ensure CCW winding so the normal points +Z.
            n = len(verts)
            pts = [v.co for v in verts]
            signed = sum(
                pts[i].x * pts[(i + 1) % n].y - pts[(i + 1) % n].x * pts[i].y
                for i in range(n)
            )
            if signed < 0:
                verts.reverse()
            try:
                bm.faces.new(verts)
                jid_fidx[junction.id] = face_count
                face_count += 1
            except ValueError:
                pass

        # Opening cutter boxes — 6-face watertight box per opening.
        oid_fidx = {}
        for w in walls:
            for op in w.openings:
                result = _compute_opening_cutter_quad(op, w, junctions_by_id)
                if result is None:
                    continue
                p0, p1, p2, p3, z, eff_h = result
                z_top = z + eff_h
                b = [bm.verts.new((p[0], p[1], z)) for p in (p0, p1, p2, p3)]
                t = [bm.verts.new((p[0], p[1], z_top)) for p in (p0, p1, p2, p3)]
                wall_vert_count += 8
                bm.verts.ensure_lookup_table()
                first_fidx = face_count
                box_faces = [
                    (b[0], b[1], b[2], b[3]),  # bottom — normal -Z
                    (t[3], t[2], t[1], t[0]),  # top — normal +Z
                    (b[1], b[0], t[0], t[1]),  # side 0-1
                    (b[2], b[1], t[1], t[2]),  # side 1-2
                    (b[3], b[2], t[2], t[3]),  # side 2-3
                    (b[0], b[3], t[3], t[0]),  # side 3-0
                ]
                for fv in box_faces:
                    try:
                        bm.faces.new(fv)
                        face_count += 1
                    except ValueError:
                        pass
                oid_fidx[op.id] = list(range(first_fidx, face_count))

        # Room floor faces (interior boundary polygons).
        # These are separate faces tagged is_wall=0 so GN can filter them.
        # Note: door cutters now start at z=+0.01 (above Z=0), so the wall
        # solid's bottom face is preserved at door positions — no threshold
        # face is needed to fill the gap at floor level.
        rid_fidx = {}
        for room in rooms:
            inner_poly = _compute_room_inner_polygon(room, self.sg, junctions_by_id)
            face_verts = []

            if inner_poly is not None:
                for x, y in inner_poly:
                    face_verts.append(bm.verts.new((x, y, 0.0)))
            else:
                # Fallback to centerline cycle if interior polygon cannot be
                # computed for a degenerate topology corner case.
                for jid in room.cycle:
                    j = junctions_by_id.get(jid)
                    if j is not None:
                        face_verts.append(bm.verts.new((j.position[0], j.position[1], 0.0)))

            bm.verts.ensure_lookup_table()
            if len(face_verts) >= 3:
                try:
                    # Ensure CCW winding so the face normal points +Z.
                    # nx.find_cycle() traversal order is non-deterministic across
                    # platforms/versions; compute signed shoelace area and reverse
                    # if clockwise (signed < 0) before creating the face.
                    pts = [v.co for v in face_verts]
                    n = len(pts)
                    signed = sum(
                        pts[i].x * pts[(i + 1) % n].y - pts[(i + 1) % n].x * pts[i].y
                        for i in range(n)
                    )
                    if signed < 0:
                        face_verts.reverse()
                    bm.faces.new(face_verts)
                    rid_fidx[room.id] = face_count
                    face_count += 1
                except ValueError:
                    pass

        bm.faces.ensure_lookup_table()

        self._wid_fidx = wid_fidx
        self._rid_fidx = rid_fidx
        self._oid_fidx = oid_fidx
        self._jid_fidx = jid_fidx
        self._bm = bm

    # Phase 2: write named attributes on face domain.
    def _phase2_attributes(self):
        mesh = self.obj.data
        bm = self._bm

        bm.to_mesh(mesh)
        bm.free()
        self._bm = None

        walls = self.sg.get_all_walls()
        rooms = self.rg.get_all_rooms()

        # Face domain: is_wall (1 = wall quad, 0 = room floor), is_opening (1 = cutter),
        # wall_id, wall_height, room_id, room_area, room_perimeter.
        is_wall_attr = self._ensure_mesh_attr(mesh, "is_wall", 'INT', 'FACE')
        is_opening_attr = self._ensure_mesh_attr(mesh, "is_opening", 'INT', 'FACE')
        wid_attr = self._ensure_mesh_attr(mesh, "wall_id", 'INT', 'FACE')
        wheight_attr = self._ensure_mesh_attr(mesh, "wall_height", 'FLOAT', 'FACE')
        wthick_attr = self._ensure_mesh_attr(mesh, "wall_thickness", 'FLOAT', 'FACE')
        rid_attr = self._ensure_mesh_attr(mesh, "room_id", 'INT', 'FACE')
        rarea_attr = self._ensure_mesh_attr(mesh, "room_area", 'FLOAT', 'FACE')
        rperim_attr = self._ensure_mesh_attr(mesh, "room_perimeter", 'FLOAT', 'FACE')

        walls_by_id = {w.id: w for w in walls}
        for wid, fidx in self._wid_fidx.items():
            w = walls_by_id.get(wid)
            if w is None:
                continue
            is_wall_attr.data[fidx].value = 1
            is_opening_attr.data[fidx].value = 0
            wid_attr.data[fidx].value = self.id_mapper.get(w.id)
            wheight_attr.data[fidx].value = w.height
            wthick_attr.data[fidx].value = w.thickness

        # Opening cutter faces — all faces of each box are tagged is_opening=1.
        for oid, fidx_list in self._oid_fidx.items():
            for fidx in fidx_list:
                is_wall_attr.data[fidx].value = 0
                is_opening_attr.data[fidx].value = 1

        # Junction fill faces — extruded the same way as wall quads.
        for jid, fidx in self._jid_fidx.items():
            walls_here = self.sg.get_walls_for_junction(jid)
            h = min(w.height for w in walls_here) if walls_here else 0.0
            is_wall_attr.data[fidx].value = 1
            is_opening_attr.data[fidx].value = 0
            wid_attr.data[fidx].value = 0
            wheight_attr.data[fidx].value = h
            wthick_attr.data[fidx].value = 0

        for room in rooms:
            fidx = self._rid_fidx.get(room.id)
            if fidx is not None:
                is_wall_attr.data[fidx].value = 0
                is_opening_attr.data[fidx].value = 0
                rid_attr.data[fidx].value = self.id_mapper.get(room.id)
                rarea_attr.data[fidx].value = room.area
                rperim_attr.data[fidx].value = room.perimeter

        mesh.update()
        self.obj.update_tag()
        # Do NOT call view_layer.update() here — it forces synchronous GN
        # evaluation (including the EXACT boolean solver) blocking Python until
        # the depsgraph finishes.  With many rooms the cost compounds with each
        # wall placement.  update_tag() is sufficient: Blender will re-evaluate
        # the GN modifier lazily on the next viewport redraw.

    @staticmethod
    def _ensure_mesh_attr(mesh, name, attr_type, domain):
        # Always remove and recreate to avoid stale data from prior syncs
        # (bm.to_mesh() does not clear named attributes added via
        # mesh.attributes API, so old values at shifted face indices could
        # leak through).
        attr = mesh.attributes.get(name)
        if attr is not None:
            mesh.attributes.remove(attr)
        return mesh.attributes.new(name=name, type=attr_type, domain=domain)


# Convenience function called from operators after any L1/L2 change.
def sync_graph_to_mesh(obj, sg, rg, id_mapper=None):
    # Push any room name edits from object custom properties before sync.
    for room in rg.get_all_rooms():
        key = f"room_name_{room.id}"
        if key in obj:
            stored = str(obj[key])
            if stored != room.name:
                rg.set_room_name(room.id, stored)

    if id_mapper is None:
        id_mapper = IdMapper()
    syncer = AttributeSync(obj, sg, rg, id_mapper=id_mapper)
    syncer.full_sync()
    _persist_graphs(obj, sg, rg, id_mapper)

    # Initialize room name custom properties for newly detected rooms.
    for room in rg.get_all_rooms():
        key = f"room_name_{room.id}"
        if key not in obj:
            obj[key] = room.name


# Persistence: store graph data as JSON on the Blender object so that
# reconstruction works after addon reload / undo / file load.

def _persist_graphs(obj, sg, rg, id_mapper):
    data = {
        "junctions": [
            {"id": j.id, "x": j.position[0], "y": j.position[1]}
            for j in sg.get_all_junctions()
        ],
        "walls": [
            {
                "id": w.id,
                "start": w.junction_start,
                "end": w.junction_end,
                "thickness": w.thickness,
                "height": w.height,
                "openings": [
                    {
                        "id": op.id,
                        "type": op.opening_type,
                        "position": op.position,
                        "width": op.width,
                        "height": op.height,
                        "sill_height": op.sill_height,
                    }
                    for op in w.openings
                ],
            }
            for w in sg.get_all_walls()
        ],
        "id_map": id_mapper._map if id_mapper else {},
    }
    obj["_floorplan_graphs"] = json.dumps(data)


def reconstruct_graphs_from_mesh(obj):
    raw = obj.get("_floorplan_graphs")
    if not raw:
        return StructuralGraph(), None, IdMapper()

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return StructuralGraph(), None, IdMapper()

    sg = StructuralGraph()
    for jd in data.get("junctions", []):
        sg.add_junction((jd["x"], jd["y"]), junction_id=jd["id"])
    for wd in data.get("walls", []):
        sg.add_wall(
            wd["start"], wd["end"],
            thickness=wd["thickness"],
            height=wd["height"],
            wall_id=wd["id"],
        )
        # Restore openings for this wall.
        for od in wd.get("openings", []):
            sg.add_opening(
                wd["id"],
                opening_type=od.get("type", "DOOR"),
                position=od.get("position", 0.5),
                width=od.get("width", 0.9),
                height=od.get("height", 2.1),
                sill_height=od.get("sill_height", 0.0),
                opening_id=od.get("id"),
            )
    rg = RoomGraph(sg)

    # Restore IdMapper state so integer IDs stay stable.
    id_mapper = IdMapper()
    for uuid_str, int_id in data.get("id_map", {}).items():
        id_mapper._map[uuid_str] = int(int_id)
        id_mapper._reverse[int(int_id)] = uuid_str
    id_mapper._next = max(id_mapper._reverse.keys(), default=0) + 1

    return sg, rg, id_mapper


def persist_room_names(obj, rg):
    # Persist room names keyed by canonical cycle key (tuple of junction IDs).
    # Cycle keys are stable across undo/reload because junction IDs are
    # preserved in the _floorplan_graphs JSON property.
    names = {}
    for room in rg.get_all_rooms():
        key = RoomGraph._cycle_key(room.cycle)
        names[json.dumps(list(key))] = room.name
    obj["_floorplan_room_names"] = json.dumps(names)


def restore_room_names(obj, rg):
    # Apply persisted room names after rg.sync_from_structural_graph() has run.
    # Matches rooms by stable cycle key so names survive undo and addon reload.
    raw = obj.get("_floorplan_room_names")
    if not raw:
        return
    try:
        names = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return
    for key_json, name in names.items():
        try:
            cycle_key = tuple(json.loads(key_json))
        except Exception:
            continue
        room_id = rg._cycle_room_map.get(cycle_key)
        if room_id:
            rg.set_room_name(room_id, name)