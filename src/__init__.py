bl_info = {
    "name": "FloorPlanMaster",
    "author": "wladaosk",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > FloorPlanMaster",
    "description": "Interactive floor plan creation with parametric walls and automatic room detection",
    "category": "3D View",
}

# Ensure bundled wheels are importable.
# .whl files are zip archives — Python can import from them directly via sys.path.
# This is a fallback for development (VS Code Blender extension) where Blender
# does not run the Extensions install pipeline that would handle blender_manifest.toml.
import sys
import os

_wheels_dir = os.path.join(os.path.dirname(__file__), "wheels")
if os.path.isdir(_wheels_dir):
    for _whl in os.listdir(_wheels_dir):
        if _whl.endswith(".whl"):
            _whl_path = os.path.join(_wheels_dir, _whl)
            if _whl_path not in sys.path:
                sys.path.insert(0, _whl_path)

# Guard bpy imports so pytest can load core/ and utils/ without Blender.
try:
    import bpy
    _HAS_BPY = True
except ImportError:
    _HAS_BPY = False

from .core.structural_graph import StructuralGraph
from .core.room_graph import RoomGraph


# Per-object graph storage: obj.name -> (StructuralGraph, RoomGraph, IdMapper)
_graph_store = {}

# Handle for the persistent wall-selection highlight draw handler (POST_VIEW).
_selection_draw_handle = None


def get_graphs(obj):
    # Return (StructuralGraph, RoomGraph) for a FloorPlanMaster object.
    # Reconstructs from persisted JSON if not yet in the cache.
    if obj.name not in _graph_store:
        reset_graphs_for_obj(obj)
    sg, rg, _ = _graph_store[obj.name]
    return sg, rg


def get_id_mapper(obj):
    # Return the persistent IdMapper for a FloorPlanMaster object.
    # Ensures the same UUID->int assignments survive across sync calls.
    if obj.name not in _graph_store:
        reset_graphs_for_obj(obj)
    return _graph_store[obj.name][2]


def reset_graphs_for_obj(obj):
    # Rebuild Python graphs from the current mesh state and store them.
    # Must be called at the start of any operator with REGISTER|UNDO before
    # mutating graphs, so that Blender's undo-restored mesh is the source of
    # truth and re-execution after undo does not create duplicates.
    #
    # Room detection runs immediately after reconstruction so the graph is
    # fully consistent without needing a subsequent sync_graph_to_mesh() call
    # (e.g. after addon reload or file load).
    from .core.sync import reconstruct_graphs_from_mesh
    sg, rg, mapper = reconstruct_graphs_from_mesh(obj)
    if rg is None:
        rg = RoomGraph(sg)
    if sg.get_all_walls():
        rg.sync_from_structural_graph()
    _graph_store[obj.name] = (sg, rg, mapper)
    return sg, rg, mapper


def remove_graphs(obj):
    _graph_store.pop(obj.name, None)


def clear_graph_store():
    _graph_store.clear()


def find_floorplan_obj(context):
    # Find the existing FloorPlanMaster object in the scene.
    # Returns None if no floorplan object exists (does NOT create one).
    for obj in context.scene.objects:
        if obj.get("is_floorplan"):
            return obj
    return None


