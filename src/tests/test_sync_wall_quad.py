import math
import sys
import types

import pytest

from src.core.structural_graph import StructuralGraph


# sync.py imports bpy/bmesh at module import time, but these geometry helpers are
# pure math. Provide tiny stubs so this test file runs in normal pytest.
if "bpy" not in sys.modules:
	sys.modules["bpy"] = types.ModuleType("bpy")
if "bmesh" not in sys.modules:
	sys.modules["bmesh"] = types.ModuleType("bmesh")

from src.core.sync import _compute_wall_quad, _junction_polygon_corners


def _junction_map(sg):
	return {j.id: j for j in sg.get_all_junctions()}


def _pt_close(a, b, eps=1e-6):
	return abs(a[0] - b[0]) <= eps and abs(a[1] - b[1]) <= eps


class TestWallQuadFreeze:
	def test_l_joint_start_corner_is_angular_adjacent_intersection(self):
		sg = StructuralGraph()
		jc = sg.add_junction((0.0, 0.0))
		je = sg.add_junction((2.0, 0.0))
		jn = sg.add_junction((0.0, 2.0))

		east = sg.add_wall(jc.id, je.id, thickness=0.2)
		sg.add_wall(jc.id, jn.id, thickness=0.2)

		quad = _compute_wall_quad(east, _junction_map(sg), sg)
		assert quad is not None
		p0, _p1, _p2, p3 = quad

		# For the start junction of east wall:
		# left corner should be (+0.1, +0.1), right corner (-0.1, -0.1).
		assert _pt_close(p0, (0.1, 0.1))
		assert _pt_close(p3, (-0.1, -0.1))

	def test_straight_degree2_endpoint_avoids_miter(self):
		sg = StructuralGraph()
		jc = sg.add_junction((0.0, 0.0))
		je = sg.add_junction((2.0, 0.0))
		jw = sg.add_junction((-2.0, 0.0))

		east = sg.add_wall(jc.id, je.id, thickness=0.2)
		sg.add_wall(jc.id, jw.id, thickness=0.2)

		quad = _compute_wall_quad(east, _junction_map(sg), sg)
		assert quad is not None
		p0, _p1, _p2, p3 = quad

		# Straight-through (anti-parallel) should keep perpendicular cap at start.
		assert _pt_close(p0, (0.0, 0.1))
		assert _pt_close(p3, (0.0, -0.1))


class TestJunctionFillFreeze:
	def test_x_junction_polygon_has_four_corners(self):
		sg = StructuralGraph()
		jc = sg.add_junction((0.0, 0.0))
		je = sg.add_junction((2.0, 0.0))
		jn = sg.add_junction((0.0, 2.0))
		jw = sg.add_junction((-2.0, 0.0))
		js = sg.add_junction((0.0, -2.0))

		sg.add_wall(jc.id, je.id, thickness=0.2)
		sg.add_wall(jc.id, jn.id, thickness=0.2)
		sg.add_wall(jc.id, jw.id, thickness=0.2)
		sg.add_wall(jc.id, js.id, thickness=0.2)

		corners = _junction_polygon_corners(jc, _junction_map(sg), sg)
		assert len(corners) == 4

		# Axis-aligned symmetric X gives a 0.2 x 0.2 square around origin.
		xs = sorted(round(c[0], 6) for c in corners)
		ys = sorted(round(c[1], 6) for c in corners)
		assert xs == [-0.1, -0.1, 0.1, 0.1]
		assert ys == [-0.1, -0.1, 0.1, 0.1]

	def test_junction_polygon_is_deterministic_for_same_geometry(self):
		def build(order):
			sg = StructuralGraph()
			jc = sg.add_junction((0.0, 0.0))
			nodes = {
				"E": sg.add_junction((2.0, 0.0)),
				"N": sg.add_junction((0.0, 2.0)),
				"W": sg.add_junction((-2.0, 0.0)),
				"S": sg.add_junction((0.0, -2.0)),
			}
			for key in order:
				sg.add_wall(jc.id, nodes[key].id, thickness=0.2)
			return _junction_polygon_corners(jc, _junction_map(sg), sg)

		c1 = build(["E", "N", "W", "S"])
		c2 = build(["S", "W", "N", "E"])

		assert len(c1) == len(c2) == 4
		assert [tuple(round(v, 6) for v in p) for p in c1] == [
			tuple(round(v, 6) for v in p) for p in c2
		]
