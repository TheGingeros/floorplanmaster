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
    # Reconstructs from persisted JSON if not yet in the cache.
    if obj.name not in _graph_store:
        reset_graphs_for_obj(obj)
    sg, rg, _ = _graph_store[obj.name]
    return sg, rg


def get_id_mapper(obj):
    # Return the persistent IdMapper for a FloorPlanMaster object.
    # Ensures the same UUID->int assignments survive across sync calls.
    if obj.name not in _graph_store:
        reset_graphs_for_obj(obj)
    return _graph_store[obj.name][2]


def reset_graphs_for_obj(obj):
    # Rebuild Python graphs from the current mesh state and store them.
    # Must be called at the start of any operator with REGISTER|UNDO before
    # mutating graphs, so that Blender's undo-restored mesh is the source of
    # truth and re-execution after undo does not create duplicates.
    #
    # Room detection runs immediately after reconstruction so the graph is
    # fully consistent without needing a subsequent sync_graph_to_mesh() call
    # (e.g. after addon reload or file load).
    from .core.sync import reconstruct_graphs_from_mesh
    sg, rg, mapper = reconstruct_graphs_from_mesh(obj)
    if rg is None:
        rg = RoomGraph(sg)
    if sg.get_all_walls():
        rg.sync_from_structural_graph()
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
    from bpy.props import PointerProperty
    from .ui.properties import OpeningItem, FloorPlanSettings, populate_opening_items

    from .ui.overlays.wall_selection import draw_wall_selection
    from .ui.overlays.room_selection import draw_room_selection

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
    from .ui import overlay_manager

    def _rebuild_graph_store():
        # Repopulate _graph_store from any floorplan objects already in the scene.
        # Called on addon register() (covers in-session F8 reload) and from
        # _load_post_handler (covers file load).  After reconstruction the room
        # graph is explicitly synced so the N-panel can show rooms immediately.
        try:
            scenes = bpy.data.scenes
        except Exception:
            return
        seen = set()
        for scene in scenes:
            for obj in scene.objects:
                if obj.get("is_floorplan") and obj.name not in seen:
                    seen.add(obj.name)
                    reset_graphs_for_obj(obj)

    @bpy.app.handlers.persistent
    def _load_post_handler(dummy):
        _rebuild_graph_store()

    _addon_classes = [
        OpeningItem,
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

        overlay_manager.register()
        overlay_manager.register_layer(draw_wall_selection, '3D')
        overlay_manager.register_layer(draw_room_selection, '3D')

        bpy.app.handlers.load_post.append(_load_post_handler)
        _rebuild_graph_store()

    def unregister():
        if _load_post_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_load_post_handler)

        overlay_manager.unregister()

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