if _HAS_BPY:
    import gpu
    import math
    from gpu_extras.batch import batch_for_shader
    from mathutils import Vector
    from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, StringProperty, PointerProperty
    from .core.sync import sync_graph_to_mesh

    # Update callback guard — prevents recursive sync when the select operator
    # populates the props (which triggers the update callback).
    _updating_wall_props = False

    def _on_wall_thickness_update(self, context):
        global _updating_wall_props
        if _updating_wall_props:
            return
        wall_uuid = self.active_wall_id
        if not wall_uuid:
            return
        obj = find_floorplan_obj(context)
        if obj is None:
            return
        if obj.name not in _graph_store:
            reset_graphs_for_obj(obj)
        sg, rg, mapper = _graph_store[obj.name]
        wall = sg.get_wall(wall_uuid)
        if wall is None:
            return
        new_val = self.active_wall_thickness
        if abs(wall.thickness - new_val) < 1e-7:
            return
        try:
            sg.update_wall(wall_uuid, thickness=new_val)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)

    def _on_wall_height_update(self, context):
        global _updating_wall_props
        if _updating_wall_props:
            return
        wall_uuid = self.active_wall_id
        if not wall_uuid:
            return
        obj = find_floorplan_obj(context)
        if obj is None:
            return
        if obj.name not in _graph_store:
            reset_graphs_for_obj(obj)
        sg, rg, mapper = _graph_store[obj.name]
        wall = sg.get_wall(wall_uuid)
        if wall is None:
            return
        new_val = self.active_wall_height
        if abs(wall.height - new_val) < 1e-7:
            return
        try:
            sg.update_wall(wall_uuid, height=new_val)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)

    # Opening constants — used by OpeningItem PropertyGroup and its callbacks.
    from .utils.constants import (
        DEFAULT_DOOR_WIDTH, DEFAULT_WINDOW_WIDTH,
        DEFAULT_DOOR_HEIGHT, DEFAULT_WINDOW_HEIGHT,
        DEFAULT_WINDOW_SILL,
        MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
        MIN_OPENING_HEIGHT, MAX_HEIGHT,
    )

    # Guard — prevents opening item callbacks from firing during collection population.
    _updating_opening_items = False

    def _on_opening_type_update(self, context):
        global _updating_opening_items
        if _updating_opening_items:
            return
        _updating_opening_items = True
        try:
            if self.opening_type == 'WINDOW':
                self.sill_height = DEFAULT_WINDOW_SILL
                self.width = DEFAULT_WINDOW_WIDTH
                self.height = DEFAULT_WINDOW_HEIGHT
            else:
                self.sill_height = 0.0
                self.width = DEFAULT_DOOR_WIDTH
                self.height = DEFAULT_DOOR_HEIGHT
        finally:
            _updating_opening_items = False
        opening_id = self.opening_id
        if not opening_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, mapper = _graph_store[obj.name]
        try:
            sg.update_opening(
                opening_id,
                opening_type=self.opening_type,
                width=self.width,
                height=self.height,
                sill_height=self.sill_height,
            )
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()

    def _on_opening_width_update(self, context):
        global _updating_opening_items
        if _updating_opening_items:
            return
        opening_id = self.opening_id
        if not opening_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, mapper = _graph_store[obj.name]
        op = sg.get_opening(opening_id)
        if op is None:
            return
        w = sg.get_wall(op.wall_id)
        if w is None:
            return
        wl = sg.wall_length(op.wall_id)
        inset_s = sg.junction_inset(w.junction_start, op.wall_id)
        inset_e = sg.junction_inset(w.junction_end, op.wall_id)
        usable = max(MIN_OPENING_WIDTH, wl - inset_s - inset_e)
        max_w = min(MAX_OPENING_WIDTH, usable * 0.98)
        clamped = max(MIN_OPENING_WIDTH, min(self.width, max_w))
        if abs(clamped - self.width) > 1e-7:
            _updating_opening_items = True
            self.width = clamped
            _updating_opening_items = False
        try:
            sg.update_opening(opening_id, width=clamped)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()

    def _on_opening_height_update(self, context):
        global _updating_opening_items
        if _updating_opening_items:
            return
        opening_id = self.opening_id
        if not opening_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, mapper = _graph_store[obj.name]
        op = sg.get_opening(opening_id)
        if op is None:
            return
        w = sg.get_wall(op.wall_id)
        if w is None:
            return
        max_h = max(MIN_OPENING_HEIGHT, w.height - op.sill_height)
        clamped = max(MIN_OPENING_HEIGHT, min(self.height, max_h))
        if abs(clamped - self.height) > 1e-7:
            _updating_opening_items = True
            self.height = clamped
            _updating_opening_items = False
        try:
            sg.update_opening(opening_id, height=clamped)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()

    def _on_opening_sill_update(self, context):
        global _updating_opening_items
        if _updating_opening_items:
            return
        opening_id = self.opening_id
        if not opening_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, mapper = _graph_store[obj.name]
        op = sg.get_opening(opening_id)
        if op is None:
            return
        w = sg.get_wall(op.wall_id)
        if w is None:
            return
        max_sill = max(0.0, w.height - op.height)
        clamped = max(0.0, min(self.sill_height, max_sill))
        if abs(clamped - self.sill_height) > 1e-7:
            _updating_opening_items = True
            self.sill_height = clamped
            _updating_opening_items = False
        try:
            sg.update_opening(opening_id, sill_height=clamped)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()

    def _on_opening_position_update(self, context):
        global _updating_opening_items
        if _updating_opening_items:
            return
        opening_id = self.opening_id
        if not opening_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, mapper = _graph_store[obj.name]
        op = sg.get_opening(opening_id)
        if op is None:
            return
        w = sg.get_wall(op.wall_id)
        if w is None:
            return
        wl = sg.wall_length(op.wall_id)
        inset_s = sg.junction_inset(w.junction_start, op.wall_id)
        inset_e = sg.junction_inset(w.junction_end, op.wall_id)
        if wl >= MIN_OPENING_WIDTH:
            half_norm = (op.width / 2.0) / wl
            inset_s_norm = inset_s / wl
            inset_e_norm = inset_e / wl
            min_pos = inset_s_norm + half_norm + 0.005
            max_pos = 1.0 - inset_e_norm - half_norm - 0.005
            if min_pos > max_pos:
                min_pos = max_pos = (inset_s_norm + 1.0 - inset_e_norm) / 2.0
            clamped = max(min_pos, min(self.position, max_pos))
        else:
            clamped = self.position
        if abs(clamped - self.position) > 1e-7:
            _updating_opening_items = True
            self.position = clamped
            _updating_opening_items = False
        try:
            sg.update_opening(opening_id, position=clamped)
        except Exception:
            return
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        context.area.tag_redraw()

    class OpeningItem(bpy.types.PropertyGroup):
        # Per-opening editable item in the N-panel opening list.
        # Mirrors Opening dataclass fields with identical validation via update callbacks.
        opening_id: StringProperty(options={'HIDDEN'})
        expanded: BoolProperty(default=False)
        opening_type: EnumProperty(
            name="Type",
            items=[
                ('DOOR', "Door", "Door opening from the floor"),
                ('WINDOW', "Window", "Window opening with sill height"),
            ],
            default='DOOR',
            update=_on_opening_type_update,
        )
        width: FloatProperty(
            name="Width",
            min=MIN_OPENING_WIDTH,
            max=MAX_OPENING_WIDTH,
            precision=3,
            unit='LENGTH',
            update=_on_opening_width_update,
        )
        height: FloatProperty(
            name="Height",
            min=MIN_OPENING_HEIGHT,
            max=MAX_HEIGHT,
            precision=3,
            unit='LENGTH',
            update=_on_opening_height_update,
        )
        sill_height: FloatProperty(
            name="Sill Height",
            min=0.0,
            max=MAX_HEIGHT,
            precision=3,
            unit='LENGTH',
            update=_on_opening_sill_update,
        )
        position: FloatProperty(
            name="Position",
            description="Relative position along wall (0 = start, 1 = end)",
            min=0.01,
            max=0.99,
            precision=3,
            update=_on_opening_position_update,
        )

    # Scene-level addon settings (PropertyGroup on Scene)
    class FloorPlanSettings(bpy.types.PropertyGroup):
        default_thickness: FloatProperty(
            name="Default Wall Thickness",
            description="Default wall thickness for new walls (meters)",
            default=0.3,
            min=0.05,
            max=1.0,
            precision=3,
            unit='LENGTH',
        )
        default_height: FloatProperty(
            name="Default Wall Height",
            description="Default wall height for new walls (meters)",
            default=2.5,
            min=1.0,
            max=10.0,
            precision=2,
            unit='LENGTH',
        )

        # Active wall selection — populated by FLOORPLAN_OT_select_wall.
        active_wall_id: StringProperty(
            name="Active Wall ID",
            description="UUID of the currently selected wall (empty = none)",
            default="",
        )
        active_wall_thickness: FloatProperty(
            name="Wall Thickness",
            description="Thickness of the selected wall (meters)",
            default=0.3,
            min=0.05,
            max=1.0,
            precision=3,
            unit='LENGTH',
            update=_on_wall_thickness_update,
        )
        active_wall_height: FloatProperty(
            name="Wall Height",
            description="Height of the selected wall (meters)",
            default=2.5,
            min=1.0,
            max=10.0,
            precision=2,
            unit='LENGTH',
            update=_on_wall_height_update,
        )
        opening_items: CollectionProperty(
            name="Opening Items",
            type=OpeningItem,
        )
        openings_expanded: BoolProperty(
            name="Openings",
            default=False,
        )

    def populate_opening_items(settings, sg, wall_uuid):
        # Repopulate settings.opening_items from the graph for the given wall.
        # Called after wall selection, opening add, and opening remove so the
        # N-panel always shows current values without a manual refresh.
        global _updating_opening_items
        _updating_opening_items = True
        settings.opening_items.clear()
        for op in sg.get_openings_for_wall(wall_uuid):
            item = settings.opening_items.add()
            item.opening_id = op.id
            item.opening_type = op.opening_type
            item.width = op.width
            item.height = op.height
            item.sill_height = op.sill_height
            item.position = op.position
        _updating_opening_items = False

    def _draw_wall_selection():
        # Persistent POST_VIEW draw handler — draws a semi-transparent orange
        # box over the currently selected wall using UNIFORM_COLOR + TRIS.
        # Box is a simple OBB from junction-to-junction axis + wall.thickness;
        # does not depend on the mitered mesh geometry.
        # Registered at addon load; reads active_wall_id from FloorPlanSettings.
        context = bpy.context
        if not context or not getattr(context, 'scene', None):
            return
        settings = getattr(context.scene, 'floorplan', None)
        if not settings or not settings.active_wall_id:
            return
        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return
        sg, _rg, _ = _graph_store[obj.name]
        wall = sg.get_wall(settings.active_wall_id)
        if wall is None:
            return
        j1 = sg.get_junction(wall.junction_start)
        j2 = sg.get_junction(wall.junction_end)
        if j1 is None or j2 is None:
            return
        ax, ay = j1.position
        bx, by = j2.position
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            return
        # Unit direction along the wall and perpendicular.
        dx, dy = (bx - ax) / length, (by - ay) / length
        nx, ny = -dy, dx
        EXPAND = 0.03  # metres — extra clearance on top of neighbour insets
        hw = wall.thickness / 2.0 + EXPAND
        h = wall.height
        # Extend each end by the max half-thickness of walls connecting there
        # so the selection box covers the joint area at both junctions.
        all_walls = sg.get_all_walls()
        def _max_half_t(junction_id):
            return max(
                (w.thickness / 2.0 for w in all_walls
                 if w.id != wall.id and junction_id in (w.junction_start, w.junction_end)),
                default=0.0,
            )
        start_ext = _max_half_t(j1.id) + EXPAND
        end_ext   = _max_half_t(j2.id) + EXPAND
        # 4 base corners: start and end extended along the wall axis.
        s0x, s0y = ax - dx * start_ext, ay - dy * start_ext
        e0x, e0y = bx + dx * end_ext,   by + dy * end_ext
        b0 = Vector((s0x + nx * hw, s0y + ny * hw, -EXPAND))
        b1 = Vector((e0x + nx * hw, e0y + ny * hw, -EXPAND))
        b2 = Vector((e0x - nx * hw, e0y - ny * hw, -EXPAND))
        b3 = Vector((s0x - nx * hw, s0y - ny * hw, -EXPAND))
        b = [b0, b1, b2, b3]
        t = [Vector((v.x, v.y, h + EXPAND)) for v in b]
        # 6 faces x 2 triangles = 12 tris; both sides rendered (no culling).
        tris = []
        # Bottom
        tris += [b[0], b[1], b[2],  b[0], b[2], b[3]]
        # Top
        tris += [t[0], t[2], t[1],  t[0], t[3], t[2]]
        # Sides
        for i in range(4):
            n = (i + 1) % 4
            tris += [b[i], b[n], t[n],  b[i], t[n], t[i]]
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.face_culling_set('NONE')
        batch = batch_for_shader(shader, 'TRIS', {"pos": tris})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.55, 0.1, 0.25))
        batch.draw(shader)
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('NONE')

    from .operators import get_classes as get_operator_classes
    from .operators.pencil_tool import (
        FLOORPLAN_WT_pencil,
        register_pencil_keymap,
        unregister_pencil_keymap,
        _draw_pencil_status,
    )
    from .operators.select_wall import (
        register_select_keymap,
        unregister_select_keymap,
    )
    from .ui import get_classes as get_ui_classes

    def _rebuild_graph_store():
        # Repopulate _graph_store from any floorplan objects already in the scene.
        # Called on addon register() (covers in-session F8 reload) and from
        # _load_post_handler (covers file load).  After reconstruction the room
        # graph is explicitly synced so the N-panel can show rooms immediately.
        try:
            scenes = bpy.data.scenes
        except Exception:
            return
        seen = set()
        for scene in scenes:
            for obj in scene.objects:
                if obj.get("is_floorplan") and obj.name not in seen:
                    seen.add(obj.name)
                    reset_graphs_for_obj(obj)

    @bpy.app.handlers.persistent
    def _load_post_handler(dummy):
        _rebuild_graph_store()

    _addon_classes = [
        OpeningItem,
        FloorPlanSettings,
    ]

    def register():
        for cls in _addon_classes:
            bpy.utils.register_class(cls)

        for cls in get_operator_classes():
            bpy.utils.register_class(cls)
        for cls in get_ui_classes():
            bpy.utils.register_class(cls)

        bpy.types.Scene.floorplan = PointerProperty(type=FloorPlanSettings)

        bpy.utils.register_tool(FLOORPLAN_WT_pencil)
        register_pencil_keymap()
        register_select_keymap()
        bpy.types.STATUSBAR_HT_header.prepend(_draw_pencil_status)

        global _selection_draw_handle
        _selection_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_wall_selection, (), 'WINDOW', 'POST_VIEW'
        )

        bpy.app.handlers.load_post.append(_load_post_handler)
        _rebuild_graph_store()

    def unregister():
        if _load_post_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_load_post_handler)

        global _selection_draw_handle
        if _selection_draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_selection_draw_handle, 'WINDOW')
            _selection_draw_handle = None

        bpy.types.STATUSBAR_HT_header.remove(_draw_pencil_status)
        unregister_pencil_keymap()
        unregister_select_keymap()
        bpy.utils.unregister_tool(FLOORPLAN_WT_pencil)

        del bpy.types.Scene.floorplan

        for cls in reversed(get_ui_classes()):
            bpy.utils.unregister_class(cls)
        for cls in reversed(get_operator_classes()):
            bpy.utils.unregister_class(cls)

        for cls in reversed(_addon_classes):
            bpy.utils.unregister_class(cls)

        clear_graph_store()
