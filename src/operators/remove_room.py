# FP2 — Remove Room operator
# Deletes one room while preserving walls shared with neighboring rooms.

import json

import bpy
from bpy.props import StringProperty

from ..core.sync import sync_graph_to_mesh, persist_room_names
from ..geometry.gn_setup import ensure_gn_modifier
from ..ui.selection_state import _selection
from ..ui.properties import set_room_props_updating


class FLOORPLAN_OT_remove_room(bpy.types.Operator):
    bl_idname = "floorplan.remove_room"
    bl_label = "Remove Room"
    bl_description = "Remove this room and keep shared walls with neighboring rooms"
    bl_options = {'UNDO'}

    room_id: StringProperty()
    room_cycle_key: StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        from .. import _graph_store, find_floorplan_obj, reset_graphs_for_obj

        obj = find_floorplan_obj(context)
        if obj is None:
            self.report({'ERROR'}, "No floor plan object found")
            return {'CANCELLED'}

        # Always rebuild from current mesh/custom properties. Blender undo
        # restores object data but not Python globals like _graph_store.
        sg, rg, mapper = reset_graphs_for_obj(obj)

        room = rg.get_room(self.room_id)
        if room is None and self.room_cycle_key:
            # Room UUIDs are runtime-only and can change after reconstruction.
            # Resolve by canonical cycle key, which is stable for the same topology.
            try:
                cycle_key = tuple(json.loads(self.room_cycle_key))
            except Exception:
                cycle_key = None
            if cycle_key is not None:
                resolved_id = rg._cycle_room_map.get(cycle_key)
                if resolved_id:
                    room = rg.get_room(resolved_id)

        if room is None:
            self.report({'WARNING'}, "Room no longer exists")
            return {'CANCELLED'}

        removed_wall_ids = rg.delete_room(room.id)

        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        ensure_gn_modifier(obj)
        persist_room_names(obj, rg)

        valid_room_ids = {r.id for r in rg.get_all_rooms()}
        stale_keys = [
            k for k in list(obj.keys())
            if (k.startswith("room_name_") and k[len("room_name_"):] not in valid_room_ids)
            or (k.startswith("room_expanded_") and k[len("room_expanded_"):] not in valid_room_ids)
        ]
        for key in stale_keys:
            del obj[key]

        # Clear stale selection after topology changes.
        if _selection.room_id and _selection.room_id not in valid_room_ids:
            _selection.deselect_all(context)
        elif _selection.wall_id and sg.get_wall(_selection.wall_id) is None:
            _selection.deselect_all(context)

        set_room_props_updating(True)
        try:
            if not _selection.room_id:
                context.scene.floorplan.active_room_name = ""
        finally:
            set_room_props_updating(False)
        context.scene.floorplan.opening_items.clear()

        self.report({'INFO'}, f"Removed room and {len(removed_wall_ids)} non-shared wall(s)")
        context.area.tag_redraw()
        return {'FINISHED'}
