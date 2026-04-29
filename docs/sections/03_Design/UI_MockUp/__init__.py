bl_info = {
    "name": "FloorPlanMaster UI MockUp",
    "author": "wladaosk",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > FloorPlanMaster",
    "description": "Interactive UI mockup for FloorPlanMaster addon design (no functionality)",
    "category": "3D View",
}

import bpy
import blf
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)


# Persistent HUD draw handler reference
_hud_draw_handle = None
_room_highlight_handle = None


def _draw_room_highlight():
    import math as _math
    context = bpy.context
    if not context or not getattr(context, 'scene', None):
        return
    settings = getattr(context.scene, 'mockup_fp', None)
    if settings is None or settings.selected_room_index < 0:
        return
    idx = settings.selected_room_index
    if idx >= len(settings.rooms):
        return
    room = settings.rooms[idx]

    rv3d = getattr(context, 'region_data', None)
    region = getattr(context, 'region', None)
    if rv3d is None or region is None:
        return

    from bpy_extras.view3d_utils import location_3d_to_region_2d
    from mathutils import Vector

    cx, cy = room.mock_cx, room.mock_cy
    hw, hd = room.mock_hw, room.mock_hd
    corners_3d = [
        Vector((cx - hw, cy - hd, 0.0)),
        Vector((cx + hw, cy - hd, 0.0)),
        Vector((cx + hw, cy + hd, 0.0)),
        Vector((cx - hw, cy + hd, 0.0)),
    ]
    corners_2d = [location_3d_to_region_2d(region, rv3d, v) for v in corners_3d]
    if any(c is None for c in corners_2d):
        return

    import gpu
    from gpu_extras.batch import batch_for_shader

    tris = [
        corners_2d[0], corners_2d[1], corners_2d[2],
        corners_2d[0], corners_2d[2], corners_2d[3],
    ]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    batch = batch_for_shader(shader, 'TRIS', {"pos": [(v.x, v.y) for v in tris]})
    shader.bind()
    shader.uniform_float("color", (1.0, 0.55, 0.1, 0.18))
    batch.draw(shader)

    # Outline
    loop = corners_2d + [corners_2d[0]]
    lines = []
    for i in range(len(loop) - 1):
        lines += [(loop[i].x, loop[i].y), (loop[i+1].x, loop[i+1].y)]
    gpu.state.line_width_set(2.0)
    batch_lines = batch_for_shader(shader, 'LINES', {"pos": lines})
    shader.uniform_float("color", (1.0, 0.55, 0.1, 0.85))
    batch_lines.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


# Dimension overlay ---------------------------------------------------------

_dimension_draw_handle = None
_gizmo_draw_handle = None

# Static floor plan: list of (start_xyz, end_xyz) wall segments.
# Layout (metres, Z=0 plane):
#   Living Room: (0,0)-(6,5)   30 m²
#   Kitchen:     (6,0)-(10,5)  20 m²
#   Bedroom:     (0,5)-(6,9)   24 m²
_DEMO_WALLS = [
    ((0, 0, 0),  (6, 0, 0)),   # outer bottom-left   6.0 m
    ((6, 0, 0),  (10, 0, 0)),  # outer bottom-right  4.0 m
    ((10, 0, 0), (10, 5, 0)),  # outer right          5.0 m
    ((10, 5, 0), (6, 5, 0)),   # top kitchen          4.0 m
    ((6, 5, 0),  (6, 9, 0)),   # outer right bedroom  4.0 m
    ((6, 9, 0),  (0, 9, 0)),   # top bedroom          6.0 m
    ((0, 9, 0),  (0, 0, 0)),   # outer left           9.0 m
    ((6, 0, 0),  (6, 5, 0)),   # interior LR/Kitchen  5.0 m
    ((0, 5, 0),  (6, 5, 0)),   # interior LR/Bedroom  6.0 m
]

_DEMO_ROOMS = [
    {"name": "Living Room", "area": 30.0, "cx": 3.0, "cy": 2.5},
    {"name": "Kitchen",     "area": 20.0, "cx": 8.0, "cy": 2.5},
    {"name": "Bedroom",     "area": 24.0, "cx": 3.0, "cy": 7.0},
]


def _format_length(meters, unit):
    if unit == 'CM': return f"{meters * 100:.1f} cm"
    if unit == 'MM': return f"{meters * 1000:.0f} mm"
    if unit == 'FT': return f"{meters * 3.28084:.2f} ft"
    if unit == 'IN': return f"{meters * 39.3701:.1f}\""
    return f"{meters:.2f} m"


