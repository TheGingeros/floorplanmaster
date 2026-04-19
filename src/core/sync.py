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


def _compute_wall_quad(wall, junctions_by_id, sg):
    # Returns (p0, p1, p2, p3) — the 4 2D corners of the wall outline, ordered
    # as a quad going around the wall:
    #   p0, p1 = left side (start -> end)
    #   p3, p2 = right side (start -> end)   (so the quad winds CCW when viewed from above)
    #
    # At each junction end:
    #   - If the junction has other walls: compute the intersection of this
    #     wall's side line with each neighbour's side line and pick the one
    #     that extends the wall the least (avoids over-extension).
    #   - If the junction is a free endpoint: cap perpendicularly.
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

    ux, uy = dx / L, dy / L          # unit along wall
    nx, ny = _perp(dx, dy)           # unit left-normal
    ht = wall.thickness / 2.0

    # The two raw side offsets for this wall.
    left_off = (nx * ht, ny * ht)
    right_off = (-nx * ht, -ny * ht)

    def _corner(junction, is_start, side_off):
        # Compute the corner for one end and one side of the wall.
        jx, jy = junction.position
        # Raw endpoint on this side.
        raw = (jx + side_off[0], jy + side_off[1])

        # Wall direction (away from junction toward the other end).
        wall_dir = (ux, uy) if is_start else (-ux, -uy)

        neighbors = [w for w in sg.get_walls_for_junction(junction.id) if w.id != wall.id]
        if not neighbors:
            return raw  # free end — perpendicular cap

        best = raw
        best_t = 0.0  # signed distance from raw along wall_dir; closest wins

        for nb in neighbors:
            other_jid = nb.junction_end if nb.junction_start == junction.id else nb.junction_start
            other_j = junctions_by_id.get(other_jid)
            if other_j is None:
                continue
            nbdx = other_j.position[0] - jx
            nbdy = other_j.position[1] - jy
            nb_L = math.sqrt(nbdx * nbdx + nbdy * nbdy)
            if nb_L < 1e-8:
                continue
            nb_ux, nb_uy = nbdx / nb_L, nbdy / nb_L
            nb_nx, nb_ny = _perp(nbdx, nbdy)
            nb_ht = nb.thickness / 2.0

            # Determine which side of the neighbour wall to intersect with.
            # nb direction is outgoing from junction.  If junction is the
            # neighbour's START, outgoing = forward, so _perp gives the true
            # forward-left normal.  If junction is the neighbour's END,
            # outgoing = -forward, so _perp gives the forward-RIGHT normal
            # (labels are flipped).  We always want same-side pairing
            # (our left ↔ nb forward-left, our right ↔ nb forward-right),
            # so flip when the neighbour connects at its end.
            is_local_left = (side_off[0] * nx + side_off[1] * ny) > 0
            nb_at_start = (junction.id == nb.junction_start)
            use_nb_left = is_local_left if nb_at_start else not is_local_left
            if use_nb_left:
                nb_side_off = (nb_nx * nb_ht, nb_ny * nb_ht)
            else:
                nb_side_off = (-nb_nx * nb_ht, -nb_ny * nb_ht)

            p_this, d_this = _wall_side_line(jx, jy, ux if is_start else -ux,
                                              uy if is_start else -uy,
                                              side_off[0], side_off[1])
            p_nb, d_nb = _wall_side_line(jx, jy, nb_ux, nb_uy,
                                          nb_side_off[0], nb_side_off[1])

            pt = _line_intersect(p_this, d_this, p_nb, d_nb)
            if pt is None:
                continue

            # t = signed distance from raw point along wall direction.
            t = (pt[0] - raw[0]) * wall_dir[0] + (pt[1] - raw[1]) * wall_dir[1]

            if best is raw or abs(t) < abs(best_t):
                best = pt
                best_t = t

        return best

    p0 = _corner(j_start, True,  left_off)
    p1 = _corner(j_end,   False, left_off)
    p2 = _corner(j_end,   False, right_off)
    p3 = _corner(j_start, True,  right_off)
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

    # Shift Z down and height up to avoid coplanar faces with wall floor/top.
    z = max(opening.sill_height - OPENING_CUTTER_Z_OVERSHOOT, -OPENING_CUTTER_Z_OVERSHOOT)
    effective_height = opening.height + 2 * OPENING_CUTTER_Z_OVERSHOOT

    return (p0, p1, p2, p3, z, effective_height)


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

        # Opening cutter boxes — 6-face watertight box per opening.
        # Creating a proper closed manifold with consistent outward normals
        # is critical for the EXACT boolean solver to produce clean results.
        # ExtrudeMesh leaves the bottom face normal pointing inward, which
        # breaks boolean; building boxes in Python avoids this entirely.
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

        # Room centerline faces (floor polygons) — use junction positions.
        # These are separate faces tagged is_wall=0 so GN can filter them.
        jid_vidx = {}
        for i, j in enumerate(junctions):
            bm.verts.new((j.position[0], j.position[1], 0.0))
            jid_vidx[j.id] = wall_vert_count + i
        bm.verts.ensure_lookup_table()

        rid_fidx = {}
        for room in rooms:
            face_verts = []
            for jid in room.cycle:
                vidx = jid_vidx.get(jid)
                if vidx is not None:
                    face_verts.append(bm.verts[vidx])
            if len(face_verts) >= 3:
                try:
                    bm.faces.new(face_verts)
                    rid_fidx[room.id] = face_count
                    face_count += 1
                except ValueError:
                    pass

        bm.faces.ensure_lookup_table()

        self._wid_fidx = wid_fidx
        self._rid_fidx = rid_fidx
        self._oid_fidx = oid_fidx
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
        try:
            bpy.context.view_layer.update()
        except Exception:
            pass

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
    if id_mapper is None:
        id_mapper = IdMapper()
    syncer = AttributeSync(obj, sg, rg, id_mapper=id_mapper)
    syncer.full_sync()
    _persist_graphs(obj, sg, rg, id_mapper)


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