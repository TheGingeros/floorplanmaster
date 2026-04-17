# Layer 3 — Synchronisation bridge: Python graphs -> Blender mesh
# Two-phase sync:
#   Phase 1: topology — vertices, edges, faces mirroring L1/L2
#   Phase 2: attributes — named attributes on mesh domains

import math
import bpy
import bmesh

from .structural_graph import StructuralGraph
from .room_graph import RoomGraph


# UUID string -> stable integer ID for GPU-friendly named attributes.
# Maintains a persistent mapping per sync session so IDs stay consistent.
class IdMapper:
    def __init__(self):
        self._map = {}      # uuid_str -> int
        self._reverse = {}  # int -> uuid_str
        self._next = 1

    def get(self, uuid_str):
        if uuid_str not in self._map:
            int_id = self._next
            self._map[uuid_str] = int_id
            self._reverse[int_id] = uuid_str
            self._next += 1
        return self._map[uuid_str]

    def lookup_uuid(self, int_id):
        # Reverse lookup: integer attribute value -> UUID string.
        return self._reverse.get(int_id)

    def clear(self):
        self._map.clear()
        self._reverse.clear()
        self._next = 1


# Main sync class operating on one Blender object.
class AttributeSync:

    def __init__(self, obj, sg, rg, id_mapper=None):
        self.obj = obj
        self.sg = sg
        self.rg = rg
        # Use the provided persistent mapper; fall back to a fresh one.
        self.id_mapper = id_mapper if id_mapper is not None else IdMapper()

    def full_sync(self):
        # Run phase 1 + phase 2 in sequence.
        self._phase1_topology()
        self._phase2_attributes()

    # Phase 1: build base mesh topology from L1 + L2 data.
    def _phase1_topology(self):
        mesh = self.obj.data
        bm = bmesh.new()

        junctions = self.sg.get_all_junctions()
        walls = self.sg.get_all_walls()

        # Sync rooms from L1 before reading cycles.
        self.rg.sync_from_structural_graph()
        rooms = self.rg.get_all_rooms()

        # Create vertices in order; store junction_id -> creation index.
        # BMVert Python wrappers must NOT be kept across subsequent mutations
        # (adding edges/faces reallocates the C arrays and invalidates them).
        jid_vidx = {}
        for i, j in enumerate(junctions):
            bm.verts.new((j.position[0], j.position[1], 0.0))
            jid_vidx[j.id] = i
        bm.verts.ensure_lookup_table()

        # Create edges; store wall_id -> creation index.
        wid_eidx = {}
        edge_count = 0
        for w in walls:
            vidx1 = jid_vidx.get(w.junction_start)
            vidx2 = jid_vidx.get(w.junction_end)
            if vidx1 is not None and vidx2 is not None:
                bm.edges.new((bm.verts[vidx1], bm.verts[vidx2]))
                wid_eidx[w.id] = edge_count
                edge_count += 1
        bm.edges.ensure_lookup_table()

        # Create faces; store room_id -> creation index.
        rid_fidx = {}
        face_count = 0
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
                    # Face already exists or verts not valid — skip.
                    pass
        bm.faces.ensure_lookup_table()

        # Store integer index mappings for phase 2.
        self._jid_vidx = jid_vidx
        self._wid_eidx = wid_eidx
        self._rid_fidx = rid_fidx
        self._bm = bm

    # Phase 2: write named attributes on mesh domains.
    # Attributes are written using the mesh.attributes API (not bmesh layers)
    # because bmesh custom-data layers do not reliably transfer to the modern
    # attribute system that GN Named Attribute nodes read from.
    def _phase2_attributes(self):
        mesh = self.obj.data
        bm = self._bm

        # Write topology (verts, edges, faces) to mesh first.
        bm.to_mesh(mesh)
        bm.free()
        self._bm = None

        junctions = self.sg.get_all_junctions()
        walls = self.sg.get_all_walls()
        rooms = self.rg.get_all_rooms()
        junctions_by_id = {j.id: j for j in junctions}

        # Vertex domain: junction_id
        jid_attr = self._ensure_mesh_attr(mesh, "junction_id", 'INT', 'POINT')
        for j in junctions:
            vidx = self._jid_vidx.get(j.id)
            if vidx is not None:
                jid_attr.data[vidx].value = self.id_mapper.get(j.id)

        # Edge domain: wall_id, wall_thickness, wall_height,
        # fp_length, fp_dir_x, fp_dir_y (pre-computed geometry for GN tree).
        wid_attr = self._ensure_mesh_attr(mesh, "wall_id", 'INT', 'EDGE')
        wthick_attr = self._ensure_mesh_attr(mesh, "wall_thickness", 'FLOAT', 'EDGE')
        wheight_attr = self._ensure_mesh_attr(mesh, "wall_height", 'FLOAT', 'EDGE')
        length_attr = self._ensure_mesh_attr(mesh, "fp_length", 'FLOAT', 'EDGE')
        dir_x_attr = self._ensure_mesh_attr(mesh, "fp_dir_x", 'FLOAT', 'EDGE')
        dir_y_attr = self._ensure_mesh_attr(mesh, "fp_dir_y", 'FLOAT', 'EDGE')
        for w in walls:
            eidx = self._wid_eidx.get(w.id)
            if eidx is not None:
                wid_attr.data[eidx].value = self.id_mapper.get(w.id)
                wthick_attr.data[eidx].value = w.thickness
                wheight_attr.data[eidx].value = w.height
                j_start = junctions_by_id.get(w.junction_start)
                j_end = junctions_by_id.get(w.junction_end)
                if j_start and j_end:
                    dx = j_end.position[0] - j_start.position[0]
                    dy = j_end.position[1] - j_start.position[1]
                    length = math.sqrt(dx * dx + dy * dy)
                    length_attr.data[eidx].value = length
                    if length > 1e-8:
                        dir_x_attr.data[eidx].value = dx / length
                        dir_y_attr.data[eidx].value = dy / length
                    else:
                        dir_x_attr.data[eidx].value = 1.0
                        dir_y_attr.data[eidx].value = 0.0
                else:
                    length_attr.data[eidx].value = 0.0
                    dir_x_attr.data[eidx].value = 1.0
                    dir_y_attr.data[eidx].value = 0.0

        # Face domain: room_id, room_area, room_perimeter
        rid_attr = self._ensure_mesh_attr(mesh, "room_id", 'INT', 'FACE')
        rarea_attr = self._ensure_mesh_attr(mesh, "room_area", 'FLOAT', 'FACE')
        rperim_attr = self._ensure_mesh_attr(mesh, "room_perimeter", 'FLOAT', 'FACE')
        for room in rooms:
            fidx = self._rid_fidx.get(room.id)
            if fidx is not None:
                rid_attr.data[fidx].value = self.id_mapper.get(room.id)
                rarea_attr.data[fidx].value = room.area
                rperim_attr.data[fidx].value = room.perimeter

        mesh.update()

        # Tag the object so Blender's depsgraph re-evaluates the GN modifier.
        self.obj.update_tag()
        # Force an immediate depsgraph flush so the GN modifier reads the new
        # named attributes on the same frame they are written. Without this,
        # Blender defers re-evaluation until the next scene property change.
        try:
            bpy.context.view_layer.update()
        except Exception:
            pass

    @staticmethod
    def _ensure_mesh_attr(mesh, name, attr_type, domain):
        # Get or create a mesh attribute. If one exists with mismatched
        # type/domain, remove and recreate it.
        attr = mesh.attributes.get(name)
        if attr is not None:
            if attr.data_type == attr_type and attr.domain == domain:
                return attr
            mesh.attributes.remove(attr)
        return mesh.attributes.new(name=name, type=attr_type, domain=domain)


