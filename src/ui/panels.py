# N-panel sidebar for FloorPlanMaster.
# Sections: Wall Properties (top-level), Tools, Rooms, Settings (under main).
# References: 05_ui_ux_npanel.md

import bpy
import json

from ..utils.constants import DEFAULT_DOOR_WIDTH, DEFAULT_WINDOW_WIDTH
from ..utils.unit_format import format_area, format_length


def _get_panel_floorplan_obj(context):
    from .. import find_floorplan_obj, get_selected_floorplan_obj

    obj = find_floorplan_obj(context)
    if obj is not None:
        return obj
    return get_selected_floorplan_obj(context)


def _sync_room_names_to_object(obj, rg):
    # Sync room names between RoomGraph and object custom properties.
    # Custom properties keyed by "room_name_{room.id}" enable inline prop() editing.
    rooms = rg.get_all_rooms()
    for room in rooms:
        key = f"room_name_{room.id}"
        if key not in obj:
            obj[key] = room.name
        else:
            stored = obj[key]
            if stored != room.name:
                # Graph was updated externally (e.g. new room created with auto-name).
                obj[key] = room.name

    # Clean up orphaned keys for rooms that no longer exist.
    room_ids = {room.id for room in rooms}
    keys_to_remove = [
        k for k in obj.keys()
        if k.startswith("room_name_") and k[len("room_name_"):] not in room_ids
    ]
    for k in keys_to_remove:
        del obj[k]


def _push_room_names_from_object(obj, rg, context=None):
    # Push any user edits from object custom properties back into the RoomGraph.
    # If context is provided, also persists changes and refreshes active_room_name.
    changed = False
    for room in rg.get_all_rooms():
        key = f"room_name_{room.id}"
        if key in obj:
            stored = obj[key]
            if stored != room.name:
                old_name = room.name
                effective_name = rg.set_room_name(room.id, stored)
                if effective_name != stored:
                    obj[key] = effective_name
                if effective_name != old_name:
                    changed = True
    if changed:
        from ..core.sync import persist_room_names
        persist_room_names(obj, rg)
        if context is not None:
            from .selection_state import _selection
            from .properties import set_room_props_updating
            room_uuid = _selection.room_id
            if room_uuid:
                updated_room = rg.get_room(room_uuid)
                if updated_room is not None:
                    set_room_props_updating(True)
                    try:
                        context.scene.floorplan.active_room_name = updated_room.name
                    finally:
                        set_room_props_updating(False)


def _room_walls(sg, room):
    # Return boundary walls in room cycle order.
    walls = []
    n = len(room.cycle)
    for i in range(n):
        jid_a = room.cycle[i]
        jid_b = room.cycle[(i + 1) % n]
        wall = sg.get_wall_between(jid_a, jid_b)
        if wall is not None:
            walls.append(wall)
    return walls


# -- UI-only operator: toggle room expand/collapse in the N-panel --

