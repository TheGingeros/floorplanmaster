# FP2 — Add Opening operator
# Adds a door or window opening to the currently selected wall.
# The redo panel (F9 / bottom-left) allows the user to adjust type and parameters.

import bpy
from bpy.props import EnumProperty, FloatProperty

from ..utils.constants import (
    DEFAULT_DOOR_WIDTH, DEFAULT_WINDOW_WIDTH,
    DEFAULT_DOOR_HEIGHT, DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_SILL,
    MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
    MIN_OPENING_HEIGHT, MAX_HEIGHT,
)


class FLOORPLAN_OT_add_opening(bpy.types.Operator):
    bl_idname = "floorplan.add_opening"
    bl_label = "Add Opening"
    bl_description = "Add a door or window opening to the selected wall"
    bl_options = {'REGISTER', 'UNDO'}

    opening_type: EnumProperty(
        name="Type",
        items=[
            ('DOOR', "Door", "Door opening from the floor"),
            ('WINDOW', "Window", "Window opening with sill height"),
        ],
        default='DOOR',
    )
    width: FloatProperty(
        name="Width",
        default=DEFAULT_DOOR_WIDTH,
        min=MIN_OPENING_WIDTH,
        max=MAX_OPENING_WIDTH,
        precision=3,
        unit='LENGTH',
    )
    height: FloatProperty(
        name="Height",
        default=DEFAULT_DOOR_HEIGHT,
        min=MIN_OPENING_HEIGHT,
        max=MAX_HEIGHT,
        precision=3,
        unit='LENGTH',
    )
    sill_height: FloatProperty(
        name="Sill Height",
        description="Distance from floor to bottom of opening (doors = 0)",
        default=0.0,
        min=0.0,
        max=MAX_HEIGHT,
        precision=3,
        unit='LENGTH',
    )
    position: FloatProperty(
        name="Position",
        description="Relative position along wall (0 = start, 1 = end)",
        default=0.5,
        min=0.01,
        max=0.99,
        precision=3,
    )

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "floorplan"):
            return False
        return context.scene.floorplan.active_wall_id != ""

    def execute(self, context):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
        from ..core.sync import sync_graph_to_mesh
        from ..geometry.gn_setup import ensure_gn_modifier
        from ..core.validators import ValidationError

        settings = context.scene.floorplan
        wall_uuid = settings.active_wall_id
        if not wall_uuid:
            self.report({'WARNING'}, "No wall selected")
            return {'CANCELLED'}

        obj = find_floorplan_obj(context)
        if obj is None:
            self.report({'WARNING'}, "No floorplan object found")
            return {'CANCELLED'}

        # Rebuild graphs from mesh (handles undo correctly — each redo
        # undoes the mesh, then re-executes with updated params).
        sg, rg, mapper = reset_graphs_for_obj(obj)

        wall = sg.get_wall(wall_uuid)
        if wall is None:
            self.report({'WARNING'}, "Wall no longer exists")
            return {'CANCELLED'}

        # For doors, force sill_height to 0.
        sill = 0.0 if self.opening_type == 'DOOR' else self.sill_height

        try:
            sg.add_opening(
                wall_uuid,
                opening_type=self.opening_type,
                position=self.position,
                width=self.width,
                height=self.height,
                sill_height=sill,
            )
        except (ValidationError, ValueError) as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        ensure_gn_modifier(obj)
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        # Set sensible defaults based on opening type.
        if self.opening_type == 'WINDOW':
            self.width = DEFAULT_WINDOW_WIDTH
            self.height = DEFAULT_WINDOW_HEIGHT
            self.sill_height = DEFAULT_WINDOW_SILL
        else:
            self.width = DEFAULT_DOOR_WIDTH
            self.height = DEFAULT_DOOR_HEIGHT
            self.sill_height = 0.0
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "opening_type")
        layout.prop(self, "width")
        layout.prop(self, "height")
        if self.opening_type == 'WINDOW':
            layout.prop(self, "sill_height")
        layout.prop(self, "position")


class FLOORPLAN_OT_remove_opening(bpy.types.Operator):
    bl_idname = "floorplan.remove_opening"
    bl_label = "Remove Opening"
    bl_description = "Remove an opening from the wall"
    bl_options = {'REGISTER', 'UNDO'}

    opening_id: bpy.props.StringProperty(options={'HIDDEN'})

    def execute(self, context):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
        from ..core.sync import sync_graph_to_mesh
        from ..geometry.gn_setup import ensure_gn_modifier

        obj = find_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}

        if obj.name not in _graph_store:
            reset_graphs_for_obj(obj)
        sg, rg, mapper = _graph_store[obj.name]

        if not sg.remove_opening(self.opening_id):
            self.report({'WARNING'}, "Opening not found")
            return {'CANCELLED'}

        ensure_gn_modifier(obj)
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()
        return {'FINISHED'}
