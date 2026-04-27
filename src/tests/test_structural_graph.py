import math
import pytest

from src.core.structural_graph import StructuralGraph, Junction, Wall, Opening
from src.core.validators import (
    ValidationError,
    E_JUNCTION_DUPLICATE,
    E_WALL_DUPLICATE,
    E_WALL_SELF_LOOP,
    E_OPENING_TOO_LARGE,
    E_OPENING_OVERLAP,
    E_OPENING_EXCEEDS_WALL,
    E_OPENING_WIDTH_OUT_OF_RANGE,
    E_OPENING_HEIGHT_OUT_OF_RANGE,
)


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
        w = sg.add_wall(j1.id, j2.id, thickness=0.3, height=4.0)
        assert w.thickness == 0.3
        assert w.height == 4.0

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
        sg.update_wall(w.id, thickness=0.5, height=5.0)
        assert w.thickness == 0.5
        assert w.height == 5.0

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

    def test_dangling_wall_from_room_junction_preserves_room(self):
        # Core regression: drawing an open wall from a junction of an existing
        # room must NOT destroy that room's cycle.  Before the leaf-prune fix,
        # NetworkX could route the dangling node inside the existing face,
        # causing traverse_face() to return a degenerate cycle with a repeated
        # junction — which then replaced the valid room in the room graph.
        sg, juncs, _ = make_square_graph()
        j_dangling = sg.add_junction((0.5, 2.0))
        # Attach dangling wall to the top-left junction of the square.
        sg.add_wall(juncs[3].id, j_dangling.id)
        cycles = sg.detect_minimal_cycles()
        # Exactly one room — the original square; the dangling wall forms no cycle.
        assert len(cycles) == 1
        assert len(cycles[0]) == 4
        # No junction should appear twice in the returned cycle.
        assert len(set(cycles[0])) == len(cycles[0])

    def test_dangling_wall_no_cycles_yet(self):
        # A single open wall should return no cycles even with a junction snapped
        # to a previously-isolated point.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((3, 0))
        sg.add_wall(j1.id, j2.id)
        assert sg.detect_minimal_cycles() == []

    def test_multiple_dangling_walls_from_room_junction(self):
        # Two dangling walls from two different junctions of the same room must
        # not corrupt cycle detection.
        sg, juncs, _ = make_square_graph()
        jd1 = sg.add_junction((2.0, 0.5))
        jd2 = sg.add_junction((-1.0, 0.5))
        sg.add_wall(juncs[1].id, jd1.id)
        sg.add_wall(juncs[0].id, jd2.id)
        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 1
        assert len(set(cycles[0])) == len(cycles[0])

    def test_room_cycles_correct_after_closing_dangling_wall(self):
        # After closing the dangling wall into a second room, both rooms must be
        # detected and each cycle must contain only distinct junction IDs.
        sg, juncs, _ = make_square_graph()
        # Add three walls to form a second room sharing j3–j0 (top edge).
        jd1 = sg.add_junction((0.0, 2.0))
        jd2 = sg.add_junction((1.0, 2.0))
        # juncs order from make_square_graph: (0,0) (1,0) (1,1) (0,1)
        top_left = juncs[3]   # (0, 1)
        top_right = juncs[2]  # (1, 1)
        sg.add_wall(top_left.id, jd1.id)
        sg.add_wall(jd1.id, jd2.id)
        sg.add_wall(jd2.id, top_right.id)
        cycles = sg.detect_minimal_cycles()
        assert len(cycles) == 2
        for c in cycles:
            assert len(set(c)) == len(c), f"Cycle has repeated junction: {c}"


