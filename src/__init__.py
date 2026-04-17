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


def remove_graphs(obj):
    _graph_store.pop(obj.name, None)


def clear_graph_store():
    _graph_store.clear()


if _HAS_BPY:
    from bpy.props import FloatProperty, IntProperty, EnumProperty, PointerProperty

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
        grid_density: FloatProperty(
            name="Grid Density",
            description="Snap grid spacing (meters)",
            default=0.5,
            min=0.01,
            max=10.0,
            precision=2,
            unit='LENGTH',
        )
        dimension_text_size: IntProperty(
            name="Dimension Text Size",
            description="Font size for dimension overlay (pixels)",
            default=14,
            min=8,
            max=48,
        )

    from .operators import get_classes as get_operator_classes
    from .operators.pencil_tool import (
        FLOORPLAN_WT_pencil,
        register_pencil_keymap,
        unregister_pencil_keymap,
        _draw_pencil_status,
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
        bpy.types.STATUSBAR_HT_header.prepend(_draw_pencil_status)

    def unregister():
        bpy.types.STATUSBAR_HT_header.remove(_draw_pencil_status)
        unregister_pencil_keymap()
        bpy.utils.unregister_tool(FLOORPLAN_WT_pencil)

        del bpy.types.Scene.floorplan

        for cls in reversed(get_ui_classes()):
            bpy.utils.unregister_class(cls)
        for cls in reversed(get_operator_classes()):
            bpy.utils.unregister_class(cls)

        for cls in reversed(_addon_classes):
            bpy.utils.unregister_class(cls)

        clear_graph_store()
