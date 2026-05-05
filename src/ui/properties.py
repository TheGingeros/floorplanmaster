# PropertyGroups and their update callbacks for FloorPlanMaster.
# OpeningItem — per-opening editable item in the N-panel list.
# FloorPlanSettings — scene-level addon settings (PointerProperty on Scene).
# populate_opening_items — repopulate the opening list after wall selection / CRUD.
# set_wall_props_updating — expose the circular-update guard for operators.

import bpy
import time
from bpy.props import (
    BoolProperty, CollectionProperty, EnumProperty,
    FloatProperty, StringProperty,
)

from .selection_state import _selection
from ..core.sync import sync_graph_to_mesh, sync_graph_to_mesh_local
from ..utils.constants import (
    DEFAULT_DOOR_WIDTH, DEFAULT_WINDOW_WIDTH,
    DEFAULT_DOOR_HEIGHT, DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_SILL,
    MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
    MIN_OPENING_HEIGHT, MAX_HEIGHT,
)

_updating_wall_props = False
_updating_wall_xy_props = False
_updating_opening_items = False
_updating_room_props = False
_pending_wall_sync_tokens = {}
_WALL_SYNC_DEBOUNCE_SECONDS = 0.12


def _schedule_debounced_wall_sync(obj_name: str, wall_uuid: str) -> None:
    # Collapse rapid UI slider updates into a single sync pass.
    key = (obj_name, wall_uuid)
    token = time.monotonic()
    _pending_wall_sync_tokens[key] = token

    def _flush_wall_sync():
        if _pending_wall_sync_tokens.get(key) != token:
            return None

        from .. import _graph_store

        bundle = _graph_store.get(obj_name)
        if bundle is None:
            _pending_wall_sync_tokens.pop(key, None)
            return None

        obj = bpy.data.objects.get(obj_name)
        if obj is None or not obj.get("is_floorplan"):
            _pending_wall_sync_tokens.pop(key, None)
            return None

        sg, rg, mapper = bundle
        sync_graph_to_mesh_local(
            obj,
            sg,
            rg,
            id_mapper=mapper,
            dirty_wall_ids=[wall_uuid],
            fallback_full_sync=True,
        )
        _pending_wall_sync_tokens.pop(key, None)
        return None

    bpy.app.timers.register(_flush_wall_sync, first_interval=_WALL_SYNC_DEBOUNCE_SECONDS)


def set_wall_props_updating(val: bool) -> None:
    global _updating_wall_props
    _updating_wall_props = val


def set_wall_xy_props_updating(val: bool) -> None:
    global _updating_wall_xy_props
    _updating_wall_xy_props = val


def set_room_props_updating(val: bool) -> None:
    global _updating_room_props
    _updating_room_props = val


def _restore_opening_item_from_graph(item, opening):
    global _updating_opening_items
    _updating_opening_items = True
    try:
        item.opening_type = opening.opening_type
        item.width = opening.width
        item.height = opening.height
        item.sill_height = opening.sill_height
        item.position = opening.position
    finally:
        _updating_opening_items = False


def _on_room_name_update(self, context):
    global _updating_room_props
    if _updating_room_props:
        return
    from .selection_state import _selection
    room_uuid = _selection.room_id
    if not room_uuid:
        return
    from .. import find_floorplan_obj, _graph_store
    from ..core.sync import persist_room_names
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
        return
    sg, rg, mapper = _graph_store[obj.name]
    effective_name = rg.set_room_name(room_uuid, self.active_room_name)
    if effective_name is None:
        return
    if self.active_room_name != effective_name:
        _updating_room_props = True
        try:
            self.active_room_name = effective_name
        finally:
            _updating_room_props = False
    # Keep the inline rooms-list custom property in sync.
    obj[f"room_name_{room_uuid}"] = effective_name
    persist_room_names(obj, rg)


def _on_display_unit_update(self, context):
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    unit_settings = getattr(scene, "unit_settings", None)
    if unit_settings is None:
        return

    if self.display_unit in {'M', 'CM', 'MM'}:
        unit_settings.system = 'METRIC'
        if self.display_unit == 'CM':
            unit_settings.length_unit = 'CENTIMETERS'
        elif self.display_unit == 'MM':
            unit_settings.length_unit = 'MILLIMETERS'
        else:
            unit_settings.length_unit = 'METERS'
    else:
        unit_settings.system = 'IMPERIAL'
        if self.display_unit == 'IN':
            unit_settings.length_unit = 'INCHES'
        else:
            unit_settings.length_unit = 'FEET'

    screen = getattr(context, "screen", None)
    if screen is not None:
        for area in screen.areas:
            area.tag_redraw()


def _on_wall_thickness_update(self, context):
    global _updating_wall_props
    if _updating_wall_props:
        return
    from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
    wall_uuid = _selection.wall_id
    if not wall_uuid:
        return
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj):
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
    _schedule_debounced_wall_sync(obj.name, wall_uuid)


def _on_wall_height_update(self, context):
    global _updating_wall_props
    if _updating_wall_props:
        return
    from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
    wall_uuid = _selection.wall_id
    if not wall_uuid:
        return
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj):
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
    _schedule_debounced_wall_sync(obj.name, wall_uuid)


