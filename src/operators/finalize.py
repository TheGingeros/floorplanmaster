# FP4 — Finalize operator
# Converts the procedural FloorPlan object to a static mesh ready for export.

import bpy
from bpy.props import BoolProperty, EnumProperty

from ..core.final_mesh_builder import build_final_mesh_from_graph
from ..ui.selection_state import _selection


def _resolve_finalize_floorplan_obj(context):
    from .. import find_floorplan_obj, get_selected_floorplan_obj

    obj = find_floorplan_obj(context)
    if obj is not None:
        return obj
    return get_selected_floorplan_obj(context)


def _strip_modifiers(obj):
    for mod in list(obj.modifiers):
        obj.modifiers.remove(mod)


def _convert_all_corner_float2_attrs_to_uv(mesh):
    # Convert all FACE CORNER float2 attributes to UV layers.
    # Exporters read UV layers, not generic attributes.
    for attr in list(mesh.attributes):
        if attr.domain != 'CORNER':
            continue
        if attr.data_type != 'FLOAT2':
            continue

        uv_layer = mesh.uv_layers.get(attr.name)
        if uv_layer is None:
            uv_layer = mesh.uv_layers.new(name=attr.name)

        # Attribute and UV loop domains are both loop-indexed.
        loop_count = min(len(attr.data), len(uv_layer.data))
        for i in range(loop_count):
            data_item = attr.data[i]
            vec = getattr(data_item, "vector", None)
            if vec is None:
                vec = getattr(data_item, "value", None)
            if vec is None:
                continue
            uv_layer.data[i].uv = (float(vec[0]), float(vec[1]))


def _assign_default_material(mesh):
    mat = bpy.data.materials.get("FloorPlan_Default")
    if mat is None:
        mat = bpy.data.materials.new(name="FloorPlan_Default")

    mesh.materials.clear()
    mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.material_index = 0


def _set_faces_shade_flat(mesh):
    for poly in mesh.polygons:
        poly.use_smooth = False
    mesh.update()


def _cleanup_named_attributes(mesh):
    # Remove removable named attributes from the baked mesh.
    # Blender keeps some internal/required attributes protected.
    for attr in list(mesh.attributes):
        if getattr(attr, "is_internal", False):
            continue
        try:
            mesh.attributes.remove(attr)
        except RuntimeError:
            # Keep required attributes that Blender marks as non-removable.
            continue


def _remove_floorplan_identity(obj):
    # Baked output is intentionally no longer parametric.
    keys_to_remove = [
        "is_floorplan",
        "_floorplan_graphs",
        "_floorplan_room_names",
    ]
    keys_to_remove.extend([k for k in obj.keys() if k.startswith("room_name_")])
    keys_to_remove.extend([k for k in obj.keys() if k.startswith("room_expanded_")])

    for key in keys_to_remove:
        if key in obj:
            del obj[key]


def _duplicate_object(source_obj, context):
    dup = source_obj.copy()
    dup.name = f"{source_obj.name}_Baked"
    if source_obj.users_collection:
        for col in source_obj.users_collection:
            col.objects.link(dup)
    else:
        context.scene.collection.objects.link(dup)
    return dup