def _create_demo_mesh():
    """Create a static wireframe floor plan mesh in the scene (runs from timer)."""
    name = "FloorPlan_Demo"
    if name in bpy.data.objects:
        return

    verts_dict = {}
    verts_list = []
    edges_list = []

    def _vidx(co):
        key = (round(co[0], 4), round(co[1], 4), round(co[2], 4))
        if key not in verts_dict:
            verts_dict[key] = len(verts_list)
            verts_list.append(co)
        return verts_dict[key]

    for (a, b) in _DEMO_WALLS:
        edges_list.append((_vidx(a), _vidx(b)))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts_list, edges_list, [])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    obj.display_type = 'WIRE'
    for scene in bpy.data.scenes:
        scene.collection.objects.link(obj)


def _draw_dimensions():
    """POST_PIXEL handler: draw wall lengths and room labels on the Z=0 floor plan."""
    context = bpy.context
    if not context or not getattr(context, 'scene', None):
        return
    settings = getattr(context.scene, 'mockup_fp', None)
    if settings is None:
        return
    if not settings.show_dimensions and not settings.show_labels:
        return

    # Only draw inside the 3-D viewport window
    space = getattr(context, 'space_data', None)
    if space is None or space.type != 'VIEW_3D':
        return
    rv3d = getattr(context, 'region_data', None)
    region = getattr(context, 'region', None)
    if rv3d is None or region is None:
        return

    from bpy_extras.view3d_utils import location_3d_to_region_2d
    from mathutils import Vector

    unit = settings.display_unit
    font_id = 0

    # Wall lengths — small blue text at edge midpoint.
    if settings.show_dimensions and settings.show_labels and settings.show_wall_labels:
        blf.size(font_id, 12)
        blf.color(font_id, 0.25, 0.65, 1.0, 1.0)
        for (a, b) in _DEMO_WALLS:
            va, vb = Vector(a), Vector(b)
            mid = (va + vb) * 0.5
            pt2d = location_3d_to_region_2d(region, rv3d, mid)
            if pt2d is None:
                continue
            label = _format_length((vb - va).length, unit)
            w, _ = blf.dimensions(font_id, label)
            blf.position(font_id, pt2d.x - w * 0.5, pt2d.y + 6, 0)
            blf.draw(font_id, label)

    # Room labels — centered at room centroid.
    if settings.show_labels and settings.show_room_labels:
        blf.size(font_id, 14)
        for room in _DEMO_ROOMS:
            pt2d = location_3d_to_region_2d(region, rv3d, Vector((room["cx"], room["cy"], 0.0)))
            if pt2d is None:
                continue
            name_label = room["name"]
            area_label = f"{room['area']:.1f} m\u00b2"

            blf.color(font_id, 0.95, 0.95, 0.95, 0.95)
            w, h = blf.dimensions(font_id, name_label)
            blf.position(font_id, pt2d.x - w * 0.5, pt2d.y + 4, 0)
            blf.draw(font_id, name_label)

            blf.color(font_id, 0.65, 0.90, 0.65, 0.90)
            w2, h2 = blf.dimensions(font_id, area_label)
            blf.position(font_id, pt2d.x - w2 * 0.5, pt2d.y - h2 - 4, 0)
            blf.draw(font_id, area_label)


