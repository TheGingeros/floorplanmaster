# Selection state — module-level singleton tracking which element is selected.
# Pure Python, no bpy — safe to import without Blender (pytest).
#
# Usage:
#   from .selection_state import _selection
#   _selection.select_wall(uuid, context, object_name=obj.name)
#   _selection.select_room(uuid, context, object_name=obj.name)
#   _selection.select_opening(uuid)         # keeps the current object context
#   _selection.deselect_all(context)        # clears everything
#
# Overlay layers and panel poll() functions read .object_name plus
# .wall_id / .room_id / .opening_id to keep selection scoped to one object.


class SelectionState:
    def __init__(self):
        self.object_name = ""
        self.wall_id = ""
        self.room_id = ""
        self.opening_id = ""
        # True when the room was selected by clicking in the viewport.
        # False when the room is only highlighted because its panel dropdown is open.
        # Used by FLOORPLAN_PT_room_properties.poll() to decide whether to show
        # the top-panel with room details (viewport click) or just the overlay
        # highlight (panel dropdown open).
        self.room_viewport_selected = False

    def belongs_to_object(self, obj):
        return bool(obj is not None and self.object_name and obj.name == self.object_name)

    def has_wall_for_object(self, obj):
        return bool(self.wall_id and self.belongs_to_object(obj))

    def has_room_for_object(self, obj):
        return bool(self.room_id and self.belongs_to_object(obj))

    def select_wall(self, uuid, context=None, object_name=""):
        # Select a wall; clears any room or opening selection.
        self.object_name = object_name or ""
        self.wall_id = uuid
        self.room_id = ""
        self.room_viewport_selected = False
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()

    def select_room(self, uuid, context=None, from_viewport=False, object_name=""):
        # Select a room; clears wall and opening selection.
        # from_viewport=True: clicked in 3D view — show the top properties panel.
        # from_viewport=False: room dropdown opened in N-panel — highlight only,
        #                      do NOT show the top panel.
        self.object_name = object_name or ""
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
        self.object_name = ""
        self.wall_id = ""
        self.room_id = ""
        self.room_viewport_selected = False
        self.opening_id = ""
        if context is not None:
            context.area.tag_redraw()


_selection = SelectionState()
