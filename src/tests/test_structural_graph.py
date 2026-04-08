import math
import pytest

from src.core.structural_graph import StructuralGraph, Junction, Wall
from src.core.validators import ValidationError, E_JUNCTION_DUPLICATE, E_WALL_DUPLICATE, E_WALL_SELF_LOOP


# Helpers
def make_square_graph():
    # Create a graph with 4 junctions forming a unit square and 4 walls.
    sg = StructuralGraph()
    j1 = sg.add_junction((0, 0))
    j2 = sg.add_junction((1, 0))
    j3 = sg.add_junction((1, 1))
    j4 = sg.add_junction((0, 1))
    w1 = sg.add_wall(j1.id, j2.id)
    w2 = sg.add_wall(j2.id, j3.id)
    w3 = sg.add_wall(j3.id, j4.id)
    w4 = sg.add_wall(j4.id, j1.id)
    return sg, [j1, j2, j3, j4], [w1, w2, w3, w4]


# Junction CRUD
class TestJunctionCRUD:
    def test_add_junction(self):
        sg = StructuralGraph()
        j = sg.add_junction((1.0, 2.0))
        assert isinstance(j, Junction)
        assert j.position == (1.0, 2.0)
        assert sg.junction_count() == 1

    def test_add_junction_with_priority(self):
        sg = StructuralGraph()
        j = sg.add_junction((0, 0), snap_priority=5)
        assert j.snap_priority == 5

    def test_duplicate_position_rejected(self):
        sg = StructuralGraph()
        sg.add_junction((1, 2))
        with pytest.raises(ValidationError, match=E_JUNCTION_DUPLICATE):
            sg.add_junction((1, 2))

    def test_get_junction(self):
        sg = StructuralGraph()
        j = sg.add_junction((3, 4))
        assert sg.get_junction(j.id) is j

    def test_get_nonexistent(self):
        sg = StructuralGraph()
        assert sg.get_junction("nonexistent") is None

    def test_get_all_junctions(self):
        sg = StructuralGraph()
        sg.add_junction((0, 0))
        sg.add_junction((1, 0))
        assert len(sg.get_all_junctions()) == 2

    def test_remove_junction(self):
        sg = StructuralGraph()
        j = sg.add_junction((0, 0))
        sg.remove_junction(j.id)
        assert sg.junction_count() == 0
        assert sg.get_junction(j.id) is None

    def test_remove_junction_cascades_walls(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        sg.remove_junction(j1.id)
        assert sg.wall_count() == 0
        assert sg.get_wall(w.id) is None

    def test_find_junctions_near(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        sg.add_junction((10, 10))
        results = sg.find_junctions_near((0.1, 0.1), radius=1.0)
        assert len(results) == 1
        assert results[0][0].id == j1.id

    def test_find_junctions_near_empty(self):
        sg = StructuralGraph()
        sg.add_junction((10, 10))
        assert sg.find_junctions_near((0, 0), radius=1.0) == []

    def test_move_junction(self):
        sg = StructuralGraph()
        j = sg.add_junction((0, 0))
        sg.move_junction(j.id, (5, 5))
        assert sg.get_junction(j.id).position == (5, 5)

    def test_move_junction_to_occupied_position(self):
        sg = StructuralGraph()
        sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 1))
        with pytest.raises(ValidationError, match=E_JUNCTION_DUPLICATE):
            sg.move_junction(j2.id, (0, 0))

    def test_move_junction_to_own_position(self):
        sg = StructuralGraph()
        j = sg.add_junction((3, 3))
        sg.move_junction(j.id, (3, 3))  # Should not raise.
        assert j.position == (3, 3)

    def test_remove_frees_position(self):
        sg = StructuralGraph()
        j = sg.add_junction((0, 0))
        sg.remove_junction(j.id)
        # Should be able to add at the same position now.
        j2 = sg.add_junction((0, 0))
        assert j2.position == (0, 0)


