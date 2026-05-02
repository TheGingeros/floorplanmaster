import pytest

from src.core.structural_graph import StructuralGraph
from src.core.room_graph import RoomGraph, Room, Adjacency


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


def make_single_room_with_branch():
    # One closed room plus one branch wall that does not participate in any cycle.
    sg, rg, juncs = make_single_room()
    j_branch = sg.add_junction((0, -2))
    w_branch = sg.add_wall(juncs[0].id, j_branch.id)
    rg.sync_from_structural_graph()
    return sg, rg, w_branch


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


def make_l_shape_three_rooms():
    # Three 3x3 rooms in an L shape where the middle-lower room shares
    # one wall with the left room and one wall with the upper room.
    sg = StructuralGraph()
    j1 = sg.add_junction((0, 0))
    j2 = sg.add_junction((3, 0))
    j3 = sg.add_junction((6, 0))
    j4 = sg.add_junction((6, 3))
    j5 = sg.add_junction((6, 6))
    j6 = sg.add_junction((3, 6))
    j7 = sg.add_junction((3, 3))
    j8 = sg.add_junction((0, 3))

    # Outer shell.
    sg.add_wall(j1.id, j2.id)
    sg.add_wall(j2.id, j3.id)
    sg.add_wall(j3.id, j4.id)
    sg.add_wall(j4.id, j5.id)
    sg.add_wall(j5.id, j6.id)
    sg.add_wall(j6.id, j7.id)
    sg.add_wall(j7.id, j8.id)
    sg.add_wall(j8.id, j1.id)

    # Shared walls around the middle room.
    sg.add_wall(j2.id, j7.id)  # shared with left room
    sg.add_wall(j7.id, j4.id)  # shared with upper room

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    return sg, rg


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
        # Resync after geometry change.
        sg.move_junction(juncs[2].id, (4, 4))
        rg.sync_from_structural_graph()
        room = rg.get_all_rooms()[0]
        assert room.name == "Living Room"

    def test_room_removed_on_wall_delete(self):
        sg, rg, _ = make_single_room()
        assert len(rg.get_all_rooms()) == 1
        walls = sg.get_all_walls()
        sg.remove_wall(walls[0].id)
        rg.sync_from_structural_graph()
        assert rg.get_all_rooms() == []

    def test_room_unchanged_when_non_cycle_wall_removed(self):
        sg, rg, w_branch = make_single_room_with_branch()
        assert len(rg.get_all_rooms()) == 1

        sg.remove_wall(w_branch.id)
        rg.sync_from_structural_graph()

        assert len(rg.get_all_rooms()) == 1

    def test_room_metrics_recomputed_after_wall_normal_slide(self):
        sg, rg, juncs = make_single_room()

        wall = sg.get_wall_between(juncs[0].id, juncs[1].id)
        assert wall is not None

        # Slide the bottom wall upward by 1 m using midpoint edit.
        sg.slide_wall_normal(wall.id, target_mid_x=1.5, target_mid_y=1.0)
        rg.sync_from_structural_graph()

        room = rg.get_all_rooms()[0]
        assert room.area == pytest.approx(6.0)
        assert room.perimeter == pytest.approx(10.0)


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

    def test_total_area(self):
        _, rg, _ = make_two_rooms()
        assert rg.total_area() == pytest.approx(18.0)


# Room metadata

class TestRoomMetadata:
    def test_set_name(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_name(room.id, "Kitchen")
        assert room.name == "Kitchen"

    def test_blank_name_keeps_previous_name(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_name(room.id, "Kitchen")

        effective_name = rg.set_room_name(room.id, "")

        assert effective_name == "Kitchen"
        assert room.name == "Kitchen"

    def test_whitespace_name_keeps_previous_name(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        rg.set_room_name(room.id, "Kitchen")

        effective_name = rg.set_room_name(room.id, "   ")

        assert effective_name == "Kitchen"
        assert room.name == "Kitchen"


class TestRoomDefaultNumbering:
    def test_default_name_uses_next_free_number(self):
        _, rg, _ = make_two_rooms()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 2

        rooms[0].name = "Room 10"
        rooms[1].name = "Office"
        rg.recompute_default_room_counter()

        candidate = rg._allocate_default_room_name()
        assert candidate == "Room 11"

    def test_counter_is_raised_by_existing_default_names(self):
        _, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]
        room.name = "Room 7"
        rg.recompute_default_room_counter()

        candidate = rg._allocate_default_room_name()
        assert candidate == "Room 8"


class TestRoomDeletion:
    def test_delete_single_room_removes_all_walls(self):
        sg, rg, _ = make_single_room()
        room = rg.get_all_rooms()[0]

        removed = rg.delete_room(room.id)

        assert len(removed) == 4
        assert rg.get_all_rooms() == []
        assert sg.wall_count() == 0
        assert sg.junction_count() == 0

    def test_delete_middle_room_keeps_shared_walls(self):
        sg, rg = make_l_shape_three_rooms()
        rooms = rg.get_all_rooms()
        assert len(rooms) == 3

        # The middle-lower room has centroid around (4.5, 1.5).
        room_b = min(rooms, key=lambda r: (r.centroid[0] - 4.5) ** 2 + (r.centroid[1] - 1.5) ** 2)

        j_a = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 3.0) ** 2 + (j.position[1] - 0.0) ** 2)
        j_b = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 3.0) ** 2 + (j.position[1] - 3.0) ** 2)
        j_c = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 6.0) ** 2 + (j.position[1] - 3.0) ** 2)

        shared_ab = sg.get_wall_between(j_a.id, j_b.id)
        shared_bc = sg.get_wall_between(j_b.id, j_c.id)
        assert shared_ab is not None
        assert shared_bc is not None

        rg.delete_room(room_b.id)

        # Shared walls with neighboring rooms must remain.
        assert sg.get_wall(shared_ab.id) is not None
        assert sg.get_wall(shared_bc.id) is not None

        # Two rooms should remain after deleting the middle one.
        assert len(rg.get_all_rooms()) == 2

    def test_delete_room_removes_non_shared_boundary_walls(self):
        sg, rg = make_l_shape_three_rooms()
        rooms = rg.get_all_rooms()
        room_b = min(rooms, key=lambda r: (r.centroid[0] - 4.5) ** 2 + (r.centroid[1] - 1.5) ** 2)

        # Non-shared walls of middle room: bottom and right.
        j_bottom_l = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 3.0) ** 2 + (j.position[1] - 0.0) ** 2)
        j_bottom_r = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 6.0) ** 2 + (j.position[1] - 0.0) ** 2)
        j_right_t = min(sg.get_all_junctions(), key=lambda j: (j.position[0] - 6.0) ** 2 + (j.position[1] - 3.0) ** 2)

        bottom = sg.get_wall_between(j_bottom_l.id, j_bottom_r.id)
        right = sg.get_wall_between(j_bottom_r.id, j_right_t.id)
        assert bottom is not None
        assert right is not None

        rg.delete_room(room_b.id)

        assert sg.get_wall(bottom.id) is None
        assert sg.get_wall(right.id) is None