def _draw_gizmos():
    """POST_VIEW handler: static gizmo mockup on the bottom wall (0,0)-(6,0)."""
    context = bpy.context
    if not context or not getattr(context, 'scene', None):
        return
    settings = getattr(context.scene, 'mockup_fp', None)
    if settings is None or not settings.show_gizmos:
        return
    space = getattr(context, 'space_data', None)
    if space is None or space.type != 'VIEW_3D':
        return

    import gpu
    import math as _math
    from gpu_extras.batch import batch_for_shader
    from mathutils import Vector

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')

    def _arrow(origin, direction, length, color, lw=2.5):
        """Draw a line + filled arrowhead triangle."""
        tip = origin + direction * length
        neck = origin + direction * (length * 0.72)
        up = Vector((0, 0, 1))
        perp = direction.cross(up)
        if perp.length < 1e-4:
            perp = Vector((1, 0, 0))
        else:
            perp.normalize()
        hw = length * 0.10
        shader.bind()
        shader.uniform_float("color", color)
        gpu.state.line_width_set(lw)
        batch_for_shader(shader, 'LINES', {"pos": [origin, neck]}).draw(shader)
        gpu.state.line_width_set(1.0)
        batch_for_shader(shader, 'TRIS', {"pos": [
            tip, neck + perp * hw, neck - perp * hw,
        ]}).draw(shader)

    mid = Vector((3.0, 0.0, 0.0))

    # Thickness gizmo (cyan, Y-axis perpendicular to wall)
    _arrow(mid, Vector((0, 1, 0)),  0.70, (0.35, 0.80, 1.0, 1.0))
    _arrow(mid, Vector((0, -1, 0)), 0.70, (0.35, 0.80, 1.0, 1.0))

    # Height gizmo (green, Z-axis)
    _arrow(mid, Vector((0, 0, 1)), 0.90, (0.25, 0.95, 0.35, 1.0))

    # Junction move gizmo — circle at junction (6, 0, 0)
    jct = Vector((6.0, 0.0, 0.0))
    r, n = 0.28, 32
    pts = [Vector((jct.x + r * _math.cos(2 * _math.pi * i / n),
                   jct.y + r * _math.sin(2 * _math.pi * i / n), 0.0))
           for i in range(n)]
    lines = [v for i in range(n) for v in (pts[i], pts[(i + 1) % n])]
    shader.bind()
    shader.uniform_float("color", (1.0, 0.85, 0.15, 1.0))
    gpu.state.line_width_set(3.0)
    batch_for_shader(shader, 'LINES', {"pos": lines}).draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    gpu.state.depth_test_set('LESS_EQUAL')


def _cursor_timer():
    # Runs every 50 ms; sets the cursor to a pencil when the pencil tool is active.
    try:
        context = bpy.context
        if not context or not getattr(context, 'workspace', None):
            return 0.05
        if not getattr(context, 'window', None):
            return 0.05
        tool = context.workspace.tools.from_space_view3d_mode("OBJECT")
        if tool and tool.idname == "mockup_fp.pencil_tool":
            context.window.cursor_set('PAINT_BRUSH')
        else:
            context.window.cursor_set('DEFAULT')
    except Exception:
        pass
    return 0.05


def _draw_hud():
    context = bpy.context
    if not context or not getattr(context, "workspace", None):
        return
    tool = context.workspace.tools.from_space_view3d_mode("OBJECT")
    if tool is None or tool.idname != "mockup_fp.pencil_tool":
        return

    font_id = 0
    blf.size(font_id, 16)
    blf.color(font_id, 0.7, 0.9, 1.0, 0.9)
    blf.position(font_id, 20, 40, 0)
    blf.draw(font_id, "FloorPlan Pencil \u2014 Waiting for input")


# Status bar draw function (keyboard hints)
def _draw_status_bar(self, context):
    if not context or not getattr(context, "workspace", None):
        return
    tool = context.workspace.tools.from_space_view3d_mode("OBJECT")
    if tool is None or tool.idname != "mockup_fp.pencil_tool":
        return
    layout = self.layout
    layout.label(text="", icon='MOUSE_LMB')
    layout.label(text="Place first junction")
    layout.label(text="", icon='EVENT_Z')
    layout.label(text="Undo")
    layout.label(text="", icon='EVENT_ESC')
    layout.label(text="Exit tool")


# PropertyGroup: single room item
class MockupRoom(bpy.types.PropertyGroup):
    expanded: BoolProperty(default=False)
    room_name: StringProperty(name="Name", default="Room")
    area: FloatProperty(name="Area", default=0.0, precision=2, unit='AREA')
    perimeter: FloatProperty(name="Perimeter", default=0.0, precision=2, unit='LENGTH')
    height: FloatProperty(
        name="Height", default=2.5, min=1.0, max=10.0, precision=2, unit='LENGTH',
    )
    wall_count: IntProperty(name="Walls", default=0)
    # Mockup viewport rectangle (center + half-extents in world metres, Z=0 plane)
    mock_cx: FloatProperty(default=0.0)
    mock_cy: FloatProperty(default=0.0)
    mock_hw: FloatProperty(default=2.0)  # half-width
    mock_hd: FloatProperty(default=2.0)  # half-depth


# PropertyGroup: single opening item
class MockupOpening(bpy.types.PropertyGroup):
    expanded: BoolProperty(default=False)
    opening_name: StringProperty(name="Name", default="Opening")
    opening_type: EnumProperty(
        name="Type",
        items=[
            ('DOOR', "Door", "Door opening from the floor"),
            ('WINDOW', "Window", "Window opening with sill height"),
        ],
        default='DOOR',
    )
    width: FloatProperty(
        name="Width", default=0.9, min=0.3, max=5.0, precision=3, unit='LENGTH',
    )
    height: FloatProperty(
        name="Height", default=2.1, min=0.3, max=10.0, precision=3, unit='LENGTH',
    )
    sill_height: FloatProperty(
        name="Sill Height", default=0.0, min=0.0, max=10.0, precision=3, unit='LENGTH',
    )
    position: FloatProperty(
        name="Position",
        description="Relative position along wall (0 = start, 1 = end)",
        default=0.5, min=0.01, max=0.99, precision=3,
    )


