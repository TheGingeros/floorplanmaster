import uuid

from ..utils.math_helpers import polygon_area, polygon_centroid, polygon_perimeter, aspect_ratio
from .validators import validate_room_area, validate_aspect_ratio, validate_room_vertex_count
from .structural_graph import StructuralGraph


# Room — node in the room graph (Layer 2)
class Room:
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
    def __init__(self, room_a_id, room_b_id, shared_wall_id):
        self.room_a = room_a_id
        self.room_b = room_b_id
        self.shared_wall = shared_wall_id

    def __repr__(self):
        return f"Adjacency({self.room_a[:8]}↔{self.room_b[:8]})"


# RoomGraph — Layer 2
class RoomGraph:
    # Semantic dual graph derived from StructuralGraph (Layer 1).
    # Rooms are created/removed automatically based on cycle detection.

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
        # Detect cycles in Layer 1 and create/update/remove rooms accordingly.
        # This is the core lazy detection mechanism.
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
            room.name = f"Room {self._next_room_number}"
            self._next_room_number += 1
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

    # Room queries
    def get_room(self, room_id):
        return self._rooms.get(room_id)

    def get_all_rooms(self):
        return list(self._rooms.values())

    def total_area(self):
        return sum(r.area for r in self._rooms.values())

    # Room metadata updates
    def set_room_name(self, room_id, name):
        room = self._rooms.get(room_id)
        if room:
            room.name = name

    # Adjacency queries
    def get_adjacencies(self):
        return list(self._adjacencies)

    def get_neighbors(self, room_id):
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
        for adj in self._adjacencies:
            pair = {adj.room_a, adj.room_b}
            if pair == {room_id_a, room_id_b}:
                return True
        return False

    # Internal helpers
    @staticmethod
    def _cycle_key(cycle):
        # Canonical key for a cycle — rotation/direction independent.
        # Normalise: pick smallest element, then choose direction giving
        # lexicographically smallest sequence.
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
        max_h = 0.0
        n = len(cycle)
        for i in range(n):
            jid_a = cycle[i]
            jid_b = cycle[(i + 1) % n]
            wall = self._sg.get_wall_between(jid_a, jid_b)
            if wall and wall.height > max_h:
                max_h = wall.height
        return max_h

    def _rebuild_adjacencies(self):
        # Two rooms are adjacent if they share at least one wall (edge).
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
