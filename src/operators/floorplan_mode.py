# FloorPlan Mode — modal event controller + mode toggle operator
#
# FLOORPLAN_OT_floorplan_modal runs while semantic FloorPlan mode is active.
# It consumes non-navigation events to prevent accidental tool shortcuts from
# firing (W, G, Tab, …) while the user edits the floor plan.
#
# Event handling inside the modal:
#   Navigation (orbit/zoom/pan)  → PASS_THROUGH  (Blender handles normally)
#   Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y → PASS_THROUGH  (classic undo/redo)
#   N                            → PASS_THROUGH  (toggle 3D View sidebar)
#   LMB (pencil not active)      → wall/room selection via _pick_element
#   LMB (pencil active)          → PASS_THROUGH  (pencil tool owns the click)
#   X                            → remove selected wall or consume the key
#   Shift+Q                      → disable mode + FINISHED
#   Everything else              → RUNNING_MODAL (consumed)
#
# FLOORPLAN_OT_toggle_mode is bound to Shift+Q via register_floorplan_mode_keymap.
# When mode is OFF: keymap fires toggle_mode → enables mode → invokes the modal.
# When mode is ON:  modal intercepts Shift+Q before the keymap → disables mode.

import json

import bpy

from .select_wall import _pick_element, _clear_semantic_selection_ui
from ..ui.selection_state import _selection


_NAVIGATION_EVENT_TYPES = frozenset({
    'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
    'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE',
    'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
    'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9',
    'NUMPAD_PERIOD', 'NUMPAD_PLUS', 'NUMPAD_MINUS', 'NUMPAD_SLASH',
    'TRACKPADPAN', 'TRACKPADZOOM',
})


def _mouse_region_type(context, event):
    window = getattr(context, 'window', None)
    screen = getattr(window, 'screen', None)
    if screen is None:
        return None, None

    mouse_x = getattr(event, 'mouse_x', None)
    mouse_y = getattr(event, 'mouse_y', None)
    if mouse_x is None or mouse_y is None:
        return None, None

    for area in screen.areas:
        if not (area.x <= mouse_x < area.x + area.width and area.y <= mouse_y < area.y + area.height):
            continue
        for region in area.regions:
            if region.x <= mouse_x < region.x + region.width and region.y <= mouse_y < region.y + region.height:
                return area, region
        return area, None

    return None, None