# Main settings PropertyGroup
class MockupFloorPlanSettings(bpy.types.PropertyGroup):
    # Defaults for new walls (also shown in tool header when pencil active)
    default_thickness: FloatProperty(
        name="Default Wall Thickness",
        description="Default wall thickness for new walls (meters)",
        default=0.3, min=0.05, max=1.0, precision=3, unit='LENGTH',
    )
    default_height: FloatProperty(
        name="Default Wall Height",
        description="Default wall height for new walls (meters)",
        default=2.5, min=1.0, max=10.0, precision=2, unit='LENGTH',
    )

    # Display unit for dimensions and labels
    display_unit: EnumProperty(
        name="Units",
        description="Unit system used for displaying dimensions",
        items=[
            ('M',  "Meters (m)",      "Display measurements in metres"),
            ('CM', "Centimeters (cm)", "Display measurements in centimetres"),
            ('MM', "Millimeters (mm)", "Display measurements in millimetres"),
            ('FT', "Feet (ft)",        "Display measurements in feet"),
            ('IN', "Inches (in)",      "Display measurements in inches"),
        ],
        default='M',
    )

    # Wall draw mode (tool header)
    wall_draw_mode: EnumProperty(
        name="Alignment",
        description="Wall position relative to drawing line",
        items=[
            ('LEFT', "Left", "Wall on left side of drawing line"),
            ('CENTER', "Center", "Wall centered on drawing line"),
            ('RIGHT', "Right", "Wall on right side of drawing line"),
        ],
        default='CENTER',
    )

    # Active wall (always visible in mockup)
    active_wall_thickness: FloatProperty(
        name="Wall Thickness",
        description="Thickness of the selected wall",
        default=0.25, min=0.05, max=1.0, precision=3, unit='LENGTH',
    )
    active_wall_height: FloatProperty(
        name="Wall Height",
        description="Height of the selected wall",
        default=2.8, min=1.0, max=10.0, precision=2, unit='LENGTH',
    )

    # Room collection (populated at register time)
    rooms: CollectionProperty(type=MockupRoom)
    selected_room_index: IntProperty(default=-1)

    # Opening collection for the active wall
    openings: CollectionProperty(type=MockupOpening)
    openings_expanded: BoolProperty(name="Openings", default=False)

    # Finalize popover options
    finalize_organize: BoolProperty(
        name="Organize Objects in Scene",
        description="Group generated objects into a collection",
        default=True,
    )
    finalize_materials: BoolProperty(
        name="Assign Materials",
        description="Automatically assign basic materials to walls and floors",
        default=True,
    )
    finalize_keep_original: BoolProperty(
        name="Preserve Original",
        description="Keep the original floor plan object alongside the finalized mesh",
        default=False,
    )

    # Overlay settings
    show_dimensions: BoolProperty(
        name="Dimensions",
        description="Show wall lengths and room areas in viewport",
        default=True,
    )
    show_room_colors: BoolProperty(
        name="Room Colors",
        description="Show colored room fills in viewport",
        default=True,
    )
    show_labels: BoolProperty(
        name="Labels",
        description="Show room, wall and opening labels in the viewport",
        default=True,
    )
    show_room_labels: BoolProperty(
        name="Room Labels",
        description="Show room names in viewport",
        default=True,
    )
    show_wall_labels: BoolProperty(
        name="Wall Labels",
        description="Show wall number and length labels in viewport",
        default=True,
    )
    show_door_labels: BoolProperty(
        name="Door Labels",
        description="Show door opening labels in viewport",
        default=True,
    )
    show_window_labels: BoolProperty(
        name="Window Labels",
        description="Show window opening labels in viewport",
        default=True,
    )
    show_wall_highlight: BoolProperty(
        name="Highlights",
        description="Show wall edges plus door/window edge highlights in viewport",
        default=True,
    )
    show_wall_edge_highlights: BoolProperty(
        name="Wall Highlights",
        description="Show wall edge highlights in viewport",
        default=True,
    )
    show_door_edge_highlights: BoolProperty(
        name="Door Highlights",
        description="Show door opening edge highlights in viewport",
        default=True,
    )
    show_window_edge_highlights: BoolProperty(
        name="Window Highlights",
        description="Show window opening edge highlights in viewport",
        default=True,
    )
    show_gizmos: BoolProperty(
        name="Gizmos",
        description="Show interactive manipulators on selected elements",
        default=True,
    )