# Opening CRUD
class TestOpeningCRUD:
    def _wall_2m(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((2, 0))
        w = sg.add_wall(j1.id, j2.id, height=3.0)
        return sg, w

    def test_add_door(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id, opening_type='DOOR', width=0.9, height=2.1, sill_height=0.0)
        assert isinstance(op, Opening)
        assert op.opening_type == 'DOOR'
        assert op.width == 0.9
        assert op.height == 2.1
        assert op.sill_height == 0.0
        assert op.position == 0.5

    def test_add_window(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id, opening_type='WINDOW', width=1.2, height=1.2, sill_height=0.9)
        assert op.opening_type == 'WINDOW'
        assert op.sill_height == 0.9

    def test_opening_stored_on_wall(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id)
        assert len(w.openings) == 1

    def test_get_opening(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id)
        assert sg.get_opening(op.id) is op

    def test_get_opening_nonexistent(self):
        sg, w = self._wall_2m()
        assert sg.get_opening("fake") is None

    def test_get_openings_for_wall(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, position=0.3, width=0.5)
        sg.add_opening(w.id, position=0.8, width=0.5)
        openings = sg.get_openings_for_wall(w.id)
        assert len(openings) == 2

    def test_remove_opening(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id)
        assert sg.remove_opening(op.id) is True
        assert len(w.openings) == 0
        assert sg.get_opening(op.id) is None

    def test_remove_opening_nonexistent(self):
        sg, w = self._wall_2m()
        assert sg.remove_opening("fake") is False

    def test_update_opening(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id, width=0.9, height=2.1)
        sg.update_opening(op.id, width=1.0, height=2.5)
        assert op.width == 1.0
        assert op.height == 2.5

    def test_update_opening_type(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id, opening_type='DOOR')
        sg.update_opening(op.id, opening_type='WINDOW', sill_height=0.9, height=1.2)
        assert op.opening_type == 'WINDOW'
        assert op.sill_height == 0.9

    def test_wall_removal_cascades_openings(self):
        sg, w = self._wall_2m()
        op = sg.add_opening(w.id)
        sg.remove_wall(w.id)
        assert sg.get_opening(op.id) is None

    # Validation tests
    def test_opening_too_wide_for_wall(self):
        sg, w = self._wall_2m()  # wall length = 2m
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            sg.add_opening(w.id, width=2.5, position=0.5)

    def test_opening_extends_beyond_wall_start(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            sg.add_opening(w.id, width=0.9, position=0.1)

    def test_opening_extends_beyond_wall_end(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            sg.add_opening(w.id, width=0.9, position=0.9)

    def test_opening_overlap_rejected(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, width=0.8, position=0.3)
        with pytest.raises(ValidationError, match=E_OPENING_OVERLAP):
            sg.add_opening(w.id, width=0.8, position=0.5)

    def test_opening_no_overlap(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, width=0.5, position=0.2)
        op2 = sg.add_opening(w.id, width=0.5, position=0.8)
        assert op2 is not None

    def test_opening_touch_rejected(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, width=0.5, position=0.25)
        with pytest.raises(ValidationError, match=E_OPENING_OVERLAP):
            sg.add_opening(w.id, width=0.5, position=0.75)

    def test_opening_exceeds_wall_height(self):
        sg, w = self._wall_2m()  # wall height = 3.0
        with pytest.raises(ValidationError, match=E_OPENING_EXCEEDS_WALL):
            sg.add_opening(w.id, height=2.0, sill_height=2.0)

    def test_opening_width_too_small(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValidationError, match=E_OPENING_WIDTH_OUT_OF_RANGE):
            sg.add_opening(w.id, width=0.1)

    def test_opening_width_too_large(self):
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((10, 0))
        w = sg.add_wall(j1.id, j2.id)
        with pytest.raises(ValidationError, match=E_OPENING_WIDTH_OUT_OF_RANGE):
            sg.add_opening(w.id, width=6.0)

    def test_opening_height_too_small(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            sg.add_opening(w.id, height=0.1)

    def test_opening_height_exceeds_wall(self):
        sg, w = self._wall_2m()  # wall height = 3.0
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            sg.add_opening(w.id, height=4.0)

    def test_negative_sill_rejected(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            sg.add_opening(w.id, sill_height=-0.1)

    def test_nonexistent_wall_rejected(self):
        sg, w = self._wall_2m()
        with pytest.raises(ValueError):
            sg.add_opening("fake_wall_id")

    def test_update_opening_overlap_rejected(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, width=0.5, position=0.2)
        op2 = sg.add_opening(w.id, width=0.5, position=0.8)
        with pytest.raises(ValidationError, match=E_OPENING_OVERLAP):
            sg.update_opening(op2.id, position=0.3)

    def test_wall_full_detected_for_new_opening(self):
        sg, w = self._wall_2m()
        sg.add_opening(w.id, width=0.5, position=0.25)
        sg.add_opening(w.id, width=0.5, position=0.75)
        assert sg.max_opening_width(w.id) < 0.3
        assert sg.can_fit_opening(w.id, 0.3) is False

    def test_width_limit_at_position_respects_neighbors(self):
        sg, w = self._wall_2m()
        left = sg.add_opening(w.id, width=0.4, position=0.2)
        right = sg.add_opening(w.id, width=0.4, position=0.8)
        middle = sg.add_opening(w.id, width=0.2, position=0.5)
        assert sg.max_opening_width_at_position(w.id, middle.position, exclude_opening_id=middle.id) == pytest.approx(0.8, abs=1e-4)


# junction_inset() and inset-aware opening placement
class TestJunctionInset:
    def test_free_endpoint_returns_zero(self):
        # A wall with no connecting walls has inset 0 at both ends.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((4, 0))
        w = sg.add_wall(j1.id, j2.id)
        assert sg.junction_inset(j1.id, w.id) == pytest.approx(0.0)
        assert sg.junction_inset(j2.id, w.id) == pytest.approx(0.0)

    def test_t_junction_inset_equals_connecting_half_thickness(self):
        # Wall A (horizontal, 4m) has a perpendicular wall B (thickness=0.2)
        # connecting at j2. Inset at j2 for wall A = 0.2/2 = 0.1.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((4, 0))
        j3 = sg.add_junction((4, 2))
        wA = sg.add_wall(j1.id, j2.id, thickness=0.15)
        wB = sg.add_wall(j2.id, j3.id, thickness=0.2)
        assert sg.junction_inset(j1.id, wA.id) == pytest.approx(0.0)  # free end
        assert sg.junction_inset(j2.id, wA.id) == pytest.approx(0.1)  # wB.thickness/2

    def test_multiple_neighbors_takes_max(self):
        # Center junction connected to three walls. The inset for each wall
        # at the center junction is max(other two thicknesses) / 2.
        sg = StructuralGraph()
        jc = sg.add_junction((0, 0))
        j1 = sg.add_junction((-2, 0))
        j2 = sg.add_junction((2, 0))
        j3 = sg.add_junction((0, 2))
        w1 = sg.add_wall(jc.id, j1.id, thickness=0.1)
        w2 = sg.add_wall(jc.id, j2.id, thickness=0.2)
        w3 = sg.add_wall(jc.id, j3.id, thickness=0.3)
        # For w1 at jc: neighbors are w2 (t=0.2) and w3 (t=0.3) -> max half = 0.15
        assert sg.junction_inset(jc.id, w1.id) == pytest.approx(0.15)
        # For w3 at jc: neighbors are w1 (t=0.1) and w2 (t=0.2) -> max half = 0.1
        assert sg.junction_inset(jc.id, w3.id) == pytest.approx(0.1)

    def test_inset_enforced_on_add_opening(self):
        # Wall 4m long, connecting wall (t=0.4) at start junction -> inset_start=0.2
        # t_min = 0.2/4 = 0.05
        # Opening at position=0.08 with half_norm=0.05 -> t_start=0.03 < 0.05 -> raises
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((4, 0))
        j3 = sg.add_junction((0, 2))
        wA = sg.add_wall(j1.id, j2.id, height=3.0)
        sg.add_wall(j1.id, j3.id, thickness=0.4)
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            sg.add_opening(wA.id, width=0.4, position=0.08)

    def test_inset_allows_placement_in_usable_span(self):
        # Same geometry but placement well within usable span -> should succeed.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((4, 0))
        j3 = sg.add_junction((0, 2))
        wA = sg.add_wall(j1.id, j2.id, height=3.0)
        sg.add_wall(j1.id, j3.id, thickness=0.4)
        op = sg.add_opening(wA.id, width=0.9, position=0.5)
        assert op is not None

    def test_inset_on_update_opening_enforced(self):
        # Moving an opening from center into the inset zone should be rejected.
        sg = StructuralGraph()
        j1 = sg.add_junction((0, 0))
        j2 = sg.add_junction((4, 0))
        j3 = sg.add_junction((4, 2))
        wA = sg.add_wall(j1.id, j2.id, height=3.0)
        sg.add_wall(j2.id, j3.id, thickness=0.4)  # inset_end = 0.2 -> t_max = 1 - 0.05 = 0.95
        op = sg.add_opening(wA.id, width=0.9, position=0.5)
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            sg.update_opening(op.id, position=0.97)  # t_end = 0.97 + 0.1125 = 1.0825 > 0.95
