# FP2 — Add Opening operator
# Adds a door or window opening to the currently selected wall.
# The redo panel (F9 / bottom-left) allows the user to adjust type and parameters.
# Values are clamped via check() so the UI never shows validation errors.

import bpy
from bpy.props import EnumProperty, FloatProperty, StringProperty

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

    # Hidden props cached on invoke — used by check() for clamping without
    # needing to access the graph store (which may be stale during redo).
    # SKIP_SAVE is intentionally omitted: Blender must store these in the redo
    # history so they are available across redo panel re-executions.
    cached_wall_height: FloatProperty(options={'HIDDEN'})
    cached_wall_length: FloatProperty(options={'HIDDEN'})
    # Tracks previous type so check() can apply defaults on type switch.
    prev_type: StringProperty(options={'HIDDEN'}, default='')
    # Snapshot of the target wall UUID at invoke time — redo always targets
    # this wall, even if the user selects a different wall in between.
    target_wall_id: StringProperty(options={'HIDDEN'}, default='')

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "floorplan"):
            return False
        return context.scene.floorplan.active_wall_id != ""

    def check(self, context):
        # Clamp all values to valid ranges based on wall dimensions.
        # Called before every execute() triggered by the redo panel.
        # NOTE: type-switch defaults are applied in execute() only, so that
        # prev_type stays at the old value and execute() can reliably detect
        # the switch even if Blender re-reads stored property values between
        # check() and execute().
        changed = False
        wh = self.cached_wall_height
        wl = self.cached_wall_length

        if wh <= 0 or wl <= 0:
            return changed

        # Doors always have sill = 0.
        if self.opening_type == 'DOOR' and self.sill_height != 0.0:
            self.sill_height = 0.0
            changed = True

        # Clamp height to fit within wall.
        max_h = wh - self.sill_height
        if max_h < MIN_OPENING_HEIGHT:
            max_h = MIN_OPENING_HEIGHT
        if self.height > max_h:
            self.height = max_h
            changed = True

        # Clamp sill so opening doesn't exceed wall top.
        max_sill = wh - self.height
        if max_sill < 0:
            max_sill = 0
        if self.sill_height > max_sill:
            self.sill_height = max_sill
            changed = True

        # Clamp width to fit within wall length.
        max_w = min(MAX_OPENING_WIDTH, wl * 0.98)
        if max_w < MIN_OPENING_WIDTH:
            max_w = MIN_OPENING_WIDTH
        if self.width > max_w:
            self.width = max_w
            changed = True

        # Clamp position so opening stays within wall bounds.
        if wl > 0:
            half_norm = (self.width / 2.0) / wl
            min_pos = half_norm + 0.005
            max_pos = 1.0 - half_norm - 0.005
            if min_pos > max_pos:
                min_pos = max_pos = 0.5
            if self.position < min_pos:
                self.position = min_pos
                changed = True
            if self.position > max_pos:
                self.position = max_pos
                changed = True

        return changed

    def execute(self, context):
        from .. import find_floorplan_obj, reset_graphs_for_obj
        from ..core.sync import sync_graph_to_mesh
        from ..geometry.gn_setup import ensure_gn_modifier

        # Use the snapshot from invoke, not the live scene property — ensures
        # redo always targets the originally selected wall.
        wall_uuid = self.target_wall_id
        if not wall_uuid:
            # Fallback for direct execute() calls without invoke().
            wall_uuid = context.scene.floorplan.active_wall_id
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

        # Cache wall dims for check() on subsequent redo tweaks.
        self.cached_wall_height = wall.height
        wl = sg.wall_length(wall_uuid)
        self.cached_wall_length = wl

        # Detect type switch and apply type-specific defaults.  This is the
        # authoritative place for type defaults — check() only clamps.
        # Blender's redo panel may not preserve check()-modified values for
        # execute(), so execute() must handle the switch independently.
        if self.prev_type != self.opening_type:
            if self.opening_type == 'WINDOW':
                self.sill_height = DEFAULT_WINDOW_SILL
                self.width = DEFAULT_WINDOW_WIDTH
                self.height = DEFAULT_WINDOW_HEIGHT
            else:
                self.sill_height = 0.0
                self.width = DEFAULT_DOOR_WIDTH
                self.height = DEFAULT_DOOR_HEIGHT
            self.prev_type = self.opening_type

        # Clamp values using ACTUAL wall dimensions.
        sill = 0.0 if self.opening_type == 'DOOR' else self.sill_height
        height = self.height
        width = self.width
        position = self.position

        # Height + sill must fit within wall.
        if sill + height > wall.height:
            height = wall.height - sill
        if height < MIN_OPENING_HEIGHT:
            height = MIN_OPENING_HEIGHT
            sill = min(sill, wall.height - height)
        if sill < 0:
            sill = 0.0

        # Width must fit within wall length.
        if wl > 0:
            max_w = min(MAX_OPENING_WIDTH, wl * 0.98)
            width = max(MIN_OPENING_WIDTH, min(width, max_w))

            # Position so opening stays within wall bounds.
            half_norm = (width / 2.0) / wl
            min_pos = half_norm + 0.005
            max_pos = 1.0 - half_norm - 0.005
            if min_pos > max_pos:
                min_pos = max_pos = 0.5
            position = max(min_pos, min(position, max_pos))

        try:
            sg.add_opening(
                wall_uuid,
                opening_type=self.opening_type,
                position=position,
                width=width,
                height=height,
                sill_height=sill,
            )
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        ensure_gn_modifier(obj)
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj

        # Snapshot the target wall so redo always targets the same wall,
        # even if the user selects a different wall in between.
        settings = context.scene.floorplan
        wall_uuid = settings.active_wall_id
        self.target_wall_id = wall_uuid

        # Cache wall dimensions for check() clamping.
        obj = find_floorplan_obj(context)
        if obj and wall_uuid:
            if obj.name not in _graph_store:
                reset_graphs_for_obj(obj)
            sg, _, _ = _graph_store.get(obj.name, (None, None, None))
            if sg:
                wall = sg.get_wall(wall_uuid)
                if wall:
                    self.cached_wall_height = wall.height
                    self.cached_wall_length = sg.wall_length(wall_uuid)

        # Leave prev_type as '' so that execute() always detects it as a
        # type switch on the first run and applies proper defaults.  This
        # avoids duplicating default-setting logic between invoke and execute.
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
