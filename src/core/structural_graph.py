import uuid

import networkx as nx

from ..utils.constants import DEFAULT_THICKNESS, DEFAULT_HEIGHT
from ..utils.math_helpers import edge_length, edge_angle, point_distance
from .validators import (
    ValidationError,
    validate_thickness,
    validate_height,
    E_WALL_DUPLICATE,
    E_WALL_SELF_LOOP,
    E_JUNCTION_DUPLICATE,
)


# Junction — node in the structural graph
# Representing position of one vertex, two verteces make up one wall
class Junction:
    def __init__(self, position, snap_priority=0, junction_id=None):
        self.id = junction_id or str(uuid.uuid4()) # assign given ID, if None, create a new one
        self.position = tuple(position)  # (x, y)
        self.snap_priority = snap_priority

    def __repr__(self):
        return f"Junction({self.id[:8]}, pos={self.position})"


# Wall — edge in the structural graph
class Wall:
    def __init__(
        self,
        junction_start_id,
        junction_end_id,
        thickness=DEFAULT_THICKNESS,
        height=DEFAULT_HEIGHT,
        material_id=0,
        is_external=False,
        is_bearing=False,
        wall_id=None,
    ):
        self.id = wall_id or str(uuid.uuid4())
        self.junction_start = junction_start_id # assign given ID, if None, create a new one
        self.junction_end = junction_end_id
        self.thickness = thickness
        self.height = height
        self.material_id = material_id
        self.openings = []
        self.is_external = is_external
        self.is_bearing = is_bearing

    def __repr__(self):
        return f"Wall({self.id[:8]}, {self.junction_start[:8]}→{self.junction_end[:8]})"