# Placebo operators

class MOCKUP_OT_toggle_room(bpy.types.Operator):
    bl_idname = "mockup_fp.toggle_room"
    bl_label = ""
    bl_description = "Select room and toggle detail"
    bl_options = {'INTERNAL'}

    index: IntProperty(default=0)

    def execute(self, context):
        settings = context.scene.mockup_fp
        settings.selected_room_index = self.index
        room = settings.rooms[self.index]
        room.expanded = not room.expanded
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


class MOCKUP_OT_pencil_tool(bpy.types.Operator):
    bl_idname = "mockup_fp.pencil_tool_op"
    bl_label = "FloorPlan Pencil Tool"
    bl_description = "Draw walls by placing junctions (mockup — no functionality)"

    def invoke(self, context, event):
        return {'CANCELLED'}


class MOCKUP_OT_insert_room(bpy.types.Operator):
    bl_idname = "mockup_fp.insert_room"
    bl_label = "Insert Room"
    bl_description = "Insert a rectangular room at the 3D cursor (mockup — no functionality)"

    width: FloatProperty(name="Width", default=4.0, min=0.5, max=50.0, unit='LENGTH')
    depth: FloatProperty(name="Depth", default=3.0, min=0.5, max=50.0, unit='LENGTH')
    wall_height: FloatProperty(name="Wall Height", default=2.5, min=1.0, max=10.0, unit='LENGTH')
    wall_thickness: FloatProperty(name="Wall Thickness", default=0.3, min=0.05, max=1.0, unit='LENGTH')

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Insert Room (no functionality)")
        return {'FINISHED'}


class MOCKUP_OT_add_opening(bpy.types.Operator):
    bl_idname = "mockup_fp.add_opening"
    bl_label = "Add Opening"
    bl_description = "Add a door or window opening to the selected wall (mockup)"

    opening_type: EnumProperty(
        name="Type",
        items=[('DOOR', "Door", ""), ('WINDOW', "Window", "")],
        default='DOOR',
    )

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Add Opening (no functionality)")
        return {'FINISHED'}


class MOCKUP_OT_remove_opening(bpy.types.Operator):
    bl_idname = "mockup_fp.remove_opening"
    bl_label = "Remove Opening"
    bl_description = "Remove an opening from the wall (mockup)"

    index: IntProperty(default=0)

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Remove Opening (no functionality)")
        return {'FINISHED'}


class MOCKUP_OT_remove_room(bpy.types.Operator):
    bl_idname = "mockup_fp.remove_room"
    bl_label = "Remove Room"
    bl_description = "Remove a room from the floor plan (mockup)"

    index: IntProperty(default=0)

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Remove Room (no functionality)")
        return {'FINISHED'}


class MOCKUP_OT_finalize(bpy.types.Operator):
    bl_idname = "mockup_fp.finalize"
    bl_label = "Bake"
    bl_description = "Finalize floor plan — bake to mesh (mockup)"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=280)

    def draw(self, context):
        settings = context.scene.mockup_fp
        layout = self.layout
        layout.label(text="Output Options", icon='SETTINGS')
        layout.separator()
        col = layout.column(align=True)
        col.prop(settings, "finalize_organize")
        col.prop(settings, "finalize_materials")
        col.prop(settings, "finalize_keep_original")
        layout.separator()
        layout.operator("mockup_fp.finalize_run", text="Run Bake", icon='RENDER_RESULT')

    def execute(self, context):
        return {'FINISHED'}


class MOCKUP_OT_finalize_run(bpy.types.Operator):
    bl_idname = "mockup_fp.finalize_run"
    bl_label = "Run Bake"
    bl_description = "Run the finalization pipeline (mockup)"

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Bake (no functionality)")
        return {'FINISHED'}


class MOCKUP_OT_deselect_wall(bpy.types.Operator):
    bl_idname = "mockup_fp.deselect_wall"
    bl_label = "Deselect Wall"
    bl_description = "Deselect the currently selected wall (mockup)"

    def execute(self, context):
        self.report({'INFO'}, "MockUp: Deselect Wall (no functionality)")
        return {'FINISHED'}


