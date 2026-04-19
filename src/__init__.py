bl_info = {
    "name": "FloorPlanMaster",
    "author": "wladaosk",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > FloorPlanMaster",
    "description": "Interactive floor plan creation with parametric walls and automatic room detection",
    "category": "3D View",
}

# Ensure bundled wheels are importable.
# .whl files are zip archives — Python can import from them directly via sys.path.
# This is a fallback for development (VS Code Blender extension) where Blender
# does not run the Extensions install pipeline that would handle blender_manifest.toml.
import sys
import os

_wheels_dir = os.path.join(os.path.dirname(__file__), "wheels")
if os.path.isdir(_wheels_dir):
    for _whl in os.listdir(_wheels_dir):
        if _whl.endswith(".whl"):
            _whl_path = os.path.join(_wheels_dir, _whl)
            if _whl_path not in sys.path:
                sys.path.insert(0, _whl_path)

# Guard bpy imports so pytest can load core/ and utils/ without Blender.
try:
    import bpy
    _HAS_BPY = True
except ImportError:
    _HAS_BPY = False

from .core.structural_graph import StructuralGraph
from .core.room_graph import RoomGraph


# Per-object graph storage: obj.name -> (StructuralGraph, RoomGraph, IdMapper)
_graph_store = {}

# Handle for the persistent wall-selection highlight draw handler (POST_VIEW).
_selection_draw_handle = None


def get_graphs(obj):
    # Return (StructuralGraph, RoomGraph) for a FloorPlanMaster object.
    # Creates new graphs and a persistent IdMapper if not yet tracked.
    from .core.sync import IdMapper
    key = obj.name
    if key not in _graph_store:
        sg = StructuralGraph()
        rg = RoomGraph(sg)
        _graph_store[key] = (sg, rg, IdMapper())
    sg, rg, _ = _graph_store[key]
    return sg, rg


def get_id_mapper(obj):
    # Return the persistent IdMapper for a FloorPlanMaster object.
    # Ensures the same UUID->int assignments survive across sync calls.
    from .core.sync import IdMapper
    key = obj.name
    if key not in _graph_store:
        sg = StructuralGraph()
        rg = RoomGraph(sg)
        _graph_store[key] = (sg, rg, IdMapper())
    return _graph_store[key][2]


def reset_graphs_for_obj(obj):
    # Rebuild Python graphs from the current mesh state and store them.
    # Must be called at the start of any operator with REGISTER|UNDO before
    # mutating graphs, so that Blender's undo-restored mesh is the source of
    # truth and re-execution after undo does not create duplicates.
    from .core.sync import reconstruct_graphs_from_mesh
    sg, rg, mapper = reconstruct_graphs_from_mesh(obj)
    if rg is None:
        rg = RoomGraph(sg)
    _graph_store[obj.name] = (sg, rg, mapper)
    return sg, rg, mapper


def remove_graphs(obj):
    _graph_store.pop(obj.name, None)


def clear_graph_store():
    _graph_store.clear()


def find_floorplan_obj(context):
    # Find the existing FloorPlanMaster object in the scene.
    # Returns None if no floorplan object exists (does NOT create one).
    for obj in context.scene.objects:
        if obj.get("is_floorplan"):
            return obj
    return None


