"""
FloorPlanMaster — Layer 1 + Layer 2 demo
Run from workspace root:  python -m src.demo.demo
"""
import math

from ..core.structural_graph import StructuralGraph
from ..core.room_graph import RoomGraph
from ..core.validators import ValidationError
L = 42  # left-column width for call → result alignment

def _scene(title):
    print(f"\n── {title} {'─' * max(0, 64 - len(title) - 4)}")

def _log(call, result=""):
    if result:
        print(f"  {call:<{L}}  →  {result}")
    else:
        print(f"  {call}")

def _cont(text):
    # continuation line aligned under the result column
    print(f"  {' ' * L}     {text}")

def _p(pos):
    # format position without trailing .0 when integer
    x, y = pos
    xs = f"{x:g}"
    ys = f"{y:g}"
    return f"({xs}, {ys})"

# Scene 1 — single square room
def scene_single_room():
    _scene("Scene 1 — Single Square Room  [Layer 1 → Layer 2 pipeline]")
    sg = StructuralGraph()

    j1 = sg.add_junction((0.0, 0.0))
    _log(f"add_junction{_p(j1.position)}", f"Junction  id={j1.id[:8]}")
    j2 = sg.add_junction((5.0, 0.0))
    _log(f"add_junction{_p(j2.position)}", f"Junction  id={j2.id[:8]}")
    j3 = sg.add_junction((5.0, 4.0))
    _log(f"add_junction{_p(j3.position)}", f"Junction  id={j3.id[:8]}")
    j4 = sg.add_junction((0.0, 4.0))
    _log(f"add_junction{_p(j4.position)}", f"Junction  id={j4.id[:8]}")
    print()

    for ja, jb in [(j1, j2), (j2, j3), (j3, j4), (j4, j1)]:
        w = sg.add_wall(ja.id, jb.id)
        ang = math.degrees(sg.wall_angle(w.id))
        _log(
            f"add_wall({_p(ja.position)}, {_p(jb.position)})",
            f"Wall  id={w.id[:8]}  len={sg.wall_length(w.id):.2f} m  angle={ang:>6.1f}°",
        )
    print()

    cycles = sg.detect_minimal_cycles()
    _log("detect_minimal_cycles()", f"{len(cycles)} cycle found")
    _cont(" → ".join(_p(sg.get_junction(jid).position) for jid in cycles[0]))
    print()

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    r = rg.get_all_rooms()[0]
    cx, cy = r.centroid
    _log("sync_from_structural_graph()", f"1 room  id={r.id[:8]}")
    _cont(f"area={r.area:.2f} m²  perim={r.perimeter:.2f} m  centroid=({cx:.2f}, {cy:.2f})  h={r.height:.1f} m")
    print()

    rg.set_room_name(r.id, "Living Room")
    _log('set_room_name(room, "Living Room")', f"name={r.name!r}")

    return sg, rg

# Scene 2 — two adjacent rooms
def scene_two_rooms():
    _scene("Scene 2 — Two Adjacent Rooms  [adjacency detection]")
    sg = StructuralGraph()

    j1 = sg.add_junction((0.0, 0.0))
    j2 = sg.add_junction((4.0, 0.0))
    j3 = sg.add_junction((8.0, 0.0))
    j4 = sg.add_junction((8.0, 3.0))
    j5 = sg.add_junction((4.0, 3.0))
    j6 = sg.add_junction((0.0, 3.0))
    _log("add_junction × 6", "junctions at (0,0) (4,0) (8,0) (8,3) (4,3) (0,3)")

    for ja, jb in [(j1, j2), (j2, j3), (j3, j4), (j4, j5), (j5, j6), (j6, j1)]:
        sg.add_wall(ja.id, jb.id)
    _log("add_wall × 6", "outer perimeter")

    shared = sg.add_wall(j2.id, j5.id)
    _log(f"add_wall({_p(j2.position)}, {_p(j5.position)})", f"Wall  id={shared.id[:8]}  — shared (dividing) wall")
    print()

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    rooms = rg.get_all_rooms()
    _log("sync_from_structural_graph()", f"{len(rooms)} rooms detected")
    for i, r in enumerate(rooms):
        cx, cy = r.centroid
        _cont(f"room[{i}]  id={r.id[:8]}  area={r.area:.2f} m²  perim={r.perimeter:.2f} m  centroid=({cx:.2f}, {cy:.2f})")
    print()

    adjs = rg.get_adjacencies()
    a = adjs[0]
    _log("get_adjacencies()", f"{len(adjs)} adjacency")
    _cont(f"{a.room_a[:8]} ↔ {a.room_b[:8]}  via wall {a.shared_wall[:8]}")
    print()

    result = rg.are_adjacent(rooms[0].id, rooms[1].id)
    _log("are_adjacent(room[0], room[1])", str(result))
    _log("total_area()", f"{rg.total_area():.2f} m²")

    return sg, rg

