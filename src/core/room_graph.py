"""
Layer 2 — Room Graph (semantic dual graph).

Derives rooms and adjacency information from the structural graph (Layer 1)
by detecting minimal face cycles.  Rooms are created, updated, and removed
automatically whenever :meth:`RoomGraph.sync_from_structural_graph` is called.

No bpy dependency — safe to import in unit tests without Blender.
"""

import uuid
import re

from ..utils.math_helpers import polygon_area, polygon_centroid, polygon_perimeter, aspect_ratio
from .validators import validate_room_area, validate_aspect_ratio, validate_room_vertex_count


# Room — node in the room graph (Layer 2)
class Room:
    """A room node in the semantic room graph (Layer 2).

    Derived from a minimal face cycle in the structural graph.
    Geometric attributes (``area``, ``perimeter``, ``centroid``) are
    recomputed whenever the cycle geometry changes during sync.

    Attributes:
        id (str): Unique UUID string identifier.
        cycle (list[str]): Ordered list of junction IDs forming the room boundary.
        name (str): User-editable room label (e.g. ``'Room 1'``).
        area (float): Floor area in square metres.
        perimeter (float): Boundary perimeter in metres.
        centroid (tuple[float, float]): Centroid ``(x, y)`` in metres.
        height (float): Maximum wall height along the room boundary.
    """
    def __init__(self, cycle, room_id=None):
        self.id = room_id or str(uuid.uuid4())
        self.cycle = list(cycle)  # ordered list of junction IDs
        self.name = ""
        self.area = 0.0
        self.perimeter = 0.0
        self.centroid = (0.0, 0.0)
        self.height = 0.0

    def __repr__(self):
        return f"Room({self.id[:8]}, name={self.name!r}, area={self.area:.2f})"


# Adjacency — edge in the room graph
class Adjacency:
    """An edge in the semantic room graph representing a shared wall between two rooms.

    Attributes:
        room_a (str): ID of the first :class:`Room`.
        room_b (str): ID of the second :class:`Room`.
        shared_wall (str): ID of the shared :class:`~floorplanmaster.core.structural_graph.Wall`.
    """
    def __init__(self, room_a_id, room_b_id, shared_wall_id):
        self.room_a = room_a_id
        self.room_b = room_b_id
        self.shared_wall = shared_wall_id

    def __repr__(self):
        return f"Adjacency({self.room_a[:8]}↔{self.room_b[:8]})"


