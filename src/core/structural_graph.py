import uuid

import networkx as nx

from ..utils.constants import (
    DEFAULT_THICKNESS,
    DEFAULT_HEIGHT,
    DEFAULT_CONNECTION_GROUP,
    DEFAULT_JOIN_PRIORITY,
    DEFAULT_JUNCTION_ORDER,
)
from ..utils.math_helpers import edge_length, edge_angle, point_distance
from .validators import (
    ValidationError,
    validate_thickness,
    validate_height,
    validate_opening_width,
    validate_opening_height,
    validate_opening_placement,
    validate_opening_sill,
    clamp_opening_position,
    can_fit_opening,
    get_opening_center_intervals,
    get_opening_free_spans,
    max_opening_width,
    max_opening_width_at_position,
    E_WALL_DUPLICATE,
    E_WALL_SELF_LOOP,
    E_JUNCTION_DUPLICATE,
)


# Junction — node in the structural graph
# Representing position of one vertex, two verteces make up one wall
class Junction:
    def __init__(self, position, junction_id=None):
        self.id = junction_id or str(uuid.uuid4()) # assign given ID, if None, create a new one
        self.position = tuple(position)  # (x, y)

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
        connection_group=DEFAULT_CONNECTION_GROUP,
        join_priority=DEFAULT_JOIN_PRIORITY,
        junction_order=DEFAULT_JUNCTION_ORDER,
        wall_id=None,
    ):
        self.id = wall_id or str(uuid.uuid4())
        self.junction_start = junction_start_id # assign given ID, if None, create a new one
        self.junction_end = junction_end_id
        self.thickness = thickness
        self.height = height
        # Option B groundwork: join policy metadata (currently passive).
        self.connection_group = int(connection_group)
        self.join_priority = int(join_priority)
        self.junction_order = int(junction_order)
        self.openings = []  # list of Opening objects

    def __repr__(self):
        return f"Wall({self.id[:8]}, {self.junction_start[:8]}→{self.junction_end[:8]})"


