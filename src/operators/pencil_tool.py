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

from ..core.sync import sync_graph_to_mesh, _compute_wall_quad
from ..geometry.gn_setup import ensure_gn_modifier
from ..utils.constants import SNAP_JUNCTION_TOLERANCE


# Pencil Tool states
WAITING = "WAITING"
DRAWING = "DRAWING"

# Small outward expansion applied to the GPU preview wall geometry (metres).
# Prevents z-fighting between the preview triangles and the committed mesh faces.
_GPU_PREVIEW_EXPAND = 0.02

# Module-level state for the status bar draw function.
# None = operator not active; WAITING or DRAWING = operator active.
_pencil_state = None

# Viewport navigation events that must pass through while the modal is active.
# Everything else is consumed so that tool shortcuts (W, E, G, Z, Tab, …)
# cannot fire and interrupt the drawing session.
_NAVIGATION_EVENT_TYPES = frozenset({
    'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
    'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE',
    'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
    'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9',
    'NUMPAD_PERIOD', 'NUMPAD_PLUS', 'NUMPAD_MINUS', 'NUMPAD_SLASH',
    'TRACKPADPAN', 'TRACKPADZOOM',
})


def _draw_pencil_status(self, context):
    # Draw keyboard/mouse hints in the bottom status bar using Blender icons.
    if _pencil_state is None:
        from .. import find_floorplan_obj

        if find_floorplan_obj(context) is None:
            return

        layout = self.layout
        layout.label(text="", icon='MOUSE_LMB')
        layout.label(text=" Select Wall / Room")
        return

    layout = self.layout
    if _pencil_state == WAITING:
        layout.label(text="", icon='MOUSE_LMB')
        layout.label(text=" Place first junction")
        layout.separator()
        layout.label(text="", icon='EVENT_Z')
        layout.label(text=" Undo")
        layout.separator()
        layout.label(text="", icon='EVENT_RETURN')
        layout.label(text=" Confirm")
        layout.separator()
        layout.label(text="", icon='EVENT_ESC')
        layout.label(text=" Abort")
    else:  # DRAWING
        layout.label(text="", icon='MOUSE_LMB')
        layout.label(text=" Place next junction")
        layout.separator()
        layout.label(text="", icon='MOUSE_RMB')
        layout.label(text=" Cancel line")
        layout.separator()
        layout.label(text="", icon='EVENT_Z')
        layout.label(text=" Undo")
        layout.separator()
        layout.label(text="", icon='EVENT_RETURN')
        layout.label(text=" Confirm")
        layout.separator()
        layout.label(text="", icon='EVENT_ESC')
        layout.label(text=" Abort")


def _get_floorplan_obj(context):
    # Find or create the Floor Plan mesh object in the scene.
    # Blender auto-increments duplicate datablock names (Floor Plan.001, ...).
    for obj in context.scene.objects:
        if obj.get("is_floorplan"):
            return obj
    # Create new object.
    mesh = bpy.data.meshes.new("Floor Plan")
    obj = bpy.data.objects.new("Floor Plan", mesh)
    obj["is_floorplan"] = True
    context.scene.collection.objects.link(obj)
    return obj