class FLOORPLAN_OT_floorplan_modal(bpy.types.Operator):
    bl_idname = "floorplan.floorplan_modal"
    bl_label = "FloorPlan Mode"
    bl_description = "Run semantic FloorPlan editing mode (Shift+Q to exit)"

    # Class-level guard: only one instance may run at a time.
    _running = False

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        from .. import is_floorplan_mode_active
        if not is_floorplan_mode_active(context):
            return {'CANCELLED'}
        if FLOORPLAN_OT_floorplan_modal._running:
            return {'CANCELLED'}
        FLOORPLAN_OT_floorplan_modal._running = True
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        from .. import is_floorplan_mode_active, set_floorplan_mode_active

        # Exit automatically if mode was disabled externally (object deleted,
        # file load, addon reload, etc.).
        if not is_floorplan_mode_active(context):
            return self._finish(context)

        # UI panels, headers, and other non-viewport regions inside the same
        # VIEW_3D area must remain fully usable while semantic mode is active.
        # Modal context stays anchored to the invoke region, so resolve the
        # actual hovered area/region from the mouse position instead.
        area, region = _mouse_region_type(context, event)
        if area is None or area.type != 'VIEW_3D' or region is None or region.type != 'WINDOW':
            return {'PASS_THROUGH'}

        # Navigation — let Blender orbit/zoom/pan as usual.
        if event.type in _NAVIGATION_EVENT_TYPES:
            return {'PASS_THROUGH'}

        # Keep Blender's classic undo/redo available while semantic mode runs.
        # Undo: Ctrl+Z
        # Redo: Ctrl+Shift+Z (or Ctrl+Y, depending on keymap)
        if event.ctrl and event.value == 'PRESS' and (
            event.type == 'Z' or event.type == 'Y'
        ):
            return {'PASS_THROUGH'}

        # Allow toggling the 3D View sidebar (N-panel) with the default hotkey.
        if event.type == 'N' and event.value == 'PRESS':
            return {'PASS_THROUGH'}

        # Shift+Q: disable mode and exit the modal.
        if event.type == 'Q' and event.value == 'PRESS' and event.shift:
            settings = context.scene.floorplan
            set_floorplan_mode_active(context, False)
            _clear_semantic_selection_ui(context, settings)
            if context.area:
                context.area.tag_redraw()
            return self._finish(context)

        # LMB: semantic wall/room selection.
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # While the pencil tool is drawing, it owns the interaction.
            from .pencil_tool import _pencil_state
            if _pencil_state is not None:
                return {'PASS_THROUGH'}
            self._handle_select(context, event)
            # Always consume — prevents Blender from deselecting the object.
            return {'RUNNING_MODAL'}

        # Own X inside semantic mode so Blender object deletion never fires.
        # If a wall is selected for the current FloorPlan object, reuse the
        # existing remove-wall operator (and its confirm dialog). If no wall
        # is selected, remove the selected room in the same way.
        if event.type == 'X' and event.value == 'PRESS':
            from .. import find_floorplan_obj

            obj = find_floorplan_obj(context)
            if obj is not None and _selection.has_wall_for_object(obj):
                bpy.ops.floorplan.remove_selected_wall('INVOKE_DEFAULT')
                return {'RUNNING_MODAL'}

            if (
                obj is not None
                and _selection.has_room_for_object(obj)
                and obj.name in context.scene.objects
            ):
                from .. import _graph_store, reset_graphs_for_obj

                if obj.name not in _graph_store:
                    reset_graphs_for_obj(obj)

                _sg, rg, _mapper = _graph_store[obj.name]
                room = rg.get_room(_selection.room_id)
                if room is not None:
                    bpy.ops.floorplan.remove_room(
                        'INVOKE_DEFAULT',
                        room_id=room.id,
                        room_cycle_key=json.dumps(list(rg._cycle_key(room.cycle))),
                    )
            return {'RUNNING_MODAL'}

        # All other events consumed to prevent accidental shortcuts.
        return {'RUNNING_MODAL'}

    def _handle_select(self, context, event):
        # Inline selection logic so the real event coordinates (mouse_region_x/y)
        # are used directly — avoids coordinate loss from bpy.ops re-dispatch.
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
        from ..ui.properties import set_wall_props_updating, populate_opening_items

        settings = context.scene.floorplan
        obj = find_floorplan_obj(context)
        if obj is None:
            return

        if obj.name not in _graph_store:
            sg, rg, mapper = reset_graphs_for_obj(obj)
            if not sg.get_all_walls():
                return
        sg, rg, mapper = _graph_store[obj.name]

        result = _pick_element(
            context, sg, rg,
            event.mouse_region_x, event.mouse_region_y,
        )

        if result is not None and result[0] == 'wall':
            wall_uuid = result[1]
            wall = sg.get_wall(wall_uuid)
            if wall is None:
                _clear_semantic_selection_ui(context, settings)
                return
            _selection.select_wall(wall_uuid, context, object_name=obj.name)
            set_wall_props_updating(True)
            try:
                settings.active_wall_thickness = wall.thickness
                settings.active_wall_height = wall.height
            finally:
                set_wall_props_updating(False)
            populate_opening_items(settings, sg, wall_uuid)
            context.area.tag_redraw()
            return

        if result is not None and result[0] == 'room':
            room_uuid = result[1]
            room = rg.get_room(room_uuid)
            if room is None:
                _clear_semantic_selection_ui(context, settings)
                return
            _selection.select_room(room_uuid, context, from_viewport=True, object_name=obj.name)
            from ..ui.properties import set_room_props_updating
            set_room_props_updating(True)
            try:
                settings.active_room_name = room.name
            finally:
                set_room_props_updating(False)
            settings.active_wall_thickness = 0.0
            settings.active_wall_height = 0.0
            settings.opening_items.clear()
            context.area.tag_redraw()
            return

        # Missed — clear selection.
        _clear_semantic_selection_ui(context, settings)

    def _finish(self, context):
        FLOORPLAN_OT_floorplan_modal._running = False
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_mode(bpy.types.Operator):
    bl_idname = "floorplan.toggle_mode"
    bl_label = "Toggle FloorPlan Mode"
    bl_description = "Enable or disable semantic FloorPlan mode for the active floor plan object"

    @classmethod
    def poll(cls, context):
        from .. import get_selected_floorplan_obj, is_floorplan_mode_active
        return is_floorplan_mode_active(context) or get_selected_floorplan_obj(context) is not None

    def execute(self, context):
        from .. import is_floorplan_mode_active, set_floorplan_mode_active, toggle_floorplan_mode

        settings = context.scene.floorplan
        if is_floorplan_mode_active(context):
            # Mode already on: disable it. The running modal will self-terminate
            # on its next event (is_floorplan_mode_active will return False).
            set_floorplan_mode_active(context, False)
            _clear_semantic_selection_ui(context, settings)
        else:
            # Mode off: enable it and launch the modal controller.
            toggle_floorplan_mode(context)
            if (
                is_floorplan_mode_active(context)
                and context.area is not None
                and context.area.type == 'VIEW_3D'
            ):
                bpy.ops.floorplan.floorplan_modal('INVOKE_DEFAULT')

        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


def register_floorplan_mode_keymap():
    # Shift+Q toggles semantic mode on the selected active FloorPlan object.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(
        "floorplan.toggle_mode",
        type='Q',
        value='PRESS',
        shift=True,
    )
    return km, kmi


def unregister_floorplan_mode_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.get('Object Mode')
    if km:
        to_remove = [kmi for kmi in km.keymap_items if kmi.idname == "floorplan.toggle_mode"]
        for kmi in to_remove:
            km.keymap_items.remove(kmi)
