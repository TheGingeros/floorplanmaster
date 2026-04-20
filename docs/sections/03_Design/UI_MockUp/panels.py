# N-panel UI for FloorPlanMaster UI MockUp.
# All panels are placebo — interactive layout with static data.

import bpy


def _ensure_data(context):
    # Schedule deferred population if data is missing (cannot write during draw).
    settings = context.scene.mockup_fp
    if len(settings.rooms) == 0:
        import bpy as _bpy
        from . import _populate_mockup_data as _pop
        if not _bpy.app.timers.is_registered(_pop):
            _bpy.app.timers.register(_pop, first_interval=0.0)


# Wall Properties — separate top-level panel at the top of the tab.
# Always visible in this mockup (no poll condition).

class MOCKUP_PT_wall_properties(bpy.types.Panel):
    bl_label = "Selected Wall Properties"
    bl_idname = "MOCKUP_PT_wall_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mockup_fp

        layout.label(text="Wall #3  (3.50 m)", icon='MOD_BUILD')

        col = layout.column(align=True)
        col.prop(settings, "active_wall_thickness")
        col.prop(settings, "active_wall_height")

        layout.separator()
        row = layout.row(align=True)
        op = row.operator("mockup_fp.add_opening", text="Add Door", icon='MESH_PLANE')
        op.opening_type = 'DOOR'
        op = row.operator("mockup_fp.add_opening", text="Add Window", icon='WINDOW')
        op.opening_type = 'WINDOW'

        # Openings list
        _ensure_data(context)
        if len(settings.openings) > 0:
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
                for idx, opening in enumerate(settings.openings):
                    box = layout.box()

                    # Header row: expand toggle + editable name + remove button
                    header = box.row(align=True)
                    header.prop(
                        opening, "expanded",
                        icon='TRIA_DOWN' if opening.expanded else 'TRIA_RIGHT',
                        text="", emboss=False,
                    )
                    type_icon = 'MESH_PLANE' if opening.opening_type == 'DOOR' else 'WINDOW'
                    header.label(text="", icon=type_icon)
                    header.prop(opening, "opening_name", text="")
                    remove = header.operator("mockup_fp.remove_opening", text="", icon='X')
                    remove.index = idx

                    if opening.expanded:
                        col = box.column(align=True)
                        col.prop(opening, "opening_type")
                        col.prop(opening, "width")
                        col.prop(opening, "height")
                        if opening.opening_type == 'WINDOW':
                            col.prop(opening, "sill_height")
                        col.prop(opening, "position")




# Main panel (tab container)

class MOCKUP_PT_main(bpy.types.Panel):
    bl_label = "FloorPlanMaster"
    bl_idname = "MOCKUP_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_order = 1

    def draw(self, context):
        pass


# Sub-panel: Tools

class MOCKUP_PT_tools(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "MOCKUP_PT_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "MOCKUP_PT_main"

    def draw(self, context):
        layout = self.layout
        layout.operator("mockup_fp.pencil_tool_op", text="Draw with Pencil", icon='GREASEPENCIL')
        layout.separator()
        layout.operator("mockup_fp.insert_room", text="Insert Room", icon='MESH_PLANE')
        layout.separator()
        layout.operator("mockup_fp.finalize", text="Bake", icon='RENDER_RESULT')


# Sub-panel: Rooms

class MOCKUP_PT_rooms(bpy.types.Panel):
    bl_label = "Rooms"
    bl_idname = "MOCKUP_PT_rooms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "MOCKUP_PT_main"

    def draw_header(self, context):
        self.layout.label(text="", icon='HOME')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mockup_fp
        _ensure_data(context)

        if len(settings.rooms) == 0:
            layout.label(text="No rooms detected yet.", icon='INFO')
            return

        for idx, room in enumerate(settings.rooms):
            box = layout.box()

            # Header row: expand+select toggle + editable name + X remove button
            header = box.row(align=True)
            toggle = header.operator(
                "mockup_fp.toggle_room",
                icon='TRIA_DOWN' if room.expanded else 'TRIA_RIGHT',
                text="", emboss=False,
            )
            toggle.index = idx
            header.prop(room, "room_name", text="")
            op = header.operator("mockup_fp.remove_room", text="", icon='X')
            op.index = idx

            if room.expanded:
                col = box.column(align=True)
                for label_text in (
                    f"Area: {room.area:.2f} m\u00b2",
                    f"Perimeter: {room.perimeter:.2f} m",
                    f"Walls: {room.wall_count}",
                ):
                    row = col.row()
                    row.scale_y = 1.4
                    row.label(text=label_text)
                col.separator(factor=0.5)
                col.prop(room, "height")


# Sub-panel: Settings

class MOCKUP_PT_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "MOCKUP_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "MOCKUP_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mockup_fp

        col = layout.column(align=True)
        col.prop(settings, "display_unit")
        col.separator()
        col.prop(settings, "default_thickness")
        col.prop(settings, "default_height")


# Sub-panel: Overlay Settings

class MOCKUP_PT_overlay(bpy.types.Panel):
    bl_label = "Overlay Settings"
    bl_idname = "MOCKUP_PT_overlay"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FloorPlanMaster"
    bl_parent_id = "MOCKUP_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mockup_fp

        col = layout.column(align=True)
        col.prop(settings, "show_dimensions", icon='DRIVER_DISTANCE')
        col.prop(settings, "show_room_colors", icon='COLOR')
        col.prop(settings, "show_room_labels", icon='SORTALPHA')
        col.prop(settings, "show_wall_highlight", icon='SHADING_BBOX')
        col.prop(settings, "show_gizmos", icon='GIZMO')


# Finalize popover

def get_panel_classes():
    return [
        MOCKUP_PT_wall_properties,
        MOCKUP_PT_main,
        MOCKUP_PT_tools,
        MOCKUP_PT_rooms,
        MOCKUP_PT_settings,
        MOCKUP_PT_overlay,
    ]