def detach_floorplan_object(
    context,
    source_obj,
    *,
    keep_original=False,
    cleanup_attributes=True,
    assign_default_material=True,
    apply_flat_shading=False,
    include_ceiling=False,
    include_outer_faces=True,
):
    # Convert procedural FloorPlan object into a plain mesh object.
    from .. import (
        find_floorplan_obj,
        is_floorplan_mode_active,
        remove_graphs,
        reset_graphs_for_obj,
        set_floorplan_mode_active,
    )
    from ..ui.properties import set_room_props_updating, set_wall_props_updating

    # If semantic mode owns this object, disable mode first.
    if is_floorplan_mode_active(context):
        mode_obj = find_floorplan_obj(context)
        if mode_obj is not None and mode_obj.name == source_obj.name:
            set_floorplan_mode_active(context, False)

    # Rebuild from canonical graph state before baking mesh output.
    sg, rg, _mapper = reset_graphs_for_obj(source_obj)

    target_obj = _duplicate_object(source_obj, context) if keep_original else source_obj
    baked_mesh = build_final_mesh_from_graph(
        sg,
        rg,
        mesh_name=f"{target_obj.name}_BakedMesh",
        include_ceiling=include_ceiling,
        include_outer_faces=include_outer_faces,
    )
    old_mesh = target_obj.data
    target_obj.data = baked_mesh

    _strip_modifiers(target_obj)

    context.view_layer.objects.active = target_obj
    target_obj.select_set(True)
    if target_obj is not source_obj:
        source_obj.select_set(False)

    _convert_all_corner_float2_attrs_to_uv(target_obj.data)
    if assign_default_material:
        _assign_default_material(target_obj.data)
    if cleanup_attributes:
        _cleanup_named_attributes(target_obj.data)

    _remove_floorplan_identity(target_obj)

    if not keep_original:
        remove_graphs(source_obj)
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

    if old_mesh is not None and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    target_obj.data.update()
    if apply_flat_shading:
        _set_faces_shade_flat(target_obj.data)

    if context.area:
        context.area.tag_redraw()

    return target_obj


class FLOORPLAN_OT_finalize(bpy.types.Operator):
    bl_idname = "floorplan.finalize"
    bl_label = "Bake"
    bl_description = "Finalize floor plan into a static mesh"
    bl_options = {'REGISTER', 'UNDO'}

    output_organization: EnumProperty(
        name="Output Organization",
        description="Scope limited to single baked object for now",
        items=[
            ('SINGLE_OBJECT', "Single Object", "Bake as one static mesh object"),
        ],
        default='SINGLE_OBJECT',
    )
    material_assignment: EnumProperty(
        name="Material Assignment",
        description="Scope limited to default material fallback for now",
        items=[
            ('DEFAULT', "Default Blender Material", "Assign one default material to all polygons"),
        ],
        default='DEFAULT',
    )
    cleanup_attributes: BoolProperty(
        name="Clean Named Attributes",
        description="Remove named mesh attributes from baked output",
        default=True,
    )
    keep_original: BoolProperty(
        name="Keep Original",
        description="Duplicate and bake a copy instead of baking destructively",
        default=True,
    )
    include_ceiling: BoolProperty(
        name="Add Ceiling",
        description="Add room ceiling faces at room top heights",
        default=False,
    )
    include_outer_faces: BoolProperty(
        name="Include Outer Faces",
        description="Keep outward wall faces; disable for inward-facing walls only",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def invoke(self, context, event):
        if _resolve_finalize_floorplan_obj(context) is None:
            self.report({'ERROR'}, "No floor plan object found")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "output_organization")
        col.prop(self, "material_assignment")
        col.prop(self, "cleanup_attributes")
        col.prop(self, "keep_original")
        col.prop(self, "include_ceiling")
        col.prop(self, "include_outer_faces")

    def execute(self, context):
        from .. import reset_graphs_for_obj

        source_obj = _resolve_finalize_floorplan_obj(context)
        if source_obj is None:
            self.report({'ERROR'}, "No floor plan object found")
            return {'CANCELLED'}

        # Validate graph reconstruction before conversion.
        reset_graphs_for_obj(source_obj)

        target_obj = detach_floorplan_object(
            context,
            source_obj,
            keep_original=self.keep_original,
            cleanup_attributes=self.cleanup_attributes,
            assign_default_material=True,
            apply_flat_shading=True,
            include_ceiling=self.include_ceiling,
            include_outer_faces=self.include_outer_faces,
        )

        if self.keep_original:
            self.report({'INFO'}, f"Baked copy created: {target_obj.name}")
        else:
            self.report({'INFO'}, f"Baked object: {target_obj.name}")

        return {'FINISHED'}