def _sync_wall_xy_edit(self, context, edit_mode):
    global _updating_wall_props, _updating_wall_xy_props
    if _updating_wall_props or _updating_wall_xy_props:
        return

    from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj

    wall_uuid = _selection.wall_id
    if not wall_uuid:
        return

    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj):
        return

    if obj.name not in _graph_store:
        reset_graphs_for_obj(obj)
    sg, rg, mapper = _graph_store[obj.name]
    wall = sg.get_wall(wall_uuid)
    if wall is None:
        return

    try:
        if edit_mode == 'start':
            sg.move_junction_xy(
                wall.junction_start,
                self.active_wall_start_x,
                self.active_wall_start_y,
            )
        elif edit_mode == 'end':
            sg.move_junction_xy(
                wall.junction_end,
                self.active_wall_end_x,
                self.active_wall_end_y,
            )
        elif edit_mode == 'middle':
            j_start = sg.get_junction(wall.junction_start)
            j_end = sg.get_junction(wall.junction_end)
            if j_start is None or j_end is None:
                return
            sx, sy = j_start.position
            ex, ey = j_end.position
            dx = ex - sx
            dy = ey - sy
            length = (dx * dx + dy * dy) ** 0.5
            if length < 1e-9:
                return
            nx = -dy / length
            ny = dx / length
            mid_x = (sx + ex) * 0.5
            mid_y = (sy + ey) * 0.5
            current_n = mid_x * nx + mid_y * ny
            target_n = self.active_wall_mid_normal
            delta_n = target_n - current_n
            sg.slide_wall_normal(
                wall_uuid,
                mid_x + nx * delta_n,
                mid_y + ny * delta_n,
            )
        else:
            return
    except Exception:
        return

    rg.sync_from_structural_graph()
    sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
    populate_active_wall_props(self, sg, wall_uuid)
    populate_opening_items(self, sg, wall_uuid)
    if context.area:
        context.area.tag_redraw()


def _on_wall_start_x_update(self, context):
    _sync_wall_xy_edit(self, context, 'start')


def _on_wall_start_y_update(self, context):
    _sync_wall_xy_edit(self, context, 'start')


def _on_wall_end_x_update(self, context):
    _sync_wall_xy_edit(self, context, 'end')


def _on_wall_end_y_update(self, context):
    _sync_wall_xy_edit(self, context, 'end')


def _on_wall_mid_normal_update(self, context):
    _sync_wall_xy_edit(self, context, 'middle')


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
    from .. import find_floorplan_obj, _graph_store
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
        return
    sg, rg, mapper = _graph_store[obj.name]
    op = sg.get_opening(opening_id)
    if op is None:
        return
    max_w = min(MAX_OPENING_WIDTH, sg.max_opening_width(op.wall_id, exclude_opening_id=opening_id))
    if max_w < MIN_OPENING_WIDTH:
        _restore_opening_item_from_graph(self, op)
        return
    if self.width > max_w:
        _updating_opening_items = True
        self.width = max_w
        _updating_opening_items = False
    clamped_pos = sg.clamp_opening_position(op.wall_id, self.width, self.position, exclude_opening_id=opening_id)
    if clamped_pos is not None and abs(clamped_pos - self.position) > 1e-7:
        _updating_opening_items = True
        self.position = clamped_pos
        _updating_opening_items = False
    try:
        sg.update_opening(
            opening_id,
            opening_type=self.opening_type,
            width=self.width,
            height=self.height,
            sill_height=self.sill_height,
            position=self.position,
        )
    except Exception:
        _restore_opening_item_from_graph(self, op)
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
    from .. import find_floorplan_obj, _graph_store
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
        return
    sg, rg, mapper = _graph_store[obj.name]
    op = sg.get_opening(opening_id)
    if op is None:
        return
    max_w = min(MAX_OPENING_WIDTH, sg.max_opening_width_at_position(
        op.wall_id,
        op.position,
        exclude_opening_id=opening_id,
    ))
    if max_w < MIN_OPENING_WIDTH:
        _restore_opening_item_from_graph(self, op)
        return
    clamped = max(MIN_OPENING_WIDTH, min(self.width, max_w))
    if abs(clamped - self.width) > 1e-7:
        _updating_opening_items = True
        self.width = clamped
        _updating_opening_items = False
    try:
        sg.update_opening(opening_id, width=clamped)
    except Exception:
        _restore_opening_item_from_graph(self, op)
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
    from .. import find_floorplan_obj, _graph_store
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
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
        _restore_opening_item_from_graph(self, op)
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
    from .. import find_floorplan_obj, _graph_store
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
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
        _restore_opening_item_from_graph(self, op)
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
    from .. import find_floorplan_obj, _graph_store
    obj = find_floorplan_obj(context)
    if obj is None or not _selection.belongs_to_object(obj) or obj.name not in _graph_store:
        return
    sg, rg, mapper = _graph_store[obj.name]
    op = sg.get_opening(opening_id)
    if op is None:
        return
    clamped = sg.clamp_opening_position(
        op.wall_id,
        op.width,
        self.position,
        exclude_opening_id=opening_id,
    )
    if clamped is None:
        _restore_opening_item_from_graph(self, op)
        return
    if abs(clamped - self.position) > 1e-7:
        _updating_opening_items = True
        self.position = clamped
        _updating_opening_items = False
    try:
        sg.update_opening(opening_id, position=clamped)
    except Exception:
        _restore_opening_item_from_graph(self, op)
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