# Opening — door or window on a wall
class Opening:
    def __init__(
        self,
        wall_id,
        opening_type='DOOR',
        position=0.5,
        width=0.9,
        height=2.1,
        sill_height=0.0,
        opening_id=None,
    ):
        self.id = opening_id or str(uuid.uuid4())
        self.wall_id = wall_id
        self.opening_type = opening_type  # 'DOOR' or 'WINDOW'
        self.position = position          # 0.0–1.0 along wall centerline
        self.width = width
        self.height = height
        self.sill_height = sill_height    # distance from floor (0 for doors)

    def __repr__(self):
        return f"Opening({self.id[:8]}, {self.opening_type}, t={self.position:.2f})"


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
        # Cache for the leaf-pruned graph used by detect_minimal_cycles.
        # Invalidated whenever topology changes (add/remove junction or wall,
        # move junction).  Avoids an O(V+E) graph copy on every wall placement.
        self._pruned_graph_cache = None
        self._topology_dirty = True

    # -- helpers --
    @staticmethod
    def _pos_key(position, precision=6):
        # Round to avoid floating-point duplicates.
        return (round(position[0], precision), round(position[1], precision))

    def _edge_key(self, jid_a, jid_b):
        # Canonical unordered pair.
        return tuple(sorted((jid_a, jid_b)))

    # Junction CRUD
    def add_junction(self, position, junction_id=None):
        pk = self._pos_key(position)
        if pk in self._pos_index:
            raise ValidationError(
                E_JUNCTION_DUPLICATE,
                f"Junction already exists at {position}",
            )
        j = Junction(position, junction_id)
        self._junctions[j.id] = j
        self._graph.add_node(j.id, pos=j.position)
        self._pos_index[pk] = j.id
        self._topology_dirty = True
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
        self._topology_dirty = True

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
        self._topology_dirty = True

    # Wall CRUD
    def add_wall(
        self,
        junction_start_id,
        junction_end_id,
        thickness=DEFAULT_THICKNESS,
        height=DEFAULT_HEIGHT,
        connection_group=DEFAULT_CONNECTION_GROUP,
        join_priority=DEFAULT_JOIN_PRIORITY,
        junction_order=DEFAULT_JUNCTION_ORDER,
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
            connection_group=connection_group,
            join_priority=join_priority,
            junction_order=junction_order,
            wall_id=wall_id,
        )
        self._walls[w.id] = w
        self._graph.add_edge(junction_start_id, junction_end_id, wall_id=w.id)
        self._topology_dirty = True
        return w

    def remove_wall(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return
        ek = self._edge_key(w.junction_start, w.junction_end)
        if self._graph.has_edge(*ek):
            self._graph.remove_edge(*ek)
        del self._walls[wall_id]
        self._topology_dirty = True

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
        if "connection_group" in kwargs:
            w.connection_group = int(kwargs["connection_group"])
        if "join_priority" in kwargs:
            w.join_priority = int(kwargs["join_priority"])
        if "junction_order" in kwargs:
            w.junction_order = int(kwargs["junction_order"])

    # Opening CRUD
    def add_opening(
        self,
        wall_id,
        opening_type='DOOR',
        position=0.5,
        width=0.9,
        height=2.1,
        sill_height=0.0,
        opening_id=None,
    ):
        w = self._walls.get(wall_id)
        if w is None:
            raise ValueError(f"Wall {wall_id} does not exist")

        validate_opening_width(width)
        validate_opening_height(height, wall_height=w.height)
        validate_opening_sill(sill_height, height, w.height)

        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        if not can_fit_opening(
            width,
            wl,
            existing_openings=w.openings,
            inset_start=inset_s,
            inset_end=inset_e,
        ):
            raise ValidationError(
                "E_OPENING_TOO_LARGE",
                f"Wall {wall_id[:8]} has no remaining span for opening width {width:.3f}",
            )
        validate_opening_placement(
            position,
            width,
            wl,
            existing_openings=w.openings,
            inset_start=inset_s,
            inset_end=inset_e,
        )

        op = Opening(
            wall_id,
            opening_type=opening_type,
            position=position,
            width=width,
            height=height,
            sill_height=sill_height,
            opening_id=opening_id,
        )
        w.openings.append(op)
        return op

    def remove_opening(self, opening_id):
        for w in self._walls.values():
            for i, op in enumerate(w.openings):
                if op.id == opening_id:
                    w.openings.pop(i)
                    return True
        return False

    def get_opening(self, opening_id):
        for w in self._walls.values():
            for op in w.openings:
                if op.id == opening_id:
                    return op
        return None

    def get_openings_for_wall(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return []
        return sorted(w.openings, key=lambda op: (op.position, op.id))

    def get_opening_free_spans(self, wall_id, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return []
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return get_opening_free_spans(
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def get_opening_center_intervals(self, wall_id, width, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return []
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return get_opening_center_intervals(
            width,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def can_fit_opening(self, wall_id, width, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return False
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return can_fit_opening(
            width,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def clamp_opening_position(self, wall_id, width, position, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return None
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return clamp_opening_position(
            position,
            width,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def max_opening_width(self, wall_id, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return max_opening_width(
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def max_opening_width_at_position(self, wall_id, position, exclude_opening_id=None):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        wl = self.wall_length(wall_id)
        inset_s = self.junction_inset(w.junction_start, wall_id)
        inset_e = self.junction_inset(w.junction_end, wall_id)
        others = [op for op in w.openings if op.id != exclude_opening_id]
        return max_opening_width_at_position(
            position,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

    def update_opening(self, opening_id, **kwargs):
        op = self.get_opening(opening_id)
        if op is None:
            return
        w = self._walls.get(op.wall_id)
        if w is None:
            return

        new_width = kwargs.get("width", op.width)
        new_height = kwargs.get("height", op.height)
        new_sill = kwargs.get("sill_height", op.sill_height)
        new_pos = kwargs.get("position", op.position)
        new_type = kwargs.get("opening_type", op.opening_type)

        validate_opening_width(new_width)
        validate_opening_height(new_height, wall_height=w.height)
        validate_opening_sill(new_sill, new_height, w.height)

        wl = self.wall_length(op.wall_id)
        others = [o for o in w.openings if o.id != opening_id]
        inset_s = self.junction_inset(w.junction_start, op.wall_id)
        inset_e = self.junction_inset(w.junction_end, op.wall_id)
        if not can_fit_opening(
            new_width,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        ):
            raise ValidationError(
                "E_OPENING_TOO_LARGE",
                f"Wall {op.wall_id[:8]} has no remaining span for opening width {new_width:.3f}",
            )
        validate_opening_placement(
            new_pos,
            new_width,
            wl,
            existing_openings=others,
            inset_start=inset_s,
            inset_end=inset_e,
        )

        op.width = new_width
        op.height = new_height
        op.sill_height = new_sill
        op.position = new_pos
        op.opening_type = new_type


    # Geometry queries
    def wall_length(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        p1 = self._junctions[w.junction_start].position
        p2 = self._junctions[w.junction_end].position
        return edge_length(p1, p2)

    def junction_inset(self, junction_id, wall_id):
        # Conservative inset along wall_id at junction_id caused by connecting walls.
        # Returns max(neighbor.thickness / 2) for all walls sharing that junction.
        # Returns 0.0 for free endpoints (no connecting walls).
        # Used to restrict opening positions to the visible (non-overlapping) wall surface.
        neighbors = [w for w in self.get_walls_for_junction(junction_id) if w.id != wall_id]
        if not neighbors:
            return 0.0
        return max(w.thickness / 2.0 for w in neighbors)

    def wall_angle(self, wall_id):
        w = self._walls.get(wall_id)
        if w is None:
            return 0.0
        p1 = self._junctions[w.junction_start].position
        p2 = self._junctions[w.junction_end].position
        return edge_angle(p1, p2)

    # Topology analysis
    def _prune_leaves(self, g):
        # Iteratively remove degree-0 and degree-1 nodes until stable.
        # Dangling endpoints (open wall segments) are degree-1; they have no
        # role in any closed cycle and their presence confuses the planar
        # embedding — NetworkX may route them "inside" an existing face,
        # causing traverse_face() to revisit a junction twice and return a
        # degenerate cycle that destroys the existing room floor face.
        #
        # Result is cached and only recomputed when _topology_dirty is set,
        # which happens on every add/remove junction/wall and move_junction.
        # This avoids an O(V+E) graph copy on every wall placement click.
        if not self._topology_dirty and self._pruned_graph_cache is not None:
            return self._pruned_graph_cache
        pruned = g.copy()
        changed = True
        while changed:
            leaves = [n for n, d in pruned.degree() if d <= 1]
            changed = bool(leaves)
            pruned.remove_nodes_from(leaves)
        self._pruned_graph_cache = pruned
        self._topology_dirty = False
        return pruned

    def detect_minimal_cycles(self):
        # Detect all minimal (face) cycles in the planar graph.
        # Uses minimum_cycle_basis (MCB) — an algebraic approach that returns
        # exactly the inner face cycles without any outer-boundary face.
        # This avoids the combinatorial planar embedding path which can
        # mis-order neighbors geometrically and produce a self-intersecting
        # "outer face" whose shoelace area is smaller than an inner room,
        # causing the wrong face to be dropped and adjacent rooms to be merged.
        #
        # Leaf pruning is applied first: dangling wall segments (degree-1 nodes)
        # are stripped so MCB only sees nodes belonging to closed cycles.
        if self._graph.number_of_edges() < 3:
            return []
        pruned = self._prune_leaves(self._graph)
        if pruned.number_of_edges() < 3:
            return []

        return self._detect_cycles_fallback(pruned)

    def _detect_cycles_planar(self, graph):
        # Use the planar embedding traverse_face() to enumerate all faces.
        is_planar, embedding = nx.check_planarity(graph)
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

    def _detect_cycles_fallback(self, graph):
        # Fallback for disconnected or non-planar graphs.
        try:
            basis = nx.minimum_cycle_basis(graph)
        except nx.NetworkXError:
            return []
        # minimum_cycle_basis returns sets of nodes; we need ordered cycles.
        ordered_cycles = []
        for cycle_nodes in basis:
            ordered = self._order_cycle(cycle_nodes, graph)
            if ordered and len(ordered) >= 3:
                ordered_cycles.append(ordered)
        return ordered_cycles

    def _order_cycle(self, node_set, graph=None):
        # Given a set of nodes forming a cycle, return them in traversal order.
        if graph is None:
            graph = self._graph
        sub = graph.subgraph(node_set)
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
