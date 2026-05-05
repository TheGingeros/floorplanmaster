import sys
import types


# final_mesh_builder imports bpy/bmesh at module import time.
if "bpy" not in sys.modules:
    sys.modules["bpy"] = types.ModuleType("bpy")
if "bmesh" not in sys.modules:
    sys.modules["bmesh"] = types.ModuleType("bmesh")

from src.core.final_mesh_builder import _room_ceiling_height, _wall_interior_sides
from src.core.room_graph import RoomGraph
from src.core.structural_graph import StructuralGraph


def _build_two_room_layout():
    sg = StructuralGraph()
    j00 = sg.add_junction((0.0, 0.0))
    j20 = sg.add_junction((2.0, 0.0))
    j40 = sg.add_junction((4.0, 0.0))
    j42 = sg.add_junction((4.0, 2.0))
    j22 = sg.add_junction((2.0, 2.0))
    j02 = sg.add_junction((0.0, 2.0))

    sg.add_wall(j00.id, j20.id, height=3.0)
    sg.add_wall(j20.id, j40.id, height=2.8)
    sg.add_wall(j40.id, j42.id, height=2.8)
    sg.add_wall(j42.id, j22.id, height=3.2)
    sg.add_wall(j22.id, j02.id, height=3.2)
    sg.add_wall(j02.id, j00.id, height=3.0)
    shared = sg.add_wall(j20.id, j22.id, height=2.6)

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    return sg, rg, shared.id


def test_wall_interior_sides_marks_shared_wall_as_both_sides():
    sg, rg, shared_wall_id = _build_two_room_layout()
    junctions = {j.id: j for j in sg.get_all_junctions()}

    sides = _wall_interior_sides(sg, rg, junctions)

    assert shared_wall_id in sides
    assert sides[shared_wall_id] == {"L", "R"}


def test_wall_interior_sides_marks_boundary_walls_single_side():
    sg, rg, _ = _build_two_room_layout()
    junctions = {j.id: j for j in sg.get_all_junctions()}

    sides = _wall_interior_sides(sg, rg, junctions)

    one_sided_count = sum(1 for wall_sides in sides.values() if len(wall_sides) == 1)
    assert one_sided_count >= 4


def test_room_ceiling_height_uses_min_boundary_wall_height():
    sg = StructuralGraph()
    j1 = sg.add_junction((0.0, 0.0))
    j2 = sg.add_junction((4.0, 0.0))
    j3 = sg.add_junction((4.0, 3.0))
    j4 = sg.add_junction((0.0, 3.0))

    sg.add_wall(j1.id, j2.id, height=3.0)
    sg.add_wall(j2.id, j3.id, height=2.4)
    sg.add_wall(j3.id, j4.id, height=2.8)
    sg.add_wall(j4.id, j1.id, height=3.2)

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    room = rg.get_all_rooms()[0]
    junctions = {j.id: j for j in sg.get_all_junctions()}

    z = _room_ceiling_height(room, sg, junctions)

    assert z == 2.4
