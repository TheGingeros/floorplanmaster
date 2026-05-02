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

# Semantic interaction mode state.
# Empty string means the mode is disabled.
_mode_object_name = ""
# Cached VIEW_3D overlay outline state per space pointer while mode is active.
_mode_restore_outline_selected = {}


def _iter_view3d_spaces():
    if not _HAS_BPY:
        return
    wm = getattr(bpy.context, 'window_manager', None)
    if wm is None:
        return
    for window in wm.windows:
        screen = getattr(window, 'screen', None)
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    yield space


def _set_selected_outline_visible(visible):
    global _mode_restore_outline_selected
    if not _HAS_BPY:
        return
    if visible:
        if not _mode_restore_outline_selected:
            return
        restore = dict(_mode_restore_outline_selected)
        _mode_restore_outline_selected.clear()
        for space in _iter_view3d_spaces():
            key = space.as_pointer()
            if key not in restore:
                continue
            try:
                space.overlay.show_outline_selected = bool(restore[key])
            except Exception:
                pass
        return

    if _mode_restore_outline_selected:
        return
    for space in _iter_view3d_spaces():
        key = space.as_pointer()
        try:
            _mode_restore_outline_selected[key] = bool(space.overlay.show_outline_selected)
            space.overlay.show_outline_selected = False
        except Exception:
            pass


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
        from .core.sync import restore_room_names
        restore_room_names(obj, rg)
    _graph_store[obj.name] = (sg, rg, mapper)
    # Safely initialize room-name custom properties (N-panel editability).
    # Wrap in try-except to handle read-only draw context gracefully.
    try:
        for room in rg.get_all_rooms():
            key = f"room_name_{room.id}"
            if key not in obj:
                obj[key] = room.name
    except (AttributeError, RuntimeError):
        # Context is read-only (e.g., panel draw). Will be initialized in
        # depsgraph_update_handler or _rebuild_graph_store on next safe write.
        pass
    return sg, rg, mapper


def remove_graphs(obj):
    _graph_store.pop(obj.name, None)


def clear_graph_store():
    _graph_store.clear()


def is_floorplan_obj(obj):
    return obj is not None and bool(obj.get("is_floorplan"))


def has_floorplan_obj(context):
    if context is None or getattr(context, 'scene', None) is None:
        return False
    return any(is_floorplan_obj(obj) for obj in context.scene.objects)


def get_floorplan_obj_by_name(context, object_name):
    if context is None or getattr(context, 'scene', None) is None or not object_name:
        return None
    obj = context.scene.objects.get(object_name)
    if is_floorplan_obj(obj):
        return obj
    return None


def get_selected_floorplan_obj(context):
    # Return active FloorPlan object only when it is also explicitly selected.
    obj = getattr(context, 'active_object', None)
    if is_floorplan_obj(obj) and obj.select_get():
        return obj
    return None


def is_floorplan_obj_visible(context, obj):
    if not is_floorplan_obj(obj):
        return False
    try:
        return bool(obj.visible_get(view_layer=context.view_layer))
    except Exception:
        try:
            return not obj.hide_get()
        except Exception:
            return not getattr(obj, "hide_viewport", False)


def find_floorplan_obj(context):
    # Return FloorPlan object that currently owns semantic mode.
    # Mode ownership is independent from temporary Blender active selection.
    if not _mode_object_name:
        return None
    return get_floorplan_obj_by_name(context, _mode_object_name)


def is_floorplan_mode_active(context):
    # True when semantic mode is enabled and its owner object still exists.
    global _mode_object_name
    if not _mode_object_name:
        return False
    if get_floorplan_obj_by_name(context, _mode_object_name) is not None:
        return True
    # Mode owner vanished (delete/load/reload): restore viewport outline state.
    _set_selected_outline_visible(True)
    _mode_object_name = ""
    return False


def set_floorplan_mode_active(context, enabled):
    # Enable/disable semantic mode for the active+selected FloorPlan object.
    global _mode_object_name
    if not enabled:
        _set_selected_outline_visible(True)
        _mode_object_name = ""
        return False
    obj = get_selected_floorplan_obj(context)
    if obj is None:
        _set_selected_outline_visible(True)
        _mode_object_name = ""
        return False
    _mode_object_name = obj.name
    _set_selected_outline_visible(False)
    return True


def toggle_floorplan_mode(context):
    # Toggle semantic mode for the active+selected FloorPlan object.
    global _mode_object_name
    obj = get_selected_floorplan_obj(context)
    if obj is None:
        _set_selected_outline_visible(True)
        _mode_object_name = ""
        return False
    if _mode_object_name == obj.name:
        _set_selected_outline_visible(True)
        _mode_object_name = ""
        return False
    _mode_object_name = obj.name
    _set_selected_outline_visible(False)
    return True