class FloorPlanSettings(bpy.types.PropertyGroup):
    display_unit: EnumProperty(
        name="Units",
        description="Unit system used for displaying dimensions",
        items=[
            ('M', "Meters (m)", "Display measurements in meters"),
            ('CM', "Centimeters (cm)", "Display measurements in centimeters"),
            ('MM', "Millimeters (mm)", "Display measurements in millimeters"),
            ('FT', "Feet (ft)", "Display measurements in feet"),
            ('IN', "Inches (in)", "Display measurements in inches"),
        ],
        default='M',
        update=_on_display_unit_update,
    )

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
    # Viewport labels — master + per-type toggles.
    show_labels: BoolProperty(
        name="Labels",
        description="Show room, wall and opening labels in the viewport",
        default=True,
    )
    show_room_labels: BoolProperty(
        name="Room Labels",
        description="Show room name labels in the viewport",
        default=True,
    )
    show_wall_labels: BoolProperty(
        name="Wall Labels",
        description="Show wall number and length labels in the viewport",
        default=True,
    )
    show_door_labels: BoolProperty(
        name="Door Labels",
        description="Show door opening labels in the viewport",
        default=True,
    )
    show_window_labels: BoolProperty(
        name="Window Labels",
        description="Show window opening labels in the viewport",
        default=True,
    )
    # Active wall selection — editable props populated by FLOORPLAN_OT_select_wall.
    # The selected element UUID lives in _selection (selection_state.py), not here.
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
    active_wall_start_x: FloatProperty(
        name="Start X",
        description="Wall start junction X position (meters)",
        default=0.0,
        precision=3,
        unit='LENGTH',
        update=_on_wall_start_x_update,
    )
    active_wall_start_y: FloatProperty(
        name="Start Y",
        description="Wall start junction Y position (meters)",
        default=0.0,
        precision=3,
        unit='LENGTH',
        update=_on_wall_start_y_update,
    )
    active_wall_end_x: FloatProperty(
        name="End X",
        description="Wall end junction X position (meters)",
        default=0.0,
        precision=3,
        unit='LENGTH',
        update=_on_wall_end_x_update,
    )
    active_wall_end_y: FloatProperty(
        name="End Y",
        description="Wall end junction Y position (meters)",
        default=0.0,
        precision=3,
        unit='LENGTH',
        update=_on_wall_end_y_update,
    )
    active_wall_mid_normal: FloatProperty(
        name="Middle (Normal)",
        description="Wall midpoint position along wall normal (meters)",
        default=0.0,
        precision=3,
        unit='LENGTH',
        update=_on_wall_mid_normal_update,
    )
    # Active room selection — name editable via the Selected Room panel.
    active_room_name: StringProperty(
        name="Name",
        description="Name of the selected room",
        default="",
        update=_on_room_name_update,
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


def populate_active_wall_props(settings, sg, wall_uuid):
    wall = sg.get_wall(wall_uuid)
    if wall is None:
        return
    j_start = sg.get_junction(wall.junction_start)
    j_end = sg.get_junction(wall.junction_end)
    if j_start is None or j_end is None:
        return

    set_wall_props_updating(True)
    set_wall_xy_props_updating(True)
    try:
        settings.active_wall_thickness = wall.thickness
        settings.active_wall_height = wall.height

        sx, sy = j_start.position
        ex, ey = j_end.position
        dx = ex - sx
        dy = ey - sy
        length = (dx * dx + dy * dy) ** 0.5
        mid_x = (sx + ex) * 0.5
        mid_y = (sy + ey) * 0.5
        mid_normal = 0.0
        if length >= 1e-9:
            nx = -dy / length
            ny = dx / length
            mid_normal = mid_x * nx + mid_y * ny
        settings.active_wall_start_x = sx
        settings.active_wall_start_y = sy
        settings.active_wall_end_x = ex
        settings.active_wall_end_y = ey
        settings.active_wall_mid_normal = mid_normal
    finally:
        set_wall_xy_props_updating(False)
        set_wall_props_updating(False)


def clear_active_wall_props(settings):
    set_wall_props_updating(True)
    set_wall_xy_props_updating(True)
    try:
        settings.active_wall_thickness = 0.0
        settings.active_wall_height = 0.0
        settings.active_wall_start_x = 0.0
        settings.active_wall_start_y = 0.0
        settings.active_wall_end_x = 0.0
        settings.active_wall_end_y = 0.0
        settings.active_wall_mid_normal = 0.0
    finally:
        set_wall_xy_props_updating(False)
        set_wall_props_updating(False)