if _HAS_BPY:
    import gpu
    import math
    from gpu_extras.batch import batch_for_shader
    from mathutils import Vector
    from bpy.props import FloatProperty, StringProperty, PointerProperty
    from .core.sync import sync_graph_to_mesh, _compute_wall_quad

    # Update callback guard — prevents recursive sync when the select operator
    # populates the props (which triggers the update callback).
    _updating_wall_props = False

    def _on_wall_thickness_update(self, context):
        global _updating_wall_props
        if _updating_wall_props:
            return
        wall_uuid = self.active_wall_id
        if not wall_uuid:
            return
        obj = find_floorplan_obj(context)
        if obj is None:
            return
        if obj.name not in _graph_store:
            reset_graphs_for_obj(obj)
        sg, rg, mapper = _graph_store[obj.name]
        wall = sg.get_wall(wall_uuid)
        if wall is None:
            return
        new_val = self.active_wall_thickness
        if abs(wall.thickness - new_val) < 1e-7:
            return
        try:
            sg.update_wall(wall_uuid, thickness=new_val)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)

    def _on_wall_height_update(self, context):
        global _updating_wall_props
        if _updating_wall_props:
            return
        wall_uuid = self.active_wall_id
        if not wall_uuid:
            return
        obj = find_floorplan_obj(context)
        if obj is None:
            return
        if obj.name not in _graph_store:
            reset_graphs_for_obj(obj)
        sg, rg, mapper = _graph_store[obj.name]
        wall = sg.get_wall(wall_uuid)
        if wall is None:
            return
        new_val = self.active_wall_height
        if abs(wall.height - new_val) < 1e-7:
            return
        try:
            sg.update_wall(wall_uuid, height=new_val)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)

    # Scene-level addon settings (PropertyGroup on Scene)
    class FloorPlanSettings(bpy.types.PropertyGroup):
        default_thickness: FloatProperty(
            name="Default Wall Thickness",
            description="Default wall thickness for new walls (meters)",
            default=0.3,
            min=0.05,
            max=1.0,
            precision=3,
            unit='LENGTH',
        )
        default_height: FloatProperty(
            name="Default Wall Height",
            description="Default wall height for new walls (meters)",
            default=2.5,
            min=1.0,
            max=10.0,
            precision=2,
            unit='LENGTH',
        )

        # Active wall selection — populated by FLOORPLAN_OT_select_wall.
        active_wall_id: StringProperty(
            name="Active Wall ID",
            description="UUID of the currently selected wall (empty = none)",
            default="",
        )
        active_wall_thickness: FloatProperty(
            name="Wall Thickness",
            description="Thickness of the selected wall (meters)",
            default=0.3,
            min=0.05,
            max=1.0,
            precision=3,
            unit='LENGTH',
            update=_on_wall_thickness_update,
        )
        active_wall_height: FloatProperty(
            name="Wall Height",
            description="Height of the selected wall (meters)",
            default=2.5,
            min=1.0,
            max=10.0,
            precision=2,
            unit='LENGTH',
            update=_on_wall_height_update,
        )

    def _draw_wall_selection():
        # Persistent POST_VIEW draw handler — draws a semi-transparent orange
        # box over the currently selected wall using UNIFORM_COLOR + TRIS.
        # Registered at addon load; reads active_wall_id from FloorPlanSettings.
        context = bpy.context
        if not context or not getattr(context, 'scene', None):
            return
        settings = getattr(context.scene, 'floorplan', None)
        if not settings or not settings.active_wall_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, _rg, _ = _graph_store[obj.name]
        wall = sg.get_wall(settings.active_wall_id)
        if wall is None:
            return
        junctions_by_id = {j.id: j for j in sg.get_all_junctions()}
        quad = _compute_wall_quad(wall, junctions_by_id, sg)
        if quad is None:
            return
        h = wall.height
        EXPAND = 0.03  # metres — push vertices out to avoid z-fighting
        cx = sum(p[0] for p in quad) / 4.0
        cy = sum(p[1] for p in quad) / 4.0
        b = []
        for p in quad:
            dx, dy = p[0] - cx, p[1] - cy
            norm = math.hypot(dx, dy)
            if norm > 1e-9:
                dx, dy = dx / norm * EXPAND, dy / norm * EXPAND
            else:
                dx, dy = 0.0, 0.0
            b.append(Vector((p[0] + dx, p[1] + dy, -EXPAND)))
        t = [Vector((v.x, v.y, h + EXPAND)) for v in b]
        # 6 faces x 2 triangles = 12 tris; both sides rendered (no culling).
        tris = []
        # Bottom
        tris += [b[0], b[1], b[2],  b[0], b[2], b[3]]
        # Top
        tris += [t[0], t[2], t[1],  t[0], t[3], t[2]]
        # Sides
        for i in range(4):
            n = (i + 1) % 4
            tris += [b[i], b[n], t[n],  b[i], t[n], t[i]]
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.face_culling_set('NONE')
        batch = batch_for_shader(shader, 'TRIS', {"pos": tris})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.55, 0.1, 0.25))
        batch.draw(shader)
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('NONE')

    from .operators import get_classes as get_operator_classes
    from .operators.pencil_tool import (
        FLOORPLAN_WT_pencil,
        register_pencil_keymap,
        unregister_pencil_keymap,
        _draw_pencil_status,
    )
    from .operators.select_wall import (
        register_select_keymap,
        unregister_select_keymap,
    )
    from .ui import get_classes as get_ui_classes

    _addon_classes = [
        FloorPlanSettings,
    ]

    def register():
        for cls in _addon_classes:
            bpy.utils.register_class(cls)

        for cls in get_operator_classes():
            bpy.utils.register_class(cls)
        for cls in get_ui_classes():
            bpy.utils.register_class(cls)

        bpy.types.Scene.floorplan = PointerProperty(type=FloorPlanSettings)

        bpy.utils.register_tool(FLOORPLAN_WT_pencil)
        register_pencil_keymap()
        register_select_keymap()
        bpy.types.STATUSBAR_HT_header.prepend(_draw_pencil_status)

        global _selection_draw_handle
        _selection_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_wall_selection, (), 'WINDOW', 'POST_VIEW'
        )

    def unregister():
        global _selection_draw_handle
        if _selection_draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_selection_draw_handle, 'WINDOW')
            _selection_draw_handle = None

        bpy.types.STATUSBAR_HT_header.remove(_draw_pencil_status)
        unregister_pencil_keymap()
        unregister_select_keymap()
        bpy.utils.unregister_tool(FLOORPLAN_WT_pencil)

        del bpy.types.Scene.floorplan

        for cls in reversed(get_ui_classes()):
            bpy.utils.unregister_class(cls)
        for cls in reversed(get_operator_classes()):
            bpy.utils.unregister_class(cls)

        for cls in reversed(_addon_classes):
            bpy.utils.unregister_class(cls)

        clear_graph_store()
