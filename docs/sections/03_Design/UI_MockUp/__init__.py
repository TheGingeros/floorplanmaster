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
    show_room_labels: BoolProperty(
        name="Room Labels",
        description="Show room names in viewport",
        default=True,
    )
    show_wall_highlight: BoolProperty(
        name="Selection Highlight",
        description="Show highlight on selected wall",
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
            r1.area = 28.50
            r1.perimeter = 21.40
            r1.height = 2.8
            r1.wall_count = 4
            r1.mock_cx, r1.mock_cy = 3.0, 2.5
            r1.mock_hw, r1.mock_hd = 3.0, 2.5

            r2 = settings.rooms.add()
            r2.room_name = "Kitchen"
            r2.area = 14.20
            r2.perimeter = 15.60
            r2.height = 2.5
            r2.wall_count = 4
            r2.mock_cx, r2.mock_cy = 8.5, 2.0
            r2.mock_hw, r2.mock_hd = 2.0, 1.75

            r3 = settings.rooms.add()
            r3.room_name = "Bedroom"
            r3.area = 18.75
            r3.perimeter = 17.80
            r3.height = 2.6
            r3.wall_count = 5
            r3.mock_cx, r3.mock_cy = 3.0, 7.5
            r3.mock_hw, r3.mock_hd = 2.5, 2.5

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
]


def register():
    for cls in _prop_classes:
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

    # Register status bar hints
    bpy.types.STATUSBAR_HT_header.prepend(_draw_status_bar)

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

    global _hud_draw_handle
    if _hud_draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_hud_draw_handle, 'WINDOW')
        _hud_draw_handle = None

    global _room_highlight_handle
    if _room_highlight_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_room_highlight_handle, 'WINDOW')
        _room_highlight_handle = None

    # Unregister D shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in list(km.keymap_items):
                if kmi.idname == "mockup_fp.pencil_tool_op":
                    km.keymap_items.remove(kmi)

    bpy.utils.unregister_tool(MOCKUP_WT_pencil)
    del bpy.types.Scene.mockup_fp

    for cls in reversed(get_panel_classes()):
        bpy.utils.unregister_class(cls)
    for cls in reversed(_operator_classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(_prop_classes):
        bpy.utils.unregister_class(cls)
