# Layer 3 — Synchronisation bridge: Python graphs -> Blender mesh
# Two-phase sync:
#   Phase 1: topology — vertices, edges, faces mirroring L1/L2
#   Phase 2: attributes — named attributes on mesh domains

import bpy
import bmesh

from .structural_graph import StructuralGraph
from .room_graph import RoomGraph


# UUID string -> stable integer ID for GPU-friendly named attributes.
# Maintains a persistent mapping per sync session so IDs stay consistent.
class IdMapper:
    def __init__(self):
        self._map = {}
        self._next = 1

    def get(self, uuid_str):
        if uuid_str not in self._map:
            self._map[uuid_str] = self._next
            self._next += 1
        return self._map[uuid_str]

    def clear(self):
        self._map.clear()
        self._next = 1


# Main sync class operating on one Blender object.
class AttributeSync:

    def __init__(self, obj, sg, rg):
        self.obj = obj
        self.sg = sg
        self.rg = rg
        self.id_mapper = IdMapper()

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
    def _phase2_attributes(self):
        mesh = self.obj.data
        bm = self._bm
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        junctions = self.sg.get_all_junctions()
        walls = self.sg.get_all_walls()
        rooms = self.rg.get_all_rooms()

        # Vertex attributes: junction_id
        jid_layer = self._ensure_int_layer(bm.verts.layers.int, "junction_id")
        for j in junctions:
            vidx = self._jid_vidx.get(j.id)
            if vidx is not None:
                bm.verts[vidx][jid_layer] = self.id_mapper.get(j.id)

        # Edge attributes: wall_id, wall_thickness, wall_height
        wid_layer = self._ensure_int_layer(bm.edges.layers.int, "wall_id")
        wthick_layer = self._ensure_float_layer(bm.edges.layers.float, "wall_thickness")
        wheight_layer = self._ensure_float_layer(bm.edges.layers.float, "wall_height")
        for w in walls:
            eidx = self._wid_eidx.get(w.id)
            if eidx is not None:
                e = bm.edges[eidx]
                e[wid_layer] = self.id_mapper.get(w.id)
                e[wthick_layer] = w.thickness
                e[wheight_layer] = w.height

        # Face attributes: room_id, room_area, room_perimeter, room_type
        rid_layer = self._ensure_int_layer(bm.faces.layers.int, "room_id")
        rarea_layer = self._ensure_float_layer(bm.faces.layers.float, "room_area")
        rperim_layer = self._ensure_float_layer(bm.faces.layers.float, "room_perimeter")
        rtype_layer = self._ensure_int_layer(bm.faces.layers.int, "room_type")
        for room in rooms:
            fidx = self._rid_fidx.get(room.id)
            if fidx is not None:
                f = bm.faces[fidx]
                f[rid_layer] = self.id_mapper.get(room.id)
                f[rarea_layer] = room.area
                f[rperim_layer] = room.perimeter
                f[rtype_layer] = int(room.room_type)

        # Write updated attributes to mesh and free bmesh.
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        self._bm = None

    # Helpers for ensuring bmesh custom data layers exist.
    @staticmethod
    def _ensure_int_layer(layers, name):
        layer = layers.get(name)
        if layer is None:
            layer = layers.new(name)
        return layer

    @staticmethod
    def _ensure_float_layer(layers, name):
        layer = layers.get(name)
        if layer is None:
            layer = layers.new(name)
        return layer


# Convenience function called from operators after any L1/L2 change.
def sync_graph_to_mesh(obj, sg, rg):
    syncer = AttributeSync(obj, sg, rg)
    syncer.full_sync()


# Reconstruction: rebuild L1 + L2 graphs from an existing mesh with named attributes.
def reconstruct_graphs_from_mesh(obj):
    mesh = obj.data
    if not mesh.vertices:
        return StructuralGraph(), None

    sg = StructuralGraph()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # Read junction_id attribute.
    jid_layer = bm.verts.layers.int.get("junction_id")
    wid_layer = bm.edges.layers.int.get("wall_id")
    wthick_layer = bm.edges.layers.float.get("wall_thickness")
    wheight_layer = bm.edges.layers.float.get("wall_height")

    # Reconstruct junctions.
    vidx_to_jid = {}
    for v in bm.verts:
        pos = (v.co.x, v.co.y)
        int_id = v[jid_layer] if jid_layer else v.index
        jid_str = f"reconstructed_{int_id}"
        try:
            j = sg.add_junction(pos, junction_id=jid_str)
            vidx_to_jid[v.index] = j.id
        except Exception:
            pass

    # Reconstruct walls.
    for e in bm.edges:
        v1_jid = vidx_to_jid.get(e.verts[0].index)
        v2_jid = vidx_to_jid.get(e.verts[1].index)
        if v1_jid and v2_jid:
            thickness = e[wthick_layer] if wthick_layer else 0.2
            height = e[wheight_layer] if wheight_layer else 3.0
            int_id = e[wid_layer] if wid_layer else e.index
            wid_str = f"reconstructed_{int_id}"
            try:
                sg.add_wall(v1_jid, v2_jid, thickness=thickness, height=height, wall_id=wid_str)
            except Exception:
                pass

    bm.free()

    # Build L2 from reconstructed L1.
    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()

    # Restore room metadata from custom property if present.
    room_meta = obj.get("room_metadata")
    if room_meta and isinstance(room_meta, dict):
        for room in rg.get_all_rooms():
            # room_metadata is keyed by integer room_id — we need to match.
            # For reconstructed graphs the integer id is in the IdMapper, but
            # we stored it as string key in the custom prop.
            pass  # TODO: implement metadata restore when FP3 persistence is done

    return sg, rg
