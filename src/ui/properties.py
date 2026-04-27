# PropertyGroups and their update callbacks for FloorPlanMaster.
# OpeningItem — per-opening editable item in the N-panel list.
# FloorPlanSettings — scene-level addon settings (PointerProperty on Scene).
# populate_opening_items — repopulate the opening list after wall selection / CRUD.
# set_wall_props_updating — expose the circular-update guard for operators.

import bpy
from bpy.props import (
    BoolProperty, CollectionProperty, EnumProperty,
    FloatProperty, StringProperty,
)

from .selection_state import _selection
from ..core.sync import sync_graph_to_mesh
from ..utils.constants import (
    DEFAULT_DOOR_WIDTH, DEFAULT_WINDOW_WIDTH,
    DEFAULT_DOOR_HEIGHT, DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_SILL,
    MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
    MIN_OPENING_HEIGHT, MAX_HEIGHT,
)

_updating_wall_props = False
_updating_opening_items = False
_updating_room_props = False


def set_wall_props_updating(val: bool) -> None:
    global _updating_wall_props
    _updating_wall_props = val


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
    rg.set_room_name(room_uuid, self.active_room_name)
    # Keep the inline rooms-list custom property in sync.
    obj[f"room_name_{room_uuid}"] = self.active_room_name
    persist_room_names(obj, rg)


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
    sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)


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
    sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)


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