def _pick_context(context, mx, my):
    """Return ('room'|'wall'|'junction'|'empty', index) based on 2D screen proximity."""
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    from mathutils import Vector
    rv3d = getattr(context, 'region_data', None)
    region = getattr(context, 'region', None)
    if rv3d is None or region is None:
        return ('empty', None)
    mouse = Vector((mx, my))

    # Unique junctions (deduplicated)
    seen = {}
    junctions = []
    for wall in _DEMO_WALLS:
        for pt in (wall[0], wall[1]):
            key = (round(pt[0], 3), round(pt[1], 3))
            if key not in seen:
                seen[key] = len(junctions)
                junctions.append(Vector(pt))
    for i, jct in enumerate(junctions):
        pt2d = location_3d_to_region_2d(region, rv3d, jct)
        if pt2d and (mouse - pt2d).length < 22:
            return ('junction', i)

    # Wall midpoints
    for i, (a, b) in enumerate(_DEMO_WALLS):
        mid = Vector(((a[0]+b[0])/2, (a[1]+b[1])/2, 0.0))
        pt2d = location_3d_to_region_2d(region, rv3d, mid)
        if pt2d and (mouse - pt2d).length < 32:
            return ('wall', i)

    # Room centroids
    for i, room in enumerate(_DEMO_ROOMS):
        pt2d = location_3d_to_region_2d(region, rv3d, Vector((room['cx'], room['cy'], 0.0)))
        if pt2d and (mouse - pt2d).length < 65:
            return ('room', i)

    return ('empty', None)


class MOCKUP_OT_context_menu(bpy.types.Operator):
    bl_idname = "mockup_fp.context_menu"
    bl_label = "FloorPlan Context Menu"
    bl_description = "Show context-sensitive FloorPlan menu (mockup)"

    # When set, skip pick detection and show this context type directly.
    force_type: StringProperty(default='')

    def invoke(self, context, event):
        if self.force_type:
            ctx_type = self.force_type
        else:
            ctx_type, _idx = _pick_context(
                context, event.mouse_region_x, event.mouse_region_y
            )
        bpy.ops.wm.call_menu(name=_CTX_MENU_MAP[ctx_type])
        return {'FINISHED'}


class MOCKUP_OT_ctx_action(bpy.types.Operator):
    bl_idname = "mockup_fp.ctx_action"
    bl_label = "FloorPlan Action"
    bl_description = "Context menu action (mockup \u2014 no functionality)"

    action: StringProperty(default='')

    def execute(self, context):
        self.report({'INFO'}, f"MockUp: {self.action} (no functionality)")
        return {'FINISHED'}


# Proper Menu classes for each context — open as flyout submenus.

class MOCKUP_MT_ctx_room(bpy.types.Menu):
    bl_idname = "MOCKUP_MT_ctx_room"
    bl_label = "Room"

    def draw(self, context):
        layout = self.layout
        layout.operator("mockup_fp.ctx_action", text="Rename Room",
                        icon='OUTLINER_DATA_FONT').action = 'RENAME_ROOM'
        layout.operator("mockup_fp.ctx_action", text="Delete Room",
                        icon='TRASH').action = 'DELETE_ROOM'


class MOCKUP_MT_ctx_wall(bpy.types.Menu):
    bl_idname = "MOCKUP_MT_ctx_wall"
    bl_label = "Wall"

    def draw(self, context):
        layout = self.layout
        layout.operator("mockup_fp.ctx_action", text="Edit Thickness",
                        icon='DRIVER_DISTANCE').action = 'EDIT_THICKNESS'
        layout.operator("mockup_fp.ctx_action", text="Edit Height",
                        icon='EMPTY_SINGLE_ARROW').action = 'EDIT_HEIGHT'
        layout.separator()
        layout.operator("mockup_fp.ctx_action", text="Add Opening\u2026",
                        icon='MOD_BOOLEAN').action = 'ADD_OPENING'
        layout.operator("mockup_fp.ctx_action", text="Split Wall",
                        icon='SNAP_MIDPOINT').action = 'SPLIT_WALL'
        layout.separator()
        layout.operator("mockup_fp.ctx_action", text="Delete Wall",
                        icon='TRASH').action = 'DELETE_WALL'


class MOCKUP_MT_ctx_junction(bpy.types.Menu):
    bl_idname = "MOCKUP_MT_ctx_junction"
    bl_label = "Junction"

    def draw(self, context):
        layout = self.layout
        layout.operator("mockup_fp.ctx_action", text="Delete Junction & Walls",
                        icon='TRASH').action = 'DELETE_JUNCTION'
        layout.operator("mockup_fp.ctx_action", text="Merge with Nearest",
                        icon='AUTOMERGE_ON').action = 'MERGE_JUNCTION'