# StructuralGraph — Layer 1
class StructuralGraph:
    # Planar 2D graph of junctions and walls.
    # No bpy dependency. Uses NetworkX for topology algorithms.

    def __init__(self):
        self._graph = nx.Graph()
        self._junctions = {}   # id -> Junction
        self._walls = {}       # id -> Wall
        # Spatial index: rounded position -> junction id (for duplicate detection).
        self._pos_index = {}

    # -- helpers --
    @staticmethod
    def _pos_key(position, precision=6):
        # Round to avoid floating-point duplicates.
        return (round(position[0], precision), round(position[1], precision))

    def _edge_key(self, jid_a, jid_b):
        # Canonical unordered pair.
        return tuple(sorted((jid_a, jid_b)))

    # Junction CRUD
    def add_junction(self, position, snap_priority=0, junction_id=None):
        pk = self._pos_key(position)
        if pk in self._pos_index:
            raise ValidationError(
                E_JUNCTION_DUPLICATE,
                f"Junction already exists at {position}",
            )
        j = Junction(position, snap_priority, junction_id)
        self._junctions[j.id] = j
        self._graph.add_node(j.id, pos=j.position)
        self._pos_index[pk] = j.id
        return j

    def remove_junction(self, junction_id):
        # Remove the junction and all walls connected to it.
        j = self._junctions.get(junction_id)
        if j is None:
            return
        # Collect walls to remove first (avoid mutation during iteration).
        walls_to_remove = [
            w.id for w in self._walls.values()
            if w.junction_start == junction_id or w.junction_end == junction_id
        ]
        for wid in walls_to_remove:
            self.remove_wall(wid)
        pk = self._pos_key(j.position)
        self._pos_index.pop(pk, None)
        self._graph.remove_node(junction_id)
        del self._junctions[junction_id]

    def get_junction(self, junction_id):
        return self._junctions.get(junction_id)

    def get_all_junctions(self):
        return list(self._junctions.values())

    def find_junctions_near(self, position, radius):
        # Return junctions within *radius* of *position*, sorted by distance.
        results = []
        for j in self._junctions.values():
            d = point_distance(position, j.position)
            if d <= radius:
                results.append((j, d))
        results.sort(key=lambda t: t[1])
        return results

    def move_junction(self, junction_id, new_position):
        j = self._junctions.get(junction_id)
        if j is None:
            return
        new_pk = self._pos_key(new_position)
        existing = self._pos_index.get(new_pk)
        if existing is not None and existing != junction_id:
            raise ValidationError(
                E_JUNCTION_DUPLICATE,
                f"Another junction already at {new_position}",
            )
        old_pk = self._pos_key(j.position)
        self._pos_index.pop(old_pk, None)
        j.position = tuple(new_position)
        self._pos_index[new_pk] = junction_id
        self._graph.nodes[junction_id]["pos"] = j.position

    # Wall CRUD
    def add_wall(
        self,
        junction_start_id,
        junction_end_id,
        thickness=DEFAULT_THICKNESS,
        height=DEFAULT_HEIGHT,
        material_id=0,
        is_external=False,
        is_bearing=False,
        wall_id=None,
    ):
        if junction_start_id == junction_end_id:
            raise ValidationError(E_WALL_SELF_LOOP, "Start and end junction are the same")

        if junction_start_id not in self._junctions or junction_end_id not in self._junctions:
            raise ValueError("Both junctions must exist in the graph")

        ek = self._edge_key(junction_start_id, junction_end_id)
        if self._graph.has_edge(*ek):
            raise ValidationError(E_WALL_DUPLICATE, f"Wall already exists between {ek}")

        validate_thickness(thickness)
        validate_height(height)

        w = Wall(
            junction_start_id, junction_end_id,
            thickness=thickness, height=height,
            material_id=material_id,
            is_external=is_external, is_bearing=is_bearing,
            wall_id=wall_id,
        )
        self._walls[w.id] = w
        self._graph.add_edge(junction_start_id, junction_end_id, wall_id=w.id)
        return w

    def remove_wall(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return
        ek = self._edge_key(w.junction_start, w.junction_end)
        if self._graph.has_edge(*ek):
            self._graph.remove_edge(*ek)
        del self._walls[wall_id]

    def get_wall(self, wall_id):
        return self._walls.get(wall_id)

    def get_all_walls(self):
        return list(self._walls.values())

    def get_walls_for_junction(self, junction_id):
        return [
            w for w in self._walls.values()
            if w.junction_start == junction_id or w.junction_end == junction_id
        ]

    def get_wall_between(self, jid_a, jid_b):
        # Return the wall connecting two junctions, or None.
        ek = self._edge_key(jid_a, jid_b)
        data = self._graph.edges.get(ek)
        if data is None:
            return None
        return self._walls.get(data.get("wall_id"))

    def update_wall(self, wall_id, **kwargs):
        w = self._walls.get(wall_id)
        if w is None:
            return
        if "thickness" in kwargs:
            validate_thickness(kwargs["thickness"])
            w.thickness = kwargs["thickness"]
        if "height" in kwargs:
            validate_height(kwargs["height"])
            w.height = kwargs["height"]
        if "material_id" in kwargs:
            w.material_id = kwargs["material_id"]
        if "is_external" in kwargs:
            w.is_external = kwargs["is_external"]
        if "is_bearing" in kwargs:
            w.is_bearing = kwargs["is_bearing"]

    # Geometry queries
    def wall_length(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        p1 = self._junctions[w.junction_start].position
        p2 = self._junctions[w.junction_end].position
        return edge_length(p1, p2)

    def wall_angle(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        p1 = self._junctions[w.junction_start].position
        p2 = self._junctions[w.junction_end].position
        return edge_angle(p1, p2)

    # Topology analysis
    def detect_minimal_cycles(self):
        # Detect all minimal (face) cycles in the planar graph.
        # Uses NetworkX planar embedding for face traversal when possible,
        # falls back to minimum_cycle_basis for non-planar or disconnected graphs.
        # Returns list of cycles, each cycle is a list of junction IDs in order.
        if self._graph.number_of_edges() < 3:
            return []

        try:
            return self._detect_cycles_planar()
        except nx.NetworkXException:
            return self._detect_cycles_fallback()

    def _detect_cycles_planar(self):
        # Use the planar embedding traverse_face() to enumerate all faces.
        is_planar, embedding = nx.check_planarity(self._graph)
        if not is_planar:
            raise nx.NetworkXException("Graph is not planar")

        faces = []
        visited_half_edges = set()

        for v in embedding:
            for w in embedding.neighbors_cw_order(v):
                if (v, w) in visited_half_edges:
                    continue
                face = embedding.traverse_face(v, w)
                # Mark all half-edges of this face as visited.
                for i in range(len(face)):
                    visited_half_edges.add((face[i], face[(i + 1) % len(face)]))
                if len(face) >= 3:
                    faces.append(face)

        # Filter out the outer (unbounded) face — the one with the largest area.
        # For a single room both faces have equal area; removing either is fine
        # because both represent the same polygon (just opposite winding).
        if len(faces) > 1:
            from ..utils.math_helpers import polygon_area as _pa
            faces.sort(key=lambda f: _pa(self.get_cycle_vertices(f)))
            faces = faces[:-1]

        return faces

    def _detect_cycles_fallback(self):
        # Fallback for disconnected or non-planar graphs.
        try:
            basis = nx.minimum_cycle_basis(self._graph)
        except nx.NetworkXError:
            return []
        # minimum_cycle_basis returns sets of nodes; we need ordered cycles.
        ordered_cycles = []
        for cycle_nodes in basis:
            ordered = self._order_cycle(cycle_nodes)
            if ordered and len(ordered) >= 3:
                ordered_cycles.append(ordered)
        return ordered_cycles

    def _order_cycle(self, node_set):
        # Given a set of nodes forming a cycle, return them in traversal order.
        sub = self._graph.subgraph(node_set)
        try:
            cycle = nx.find_cycle(sub)
            return [e[0] for e in cycle]
        except nx.NetworkXError:
            return list(node_set)

    def is_planar(self):
        if self._graph.number_of_nodes() < 3:
            return True
        is_planar, _ = nx.check_planarity(self._graph)
        return is_planar

    def get_cycle_vertices(self, cycle):
        # Return ordered (x,y) positions for a cycle (list of junction IDs).
        return [self._junctions[jid].position for jid in cycle if jid in self._junctions]

    # Bulk queries
    def junction_count(self):
        return len(self._junctions)

    def wall_count(self):
        return len(self._walls)
