# N-panel sidebar for FloorPlanMaster.
# Sections: Wall Properties (top-level), Tools, Rooms, Settings (under main).
# References: 05_ui_ux_npanel.md

import bpy


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


def _push_room_names_from_object(obj, rg):
    # Push any user edits from object custom properties back into the RoomGraph.
    for room in rg.get_all_rooms():
        key = f"room_name_{room.id}"
        if key in obj:
            stored = obj[key]
            if stored != room.name:
                rg.set_room_name(room.id, stored)


# -- UI-only operator: toggle room expand/collapse in the N-panel --

class FLOORPLAN_OT_toggle_room(bpy.types.Operator):
    bl_idname = "floorplan.toggle_room"
    bl_label = ""
    bl_description = "Expand or collapse room details"
    bl_options = {'INTERNAL'}

    room_id: bpy.props.StringProperty()

    def execute(self, context):
        from .. import find_floorplan_obj
        obj = find_floorplan_obj(context)
        if obj is None:
            return {'CANCELLED'}
        key = f"room_expanded_{self.room_id}"
        obj[key] = 0 if obj.get(key, 0) else 1
        context.area.tag_redraw()
        return {'FINISHED'}


# -- Wall Properties — separate top-level panel (above main) --

class FLOORPLAN_PT_wall_properties(bpy.types.Panel):
    bl_label = "Selected Wall Properties"
    bl_idname = "FLOORPLAN_PT_wall_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "floorplan"):
            return False
        return context.scene.floorplan.active_wall_id != ""

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan

        from .. import _graph_store, find_floorplan_obj
        obj = find_floorplan_obj(context)

        wall_uuid = settings.active_wall_id
        wall_label = "Wall"
        if obj is not None and obj.name in _graph_store:
            sg, _, mapper = _graph_store[obj.name]
            wall = sg.get_wall(wall_uuid)
            if wall is not None:
                wall_num = mapper.get(wall_uuid)
                length = sg.wall_length(wall_uuid)
                wall_label = f"Wall #{wall_num}  ({length:.2f} m)"

        layout.label(text=wall_label, icon='MOD_BUILD')

        col = layout.column(align=True)
        col.prop(settings, "active_wall_thickness")
        col.prop(settings, "active_wall_height")

        layout.separator()
        row = layout.row(align=True)
        op = row.operator("floorplan.add_opening", text="Add Door", icon='MESH_PLANE')
        op.opening_type = 'DOOR'
        op = row.operator("floorplan.add_opening", text="Add Window", icon='WINDOW')
        op.opening_type = 'WINDOW'

        # List existing openings on this wall.
        if obj is not None and obj.name in _graph_store:
            sg, _, mapper = _graph_store[obj.name]
            openings = sg.get_openings_for_wall(wall_uuid)
            if openings:
                layout.separator()

                # Collapsible openings header
                header = layout.row(align=True)
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
                        box = layout.box()

                        # Header row: expand toggle + type icon + #N + remove button
                        hdr = box.row(align=True)
                        hdr.prop(
                            item, "expanded",
                            icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT',
                            text="", emboss=False,
                        )
                        op_num = mapper.get(opening.id)
                        type_icon = 'MESH_PLANE' if item.opening_type == 'DOOR' else 'WINDOW'
                        hdr.label(text=f"#{op_num}", icon=type_icon)
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
    bl_order = 1

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
        from .. import _graph_store, reset_graphs_for_obj, find_floorplan_obj

        obj = find_floorplan_obj(context)

        if obj is None:
            layout.label(text="No floor plan in scene.", icon='INFO')
            return

        if obj.name not in _graph_store:
            # Lazy-populate after VS Code extension module reload,
            # which does importlib.reload() without calling register().
            reset_graphs_for_obj(obj)

        sg, rg, _mapper = _graph_store[obj.name]
        rooms = rg.get_all_rooms()

        if not rooms:
            layout.label(text="No rooms detected yet.", icon='INFO')
            return

        for room in rooms:
            box = layout.box()

            # Header row: expand toggle + editable name
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
                header.prop(obj, f'["{key}"]', text="")
            else:
                header.label(text=room.name)

            if expanded:
                col = box.column(align=True)
                for label_text in (
                    f"Area: {room.area:.2f} m²",
                    f"Perimeter: {room.perimeter:.2f} m",
                    f"Walls: {len(room.cycle)}",
                    f"Height: {room.height:.1f} m",
                ):
                    row = col.row()
                    row.scale_y = 1.4
                    row.label(text=label_text)


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
        col.prop(settings, "default_thickness")
        col.prop(settings, "default_height")