if _HAS_BPY:
    from bpy.props import PointerProperty
    from .ui.properties import OpeningItem, FloorPlanSettings, populate_opening_items

    from .ui.overlays.wall_selection import draw_wall_selection
    from .ui.overlays.wall_opening_highlight import draw_wall_opening_highlight
    from .ui.overlays.room_selection import draw_room_selection
    from .ui.overlays.active_floorplan_hint import draw_active_floorplan_hint
    from .ui.overlays.labels import draw_labels

    from .operators import get_classes as get_operator_classes
    from .operators.pencil_tool import (
        FLOORPLAN_WT_pencil,
        register_pencil_keymap,
        unregister_pencil_keymap,
        _draw_pencil_status,
    )
    from .operators.floorplan_mode import (
        register_floorplan_mode_keymap,
        unregister_floorplan_mode_keymap,
    )
    from .operators.edit_mode_detach import (
        register_edit_mode_detach_keymap,
        unregister_edit_mode_detach_keymap,
    )
    from .operators.remove_wall import (
        register_remove_wall_keymap,
        unregister_remove_wall_keymap,
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
                    # Initialize room-name custom properties so N-panel rooms are editable.
                    # Done here (not in draw()) where we can safely write to object data.
                    if obj.name in _graph_store:
                        sg_local, rg_local, _ = _graph_store[obj.name]
                        for room in rg_local.get_all_rooms():
                            key = f"room_name_{room.id}"
                            if key not in obj:
                                obj[key] = room.name

    @bpy.app.handlers.persistent
    def _depsgraph_update_handler(scene, depsgraph):
        # Push room name edits from the rooms-list custom properties to the graph.
        # Also ensure room-name custom properties exist for newly detected rooms.
        for obj in scene.objects:
            if obj.get("_floorplan_graphs") is not None and obj.name in _graph_store:
                sg_local, rg_local, _ = _graph_store[obj.name]
                # Ensure all rooms have custom properties (for N-panel editability).
                for room in rg_local.get_all_rooms():
                    key = f"room_name_{room.id}"
                    if key not in obj:
                        obj[key] = room.name
                # Push inline edits to graph if they differ.
                changed = False
                for room in rg_local.get_all_rooms():
                    key = f"room_name_{room.id}"
                    if key in obj:
                        stored = str(obj[key])
                        if stored != room.name:
                            effective_name = rg_local.set_room_name(room.id, stored)
                            if effective_name != stored:
                                obj[key] = effective_name
                            if effective_name != room.name:
                                changed = True
                if changed:
                    from .core.sync import persist_room_names
                    persist_room_names(obj, rg_local)

    @bpy.app.handlers.persistent
    def _load_post_handler(dummy):
        _rebuild_graph_store()

    @bpy.app.handlers.persistent
    def _undo_post_handler(dummy):
        # Blender undo restores mesh/custom properties but not Python globals.
        # Rebuild in-memory graphs so RoomGraph matches the undo-restored mesh.
        _rebuild_graph_store()

    @bpy.app.handlers.persistent
    def _redo_post_handler(dummy):
        # Same reasoning as undo: Python cache must follow restored Blender data.
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
        register_floorplan_mode_keymap()
        register_edit_mode_detach_keymap()
        register_remove_wall_keymap()
        bpy.types.STATUSBAR_HT_header.prepend(_draw_pencil_status)

        overlay_manager.register()
        overlay_manager.register_layer(draw_active_floorplan_hint, '2D')
        overlay_manager.register_layer(draw_wall_opening_highlight, '3D')
        overlay_manager.register_layer(draw_labels, '2D')
        overlay_manager.register_layer(draw_wall_selection, '3D')
        overlay_manager.register_layer(draw_room_selection, '3D')

        bpy.app.handlers.load_post.append(_load_post_handler)
        bpy.app.handlers.undo_post.append(_undo_post_handler)
        bpy.app.handlers.redo_post.append(_redo_post_handler)
        bpy.app.handlers.depsgraph_update_post.append(_depsgraph_update_handler)
        _rebuild_graph_store()

    def unregister():
        global _mode_object_name
        if _load_post_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_load_post_handler)
        if _undo_post_handler in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.remove(_undo_post_handler)
        if _redo_post_handler in bpy.app.handlers.redo_post:
            bpy.app.handlers.redo_post.remove(_redo_post_handler)
        if _depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(_depsgraph_update_handler)

        overlay_manager.unregister()

        bpy.types.STATUSBAR_HT_header.remove(_draw_pencil_status)
        unregister_pencil_keymap()
        unregister_floorplan_mode_keymap()
        unregister_edit_mode_detach_keymap()
        unregister_remove_wall_keymap()
        bpy.utils.unregister_tool(FLOORPLAN_WT_pencil)

        del bpy.types.Scene.floorplan

        for cls in reversed(get_ui_classes()):
            bpy.utils.unregister_class(cls)
        for cls in reversed(get_operator_classes()):
            bpy.utils.unregister_class(cls)

        for cls in reversed(_addon_classes):
            bpy.utils.unregister_class(cls)

        _set_selected_outline_visible(True)
        _mode_object_name = ""
        clear_graph_store()
