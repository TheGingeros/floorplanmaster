# N-panel sidebar for FloorPlanMaster.
# Three sections: Tools, Rooms, Settings.
# References: 05_ui_ux_npanel.md

import bpy

from ..operators.pencil_tool import _get_floorplan_obj


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


# -- Main panel (tab header) --

class FLOORPLAN_PT_main(bpy.types.Panel):
    bl_label = "FloorPlanMaster"
    bl_idname = "FLOORPLAN_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"

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

    def draw(self, context):
        layout = self.layout
        from .. import _graph_store

        obj = None
        for o in context.scene.objects:
            if o.get("is_floorplan"):
                obj = o
                break

        if obj is None or obj.name not in _graph_store:
            layout.label(text="No floor plan in scene.", icon='INFO')
            return

        sg, rg, _mapper = _graph_store[obj.name]
        rooms = rg.get_all_rooms()

        if not rooms:
            layout.label(text="No rooms detected yet.", icon='INFO')
            return

        for room in rooms:
            box = layout.box()

            # Room name — inline editable text field via object custom property
            # (key must be initialised by the operator that created the room).
            key = f"room_name_{room.id}"
            if key in obj:
                box.prop(obj, f'["{key}"]', text="", icon='HOME')
            else:
                box.label(text=room.name, icon='HOME')

            # Metrics.
            col = box.column(align=True)
            col.label(text=f"Area: {room.area:.2f} m²")
            col.label(text=f"Perimeter: {room.perimeter:.2f} m")
            col.label(text=f"Height: {room.height:.1f} m")

            # Walls count.
            wall_count = len(room.cycle)
            col.label(text=f"Walls: {wall_count}")


# -- Section: Settings --

class FLOORPLAN_PT_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "FLOORPLAN_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "FLOORPLAN_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.floorplan

        col = layout.column(align=True)
        col.prop(settings, "default_thickness")
        col.prop(settings, "default_height")


# -- Section: Wall Properties (visible only when a wall is selected) --

class FLOORPLAN_PT_wall_properties(bpy.types.Panel):
    bl_label = "Wall Properties"
    bl_idname = "FLOORPLAN_PT_wall_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "FLOORPLAN_PT_main"

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
