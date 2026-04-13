import pytest

from src.core.structural_graph import StructuralGraph
from src.core.room_graph import RoomGraph, Room, Adjacency
from src.utils.constants import RoomType


# Helpers

def make_single_room():
    # Unit square room.
    sg = StructuralGraph()
    j1 = sg.add_junction((0, 0))
    j2 = sg.add_junction((3, 0))
    j3 = sg.add_junction((3, 3))
    j4 = sg.add_junction((0, 3))
    sg.add_wall(j1.id, j2.id)
    sg.add_wall(j2.id, j3.id)
    sg.add_wall(j3.id, j4.id)
    sg.add_wall(j4.id, j1.id)
    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    return sg, rg, [j1, j2, j3, j4]


def make_two_rooms():
    # Two 3x3 rooms side by side sharing a wall.
    sg = StructuralGraph()
    j1 = sg.add_junction((0, 0))
    j2 = sg.add_junction((3, 0))
    j3 = sg.add_junction((6, 0))
    j4 = sg.add_junction((6, 3))
    j5 = sg.add_junction((3, 3))
    j6 = sg.add_junction((0, 3))

    sg.add_wall(j1.id, j2.id)
    sg.add_wall(j2.id, j3.id)
    sg.add_wall(j3.id, j4.id)
    sg.add_wall(j4.id, j5.id)
    sg.add_wall(j5.id, j6.id)
    sg.add_wall(j6.id, j1.id)
    sg.add_wall(j2.id, j5.id)  # shared wall

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    return sg, rg, [j1, j2, j3, j4, j5, j6]


# Room creation via sync

class TestRoomCreation:
    def test_single_room_detected(self):
        _, rg, _ = make_single_room()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 1

    def test_room_area(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        assert room.area == pytest.approx(9.0)

    def test_room_perimeter(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        assert room.perimeter == pytest.approx(12.0)

    def test_room_centroid(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        cx, cy = room.centroid
        assert cx == pytest.approx(1.5)
        assert cy == pytest.approx(1.5)

    def test_room_has_id(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        assert room.id
        assert isinstance(room.id, str)

    def test_two_rooms_detected(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 2

    def test_two_rooms_areas(self):
        _, rg, _ = make_two_rooms()
        areas = sorted([r.area for r in rg.get_all_rooms()])
        assert areas[0] == pytest.approx(9.0)
        assert areas[1] == pytest.approx(9.0)

    def test_no_room_for_open_graph(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        j3 = sg.add_junction((1, 1))
        sg.add_wall(j1.id, j2.id)
        sg.add_wall(j2.id, j3.id)
        rg = RoomGraph(sg)
        rg.sync_from_structural_graph()
        assert rg.get_all_rooms() == []

    def test_small_room_filtered(self):
        # Room area < 1.0 m² should be excluded.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((0.5, 0))
        j3 = sg.add_junction((0.5, 0.5))
        j4 = sg.add_junction((0, 0.5))
        sg.add_wall(j1.id, j2.id)
        sg.add_wall(j2.id, j3.id)
        sg.add_wall(j3.id, j4.id)
        sg.add_wall(j4.id, j1.id)
        rg = RoomGraph(sg)
        rg.sync_from_structural_graph()
        # 0.5*0.5=0.25 m² < 1.0 m² minimum.
        assert rg.get_all_rooms() == []


# Room persistence across sync

class TestRoomPersistence:
    def test_id_preserved_on_resync(self):
        sg, rg, juncs = make_single_room()
        room = rg.get_all_rooms()[0]
        original_id = room.id
        # Move a junction — room shape changes but ID persists.
        sg.move_junction(juncs[2].id, (4, 4))
        rg.sync_from_structural_graph()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 1
        assert rooms[0].id == original_id

    def test_area_updated_on_resync(self):
        sg, rg, juncs = make_single_room()
        # Original area: 3*3=9.
        sg.move_junction(juncs[1].id, (6, 0))
        sg.move_junction(juncs[2].id, (6, 3))
        rg.sync_from_structural_graph()
        room = rg.get_all_rooms()[0]
        assert room.area == pytest.approx(18.0)

    def test_metadata_preserved_on_resync(self):
        sg, rg, juncs = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_name(room.id, "Living Room")
        rg.set_room_type(room.id, RoomType.LIVING)
        # Resync after geometry change.
        sg.move_junction(juncs[2].id, (4, 4))
        rg.sync_from_structural_graph()
        room = rg.get_all_rooms()[0]
        assert room.name == "Living Room"
        assert room.room_type == RoomType.LIVING

    def test_room_removed_on_wall_delete(self):
        sg, rg, _ = make_single_room()
        assert len(rg.get_all_rooms()) == 1
        walls = sg.get_all_walls()
        sg.remove_wall(walls[0].id)
        rg.sync_from_structural_graph()
        assert rg.get_all_rooms() == []


# Adjacency

class TestAdjacency:
    def test_two_rooms_adjacent(self):
        _, rg, _ = make_two_rooms()
        adj = rg.get_adjacencies()
        assert len(adj) == 1

    def test_adjacency_attributes(self):
        _, rg, _ = make_two_rooms()
        adj = rg.get_adjacencies()[0]
        assert isinstance(adj, Adjacency)
        assert adj.shared_wall != ""

    def test_are_adjacent(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        assert rg.are_adjacent(rooms[0].id, rooms[1].id)

    def test_not_adjacent_single_room(self):
        _, rg, _ = make_single_room()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 1
        assert rg.get_adjacencies() == []

    def test_get_neighbors(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        neighbors = rg.get_neighbors(rooms[0].id)
        assert len(neighbors) == 1
        assert neighbors[0][0].id == rooms[1].id


# Room queries

class TestRoomQueries:
    def test_get_room(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        assert rg.get_room(room.id) is room

    def test_get_room_nonexistent(self):
        _, rg, _ = make_single_room()
        assert rg.get_room("nonexistent") is None

    def test_get_rooms_by_type(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        rg.set_room_type(rooms[0].id, RoomType.LIVING)
        rg.set_room_type(rooms[1].id, RoomType.TECHNICAL)
        assert len(rg.get_rooms_by_type(RoomType.LIVING)) == 1
        assert len(rg.get_rooms_by_type(RoomType.TECHNICAL)) == 1
        assert len(rg.get_rooms_by_type(RoomType.COMMUNICATION)) == 0

    def test_total_area(self):
        _, rg, _ = make_two_rooms()
        assert rg.total_area() == pytest.approx(18.0)

    def test_total_area_by_type(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        rg.set_room_type(rooms[0].id, RoomType.LIVING)
        assert rg.total_area(RoomType.LIVING) == pytest.approx(9.0)
        assert rg.total_area(RoomType.TECHNICAL) == pytest.approx(0.0)


# Room metadata

class TestRoomMetadata:
    def test_set_name(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_name(room.id, "Kitchen")
        assert room.name == "Kitchen"

    def test_set_type(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_type(room.id, RoomType.COMMUNICATION)
        assert room.room_type == RoomType.COMMUNICATION

    def test_default_room_type(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        assert room.room_type == RoomType.GENERIC