class MOCKUP_MT_ctx_empty(bpy.types.Menu):
    bl_idname = "MOCKUP_MT_ctx_empty"
    bl_label = "Floor Plan"

    def draw(self, context):
        layout = self.layout
        layout.operator("mockup_fp.ctx_action", text="Toggle Grid",
                        icon='GRID').action = 'TOGGLE_GRID'
        layout.operator("mockup_fp.ctx_action", text="Toggle Dimensions",
                        icon='DRIVER_DISTANCE').action = 'TOGGLE_DIMENSIONS'
        layout.separator()
        layout.operator("mockup_fp.pencil_tool_op", text="Draw with Pencil",
                        icon='GREASEPENCIL')


_CTX_MENU_MAP = {
    'room':     'MOCKUP_MT_ctx_room',
    'wall':     'MOCKUP_MT_ctx_wall',
    'junction': 'MOCKUP_MT_ctx_junction',
    'empty':    'MOCKUP_MT_ctx_empty',
}


def _draw_object_context_menu_items(self, context):
    """Appended to VIEW3D_MT_object_context_menu: 4 FloorPlan submenus."""
    layout = self.layout
    layout.separator()
    layout.label(text="FloorPlanMaster", icon='MESH_PLANE')
    layout.menu("MOCKUP_MT_ctx_room",     icon='HOME')
    layout.menu("MOCKUP_MT_ctx_wall",     icon='MESH_PLANE')
    layout.menu("MOCKUP_MT_ctx_junction", icon='DECORATE_KEYFRAME')
    layout.menu("MOCKUP_MT_ctx_empty",    icon='MESH_GRID')