class FLOORPLAN_OT_toggle_room(bpy.types.Operator):
    bl_idname = "floorplan.toggle_room"
    bl_label = ""
    bl_description = "Expand or collapse room details"
    bl_options = {'INTERNAL'}

    room_id: bpy.props.StringProperty()

    def execute(self, context):
        from .selection_state import _selection

        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"room_expanded_{self.room_id}"
        currently_expanded = bool(obj.get(key, 0))
        obj[key] = 0 if currently_expanded else 1

        if currently_expanded:
            # Collapsing: remove viewport highlight if this room was highlighted.
            if _selection.room_id == self.room_id and not _selection.room_viewport_selected:
                _selection.deselect_all(context)
        else:
            # Expanding: highlight the room in the viewport (no top panel).
            _selection.select_room(self.room_id, context, from_viewport=False, object_name=obj.name)

        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_room_walls(bpy.types.Operator):
    bl_idname = "floorplan.toggle_room_walls"
    bl_label = ""
    bl_description = "Expand or collapse room wall list"
    bl_options = {'INTERNAL'}

    room_id: bpy.props.StringProperty()

    def execute(self, context):
        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"room_walls_expanded_{self.room_id}"
        obj[key] = 0 if bool(obj.get(key, 0)) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_wall_details(bpy.types.Operator):
    bl_idname = "floorplan.toggle_wall_details"
    bl_label = ""
    bl_description = "Expand or collapse wall details"
    bl_options = {'INTERNAL'}

    wall_id: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        from .. import is_floorplan_mode_active
        return is_floorplan_mode_active(context)

    def execute(self, context):
        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"wall_details_expanded_{self.wall_id}"
        obj[key] = 0 if bool(obj.get(key, 0)) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_wall_openings(bpy.types.Operator):
    bl_idname = "floorplan.toggle_wall_openings"
    bl_label = ""
    bl_description = "Expand or collapse opening list for this wall"
    bl_options = {'INTERNAL'}

    wall_id: bpy.props.StringProperty()

    def execute(self, context):
        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"wall_openings_expanded_{self.wall_id}"
        obj[key] = 0 if bool(obj.get(key, 0)) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_wall_position(bpy.types.Operator):
    bl_idname = "floorplan.toggle_wall_position"
    bl_label = ""
    bl_description = "Expand or collapse wall position controls"
    bl_options = {'INTERNAL'}

    wall_id: bpy.props.StringProperty()

    def execute(self, context):
        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"wall_position_expanded_{self.wall_id}"
        obj[key] = 0 if bool(obj.get(key, 0)) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_toggle_room_wall_opening(bpy.types.Operator):
    bl_idname = "floorplan.toggle_room_wall_opening"
    bl_label = ""
    bl_description = "Expand or collapse opening details"
    bl_options = {'INTERNAL'}

    opening_id: bpy.props.StringProperty()

    def execute(self, context):
        obj = _get_panel_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"room_wall_opening_expanded_{self.opening_id}"
        obj[key] = 0 if bool(obj.get(key, 0)) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


class FLOORPLAN_OT_select_wall_from_room(bpy.types.Operator):
    bl_idname = "floorplan.select_wall_from_room"
    bl_label = "Select Wall"
    bl_description = "Select this wall from room details"
    bl_options = {'INTERNAL'}

    wall_id: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        from .. import is_floorplan_mode_active
        return is_floorplan_mode_active(context)

    def execute(self, context):
        from .. import _graph_store, find_floorplan_obj
        from .selection_state import _selection
        from .properties import populate_opening_items, populate_active_wall_props

        obj = find_floorplan_obj(context)
        if obj is None or obj.name not in _graph_store:
            return {'CANCELLED'}

        sg, _, _ = _graph_store[obj.name]
        wall = sg.get_wall(self.wall_id)
        if wall is None:
            return {'CANCELLED'}

        settings = context.scene.floorplan
        _selection.select_wall(self.wall_id, context, object_name=obj.name)
        populate_active_wall_props(settings, sg, self.wall_id)
        populate_opening_items(settings, sg, self.wall_id)
        context.area.tag_redraw()
        return {'FINISHED'}


# -- Room Properties — separate top-level panel (appears when a room is selected) --

class FLOORPLAN_PT_room_properties(bpy.types.Panel):
    bl_label = "Selected Room"
    bl_idname = "FLOORPLAN_PT_room_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 10

    @classmethod
    def poll(cls, context):
        from .. import find_floorplan_obj
        from .selection_state import _selection
        obj = find_floorplan_obj(context)
        # Show only when the room was selected by clicking in the viewport,
        # not when the room detail dropdown is open in the N-panel.
        return _selection.has_room_for_object(obj) and _selection.room_viewport_selected

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan
        display_unit = settings.display_unit
        from .. import is_floorplan_mode_active

        mode_active = is_floorplan_mode_active(context)
        root = layout.box()

        from .. import _graph_store, find_floorplan_obj
        from .selection_state import _selection
        obj = find_floorplan_obj(context)
        room_uuid = _selection.room_id
        if obj is None or obj.name not in _graph_store:
            return
        sg, rg, _ = _graph_store[obj.name]
        room = rg.get_room(room_uuid)
        if room is None:
            return

        root.prop(settings, "active_room_name")
        # root.separator()
        col = root.column(align=True)
        for label_text in (
            f"Area: {format_area(room.area, display_unit)}",
            f"Perimeter: {format_length(room.perimeter, display_unit)}",
            f"Walls: {len(room.cycle)}",
            f"Height: {format_length(room.height, display_unit)}",
        ):
            row = col.row()
            row.scale_y = 1.4
            row.label(text=label_text)