# Scene 3 — incremental topology change
def scene_topology_change():
    _scene("Scene 3 — Incremental Topology Change  [wall removal → room merge]")
    sg = StructuralGraph()

    j1 = sg.add_junction((0.0, 0.0))
    j2 = sg.add_junction((3.0, 0.0))
    j3 = sg.add_junction((6.0, 0.0))
    j4 = sg.add_junction((6.0, 3.0))
    j5 = sg.add_junction((3.0, 3.0))
    j6 = sg.add_junction((0.0, 3.0))
    for ja, jb in [(j1, j2), (j2, j3), (j3, j4), (j4, j5), (j5, j6), (j6, j1)]:
        sg.add_wall(ja.id, jb.id)
    shared = sg.add_wall(j2.id, j5.id)
    _log("setup: 6 junctions, 7 walls", "two 3×3 rooms with shared wall")

    rg = RoomGraph(sg)
    rg.sync_from_structural_graph()
    _log("sync_from_structural_graph()", f"{len(rg.get_all_rooms())} rooms  total area={rg.total_area():.2f} m²")
    print()

    sg.remove_wall(shared.id)
    _log(f"remove_wall(id={shared.id[:8]})", "wall removed")

    rg.sync_from_structural_graph()
    r = rg.get_all_rooms()[0]
    cx, cy = r.centroid
    _log("sync_from_structural_graph()", f"{len(rg.get_all_rooms())} room  total area={rg.total_area():.2f} m²")
    _cont(f"id={r.id[:8]}  area={r.area:.2f} m²  perim={r.perimeter:.2f} m  centroid=({cx:.2f}, {cy:.2f})")

# Scene 4 — validation errors
def scene_validation_errors():
    _scene("Scene 4 — Validation Errors  [caught at CRUD boundaries]")
    sg = StructuralGraph()
    j1 = sg.add_junction((0.0, 0.0))
    j2 = sg.add_junction((3.0, 0.0))
    sg.add_wall(j1.id, j2.id)
    _log("setup: 2 junctions, 1 wall", "base graph ready")
    print()

    cases = [
        ("add_junction(0, 0)  [duplicate position]",
         lambda: sg.add_junction((0.0, 0.0))),
        ("add_wall(j1, j2)  [duplicate edge]",
         lambda: sg.add_wall(j1.id, j2.id)),
        ("add_wall(j1, j1)  [self-loop]",
         lambda: sg.add_wall(j1.id, j1.id)),
        ("add_wall(..., thickness=0.01)  [below min 0.05 m]",
         lambda: sg.add_wall(
             sg.add_junction((10.0, 0.0)).id,
             sg.add_junction((11.0, 0.0)).id,
             thickness=0.01)),
        ("add_wall(..., thickness=1.50)  [above max 1.0 m]",
         lambda: sg.add_wall(
             sg.add_junction((20.0, 0.0)).id,
             sg.add_junction((21.0, 0.0)).id,
             thickness=1.5)),
        ("add_wall(..., height=0.5)  [below min 1.0 m]",
         lambda: sg.add_wall(
             sg.add_junction((30.0, 0.0)).id,
             sg.add_junction((31.0, 0.0)).id,
             height=0.5)),
    ]

    for call_desc, operation in cases:
        try:
            operation()
            _log(call_desc, "ERROR — no exception raised")
        except ValidationError as e:
            _log(call_desc, f"ValidationError  {e.code}")
        except ValueError as e:
            _log(call_desc, f"ValueError  {e}")


# Entry point
def main():
    print("\nFloorPlanMaster — Core Layer Demo")
    print("Pure Python, no Blender required.")
    print("Layer 1: StructuralGraph  |  Layer 2: RoomGraph")

    scene_single_room()
    scene_two_rooms()
    scene_topology_change()
    scene_validation_errors()

    print("\n── done " + "─" * 57 + "\n")

if __name__ == "__main__":
    main()
