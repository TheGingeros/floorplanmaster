# N-panel sidebar for FloorPlanMaster.
# Three sections: Tools, Rooms, Settings.
# References: 05_ui_ux_npanel.md

import bpy

from ..operators.pencil_tool import _get_floorplan_obj


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

        sg, rg = _graph_store[obj.name]
        rooms = rg.get_all_rooms()

        if not rooms:
            layout.label(text="No rooms detected yet.", icon='INFO')
            return

        for room in rooms:
            box = layout.box()

            # Room header row: name + type.
            row = box.row()
            name = room.name if room.name else f"Room {room.id[:8]}"
            row.label(text=name, icon='HOME')
            row.label(text=room.room_type.name)

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
        col.separator()
        col.prop(settings, "grid_density")
        col.prop(settings, "dimension_text_size")
