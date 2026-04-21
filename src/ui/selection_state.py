# Selection state — module-level singleton tracking which element is selected.
# Pure Python, no bpy — safe to import without Blender (pytest).
#
# Usage:
#   from .selection_state import _selection
#   _selection.select_wall(uuid, context)   # sets wall, clears room/opening
#   _selection.select_room(uuid, context)   # sets room, clears wall/opening
#   _selection.select_opening(uuid)         # sets opening; wall context preserved
#   _selection.deselect_all(context)        # clears everything
#
# Overlay layers and GizmoGroup.draw_prepare() read .wall_id / .room_id /
# .opening_id directly.  N-panel poll() functions check bool(_selection.wall_id).


class SelectionState:
    def __init__(self):
        self.wall_id = ""
        self.room_id = ""
        self.opening_id = ""
        # True when the room was selected by clicking in the viewport.
        # False when the room is only highlighted because its panel dropdown is open.
        # Used by FLOORPLAN_PT_room_properties.poll() to decide whether to show
        # the top-panel with room details (viewport click) or just the overlay
        # highlight (panel dropdown open).
        self.room_viewport_selected = False

    def select_wall(self, uuid, context=None):
        # Select a wall; clears any room or opening selection.
        self.wall_id = uuid
        self.room_id = ""
        self.room_viewport_selected = False
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()

    def select_room(self, uuid, context=None, from_viewport=False):
        # Select a room; clears wall and opening selection.
        # from_viewport=True: clicked in 3D view — show the top properties panel.
        # from_viewport=False: room dropdown opened in N-panel — highlight only,
        #                      do NOT show the top panel.
        self.wall_id = ""
        self.room_id = uuid
        self.room_viewport_selected = from_viewport
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()

    def select_opening(self, uuid, context=None):
        # Select an opening (wall context is preserved for the properties panel).
        self.opening_id = uuid
        if context is not None:
            context.area.tag_redraw()

    def deselect_all(self, context=None):
        # Clear every selection.
        self.wall_id = ""
        self.room_id = ""
        self.room_viewport_selected = False
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()


_selection = SelectionState()
