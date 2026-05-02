# Edit Mode guard for FloorPlan objects.
#
# Entering Edit Mode on a parametric FloorPlan object is destructive:
# the object is detached from FloorPlan semantics and converted to a
# regular Blender mesh first.

import bpy

from .finalize import detach_floorplan_object


class FLOORPLAN_OT_edit_mode_detach_cancel(bpy.types.Operator):
    bl_idname = "floorplan.edit_mode_detach_cancel"
    bl_label = "Cancel"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'CANCELLED'}


class FLOORPLAN_OT_edit_mode_detach_bake(bpy.types.Operator):
    bl_idname = "floorplan.edit_mode_detach_bake"
    bl_label = "Bake"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        from .. import get_selected_floorplan_obj
        return get_selected_floorplan_obj(context) is not None

    def execute(self, context):
        bpy.ops.floorplan.finalize('INVOKE_DEFAULT')
        return {'FINISHED'}


class FLOORPLAN_OT_edit_mode_detach_lose_data(bpy.types.Operator):
    bl_idname = "floorplan.edit_mode_detach_lose_data"
    bl_label = "Lose Data"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        from .. import get_selected_floorplan_obj
        return get_selected_floorplan_obj(context) is not None

    def execute(self, context):
        from .. import get_selected_floorplan_obj

        source_obj = get_selected_floorplan_obj(context)
        if source_obj is None:
            return {'PASS_THROUGH'}

        target_obj = detach_floorplan_object(
            context,
            source_obj,
            keep_original=False,
            cleanup_attributes=True,
            assign_default_material=True,
            apply_flat_shading=False,
        )

        # Ensure target object is active before switching mode.
        view_layer = context.view_layer
        for selected in context.selected_objects:
            if selected != target_obj:
                selected.select_set(False)
        view_layer.objects.active = target_obj
        target_obj.select_set(True)

        if target_obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'WARNING'}, "FloorPlan data removed. Object is now a regular editable mesh.")
        return {'FINISHED'}


class FLOORPLAN_OT_edit_mode_with_detach(bpy.types.Operator):
    bl_idname = "floorplan.edit_mode_with_detach"
    bl_label = "Enter Edit Mode (Detach FloorPlan)"
    bl_description = "Detach FloorPlan data and continue to Edit Mode"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        from .. import get_selected_floorplan_obj
        return get_selected_floorplan_obj(context) is not None

    def invoke(self, context, event):
        obj = None
        try:
            from .. import get_selected_floorplan_obj
            obj = get_selected_floorplan_obj(context)
        except Exception:
            obj = None
        if obj is None:
            return {'PASS_THROUGH'}

        def _draw_popup(menu, popup_context):
            col = menu.layout.column(align=True)
            col.label(text="Edit Mode is not available for parametric FloorPlan objects.", icon='ERROR')
            col.label(text="Choose what to do before entering mesh editing:")
            col.label(text="Bake lets you keep the data and bake into normal editable mesh.")
            col.label(text="Lose Data loses all floor plan related data.")

            row = col.row(align=True)
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator("floorplan.edit_mode_detach_cancel", text="Cancel", icon='CANCEL')
            row.operator("floorplan.edit_mode_detach_bake", text="Bake", icon='MODIFIER')
            danger = row.row(align=True)
            danger.alert = True
            danger.operator(
                "floorplan.edit_mode_detach_lose_data",
                text="Lose Data",
                icon='ERROR',
            )

        context.window_manager.popup_menu(
            _draw_popup,
            title="FloorPlan Edit Mode Warning",
            icon='ERROR',
        )
        return {'CANCELLED'}

    def draw(self, context):
        # UI is built in invoke via popup_menu callback.
        pass

    def execute(self, context):
        # UI is shown in invoke; actions run in dedicated operators.
        return {'CANCELLED'}


def register_edit_mode_detach_keymap():
    # Tab in Object Mode opens detach warning for active selected FloorPlan object.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(
        "floorplan.edit_mode_with_detach",
        type='TAB',
        value='PRESS',
    )
    return km, kmi


def unregister_edit_mode_detach_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.get('Object Mode')
    if km:
        to_remove = [kmi for kmi in km.keymap_items if kmi.idname == "floorplan.edit_mode_with_detach"]
        for kmi in to_remove:
            km.keymap_items.remove(kmi)