class FLOORPLAN_OT_pencil_tool(bpy.types.Operator):
    bl_idname = "floorplan.pencil_tool"
    bl_label = "FloorPlan Pencil Tool"
    bl_description = "Draw walls by placing junctions. LMB place, RMB cancel line, Enter confirm, ESC abort"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        # Guard: refuse to start a second instance if already running.
        global _pencil_state
        if _pencil_state is not None:
            return {'CANCELLED'}

        self._state = WAITING
        self._start_junction_id = None
        self._mouse_pos = (0, 0)
        self._cursor_world = Vector((0, 0, 0))
        self._snapped_junction = None
        self._placed_walls = []
        self._placed_junctions = []
        self._wall_lines_existing = []
        self._wall_tris_new = []
        self._floor_tris_new = []
        self._junction_positions = []

        # Get or create the FloorPlan object and rebuild graphs from the current
        # mesh so that any previous undo restoring the mesh is the source of truth.
        from .. import reset_graphs_for_obj
        self._obj = _get_floorplan_obj(context)
        # Make the FloorPlan object the active selected object so that
        # find_floorplan_obj() returns it immediately when the tool exits and
        # the N-panel can show rooms without requiring a manual click.
        context.view_layer.objects.active = self._obj
        self._obj.select_set(True)
        self._sg, self._rg, self._id_mapper = reset_graphs_for_obj(self._obj)

        # Read defaults from scene settings.
        settings = context.scene.floorplan
        self._thickness = settings.default_thickness
        self._height = settings.default_height

        # Ensure GN modifier is attached with correct dimensions.
        ensure_gn_modifier(self._obj)

        # Register GPU draw layers via the overlay manager:
        #   POST_VIEW  — 3D world-space geometry (committed walls, preview line)
        #   POST_PIXEL — 2D screen-space UI (status text, snap circle)
        from ..ui import overlay_manager
        overlay_manager.register_layer(self._draw_3d_callback, '3D')
        overlay_manager.register_layer(self._draw_2d_callback, '2D')

        # Save current view so it can be restored when the tool exits.
        rv3d = context.region_data
        self._saved_view_matrix = rv3d.view_matrix.copy()
        self._saved_view_perspective = rv3d.view_perspective
        self._saved_view_distance = rv3d.view_distance
        self._saved_view_location = rv3d.view_location.copy()

        # Switch to top-down orthographic view for 2D floor plan drawing.
        bpy.ops.view3d.view_axis(type='TOP')
        context.region_data.view_perspective = 'ORTHO'

        # Highlight the WorkSpaceTool icon in the T-panel regardless of how
        # the operator was invoked (D shortcut or toolbar button click).
        bpy.ops.wm.tool_set_by_id(name="floorplan.pencil_workspace_tool")

        self._state = WAITING
        self._update_status_bar(context)
        # Suppress Blender's native WorkSpaceTool keymap hints ("LMB FloorPlan
        # Pencil Tool") while the modal is running.  Any non-None value hides
        # the native hints; our STATUSBAR_HT_header.prepend draws instead.
        context.workspace.status_text_set(" ")
        # Populate overlay geometry immediately so existing walls and junctions
        # are visible from the first frame (WAITING state included).
        self._rebuild_wall_batch()
        context.window_manager.modal_handler_add(self)
        self._apply_cursor(context)
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

        # ESC: abort the entire tool — remove all placed walls, no sync.
        if event.type == 'ESC' and event.value == 'PRESS':
            self._finish(context, confirm=False)
            return {'CANCELLED'}

        # Enter: confirm — sync placed walls to mesh and commit undo step.
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            self._finish(context, confirm=True)
            if self._placed_walls_count > 0:
                return {'FINISHED'}
            return {'CANCELLED'}

        # RMB (DRAWING only): cancel the current line, return to WAITING.
        # In WAITING: pass through so context menus still work.
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            if self._state == DRAWING:
                # Remove isolated start junction if we created it this session
                # and no wall connects to it (e.g. first click then immediate RMB).
                if (self._start_junction_id
                        and self._start_junction_id in self._placed_junctions
                        and not self._sg.get_walls_for_junction(self._start_junction_id)):
                    self._sg.remove_junction(self._start_junction_id)
                    self._placed_junctions.remove(self._start_junction_id)
                self._state = WAITING
                self._start_junction_id = None
                self._apply_cursor(context)
                self._rebuild_wall_batch()
                self._update_status_bar(context)
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        # Z: undo last placed wall.  Always consumed so it never reaches
        # Blender's viewport shading pie menu (which is also bound to Z).
        # Works in both DRAWING and WAITING (e.g. after ESC mid-sequence).
        if event.type == 'Z' and event.value == 'PRESS':
            self._undo_last_wall(context)
            return {'RUNNING_MODAL'}

        # LMB: place junction / confirm wall.
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._update_cursor_world(context)
            self._update_snap()

            if self._state == WAITING:
                self._place_start_junction(context)
                self._state = DRAWING
                self._apply_cursor(context)
                self._update_status_bar(context)
                return {'RUNNING_MODAL'}

            elif self._state == DRAWING:
                self._place_wall_and_advance(context)
                return {'RUNNING_MODAL'}

        # Only pass through viewport navigation events.  All other keyboard
        # shortcuts are consumed so that tools (W, E, G, Tab, …) cannot be
        # activated while the pencil session is active.
        if event.type in _NAVIGATION_EVENT_TYPES:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

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

        # Rebuild GPU wall preview from L1 data — no mesh sync during drawing.
        # Full sync is deferred to _finish() so Phase 1 runs only once per session.
        self._rebuild_wall_batch()

        # Advance: end junction becomes start of next wall.
        self._start_junction_id = end_id

    def _undo_last_wall(self, context):
        if not self._placed_walls:
            # No walls left; remove the dangling start junction if we created it.
            if (self._start_junction_id
                    and self._start_junction_id in self._placed_junctions):
                if not self._sg.get_walls_for_junction(self._start_junction_id):
                    self._sg.remove_junction(self._start_junction_id)
                    self._placed_junctions.remove(self._start_junction_id)
            self._state = WAITING
            self._start_junction_id = None
            self._apply_cursor(context)
            self._rebuild_wall_batch()
            return

        last_wall_id = self._placed_walls.pop()
        wall = self._sg.get_wall(last_wall_id)
        if wall is None:
            return

        prev_start = wall.junction_start
        self._sg.remove_wall(last_wall_id)

        # Remove orphaned end junction if it was created by us and has no walls.
        end_id = wall.junction_end
        if end_id in self._placed_junctions:
            if not self._sg.get_walls_for_junction(end_id):
                self._sg.remove_junction(end_id)
                self._placed_junctions.remove(end_id)

        # Rebuild GPU wall preview.
        self._rebuild_wall_batch()

        if self._placed_walls:
            # Revert start junction to end of previous wall.
            prev_wall = self._sg.get_wall(self._placed_walls[-1])
            if prev_wall:
                self._start_junction_id = prev_wall.junction_end
                self._state = DRAWING
            else:
                self._start_junction_id = None
                self._state = WAITING
        else:
            # Last wall removed; park cursor at its start junction.
            # A second Z press will hit the empty-walls branch above and remove it.
            self._start_junction_id = prev_start
            self._state = DRAWING
        self._apply_cursor(context)

    def _apply_cursor(self, context):
        # Set the viewport cursor to reflect the current drawing state.
        # PAINT_BRUSH = ready to start a new line (WAITING)
        # CROSSHAIR   = placing the endpoint of an in-progress line (DRAWING)
        if self._state == DRAWING:
            context.window.cursor_modal_set('CROSSHAIR')
        else:
            context.window.cursor_modal_set('PAINT_BRUSH')

    def _is_top_view(self, rv3d, threshold=0.05):
        # Return True if the viewport is currently in a top-down orthographic view.
        # Checks that the view matrix row 2 (camera Z-axis) aligns with world +Z.
        if rv3d.view_perspective != 'ORTHO':
            return False
        m = rv3d.view_matrix
        return (abs(m[2][0]) < threshold
                and abs(m[2][1]) < threshold
                and m[2][2] > (1.0 - threshold))

    def _finish(self, context, confirm=True):
        # Unregister this operator's GPU draw layers from the overlay manager.
        from ..ui import overlay_manager
        overlay_manager.unregister_layer(self._draw_3d_callback, '3D')
        overlay_manager.unregister_layer(self._draw_2d_callback, '2D')
        global _pencil_state
        _pencil_state = None

        # Restore the pre-tool view only when the user is still in the top-down
        # ortho view that the tool switched to.  If the user orbited away during
        # the session, keep whatever view they navigated to.
        rv3d = context.region_data
        if rv3d and hasattr(self, '_saved_view_matrix'):
            if self._is_top_view(rv3d):
                rv3d.view_perspective = self._saved_view_perspective
                rv3d.view_distance = self._saved_view_distance
                rv3d.view_location = self._saved_view_location
                rv3d.view_matrix = self._saved_view_matrix

        # Remember count for the return-value check in modal().
        self._placed_walls_count = len(self._placed_walls)

        if confirm and self._placed_walls:
            # Confirm path: sync L1 → mesh and commit a single undo step.
            sync_graph_to_mesh(self._obj, self._sg, self._rg, id_mapper=self._id_mapper)
            ensure_gn_modifier(self._obj)
            # Update the graph cache so N-panel sees the new rooms immediately.
            from .. import _graph_store
            _graph_store[self._obj.name] = (self._sg, self._rg, self._id_mapper)
            bpy.ops.ed.undo_push(message="Draw Walls")
        else:
            # Abort path: strip every wall and junction placed this session
            # from the graph so the mesh is not modified at all.
            for wall_id in list(self._placed_walls):
                try:
                    self._sg.remove_wall(wall_id)
                except Exception:
                    pass
            for jid in list(self._placed_junctions):
                try:
                    if not self._sg.get_walls_for_junction(jid):
                        self._sg.remove_junction(jid)
                except Exception:
                    pass
            self._placed_walls.clear()
            self._placed_junctions.clear()

        # Restore native WorkSpaceTool keymap hints.
        context.workspace.status_text_set(None)
        context.window.cursor_modal_restore()
        context.area.tag_redraw()
        
        # Tag all areas (including sidebar) for redraw to refresh N-panel rooms list.
        for area in context.screen.areas:
            area.tag_redraw()

    # -- GPU overlay draw callbacks --

    def _draw_3d_callback(self, context):
        # POST_VIEW: called with the viewport matrix active — coords are world space.
        self._draw_committed_walls_3d()
        if self._floor_tris_new:
            self._draw_new_floors_3d()
        if self._state == DRAWING and self._start_junction_id:
            self._draw_preview_line_3d(context)

    def _draw_2d_callback(self, context):
        # POST_PIXEL: 2D screen-space UI elements (junction dots, status text, snap circle).
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return
        self._draw_junctions_2d(context, region, rv3d)
        self._draw_status_text(context)
        if self._snapped_junction:
            self._draw_snap_indicator(context, region, rv3d)

    def _update_status_bar(self, context):
        # Update module-level state; the draw function registered at addon
        # load reads this variable and draws accordingly.
        # Calling status_text_set on every state transition forces Blender to
        # redraw the status bar (it is a window-level region, not a screen
        # area, so tag_redraw() on screen.areas cannot reach it).
        global _pencil_state
        _pencil_state = self._state
        context.workspace.status_text_set(" ")

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

    def _draw_preview_line_3d(self, context):
        # Draw the in-progress wall preview as a 3D line in world space.
        # POST_VIEW context: no location_3d_to_region_2d projection needed.
        start_j = self._sg.get_junction(self._start_junction_id)
        if start_j is None:
            return
        start_3d = (start_j.position[0], start_j.position[1], 0.0)
        end_3d = (self._cursor_world.x, self._cursor_world.y, 0.0)
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.line_width_set(2.0)
        gpu.state.blend_set('ALPHA')
        batch = batch_for_shader(shader, 'LINES', {"pos": [start_3d, end_3d]})
        shader.bind()
        shader.uniform_float("color", (0.3, 0.6, 1.0, 0.8))
        batch.draw(shader)
        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)

    def _rebuild_wall_batch(self):
        # Recompute GPU overlay data from L1 — pure Python, no bpy.
        # Existing walls (already have mesh geometry): black centerlines at Z=0.
        # New walls (this session, no mesh yet): blue 3D filled tris.
        # All junctions: yellow dot markers (projected to 2D in POST_PIXEL).
        walls = self._sg.get_all_walls()
        junctions_by_id = {j.id: j for j in self._sg.get_all_junctions()}
        new_ids = set(self._placed_walls)
        lines_existing = []
        tris_new = []
        eps = _GPU_PREVIEW_EXPAND
        for w in walls:
            js = junctions_by_id.get(w.junction_start)
            je = junctions_by_id.get(w.junction_end)
            if js is None or je is None:
                continue
            if w.id not in new_ids:
                # Black centerline — two endpoints at Z=0.
                lines_existing += [
                    (js.position[0], js.position[1], 0.0),
                    (je.position[0], je.position[1], 0.0),
                ]
            else:
                # Full 3D box preview for newly drawn walls.
                quad = _compute_wall_quad(w, junctions_by_id, self._sg)
                if not quad:
                    continue
                p0, p1, p2, p3 = quad
                h = w.height
                cx = (p0[0] + p1[0] + p2[0] + p3[0]) * 0.25
                cy = (p0[1] + p1[1] + p2[1] + p3[1]) * 0.25
                def _exp(p, _cx=cx, _cy=cy):
                    dx, dy = p[0] - _cx, p[1] - _cy
                    dist = (dx * dx + dy * dy) ** 0.5 or 1e-9
                    return (p[0] + dx / dist * eps, p[1] + dy / dist * eps)
                corners = [_exp(p) for p in (p0, p1, p2, p3)]
                b = [(c[0], c[1], -eps) for c in corners]
                t = [(c[0], c[1], h + eps) for c in corners]
                tris_new += [t[0], t[1], t[2], t[0], t[2], t[3]]
                for i in range(4):
                    j = (i + 1) % 4
                    tris_new += [b[i], b[j], t[j], b[i], t[j], t[i]]
        self._wall_lines_existing = lines_existing
        self._wall_tris_new = tris_new
        self._junction_positions = [j.position for j in junctions_by_id.values()]
        self._floor_tris_new = self._detect_new_floors(junctions_by_id, new_ids)

    def _detect_new_floors(self, junctions_by_id, new_ids):
        # Determine which room floor polygons are genuinely new this session.
        # "Before" set: rooms already committed in the room graph (populated at
        # invoke() time from the mesh — reliable and avoids a second cycle
        # detection pass over a temp graph with the same embedding bug).
        # "After" set: all cycles in the current structural graph (including
        # new walls), detected with minimum_cycle_basis — no outer-face issue.
        if not new_ids:
            return []

        # Rooms that existed before this drawing session.
        before_cycles = {frozenset(r.cycle) for r in self._rg.get_all_rooms()}

        # All cycles in the current graph (old + new walls).
        after_cycles = self._sg.detect_minimal_cycles()
        if not after_cycles:
            return []

        floor_tris = []
        z_floor = 0.001
        for cycle in after_cycles:
            # Skip rooms that already existed before this session.
            if frozenset(cycle) in before_cycles:
                continue
            pts = [junctions_by_id[jid].position
                   for jid in cycle if jid in junctions_by_id]
            if len(pts) < 3:
                continue
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            center = (cx, cy, z_floor)
            for i in range(len(pts)):
                nxt = (i + 1) % len(pts)
                floor_tris += [
                    center,
                    (pts[i][0], pts[i][1], z_floor),
                    (pts[nxt][0], pts[nxt][1], z_floor),
                ]
        return floor_tris
        # Draw detected room floors for new walls as semi-transparent blue.
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.face_culling_set('NONE')
        batch = batch_for_shader(shader, 'TRIS', {"pos": self._floor_tris_new})
        shader.bind()
        shader.uniform_float("color", (0.20, 0.45, 0.85, 0.30))
        batch.draw(shader)
        gpu.state.face_culling_set('NONE')
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('NONE')

    def _draw_new_floors_3d(self):
        # Draw detected room floors for new walls as semi-transparent blue.
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.face_culling_set('NONE')
        batch = batch_for_shader(shader, 'TRIS', {"pos": self._floor_tris_new})
        shader.bind()
        shader.uniform_float("color", (0.20, 0.45, 0.85, 0.30))
        batch.draw(shader)
        gpu.state.face_culling_set('NONE')
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('NONE')

    def _draw_committed_walls_3d(self):
        # Draw GPU overlay geometry in POST_VIEW (world space).
        # Existing walls: thin black centerlines, depth_test disabled so they
        # are always visible through the committed mesh geometry.
        # New walls: blue semi-transparent 3D boxes (no mesh yet).
        if not self._wall_lines_existing and not self._wall_tris_new:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        if self._wall_lines_existing:
            gpu.state.depth_test_set('NONE')
            gpu.state.line_width_set(1.5)
            batch = batch_for_shader(shader, 'LINES', {"pos": self._wall_lines_existing})
            shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
            batch.draw(shader)
            gpu.state.line_width_set(1.0)
            gpu.state.depth_test_set('NONE')
        if self._wall_tris_new:
            gpu.state.blend_set('ALPHA')
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.face_culling_set('NONE')
            batch = batch_for_shader(shader, 'TRIS', {"pos": self._wall_tris_new})
            shader.uniform_float("color", (0.25, 0.50, 0.90, 0.75))
            batch.draw(shader)
            gpu.state.face_culling_set('NONE')
            gpu.state.depth_test_set('NONE')
            gpu.state.blend_set('NONE')

    def _draw_junctions_2d(self, context, region, rv3d):
        # Draw all junctions as small filled yellow circles in screen space.
        if not self._junction_positions:
            return
        import math
        segments = 16
        radius = 5.0  # pixels
        tris = []
        for pos in self._junction_positions:
            p2d = view3d_utils.location_3d_to_region_2d(
                region, rv3d, Vector((pos[0], pos[1], 0.0))
            )
            if p2d is None:
                continue
            cx, cy = p2d
            for i in range(segments):
                a1 = 2 * math.pi * i / segments
                a2 = 2 * math.pi * (i + 1) / segments
                tris += [
                    (cx, cy),
                    (cx + radius * math.cos(a1), cy + radius * math.sin(a1)),
                    (cx + radius * math.cos(a2), cy + radius * math.sin(a2)),
                ]
        if not tris:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        batch = batch_for_shader(shader, 'TRIS', {"pos": tris})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.85, 0.1, 1.0))
        batch.draw(shader)
        gpu.state.blend_set('NONE')

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
