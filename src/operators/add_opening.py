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
from ..ui.selection_state import _selection


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
    # Inset (meters) at each junction end due to connecting wall thicknesses.
    # Used to restrict position/width to the visible wall surface.
    cached_inset_start: FloatProperty(options={'HIDDEN'}, default=0.0)
    cached_inset_end: FloatProperty(options={'HIDDEN'}, default=0.0)
    # Tracks previous type so check() can apply defaults on type switch.
    prev_type: StringProperty(options={'HIDDEN'}, default='')
    # Snapshot of the target wall UUID at invoke time — redo always targets
    # this wall, even if the user selects a different wall in between.
    target_wall_id: StringProperty(options={'HIDDEN'}, default='')
    # UUID of the opening created by this operator instance.
    # Stored after first execute() so that each redo can remove-and-re-add
    # (idempotent) instead of colliding with the previous run's opening that
    # may still be in sg when Blender's undo failed to revert the mesh.
    target_opening_id: StringProperty(options={'HIDDEN'}, default='')

    @classmethod
    def poll(cls, context):
        # Keep poll minimal: the "Add Opening" button is gated by
        # FLOORPLAN_PT_wall_properties.poll() which checks active_wall_id.
        # Do NOT check active_wall_id here — during redo re-execution Blender
        # reverts the scene to the pre-op undo snapshot, which may predate the
        # select_wall call that set active_wall_id.  A False poll() would
        # silently block execute() and make the type switch appear broken.
        # execute() validates the wall UUID and returns CANCELLED if missing.
        return hasattr(context.scene, "floorplan")

    def check(self, context):
        changed = False

        # Detect type switch and apply type-specific defaults.
        # Must happen here (not in execute()) so that Blender updates the
        # redo-panel UI sliders to the new values before re-executing.
        # execute() modifying self.* properties does NOT update the UI.
        if self.prev_type not in ('', self.opening_type):
            if self.opening_type == 'WINDOW':
                self.sill_height = DEFAULT_WINDOW_SILL
                self.width = DEFAULT_WINDOW_WIDTH
                self.height = DEFAULT_WINDOW_HEIGHT
            else:
                self.sill_height = 0.0
                self.width = DEFAULT_DOOR_WIDTH
                self.height = DEFAULT_DOOR_HEIGHT
            changed = True
        self.prev_type = self.opening_type

        wh = self.cached_wall_height
        wl = self.cached_wall_length

        # A wall shorter than the minimum opening width cannot hold any opening;
        # skip clamping to avoid half_norm overflow in the position section below.
        if wh <= 0 or wl < MIN_OPENING_WIDTH:
            return changed

        # Doors always have sill = 0.
        if self.opening_type == 'DOOR' and self.sill_height != 0.0:
            self.sill_height = 0.0
            changed = True

        # Clamp height to the absolute wall bounds — height is fixed, sill gives way.
        if self.height > wh:
            self.height = wh
            changed = True
        if self.height < MIN_OPENING_HEIGHT:
            self.height = MIN_OPENING_HEIGHT
            changed = True

        # Clamp sill so the top of the opening doesn't exceed the wall.
        # Height is intentionally NOT reduced here — sill is the one that moves.
        max_sill = wh - self.height
        if max_sill < 0.0:
            max_sill = 0.0
        if self.sill_height > max_sill:
            self.sill_height = max_sill
            changed = True

        # Width max is the usable wall span — independent of position.
        # This ensures moving position never silently shrinks the width.
        inset_s = self.cached_inset_start
        inset_e = self.cached_inset_end
        usable = max(MIN_OPENING_WIDTH, wl - inset_s - inset_e)
        max_w = min(MAX_OPENING_WIDTH, usable * 0.98)
        if self.width > max_w:
            self.width = max_w
            changed = True

        # Clamp position so the opening fits at the current width.
        # Guard uses MIN_OPENING_WIDTH (not 0) so that half_norm never overflows
        # for degenerate walls — such walls already fail sg.add_opening validation.
        if wl >= MIN_OPENING_WIDTH:
            half_norm = (self.width / 2.0) / wl
            inset_s_norm = inset_s / wl
            inset_e_norm = inset_e / wl
            min_pos = inset_s_norm + half_norm + 0.005
            max_pos = 1.0 - inset_e_norm - half_norm - 0.005
            if min_pos > max_pos:
                min_pos = max_pos = (inset_s_norm + 1.0 - inset_e_norm) / 2.0
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
            wall_uuid = _selection.wall_id
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

        # Idempotent: if a previous execute() placed an opening for this
        # operator instance, remove it before re-adding with new params.
        # This handles the case where Blender's undo stack could not revert
        # the mesh (e.g. first opening in a fresh scene with no prior undo
        # step), leaving the old opening still present in sg after rebuild.
        if self.target_opening_id:
            sg.remove_opening(self.target_opening_id)
            self.target_opening_id = ''

        wall = sg.get_wall(wall_uuid)
        if wall is None:
            self.report({'WARNING'}, "Wall no longer exists")
            return {'CANCELLED'}

        # Cache wall dims and junction insets for check() on subsequent redo tweaks.
        self.cached_wall_height = wall.height
        wl = sg.wall_length(wall_uuid)
        self.cached_wall_length = wl
        self.cached_inset_start = sg.junction_inset(wall.junction_start, wall_uuid)
        self.cached_inset_end = sg.junction_inset(wall.junction_end, wall_uuid)
        # Keep prev_type in sync so check() can detect the next type switch.
        self.prev_type = self.opening_type

        # Clamp values using ACTUAL wall dimensions and insets.
        sill = 0.0 if self.opening_type == 'DOOR' else self.sill_height
        height = self.height
        width = self.width
        position = self.position

        # Height is clamped to wall bounds; sill gives way, not height.
        height = max(MIN_OPENING_HEIGHT, min(height, wall.height))
        sill = max(0.0, min(sill, wall.height - height))

        # Width: wall-level cap, independent of position.
        inset_s = self.cached_inset_start
        inset_e = self.cached_inset_end
        if wl >= MIN_OPENING_WIDTH:
            usable = max(MIN_OPENING_WIDTH, wl - inset_s - inset_e)
            max_w = min(MAX_OPENING_WIDTH, usable * 0.98)
            width = max(MIN_OPENING_WIDTH, min(width, max_w))

            # Position: clamp so the opening fits at the current width.
            half_norm = (width / 2.0) / wl
            inset_s_norm = inset_s / wl
            inset_e_norm = inset_e / wl
            min_pos = inset_s_norm + half_norm + 0.005
            max_pos = 1.0 - inset_e_norm - half_norm - 0.005
            if min_pos > max_pos:
                min_pos = max_pos = (inset_s_norm + 1.0 - inset_e_norm) / 2.0
            position = max(min_pos, min(position, max_pos))

        try:
            op = sg.add_opening(
                wall_uuid,
                opening_type=self.opening_type,
                position=position,
                width=width,
                height=height,
                sill_height=sill,
            )
            self.target_opening_id = op.id
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        ensure_gn_modifier(obj)
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        from .. import populate_opening_items
        populate_opening_items(context.scene.floorplan, sg, wall_uuid)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj

        # Snapshot the target wall so redo always targets the same wall,
        # even if the user selects a different wall in between.
        settings = context.scene.floorplan
        wall_uuid = _selection.wall_id
        self.target_wall_id = wall_uuid
        # Reset so a fresh invocation never inherits the UUID from a previous
        # one (Blender's REGISTER flag carries last-used property values into
        # the next invocation for "Repeat Last" functionality).
        self.target_opening_id = ''

        # Reset numeric params to type-specific defaults on every fresh invocation.
        # Blender's REGISTER flag carries the last-used property values into the
        # next invocation; without this reset the second opening would inherit
        # whatever the user edited on the first one via the redo panel.
        if self.opening_type == 'WINDOW':
            self.width = DEFAULT_WINDOW_WIDTH
            self.height = DEFAULT_WINDOW_HEIGHT
            self.sill_height = DEFAULT_WINDOW_SILL
        else:
            self.width = DEFAULT_DOOR_WIDTH
            self.height = DEFAULT_DOOR_HEIGHT
            self.sill_height = 0.0
        self.position = 0.5

        # Cache wall dimensions and junction insets for check() clamping.
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
                    self.cached_inset_start = sg.junction_inset(wall.junction_start, wall_uuid)
                    self.cached_inset_end = sg.junction_inset(wall.junction_end, wall_uuid)

        # Seed prev_type so check() can detect a type switch in the redo panel.
        # Leaving it as '' causes check() to skip the default-application branch
        # on the first-ever invocation because '' satisfies the guard condition.
        self.prev_type = self.opening_type
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

        op_to_remove = sg.get_opening(self.opening_id)
        wall_uuid = op_to_remove.wall_id if op_to_remove else None
        if not sg.remove_opening(self.opening_id):
            self.report({'WARNING'}, "Opening not found")
            return {'CANCELLED'}

        ensure_gn_modifier(obj)
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        if wall_uuid:
            from .. import populate_opening_items
            populate_opening_items(context.scene.floorplan, sg, wall_uuid)
        else:
            context.scene.floorplan.opening_items.clear()
        context.area.tag_redraw()
        return {'FINISHED'}