# -- Wall Properties — separate top-level panel (appears when a wall is selected) --

class FLOORPLAN_PT_wall_properties(bpy.types.Panel):
    bl_label = "Selected Wall Properties"
    bl_idname = "FLOORPLAN_PT_wall_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 11

    @classmethod
    def poll(cls, context):
        from .. import find_floorplan_obj
        from .selection_state import _selection
        obj = find_floorplan_obj(context)
        return _selection.has_wall_for_object(obj)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan
        display_unit = settings.display_unit

        from .. import _graph_store, find_floorplan_obj, is_floorplan_mode_active
        from .selection_state import _selection
        obj = find_floorplan_obj(context)
        mode_active = is_floorplan_mode_active(context)

        wall_uuid = _selection.wall_id
        wall_label = "Wall"
        if obj is not None and obj.name in _graph_store:
            sg, _, mapper = _graph_store[obj.name]
            wall = sg.get_wall(wall_uuid)
            if wall is not None:
                wall_num = mapper.get(wall_uuid)
                length = sg.wall_length(wall_uuid)
                wall_label = f"Wall #{wall_num}  ({format_length(length, display_unit)})"

        root = layout.box()
        header = root.row(align=True)
        split = header.split(factor=0.9, align=True)
        split.label(text=wall_label, icon='MOD_BUILD')
        split.operator("floorplan.remove_selected_wall", text="", icon='X')

        col = root.column(align=True)
        col.enabled = mode_active
        col.prop(settings, "active_wall_thickness")
        col.prop(settings, "active_wall_height")

        pos_box = root.box()
        pos_expanded = bool(obj.get(f"wall_position_expanded_{wall_uuid}", 0)) if obj is not None else False
        pos_header = pos_box.row(align=True)
        pos_toggle = pos_header.operator(
            "floorplan.toggle_wall_position",
            icon='TRIA_DOWN' if pos_expanded else 'TRIA_RIGHT',
            text="",
            emboss=False,
        )
        pos_toggle.wall_id = wall_uuid
        pos_header.label(text="Position", icon='EMPTY_AXIS')

        if pos_expanded:
            start_col = pos_box.column(align=True)
            start_col.enabled = mode_active
            start_col.label(text="Start")
            start_col.prop(settings, "active_wall_start_x")
            start_col.prop(settings, "active_wall_start_y")

            end_col = pos_box.column(align=True)
            end_col.enabled = mode_active
            end_col.label(text="End")
            end_col.prop(settings, "active_wall_end_x")
            end_col.prop(settings, "active_wall_end_y")

            mid_col = pos_box.column(align=True)
            mid_col.enabled = mode_active
            mid_col.label(text="Middle")
            mid_col.prop(settings, "active_wall_mid_normal")

        root.separator()
        row = root.row(align=True)
        door_enabled = True
        window_enabled = True
        if obj is not None and obj.name in _graph_store:
            sg, _, _ = _graph_store[obj.name]
            door_enabled = sg.can_fit_opening(wall_uuid, DEFAULT_DOOR_WIDTH)
            window_enabled = sg.can_fit_opening(wall_uuid, DEFAULT_WINDOW_WIDTH)

        door_row = row.row(align=True)
        door_row.enabled = door_enabled
        op = door_row.operator("floorplan.add_opening", text="Add Door", icon='MESH_PLANE')
        op.opening_type = 'DOOR'
        window_row = row.row(align=True)
        window_row.enabled = window_enabled
        op = window_row.operator("floorplan.add_opening", text="Add Window", icon='WINDOW')
        op.opening_type = 'WINDOW'
        if not door_enabled and not window_enabled:
            root.label(text="No space for another opening", icon='INFO')

        # List existing openings on this wall.
        if obj is not None and obj.name in _graph_store:
            sg, _, mapper = _graph_store[obj.name]
            openings = sg.get_openings_for_wall(wall_uuid)
            if openings:
                root.separator()

                # Collapsible openings header
                header = root.row(align=True)
                header.prop(
                    settings, "openings_expanded",
                    icon='TRIA_DOWN' if settings.openings_expanded else 'TRIA_RIGHT',
                    text="", emboss=False,
                )
                header.label(text="Openings", icon='OUTLINER_OB_LATTICE')

                if settings.openings_expanded:
                    items_by_id = {item.opening_id: item for item in settings.opening_items}
                    for opening in openings:
                        item = items_by_id.get(opening.id)
                        if item is None:
                            continue
                        box = root.box()

                        # Header row: expand toggle + type icon + #N + remove button
                        hdr = box.row(align=True)
                        hdr.prop(
                            item, "expanded",
                            icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT',
                            text="", emboss=False,
                        )
                        op_num = mapper.get(opening.id)
                        type_label = "Door" if item.opening_type == 'DOOR' else "Window"
                        hdr.label(text=f"{type_label} #{op_num}")
                        remove_op = hdr.operator("floorplan.remove_opening", text="", icon='X')
                        remove_op.opening_id = opening.id

                        if item.expanded:
                            col = box.column(align=True)
                            col.prop(item, "opening_type")
                            col.prop(item, "width")
                            col.prop(item, "height")
                            if item.opening_type == 'WINDOW':
                                col.prop(item, "sill_height")
                            col.prop(item, "position")