# WorkSpaceTool for Toolbar
class MOCKUP_WT_pencil(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "mockup_fp.pencil_tool"
    bl_label = "FloorPlan Pencil"
    bl_description = "Draw floor plan walls by placing junctions"
    bl_icon = "ops.gpencil.draw.line"
    bl_widget = None
    bl_keymap = (
        (
            "mockup_fp.pencil_tool_op",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            None,
        ),
    )

    def draw_settings(context, layout, tool):
        settings = context.scene.mockup_fp
        if context.region.type == 'UI':
            # Active tool N-panel: vertical
            col = layout.column(align=True)
            col.prop(settings, "default_thickness", text="Thickness")
            col.prop(settings, "default_height", text="Height")
            row = col.row(align=True)
            row.prop(settings, "wall_draw_mode", expand=True)
        else:
            # Tool header (top of viewport): horizontal
            row = layout.row(align=True)
            row.prop(settings, "default_thickness", text="Thickness")
            row.prop(settings, "default_height", text="Height")
            row.separator()
            sub = row.row(align=True)
            sub.prop(settings, "wall_draw_mode", expand=True)


def _populate_mockup_data():
    # Populate rooms and openings with static mockup data on first access.
    # Returns None so bpy.app.timers does not reschedule it.
    for scene in bpy.data.scenes:
        settings = getattr(scene, "mockup_fp", None)
        if settings is None:
            continue
        if len(settings.rooms) == 0:
            r1 = settings.rooms.add()
            r1.room_name = "Living Room"
            r1.area = 30.0
            r1.perimeter = 22.0
            r1.height = 2.8
            r1.wall_count = 4
            r1.mock_cx, r1.mock_cy = 3.0, 2.5
            r1.mock_hw, r1.mock_hd = 3.0, 2.5

            r2 = settings.rooms.add()
            r2.room_name = "Kitchen"
            r2.area = 20.0
            r2.perimeter = 18.0
            r2.height = 2.5
            r2.wall_count = 4
            r2.mock_cx, r2.mock_cy = 8.0, 2.5
            r2.mock_hw, r2.mock_hd = 2.0, 2.5

            r3 = settings.rooms.add()
            r3.room_name = "Bedroom"
            r3.area = 24.0
            r3.perimeter = 20.0
            r3.height = 2.6
            r3.wall_count = 4
            r3.mock_cx, r3.mock_cy = 3.0, 7.0
            r3.mock_hw, r3.mock_hd = 3.0, 2.0

        if len(settings.openings) == 0:
            o1 = settings.openings.add()
            o1.opening_name = "Front Door"
            o1.opening_type = 'DOOR'
            o1.width = 0.9
            o1.height = 2.1
            o1.sill_height = 0.0
            o1.position = 0.5

            o2 = settings.openings.add()
            o2.opening_name = "Side Window"
            o2.opening_type = 'WINDOW'
            o2.width = 1.2
            o2.height = 1.0
            o2.sill_height = 0.9
            o2.position = 0.35
    _create_demo_mesh()
    return None  # timer: do not reschedule


@bpy.app.handlers.persistent
def _load_post_handler(dummy):
    _populate_mockup_data()


from .panels import get_panel_classes

_prop_classes = [
    MockupRoom,
    MockupOpening,
    MockupFloorPlanSettings,
]

_menu_classes = [
    MOCKUP_MT_ctx_room,
    MOCKUP_MT_ctx_wall,
    MOCKUP_MT_ctx_junction,
    MOCKUP_MT_ctx_empty,
]

_operator_classes = [
    MOCKUP_OT_toggle_room,
    MOCKUP_OT_pencil_tool,
    MOCKUP_OT_insert_room,
    MOCKUP_OT_add_opening,
    MOCKUP_OT_remove_opening,
    MOCKUP_OT_remove_room,
    MOCKUP_OT_finalize,
    MOCKUP_OT_finalize_run,
    MOCKUP_OT_deselect_wall,
    MOCKUP_OT_context_menu,
    MOCKUP_OT_ctx_action,
]


def register():
    for cls in _prop_classes:
        bpy.utils.register_class(cls)
    for cls in _menu_classes:
        bpy.utils.register_class(cls)
    for cls in _operator_classes:
        bpy.utils.register_class(cls)
    for cls in get_panel_classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.mockup_fp = PointerProperty(type=MockupFloorPlanSettings)
    bpy.utils.register_tool(MOCKUP_WT_pencil)

    # Register D shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        km.keymap_items.new("mockup_fp.pencil_tool_op", type='D', value='PRESS')
        km.keymap_items.new("mockup_fp.context_menu", type='RIGHTMOUSE', value='PRESS')

    # Register cursor timer
    if not bpy.app.timers.is_registered(_cursor_timer):
        bpy.app.timers.register(_cursor_timer, first_interval=0.05, persistent=True)

    # Register HUD draw handler
    global _hud_draw_handle
    _hud_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_hud, (), 'WINDOW', 'POST_PIXEL'
    )

    # Register room selection highlight handler
    global _room_highlight_handle
    _room_highlight_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_room_highlight, (), 'WINDOW', 'POST_PIXEL'
    )

    # Register dimension overlay handler
    global _dimension_draw_handle
    _dimension_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_dimensions, (), 'WINDOW', 'POST_PIXEL'
    )

    # Register gizmo mockup handler
    global _gizmo_draw_handle
    _gizmo_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_gizmos, (), 'WINDOW', 'POST_VIEW'
    )

    # Register status bar hints
    bpy.types.STATUSBAR_HT_header.prepend(_draw_status_bar)

    # Append FloorPlan items to built-in Object Mode context menu
    bpy.types.VIEW3D_MT_object_context_menu.append(_draw_object_context_menu_items)

    # Register load handler and populate data
    bpy.app.handlers.load_post.append(_load_post_handler)
    _populate_mockup_data()


def unregister():
    if _load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post_handler)

    # Unregister cursor timer
    if bpy.app.timers.is_registered(_cursor_timer):
        bpy.app.timers.unregister(_cursor_timer)

    bpy.types.STATUSBAR_HT_header.remove(_draw_status_bar)
    bpy.types.VIEW3D_MT_object_context_menu.remove(_draw_object_context_menu_items)

    global _hud_draw_handle
    if _hud_draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_hud_draw_handle, 'WINDOW')
        _hud_draw_handle = None

    global _room_highlight_handle
    if _room_highlight_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_room_highlight_handle, 'WINDOW')
        _room_highlight_handle = None

    global _dimension_draw_handle
    if _dimension_draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_dimension_draw_handle, 'WINDOW')
        _dimension_draw_handle = None

    global _gizmo_draw_handle
    if _gizmo_draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_gizmo_draw_handle, 'WINDOW')
        _gizmo_draw_handle = None

    # Unregister D shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in list(km.keymap_items):
                if kmi.idname in ("mockup_fp.pencil_tool_op", "mockup_fp.context_menu"):
                    km.keymap_items.remove(kmi)

    bpy.utils.unregister_tool(MOCKUP_WT_pencil)
    del bpy.types.Scene.mockup_fp

    for cls in reversed(get_panel_classes()):
        bpy.utils.unregister_class(cls)
    for cls in reversed(_operator_classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(_menu_classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(_prop_classes):
        bpy.utils.unregister_class(cls)
