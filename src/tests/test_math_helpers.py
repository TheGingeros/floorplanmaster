import math
import pytest

from src.utils.math_helpers import (
    polygon_area,
    polygon_centroid,
    polygon_perimeter,
    point_distance,
    edge_length,
    edge_angle,
    angle_between_edges,
    aspect_ratio,
    point_in_polygon,
)


# polygon_area

class TestPolygonArea:
    def test_unit_square(self):
        verts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        assert polygon_area(verts) == pytest.approx(1.0)

    def test_triangle(self):
        verts = [(0, 0), (4, 0), (0, 3)]
        assert polygon_area(verts) == pytest.approx(6.0)

    def test_reversed_winding(self):
        # Area should be absolute regardless of winding order.
        verts = [(0, 0), (0, 1), (1, 1), (1, 0)]
        assert polygon_area(verts) == pytest.approx(1.0)

    def test_rectangle(self):
        verts = [(0, 0), (5, 0), (5, 3), (0, 3)]
        assert polygon_area(verts) == pytest.approx(15.0)

    def test_degenerate_line(self):
        verts = [(0, 0), (1, 0)]
        assert polygon_area(verts) == 0.0

    def test_empty(self):
        assert polygon_area([]) == 0.0

    def test_l_shape_polygon(self):
        # L-shape: 6 vertices. Bottom 3x1 + left column 1x1 = 4.0
        verts = [(0, 0), (3, 0), (3, 1), (1, 1), (1, 2), (0, 2)]
        assert polygon_area(verts) == pytest.approx(4.0)


# polygon_centroid

class TestPolygonCentroid:
    def test_unit_square(self):
        verts = [(0, 0), (2, 0), (2, 2), (0, 2)]
        cx, cy = polygon_centroid(verts)
        assert cx == pytest.approx(1.0)
        assert cy == pytest.approx(1.0)

    def test_triangle(self):
        verts = [(0, 0), (6, 0), (0, 6)]
        cx, cy = polygon_centroid(verts)
        assert cx == pytest.approx(2.0)
        assert cy == pytest.approx(2.0)

    def test_single_point(self):
        cx, cy = polygon_centroid([(3, 4)])
        assert cx == pytest.approx(3.0)
        assert cy == pytest.approx(4.0)

    def test_empty(self):
        assert polygon_centroid([]) == (0.0, 0.0)


# polygon_perimeter

class TestPolygonPerimeter:
    def test_unit_square(self):
        verts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        assert polygon_perimeter(verts) == pytest.approx(4.0)

    def test_triangle_345(self):
        verts = [(0, 0), (3, 0), (0, 4)]
        assert polygon_perimeter(verts) == pytest.approx(12.0)

    def test_single_point(self):
        assert polygon_perimeter([(0, 0)]) == 0.0


# point_distance / edge_length

class TestDistance:
    def test_horizontal(self):
        assert point_distance((0, 0), (3, 0)) == pytest.approx(3.0)

    def test_vertical(self):
        assert point_distance((0, 0), (0, 4)) == pytest.approx(4.0)

    def test_diagonal(self):
        assert point_distance((0, 0), (3, 4)) == pytest.approx(5.0)

    def test_same_point(self):
        assert point_distance((1, 2), (1, 2)) == pytest.approx(0.0)

    def test_edge_length_alias(self):
        assert edge_length((0, 0), (3, 4)) == point_distance((0, 0), (3, 4))


# edge_angle

class TestEdgeAngle:
    def test_horizontal_right(self):
        assert edge_angle((0, 0), (1, 0)) == pytest.approx(0.0)

    def test_vertical_up(self):
        assert edge_angle((0, 0), (0, 1)) == pytest.approx(math.pi / 2)

    def test_horizontal_left(self):
        assert edge_angle((0, 0), (-1, 0)) == pytest.approx(math.pi)

    def test_45_degrees(self):
        assert edge_angle((0, 0), (1, 1)) == pytest.approx(math.pi / 4)


# angle_between_edges

class TestAngleBetweenEdges:
    def test_right_angle(self):
        angle = angle_between_edges((0, 0), (1, 0), (0, 1))
        assert angle == pytest.approx(math.pi / 2)

    def test_straight_line(self):
        angle = angle_between_edges((0, 0), (-1, 0), (1, 0))
        assert angle == pytest.approx(math.pi)

    def test_full_reverse(self):
        # Same direction — expect 2π.
        angle = angle_between_edges((0, 0), (1, 0), (1, 0))
        assert angle == pytest.approx(2 * math.pi)


# aspect_ratio

class TestAspectRatio:
    def test_square(self):
        verts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        assert aspect_ratio(verts) == pytest.approx(1.0)

    def test_wide_rectangle(self):
        verts = [(0, 0), (4, 0), (4, 1), (0, 1)]
        assert aspect_ratio(verts) == pytest.approx(4.0)

    def test_tall_rectangle(self):
        verts = [(0, 0), (1, 0), (1, 4), (0, 4)]
        assert aspect_ratio(verts) == pytest.approx(0.25)

    def test_degenerate(self):
        assert aspect_ratio([(0, 0), (1, 0)]) == 1.0


# point_in_polygon

class TestPointInPolygon:
    def test_inside_square(self):
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        assert point_in_polygon((1, 1), square) is True

    def test_outside_square(self):
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        assert point_in_polygon((3, 1), square) is False

    def test_outside_above(self):
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        assert point_in_polygon((1, 3), square) is False

    def test_inside_triangle(self):
        tri = [(0, 0), (4, 0), (2, 3)]
        assert point_in_polygon((2, 1), tri) is True

    def test_outside_triangle(self):
        tri = [(0, 0), (4, 0), (2, 3)]
        assert point_in_polygon((0, 3), tri) is False

    def test_inside_thin_wall_quad(self):
        # Thin horizontal wall quad: 4m long, 0.3m thick, centered at Y=0.
        quad = [(-2, -0.15), (2, -0.15), (2, 0.15), (-2, 0.15)]
        assert point_in_polygon((0, 0), quad) is True
        assert point_in_polygon((1.5, 0.1), quad) is True

    def test_outside_thin_wall_quad(self):
        quad = [(-2, -0.15), (2, -0.15), (2, 0.15), (-2, 0.15)]
        assert point_in_polygon((0, 0.2), quad) is False
        assert point_in_polygon((2.5, 0), quad) is False

    def test_degenerate_line(self):
        assert point_in_polygon((0, 0), [(0, 0), (1, 0)]) is False

    def test_empty(self):
        assert point_in_polygon((0, 0), []) is False

    def test_concave_l_shape(self):
        # L-shape polygon.
        verts = [(0, 0), (3, 0), (3, 1), (1, 1), (1, 2), (0, 2)]
        assert point_in_polygon((0.5, 0.5), verts) is True  # bottom part
        assert point_in_polygon((0.5, 1.5), verts) is True  # left column
        assert point_in_polygon((2, 1.5), verts) is False   # outside the L