# -- Main panel (tab container) --

class FLOORPLAN_PT_main(bpy.types.Panel):
    bl_label = "FloorPlanMaster"
    bl_idname = "FLOORPLAN_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 0

    def draw(self, context):
        pass  # Sub-panels fill content.


# -- Section: Tools --

class FLOORPLAN_PT_tools(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "FLOORPLAN_PT_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "FLOORPLAN_PT_main"

    def draw_header(self, context):
        self.layout.label(text="", icon='GREASEPENCIL')

    def draw(self, context):
        layout = self.layout
        layout.operator("floorplan.pencil_tool", text="Draw with Pencil", icon='GREASEPENCIL')
        layout.separator()
        layout.operator("floorplan.insert_room", text="Insert Room", icon='MESH_PLANE')
        layout.separator()
        layout.operator("floorplan.finalize", text="Bake", icon='RENDER_RESULT')


# -- Section: Rooms --

class FLOORPLAN_PT_rooms(bpy.types.Panel):
    bl_label = "Rooms"
    bl_idname = "FLOORPLAN_PT_rooms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "FLOORPLAN_PT_main"

    def draw_header(self, context):
        self.layout.label(text="", icon='HOME')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan
        display_unit = settings.display_unit
        from .selection_state import _selection
        from .. import (
            _graph_store,
            reset_graphs_for_obj,
            has_floorplan_obj,
            is_floorplan_mode_active,
            get_selected_floorplan_obj,
        )

        mode_active = is_floorplan_mode_active(context)

        obj = _get_panel_floorplan_obj(context)

        if obj is None:
            if has_floorplan_obj(context):
                layout.label(text="Activate a floor plan object.", icon='INFO')
            else:
                layout.label(text="No floor plan in scene.", icon='INFO')
            return

        if not mode_active:
            lock_box = layout.box()
            lock_box.label(text="Read-only while FloorPlan mode is off", icon='LOCKED')
            if get_selected_floorplan_obj(context) is not None:
                lock_box.operator(
                    "floorplan.toggle_mode",
                    text="Enable FloorPlan Mode",
                    icon='PLAY',
                )

        if obj.name not in _graph_store:
            # Lazy-populate after VS Code extension module reload,
            # which does importlib.reload() without calling register().
            reset_graphs_for_obj(obj)

        sg, rg, _mapper = _graph_store[obj.name]
        # Push pending inline edits only in semantic mode where edits are allowed.
        if mode_active:
            _push_room_names_from_object(obj, rg, context)
        rooms = rg.get_all_rooms()

        if not rooms:
            layout.label(text="No rooms detected yet.", icon='INFO')
            return

        for room in rooms:
            box = layout.box()

            # Header row: expand toggle + editable name + remove button
            header = box.row(align=True)
            expanded = bool(obj.get(f"room_expanded_{room.id}", 0))
            toggle = header.operator(
                "floorplan.toggle_room",
                icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT',
                text="", emboss=False,
            )
            toggle.room_id = room.id

            key = f"room_name_{room.id}"
            if key in obj:
                name_row = header.row(align=True)
                name_row.enabled = mode_active
                name_row.prop(obj, f'["{key}"]', text="")
            else:
                header.label(text=room.name)

            remove_row = header.row(align=True)
            remove_row.enabled = mode_active
            remove_op = remove_row.operator("floorplan.remove_room", text="", icon='X')
            remove_op.room_id = room.id
            remove_op.room_cycle_key = json.dumps(list(rg._cycle_key(room.cycle)))

            if expanded:
                col = box.column(align=True)
                for label_text in (
                    f"Area: {format_area(room.area, display_unit)}",
                    f"Perimeter: {format_length(room.perimeter, display_unit)}",
                    f"Height: {format_length(room.height, display_unit)}",
                ):
                    row = col.row()
                    row.scale_y = 1.4
                    row.label(text=label_text)

                walls = _room_walls(sg, room)
                if walls:
                    col.separator()
                    walls_box = col.box()
                    walls_col = walls_box.column(align=True)
                    walls_expanded = bool(obj.get(f"room_walls_expanded_{room.id}", 1))
                    walls_header = walls_col.row(align=True)
                    walls_toggle = walls_header.operator(
                        "floorplan.toggle_room_walls",
                        icon='TRIA_DOWN' if walls_expanded else 'TRIA_RIGHT',
                        text="",
                        emboss=False,
                    )
                    walls_toggle.room_id = room.id
                    walls_header.label(text=f"Room Walls ({len(walls)})", icon='MOD_BUILD')
                    if not walls_expanded:
                        continue

                    walls_col.separator()

                    for wall in walls:
                        wall_box = walls_col.box()
                        wall_row = wall_box.row(align=True)
                        wall_num = _mapper.get(wall.id)
                        wall_len = sg.wall_length(wall.id)
                        details_expanded = bool(obj.get(f"wall_details_expanded_{wall.id}", 0))
                        wall_selected = _selection.wall_id == wall.id
                        wall_toggle_row = wall_row.row(align=True)
                        wall_toggle_row.enabled = mode_active
                        wall_toggle = wall_toggle_row.operator(
                            "floorplan.toggle_wall_details",
                            icon='TRIA_DOWN' if details_expanded else 'TRIA_RIGHT',
                            text="",
                            emboss=False,
                        )
                        wall_toggle.wall_id = wall.id
                        wall_row.label(text=f"Wall #{wall_num} ({format_length(wall_len, display_unit)})")
                        select_row = wall_row.row(align=True)
                        select_row.enabled = mode_active
                        op = select_row.operator(
                            "floorplan.select_wall_from_room",
                            text="",
                            icon='RESTRICT_SELECT_OFF',
                        )
                        op.wall_id = wall.id

                        if not details_expanded:
                            continue

                        details = wall_box.column(align=True)
                        if mode_active and wall_selected:
                            details.prop(settings, "active_wall_thickness")
                            details.prop(settings, "active_wall_height")

                            pos_box = details.box()
                            pos_expanded = bool(obj.get(f"wall_position_expanded_{wall.id}", 0))
                            pos_header = pos_box.row(align=True)
                            pos_toggle = pos_header.operator(
                                "floorplan.toggle_wall_position",
                                icon='TRIA_DOWN' if pos_expanded else 'TRIA_RIGHT',
                                text="",
                                emboss=False,
                            )
                            pos_toggle.wall_id = wall.id
                            pos_header.label(text="Position", icon='EMPTY_AXIS')

                            if pos_expanded:
                                start_col = pos_box.column(align=True)
                                start_col.label(text="Start")
                                start_col.prop(settings, "active_wall_start_x")
                                start_col.prop(settings, "active_wall_start_y")

                                end_col = pos_box.column(align=True)
                                end_col.label(text="End")
                                end_col.prop(settings, "active_wall_end_x")
                                end_col.prop(settings, "active_wall_end_y")

                                mid_col = pos_box.column(align=True)
                                mid_col.label(text="Middle")
                                mid_col.prop(settings, "active_wall_mid_normal")
                        else:
                            details.label(text=f"Thickness: {format_length(wall.thickness, display_unit)}")
                            details.label(text=f"Height: {format_length(wall.height, display_unit)}")

                        openings = sg.get_openings_for_wall(wall.id)
                        openings_expanded = bool(obj.get(f"wall_openings_expanded_{wall.id}", 0))
                        openings_header = details.row(align=True)
                        openings_toggle = openings_header.operator(
                            "floorplan.toggle_wall_openings",
                            icon='TRIA_DOWN' if openings_expanded else 'TRIA_RIGHT',
                            text="",
                            emboss=False,
                        )
                        openings_toggle.wall_id = wall.id
                        openings_header.label(text=f"Openings ({len(openings)})")
                        if not openings_expanded:
                            continue

                        if openings:
                            items_by_id = {item.opening_id: item for item in settings.opening_items} if (mode_active and wall_selected) else {}
                            for opening in openings:
                                opening_expanded = bool(obj.get(f"room_wall_opening_expanded_{opening.id}", 0))
                                opening_box = details.box()
                                opening_header = opening_box.row(align=True)
                                opening_type = "Door" if opening.opening_type == 'DOOR' else "Window"
                                opening_num = _mapper.get(opening.id)
                                opening_toggle = opening_header.operator(
                                    "floorplan.toggle_room_wall_opening",
                                    icon='TRIA_DOWN' if opening_expanded else 'TRIA_RIGHT',
                                    text="",
                                    emboss=False,
                                )
                                opening_toggle.opening_id = opening.id
                                opening_header.label(text=f"{opening_type} #{opening_num}")

                                if not opening_expanded:
                                    continue

                                opening_col = opening_box.column(align=True)
                                item = items_by_id.get(opening.id)
                                if mode_active and wall_selected and item is not None:
                                    opening_col.prop(item, "opening_type")
                                    opening_col.prop(item, "width")
                                    opening_col.prop(item, "height")
                                    if item.opening_type == 'WINDOW':
                                        opening_col.prop(item, "sill_height")
                                    opening_col.prop(item, "position")
                                else:
                                    opening_col.label(text=f"Width: {format_length(opening.width, display_unit)}")
                                    opening_col.label(text=f"Height: {format_length(opening.height, display_unit)}")
                                    if opening.opening_type == 'WINDOW':
                                        opening_col.label(text=f"Sill: {format_length(opening.sill_height, display_unit)}")
                                    opening_col.label(text=f"Position: {opening.position:.2f}")


# -- Section: Settings --

class FLOORPLAN_PT_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "FLOORPLAN_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "FLOORPLAN_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='PREFERENCES')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan

        col = layout.column(align=True)
        col.prop(settings, "display_unit")
        col.separator()
        col.prop(settings, "default_thickness")
        col.prop(settings, "default_height")
        col.separator()
        row = col.row(align=True)
        toggles = row.row(align=True)
        toggles.enabled = settings.show_wall_highlight
        toggles.prop(settings, "show_wall_edge_highlights", text="", toggle=True, icon='MOD_BUILD')
        toggles.prop(settings, "show_door_edge_highlights", text="", toggle=True, icon='MESH_PLANE')
        toggles.prop(settings, "show_window_edge_highlights", text="", toggle=True, icon='WINDOW')
        row.prop(settings, "show_wall_highlight", text="All Highlights", toggle=True, icon='SHADING_BBOX')

        col.separator()
        row = col.row(align=True)
        label_toggles = row.row(align=True)
        label_toggles.enabled = settings.show_labels
        label_toggles.prop(settings, "show_room_labels", text="", toggle=True, icon='HOME')
        label_toggles.prop(settings, "show_wall_labels", text="", toggle=True, icon='MOD_BUILD')
        label_toggles.prop(settings, "show_door_labels", text="", toggle=True, icon='MESH_PLANE')
        label_toggles.prop(settings, "show_window_labels", text="", toggle=True, icon='WINDOW')
        row.prop(settings, "show_labels", text="All Labels", toggle=True, icon='SORTALPHA')
