# FP1 — Pencil Tool (modal operator)
# State machine: WAITING -> DRAWING -> WAITING (loop)
# Snapping: junction snap (must-have, 15px tolerance)
# GPU overlay: preview line + status text (basic, needed for usability)
# References: 04_features_fp1.md, 05_ui_ux_toolbar.md, 05_ui_ux_shortcuts.md

import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector

from ..core.sync import sync_graph_to_mesh, sync_room_name_props
from ..geometry.gn_setup import ensure_gn_modifier
from ..utils.constants import SNAP_JUNCTION_TOLERANCE


# Pencil Tool states
WAITING = "WAITING"
DRAWING = "DRAWING"

# Module-level state for the status bar draw function.
# None = operator not active; WAITING or DRAWING = operator active.
_pencil_state = None


def _draw_pencil_status(self, context):
    # Draw keyboard/mouse hints in the bottom status bar using Blender icons.
    if _pencil_state is None:
        return
    layout = self.layout
    if _pencil_state == WAITING:
        layout.label(text="", icon='MOUSE_LMB')
        layout.label(text="Place first junction")
        layout.label(text="", icon='EVENT_Z')
        layout.label(text="Undo")
        layout.label(text="", icon='EVENT_ESC')
        layout.label(text="Exit tool")
    else:  # DRAWING
        layout.label(text="", icon='MOUSE_LMB')
        layout.label(text="Place junction")
        layout.label(text="", icon='EVENT_Z')
        layout.label(text="Undo")
        layout.label(text="", icon='EVENT_ESC')
        layout.label(text="Cancel line")


def _get_floorplan_obj(context):
    # Find or create the FloorPlanMaster mesh object in the scene.
    for obj in context.scene.objects:
        if obj.get("is_floorplan"):
            return obj
    # Create new object.
    mesh = bpy.data.meshes.new("FloorPlanMaster")
    obj = bpy.data.objects.new("FloorPlanMaster", mesh)
    obj["is_floorplan"] = True
    context.scene.collection.objects.link(obj)
    return obj