# Wall CRUD
class TestWallCRUD:
    def test_add_wall(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert isinstance(w, Wall)
        assert sg.wall_count() == 1

    def test_add_wall_default_params(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert w.thickness == 0.2
        assert w.height == 3.0

    def test_add_wall_custom_params(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id, thickness=0.3, height=4.0, is_external=True)
        assert w.thickness == 0.3
        assert w.height == 4.0
        assert w.is_external is True

    def test_self_loop_rejected(self):
        sg = StructuralGraph()
        j = sg.add_junction((0, 0))
        with pytest.raises(ValidationError, match=E_WALL_SELF_LOOP):
            sg.add_wall(j.id, j.id)

    def test_duplicate_wall_rejected(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        sg.add_wall(j1.id, j2.id)
        with pytest.raises(ValidationError, match=E_WALL_DUPLICATE):
            sg.add_wall(j1.id, j2.id)

    def test_duplicate_wall_reversed_rejected(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        sg.add_wall(j1.id, j2.id)
        with pytest.raises(ValidationError, match=E_WALL_DUPLICATE):
            sg.add_wall(j2.id, j1.id)

    def test_invalid_thickness(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        with pytest.raises(ValidationError):
            sg.add_wall(j1.id, j2.id, thickness=0.01)

    def test_invalid_height(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        with pytest.raises(ValidationError):
            sg.add_wall(j1.id, j2.id, height=0.5)

    def test_nonexistent_junction(self):
        sg = StructuralGraph()
        sg.add_junction((0, 0))
        with pytest.raises(ValueError):
            sg.add_wall("fake", "also_fake")

    def test_remove_wall(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        sg.remove_wall(w.id)
        assert sg.wall_count() == 0
        # Junctions remain.
        assert sg.junction_count() == 2

    def test_get_wall(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.get_wall(w.id) is w

    def test_get_all_walls(self):
        sg, _, walls = make_square_graph()
        assert len(sg.get_all_walls()) == 4

    def test_get_walls_for_junction(self):
        sg, juncs, _ = make_square_graph()
        # Corner junction should have 2 walls.
        walls = sg.get_walls_for_junction(juncs[0].id)
        assert len(walls) == 2

    def test_get_wall_between(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.get_wall_between(j1.id, j2.id) is w
        assert sg.get_wall_between(j2.id, j1.id) is w

    def test_get_wall_between_none(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        assert sg.get_wall_between(j1.id, j2.id) is None

    def test_update_wall(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        sg.update_wall(w.id, thickness=0.5, height=5.0, material_id=3)
        assert w.thickness == 0.5
        assert w.height == 5.0
        assert w.material_id == 3

    def test_update_wall_invalid_thickness(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        with pytest.raises(ValidationError):
            sg.update_wall(w.id, thickness=0.0)


# Geometry queries
class TestGeometry:
    def test_wall_length(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((3, 4))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.wall_length(w.id) == pytest.approx(5.0)

    def test_wall_angle_horizontal(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.wall_angle(w.id) == pytest.approx(0.0)

    def test_wall_angle_vertical(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((0, 1))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.wall_angle(w.id) == pytest.approx(math.pi / 2)

    def test_wall_length_after_move(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        w = sg.add_wall(j1.id, j2.id)
        sg.move_junction(j2.id, (4, 3))
        assert sg.wall_length(w.id) == pytest.approx(5.0)


# Topology (cycle detection)
class TestCycleDetection:
    def test_single_square(self):
        sg, _, _ = make_square_graph()
        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 1
        assert len(cycles[0]) == 4

    def test_no_cycles(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        sg.add_wall(j1.id, j2.id)
        assert sg.detect_minimal_cycles() == []

    def test_two_rooms_shared_wall(self):
        # Two adjacent rectangles sharing a wall.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        j3 = sg.add_junction((2, 0))
        j4 = sg.add_junction((2, 1))
        j5 = sg.add_junction((1, 1))
        j6 = sg.add_junction((0, 1))

        sg.add_wall(j1.id, j2.id)
        sg.add_wall(j2.id, j3.id)
        sg.add_wall(j3.id, j4.id)
        sg.add_wall(j4.id, j5.id)
        sg.add_wall(j5.id, j6.id)
        sg.add_wall(j6.id, j1.id)
        sg.add_wall(j2.id, j5.id)  # shared wall

        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 2

    def test_triangle(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((1, 0))
        j3 = sg.add_junction((0.5, 1))
        sg.add_wall(j1.id, j2.id)
        sg.add_wall(j2.id, j3.id)
        sg.add_wall(j3.id, j1.id)
        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 1
        assert len(cycles[0]) == 3

    def test_empty_graph(self):
        sg = StructuralGraph()
        assert sg.detect_minimal_cycles() == []

    def test_t_junction_two_cycles(self):
        # T-shape: adding one wall creates two cycles simultaneously.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((2, 0))
        j3 = sg.add_junction((2, 2))
        j4 = sg.add_junction((0, 2))
        j5 = sg.add_junction((1, 0))
        j6 = sg.add_junction((1, 2))

        # Outer rectangle.
        sg.add_wall(j1.id, j5.id)
        sg.add_wall(j5.id, j2.id)
        sg.add_wall(j2.id, j3.id)
        sg.add_wall(j3.id, j6.id)
        sg.add_wall(j6.id, j4.id)
        sg.add_wall(j4.id, j1.id)
        # Dividing wall.
        sg.add_wall(j5.id, j6.id)

        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 2

    def test_is_planar_simple(self):
        sg, _, _ = make_square_graph()
        assert sg.is_planar() is True

    def test_get_cycle_vertices(self):
        sg, juncs, _ = make_square_graph()
        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 1
        verts = sg.get_cycle_vertices(cycles[0])
        assert len(verts) == 4
        for v in verts:
            assert len(v) == 2  # (x, y) tuples