# Convenience function called from operators after any L1/L2 change.
# Pass id_mapper from the per-object store so UUID->int assignments stay stable
# across multiple sync calls (required for raycast reverse lookup).
def sync_graph_to_mesh(obj, sg, rg, id_mapper=None):
    syncer = AttributeSync(obj, sg, rg, id_mapper=id_mapper)
    syncer.full_sync()


# Reconstruction: rebuild L1 + L2 graphs from an existing mesh with named attributes.
# Uses mesh.attributes API for reading (consistent with Phase 2 writing).
def reconstruct_graphs_from_mesh(obj):
    mesh = obj.data
    if not mesh.vertices:
        return StructuralGraph(), None

    sg = StructuralGraph()

    # Read attribute accessors (may be None if mesh lacks them).
    jid_attr = mesh.attributes.get("junction_id")
    wid_attr = mesh.attributes.get("wall_id")
    wthick_attr = mesh.attributes.get("wall_thickness")
    wheight_attr = mesh.attributes.get("wall_height")

    # Reconstruct junctions from vertices.
    vidx_to_jid = {}
    for v in mesh.vertices:
        pos = (v.co.x, v.co.y)
        int_id = jid_attr.data[v.index].value if jid_attr else v.index
        jid_str = f"reconstructed_{int_id}"
        try:
            j = sg.add_junction(pos, junction_id=jid_str)
            vidx_to_jid[v.index] = j.id
        except Exception:
            pass

    # Reconstruct walls from edges.
    for e in mesh.edges:
        v1_jid = vidx_to_jid.get(e.vertices[0])
        v2_jid = vidx_to_jid.get(e.vertices[1])
        if v1_jid and v2_jid:
            thickness = wthick_attr.data[e.index].value if wthick_attr else 0.2
            height = wheight_attr.data[e.index].value if wheight_attr else 3.0
            int_id = wid_attr.data[e.index].value if wid_attr else e.index
            wid_str = f"reconstructed_{int_id}"
            try:
                sg.add_wall(v1_jid, v2_jid, thickness=thickness, height=height, wall_id=wid_str)
            except Exception:
                pass

    # Build L2 from reconstructed L1.
    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()

    # Restore room metadata from custom property if present.
    room_meta = obj.get("room_metadata")
    if room_meta and isinstance(room_meta, dict):
        for room in rg.get_all_rooms():
            pass  # TODO: implement metadata restore when FP3 persistence is done

    return sg, rg


def sync_room_name_props(obj, rg):
    # Initialize / update "room_name_{id}" custom properties on obj.
    # Must be called from operator execute() (write context), not from draw().
    rooms = rg.get_all_rooms()
    room_ids = {room.id for room in rooms}

    for room in rooms:
        key = f"room_name_{room.id}"
        if key not in obj or obj[key] != room.name:
            obj[key] = room.name

    # Remove orphaned keys.
    for k in [k for k in obj.keys() if k.startswith("room_name_") and k[len("room_name_"):] not in room_ids]:
        del obj[k]