class FLOORPLAN_OT_pencil_tool(bpy.types.Operator):
    bl_idname = "floorplan.pencil_tool"
    bl_label = "FloorPlan Pencil Tool"
    bl_description = "Draw walls by placing junctions. LMB to place, Z to undo last, ESC to cancel"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self._state = WAITING
        self._start_junction_id = None
        self._mouse_pos = (0, 0)
        self._cursor_world = Vector((0, 0, 0))
        self._snapped_junction = None
        self._draw_handler = None
        self._placed_walls = []
        self._placed_junctions = []

        # Get or create the FloorPlan object and its graphs.
        from .. import get_graphs, get_id_mapper
        self._obj = _get_floorplan_obj(context)
        self._sg, self._rg = get_graphs(self._obj)
        self._id_mapper = get_id_mapper(self._obj)

        # Read defaults from scene settings.
        settings = context.scene.floorplan
        self._thickness = settings.default_thickness
        self._height = settings.default_height

        # Ensure GN modifier is attached with correct dimensions.
        ensure_gn_modifier(self._obj)

        # Register GPU draw handler for visual feedback.
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self._draw_callback, (context,), 'WINDOW', 'POST_PIXEL'
        )

        # Switch to top-down orthographic view for 2D floor plan drawing.
        bpy.ops.view3d.view_axis(type='TOP')
        context.region_data.view_perspective = 'ORTHO'

        # Highlight the WorkSpaceTool icon in the T-panel regardless of how
        # the operator was invoked (D shortcut or toolbar button click).
        bpy.ops.wm.tool_set_by_id(name="floorplan.pencil_workspace_tool")

        self._state = WAITING
        self._update_status_bar(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        # Update mouse position and snap calculation on every mouse move.
        if event.type == 'MOUSEMOVE':
            self._mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            self._update_cursor_world(context)
            self._update_snap()
            return {'RUNNING_MODAL'}

        # ESC: cancel current line or exit tool.
        if event.type == 'ESC' and event.value == 'PRESS':
            if self._state == DRAWING:
                self._state = WAITING
                self._start_junction_id = None
                self._update_status_bar(context)
                return {'RUNNING_MODAL'}
            else:
                self._finish(context)
                return {'CANCELLED'}

        # RMB passthrough for context menu.
        if event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        # Z: undo last placed point (only in DRAWING state).
        if event.type == 'Z' and event.value == 'PRESS' and self._state == DRAWING:
            self._undo_last_wall(context)
            return {'RUNNING_MODAL'}

        # LMB: place junction / confirm wall.
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._update_cursor_world(context)
            self._update_snap()

            if self._state == WAITING:
                self._place_start_junction(context)
                self._state = DRAWING
                self._update_status_bar(context)
                return {'RUNNING_MODAL'}

            elif self._state == DRAWING:
                self._place_wall_and_advance(context)
                return {'RUNNING_MODAL'}

        # Pass through unhandled events so viewport navigation works.
        return {'PASS_THROUGH'}

    def _update_cursor_world(self, context):
        # Convert mouse 2D position to 3D world position on the XY plane (Z=0).
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        coord = (self._mouse_pos[0], self._mouse_pos[1])
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)

        # Intersect with Z=0 plane.
        if abs(direction.z) < 1e-8:
            return
        t = -origin.z / direction.z
        self._cursor_world = origin + direction * t

    def _update_snap(self):
        # Check if cursor is near an existing junction (must-have snap).
        self._snapped_junction = None
        pos = (self._cursor_world.x, self._cursor_world.y)
        nearby = self._sg.find_junctions_near(pos, radius=self._snap_world_radius())
        if nearby:
            self._snapped_junction = nearby[0][0]

    def _snap_world_radius(self):
        # Convert pixel tolerance to approximate world-space radius.
        # Rough approximation; sufficient for usability.
        return 0.3

    def _get_placement_pos(self):
        # Return world position for placement (snapped or raw cursor).
        if self._snapped_junction:
            return self._snapped_junction.position
        return (self._cursor_world.x, self._cursor_world.y)

    def _place_start_junction(self, context):
        pos = self._get_placement_pos()
        if self._snapped_junction:
            self._start_junction_id = self._snapped_junction.id
        else:
            j = self._sg.add_junction(pos)
            self._start_junction_id = j.id
            self._placed_junctions.append(j.id)

    def _place_wall_and_advance(self, context):
        pos = self._get_placement_pos()

        # Determine end junction (snap or create new).
        if self._snapped_junction:
            end_id = self._snapped_junction.id
        else:
            try:
                j = self._sg.add_junction(pos)
                end_id = j.id
                self._placed_junctions.append(j.id)
            except Exception:
                # Junction already exists at this position.
                nearby = self._sg.find_junctions_near(pos, radius=0.001)
                if nearby:
                    end_id = nearby[0][0].id
                else:
                    return

        # Avoid self-loop.
        if end_id == self._start_junction_id:
            return

        # Avoid duplicate wall.
        existing = self._sg.get_wall_between(self._start_junction_id, end_id)
        if existing:
            # Just advance the start junction to the clicked position.
            self._start_junction_id = end_id
            return

        try:
            w = self._sg.add_wall(
                self._start_junction_id, end_id,
                thickness=self._thickness,
                height=self._height,
            )
            self._placed_walls.append(w.id)
        except Exception:
            return

        # Sync L2 + L3.
        self._rg.sync_from_structural_graph()
        sync_graph_to_mesh(self._obj, self._sg, self._rg, id_mapper=self._id_mapper)
        sync_room_name_props(self._obj, self._rg)

        # Re-apply modifier inputs after mesh rebuild so GN dimensions are correct.
        ensure_gn_modifier(self._obj)

        # Advance: end junction becomes start of next wall.
        self._start_junction_id = end_id

    def _undo_last_wall(self, context):
        if not self._placed_walls:
            self._state = WAITING
            self._start_junction_id = None
            return

        last_wall_id = self._placed_walls.pop()
        wall = self._sg.get_wall(last_wall_id)
        if wall is None:
            return

        # The start junction becomes the start of the removed wall.
        prev_start = wall.junction_start

        self._sg.remove_wall(last_wall_id)

        # Remove orphaned end junction if it was created by us and has no walls.
        end_id = wall.junction_end
        if end_id in self._placed_junctions:
            walls_for_end = self._sg.get_walls_for_junction(end_id)
            if not walls_for_end:
                self._sg.remove_junction(end_id)
                self._placed_junctions.remove(end_id)

        # Sync.
        self._rg.sync_from_structural_graph()
        sync_graph_to_mesh(self._obj, self._sg, self._rg, id_mapper=self._id_mapper)
        sync_room_name_props(self._obj, self._rg)

        if self._placed_walls:
            # Revert start junction to end of previous wall.
            prev_wall = self._sg.get_wall(self._placed_walls[-1])
            if prev_wall:
                self._start_junction_id = prev_wall.junction_end
            else:
                self._start_junction_id = None
                self._state = WAITING
        else:
            self._start_junction_id = prev_start
            if self._start_junction_id:
                # Still have a starting point, stay in DRAWING.
                pass
            else:
                self._state = WAITING

    def _finish(self, context):
        # Remove GPU handler and clean up.
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None
        global _pencil_state
        _pencil_state = None
        context.area.tag_redraw()

    # -- GPU overlay draw callback --
    def _draw_callback(self, context):
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        # Draw status text.
        self._draw_status_text(context)

        # Draw snap indicator.
        if self._snapped_junction:
            self._draw_snap_indicator(context, region, rv3d)

        # Draw preview line from start junction to cursor.
        if self._state == DRAWING and self._start_junction_id:
            self._draw_preview_line(context, region, rv3d)

    def _update_status_bar(self, context):
        # Update module-level state; the draw function registered at addon
        # load reads this variable and draws accordingly.
        global _pencil_state
        _pencil_state = self._state

    def _draw_status_text(self, context):
        font_id = 0
        blf.size(font_id, 16)
        blf.color(font_id, 1.0, 1.0, 1.0, 0.8)

        if self._state == WAITING:
            blf.position(font_id, 20, 40, 0)
            blf.draw(font_id, "FloorPlan Pencil — Waiting for input")
        else:
            # Show live wall length and angle while drawing.
            if self._start_junction_id:
                start_j = self._sg.get_junction(self._start_junction_id)
                if start_j:
                    import math
                    dx = self._cursor_world.x - start_j.position[0]
                    dy = self._cursor_world.y - start_j.position[1]
                    length = math.hypot(dx, dy)
                    angle = math.degrees(math.atan2(dy, dx))
                    blf.color(font_id, 0.7, 0.9, 1.0, 0.9)
                    blf.position(font_id, 20, 40, 0)
                    blf.draw(font_id, f"FloorPlan Pencil — Length: {length:.2f} m   Angle: {angle:.1f}°")

    def _draw_preview_line(self, context, region, rv3d):
        start_j = self._sg.get_junction(self._start_junction_id)
        if start_j is None:
            return

        # Convert 3D positions to 2D screen coords.
        start_3d = Vector((start_j.position[0], start_j.position[1], 0.0))
        end_3d = self._cursor_world.copy()
        end_3d.z = 0.0

        start_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, start_3d)
        end_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, end_3d)

        if start_2d is None or end_2d is None:
            return

        # Draw line in screen space — blue for preview (design spec).
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.line_width_set(2.0)
        gpu.state.blend_set('ALPHA')
        batch = batch_for_shader(
            shader, 'LINES',
            {"pos": [start_2d, end_2d]}
        )
        shader.bind()
        shader.uniform_float("color", (0.3, 0.6, 1.0, 0.8))
        batch.draw(shader)
        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)

    def _draw_snap_indicator(self, context, region, rv3d):
        # Yellow circle at snapped junction position.
        j = self._snapped_junction
        pos_3d = Vector((j.position[0], j.position[1], 0.0))
        pos_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, pos_3d)
        if pos_2d is None:
            return

        import math
        segments = 24
        radius = 8.0  # pixels
        verts = []
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * (i + 1) / segments
            verts.append((pos_2d[0] + radius * math.cos(a1),
                          pos_2d[1] + radius * math.sin(a1)))
            verts.append((pos_2d[0] + radius * math.cos(a2),
                          pos_2d[1] + radius * math.sin(a2)))

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.line_width_set(2.0)
        gpu.state.blend_set('ALPHA')
        batch = batch_for_shader(shader, 'LINES', {"pos": verts})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.9, 0.2, 0.9))
        batch.draw(shader)
        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)


# WorkspaceTool registration for Toolbar (05_ui_ux_toolbar.md).
class FLOORPLAN_WT_pencil(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "floorplan.pencil_workspace_tool"
    bl_label = "FloorPlan Pencil"
    bl_description = "Draw floor plan walls by placing junctions"
    bl_icon = "ops.gpencil.draw.line"
    bl_widget = None
    bl_keymap = (
        (
            "floorplan.pencil_tool",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            None,
        ),
    )


def register_pencil_keymap():
    # Register D shortcut to invoke the operator directly so the tool activates
    # immediately (top view + WAITING state) without a redundant first LMB click.
    # invoke() calls tool_set_by_id internally to keep the T-panel in sync.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("floorplan.pencil_tool", type='D', value='PRESS')
    return km, kmi


def unregister_pencil_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.get('3D View')
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == "floorplan.pencil_tool":
                km.keymap_items.remove(kmi)
                break