# RoomGraph — Layer 2
class RoomGraph:
    """Layer 2 — Semantic dual graph of rooms and their adjacencies.

    Rooms are discovered automatically from minimal cycles in the
    :class:`~floorplanmaster.core.structural_graph.StructuralGraph` (Layer 1).
    Existing rooms are matched to cycles by a rotation- and direction-invariant
    canonical key so that room metadata (name, custom properties) persists
    across topology edits.
    """

    def __init__(self, structural_graph):
        self._sg = structural_graph  # reference to Layer 1
        self._rooms = {}             # room_id -> Room
        self._adjacencies = []       # list of Adjacency objects
        # Mapping: canonical cycle key -> room_id (for matching existing rooms).
        self._cycle_room_map = {}
        # Auto-incrementing room number for default names.
        self._next_room_number = 1

    # Synchronisation with Layer 1
    def sync_from_structural_graph(self):
        """Re-detect cycles from Layer 1 and create, update, or remove rooms.

        This is the core lazy synchronisation mechanism.  It should be called
        after any structural topology change (add/remove junction or wall).
        """
        detected_cycles = self._sg.detect_minimal_cycles()

        # Build canonical keys for detected cycles.
        detected_map = {}  # canonical_key -> cycle (junction ID list)
        for cycle in detected_cycles:
            key = self._cycle_key(cycle)
            detected_map[key] = cycle

        # Determine which rooms to keep, create, or remove.
        existing_keys = set(self._cycle_room_map.keys())
        new_keys = set(detected_map.keys())

        keys_to_add = new_keys - existing_keys
        keys_to_remove = existing_keys - new_keys
        keys_to_keep = existing_keys & new_keys

        # Remove rooms whose cycles no longer exist.
        for key in keys_to_remove:
            room_id = self._cycle_room_map.pop(key, None)
            if room_id:
                self._rooms.pop(room_id, None)

        # Create rooms for new cycles.
        for key in keys_to_add:
            cycle = detected_map[key]
            vertices = self._sg.get_cycle_vertices(cycle)
            if len(vertices) < 3:
                continue

            area = polygon_area(vertices)
            # Skip cycles that are too small or have bad aspect ratio (validation).
            try:
                validate_room_vertex_count(len(vertices))
                validate_room_area(area)
                ar = aspect_ratio(vertices)
                validate_aspect_ratio(ar)
            except Exception:
                continue

            room = Room(cycle)
            room.name = self._allocate_default_room_name()
            room.area = area
            room.perimeter = polygon_perimeter(vertices)
            room.centroid = polygon_centroid(vertices)
            # Height = max wall height along the cycle boundary.
            room.height = self._max_wall_height(cycle)
            self._rooms[room.id] = room
            self._cycle_room_map[key] = room.id

        # Update metrics for kept rooms (geometry may have changed).
        for key in keys_to_keep:
            room_id = self._cycle_room_map[key]
            room = self._rooms.get(room_id)
            if room is None:
                continue
            cycle = detected_map[key]
            room.cycle = list(cycle)
            vertices = self._sg.get_cycle_vertices(cycle)
            if len(vertices) >= 3:
                room.area = polygon_area(vertices)
                room.perimeter = polygon_perimeter(vertices)
                room.centroid = polygon_centroid(vertices)
                room.height = self._max_wall_height(cycle)

        # Rebuild adjacencies.
        self._rebuild_adjacencies()
        self.recompute_default_room_counter()

    # Room queries
    def get_room(self, room_id):
        """Return the :class:`Room` with the given ID, or ``None``."""
        return self._rooms.get(room_id)

    def get_all_rooms(self):
        """Return a list of all rooms in the graph."""
        return list(self._rooms.values())

    def total_area(self):
        """Return the total floor area of all rooms in square metres."""
        return sum(r.area for r in self._rooms.values())

    # Room metadata updates
    def set_room_name(self, room_id, name):
        """Set the display name of a room and return the effective name.

        Ignores blank names (returns the existing name unchanged).

        Args:
            room_id (str): Target room ID.
            name (str): Proposed new name.

        Returns:
            str | None: Effective name after update, or ``None`` if the room
            was not found.
        """
        room = self._rooms.get(room_id)
        if room is None:
            return None
        if str(name).strip() == "":
            return room.name
        room.name = name
        return room.name

    def delete_room(self, room_id):
        """Delete a room by removing its non-shared boundary walls.

        Walls shared with another room are preserved.  Junctions that become
        isolated after wall removal are also cleaned up.  Calls
        :meth:`sync_from_structural_graph` at the end.

        Args:
            room_id (str): ID of the room to delete.

        Returns:
            list[str]: IDs of the wall segments that were removed.
        """
        room = self._rooms.get(room_id)
        if room is None:
            return []

        edge_usage = self._build_edge_usage()
        removed_wall_ids = []
        touched_junctions = set()

        n = len(room.cycle)
        for i in range(n):
            jid_a = room.cycle[i]
            jid_b = room.cycle[(i + 1) % n]
            edge_key = tuple(sorted((jid_a, jid_b)))

            # Preserve boundary edges shared with another room.
            if edge_usage.get(edge_key, 0) > 1:
                continue

            wall = self._sg.get_wall_between(jid_a, jid_b)
            if wall is None:
                continue

            touched_junctions.add(wall.junction_start)
            touched_junctions.add(wall.junction_end)
            self._sg.remove_wall(wall.id)
            removed_wall_ids.append(wall.id)

        # Remove newly isolated junctions to keep Layer 1 clean.
        for jid in touched_junctions:
            if len(self._sg.get_walls_for_junction(jid)) == 0:
                self._sg.remove_junction(jid)

        self.sync_from_structural_graph()
        return removed_wall_ids

    # Adjacency queries
    def get_adjacencies(self):
        """Return a list of all :class:`Adjacency` edges."""
        return list(self._adjacencies)

    def get_neighbors(self, room_id):
        """Return all rooms adjacent to *room_id* as ``(room, adjacency)`` pairs."""
        # Return list of (room, adjacency) for all rooms adjacent to room_id.
        neighbors = []
        for adj in self._adjacencies:
            if adj.room_a == room_id:
                other = self._rooms.get(adj.room_b)
                if other:
                    neighbors.append((other, adj))
            elif adj.room_b == room_id:
                other = self._rooms.get(adj.room_a)
                if other:
                    neighbors.append((other, adj))
        return neighbors

    def are_adjacent(self, room_id_a, room_id_b):
        """Return ``True`` if the two rooms share a wall."""
        for adj in self._adjacencies:
            pair = {adj.room_a, adj.room_b}
            if pair == {room_id_a, room_id_b}:
                return True
        return False

    def recompute_default_room_counter(self):
        """Ensure the auto-increment room number stays monotonic after restore/reconstruction."""
        # Keep default-room numbering monotonic after restore/reconstruction.
        max_num = 0
        for room in self._rooms.values():
            if not room.name:
                continue
            m = re.match(r"^Room\s+(\d+)$", str(room.name).strip())
            if m:
                max_num = max(max_num, int(m.group(1)))
        self._next_room_number = max(self._next_room_number, max_num + 1, len(self._rooms) + 1)

    # Internal helpers
    def _allocate_default_room_name(self):
        """Allocate the next unused 'Room N' label and advance the counter."""
        used = set()
        for room in self._rooms.values():
            if not room.name:
                continue
            m = re.match(r"^Room\s+(\d+)$", str(room.name).strip())
            if m:
                used.add(int(m.group(1)))

        n = max(1, self._next_room_number)
        while n in used:
            n += 1
        self._next_room_number = n + 1
        return f"Room {n}"

    @staticmethod
    def _cycle_key(cycle):
        """Return a rotation- and direction-invariant canonical key for a cycle.

        Picks the minimum junction ID as the starting point then chooses the
        rotation direction (forward vs. reverse) that yields the
        lexicographically smallest tuple.
        """
        if not cycle:
            return ()
        min_val = min(cycle)
        idx = cycle.index(min_val)
        n = len(cycle)
        # Forward rotation.
        forward = tuple(cycle[(idx + i) % n] for i in range(n))
        # Reverse rotation.
        reverse = tuple(cycle[(idx - i) % n] for i in range(n))
        return min(forward, reverse)

    def _max_wall_height(self, cycle):
        """Return the maximum wall height along the room boundary cycle."""
        max_h = 0.0
        n = len(cycle)
        for i in range(n):
            jid_a = cycle[i]
            jid_b = cycle[(i + 1) % n]
            wall = self._sg.get_wall_between(jid_a, jid_b)
            if wall and wall.height > max_h:
                max_h = wall.height
        return max_h

    def _build_edge_usage(self):
        """Return a dict mapping each boundary edge key to the count of rooms using it."""
        edge_usage = {}
        for room in self._rooms.values():
            n = len(room.cycle)
            for i in range(n):
                ek = tuple(sorted((room.cycle[i], room.cycle[(i + 1) % n])))
                edge_usage[ek] = edge_usage.get(ek, 0) + 1
        return edge_usage

    def _rebuild_adjacencies(self):
        """Rebuild the adjacency list from the current room set.

        Two rooms are adjacent if they share at least one wall edge.
        """
        self._adjacencies = []
        if len(self._rooms) < 2:
            return

        # Build edge -> list of room_ids mapping.
        edge_rooms = {}  # (jid_a, jid_b) sorted -> [room_ids]
        for room in self._rooms.values():
            n = len(room.cycle)
            for i in range(n):
                ek = tuple(sorted((room.cycle[i], room.cycle[(i + 1) % n])))
                edge_rooms.setdefault(ek, []).append(room.id)

        seen = set()
        for ek, rids in edge_rooms.items():
            if len(rids) == 2:
                pair = tuple(sorted(rids))
                if pair not in seen:
                    seen.add(pair)
                    wall = self._sg.get_wall_between(ek[0], ek[1])
                    wall_id = wall.id if wall else ""
                    self._adjacencies.append(Adjacency(pair[0], pair[1], wall_id))
