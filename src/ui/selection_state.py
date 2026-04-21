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

    def select_wall(self, uuid, context=None):
        # Select a wall; clears any room or opening selection.
        self.wall_id = uuid
        self.room_id = ""
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()

    def select_room(self, uuid, context=None):
        # Select a room; clears wall and opening selection.
        self.wall_id = ""
        self.room_id = uuid
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
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()


_selection = SelectionState()
