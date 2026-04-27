# FP2 — Remove selected wall operator
# Removes the currently selected wall, updates rooms, and syncs mesh/GN.

import bpy

from ..core.sync import sync_graph_to_mesh, persist_room_names
from ..geometry.gn_setup import ensure_gn_modifier
from ..ui.selection_state import _selection
from ..ui.properties import set_room_props_updating, set_wall_props_updating


class FLOORPLAN_OT_remove_selected_wall(bpy.types.Operator):
    bl_idname = "floorplan.remove_selected_wall"
    bl_label = "Remove Selected Wall"
    bl_description = "Remove the selected wall"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        from .. import find_floorplan_obj

        # No selected wall: allow Blender's native X behavior to continue.
        obj = find_floorplan_obj(context)
        if obj is None or not _selection.has_wall_for_object(obj):
            return {'PASS_THROUGH'}
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        from .. import find_floorplan_obj, reset_graphs_for_obj

        wall_uuid = _selection.wall_id
        if not wall_uuid:
            self.report({'WARNING'}, "No wall is selected")
            return {'CANCELLED'}

        obj = find_floorplan_obj(context)
        if obj is None:
            self.report({'ERROR'}, "No floor plan object found")
            return {'CANCELLED'}

        # Always rebuild from current mesh/custom properties. Blender undo
        # restores object data but not Python globals like _graph_store.
        sg, rg, mapper = reset_graphs_for_obj(obj)

        wall = sg.get_wall(wall_uuid)
        if wall is None:
            _selection.deselect_all(context)
            self.report({'WARNING'}, "Selected wall no longer exists")
            return {'CANCELLED'}

        before_rooms = len(rg.get_all_rooms())
        touched_junctions = {wall.junction_start, wall.junction_end}

        sg.remove_wall(wall_uuid)
        for jid in touched_junctions:
            if len(sg.get_walls_for_junction(jid)) == 0:
                sg.remove_junction(jid)

        rg.sync_from_structural_graph()

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

        _selection.deselect_all(context)

        settings = context.scene.floorplan
        set_wall_props_updating(True)
        try:
            settings.active_wall_thickness = 0.0
            settings.active_wall_height = 0.0
        finally:
            set_wall_props_updating(False)

        set_room_props_updating(True)
        try:
            settings.active_room_name = ""
        finally:
            set_room_props_updating(False)
        settings.opening_items.clear()

        removed_rooms = max(0, before_rooms - len(rg.get_all_rooms()))
        if removed_rooms:
            self.report({'INFO'}, f"Removed wall and {removed_rooms} room(s)")
        else:
            self.report({'INFO'}, "Removed wall")
        context.area.tag_redraw()
        return {'FINISHED'}


def register_remove_wall_keymap():
    # X in Object Mode — removes selected floorplan wall after confirmation.
    # Returns PASS_THROUGH when no wall is selected, so native Blender X keeps working.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(
        "floorplan.remove_selected_wall",
        type='X',
        value='PRESS',
    )
    return km, kmi


def unregister_remove_wall_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.get('Object Mode')
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == "floorplan.remove_selected_wall":
                km.keymap_items.remove(kmi)
                break