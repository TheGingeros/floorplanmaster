# FP2 — Select Wall / Room operator
# Click anywhere in the viewport to select a wall or room (or deselect if clicking empty space).
# Projects wall 3D boxes and room floor polygons to 2D screen space and tests mouse against them.
# Works in any view (ortho, perspective, any angle).
# References: 04_features_fp2.md

import bpy
from bpy_extras import view3d_utils

from mathutils import Vector

from ..core.sync import _compute_wall_quad
from ..utils.math_helpers import point_in_polygon
from ..ui.selection_state import _selection


def _raycast_floorplan_object(context, mx, my):
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None

    coord = (float(mx), float(my))
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    depsgraph = context.evaluated_depsgraph_get()
    hit, _location, _normal, _index, obj, _matrix = context.scene.ray_cast(
        depsgraph,
        origin,
        direction,
    )
    if hit and obj is not None and obj.get("is_floorplan"):
        return obj
    return None


def _clear_semantic_selection_ui(context, settings):
    from ..ui.properties import set_room_props_updating, set_wall_props_updating

    _selection.deselect_all(context)

    set_wall_props_updating(True)
    try:
        settings.active_wall_thickness = 0.0
        settings.active_wall_height = 0.0
    finally:
        set_wall_props_updating(False)

    set_room_props_updating(True)
    try:
        settings.active_room_name = ""
    finally:
        set_room_props_updating(False)

    settings.opening_items.clear()


def _activate_floorplan_object(context, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj


def _pick_element(context, sg, rg, mx, my):
    # Project wall 3D box faces to 2D screen space, collect all walls whose
    # screen projection contains the mouse, then return the one closest to the
    # camera (highest view-space Z) so occluded walls behind visible ones are
    # never accidentally selected.
    # If no wall is hit, test room floor polygons (flat faces at Z=0) the same way.
    # Returns ('wall', wall_uuid), ('room', room_uuid), or None.
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None

    mouse = (float(mx), float(my))

    walls = sg.get_all_walls()
    junctions = sg.get_all_junctions()
    junctions_by_id = {j.id: j for j in junctions}

    hits = []  # (view_z, wall_id) — view_z is higher (less negative) for closer walls

    for wall in walls:
        quad = _compute_wall_quad(wall, junctions_by_id, sg)
        if quad is None:
            continue

        h = wall.height
        b = [Vector((p[0], p[1], 0.0)) for p in quad]
        t = [Vector((p[0], p[1], h)) for p in quad]

        faces_3d = [
            b,
            t,
            [b[0], b[1], t[1], t[0]],
            [b[1], b[2], t[2], t[1]],
            [b[2], b[3], t[3], t[2]],
            [b[3], b[0], t[0], t[3]],
        ]

        wall_hit = False
        for face3d in faces_3d:
            pts_2d = []
            skip = False
            for v in face3d:
                p2d = view3d_utils.location_3d_to_region_2d(region, rv3d, v)
                if p2d is None:
                    skip = True
                    break
                pts_2d.append((p2d.x, p2d.y))
            if skip:
                continue
            if point_in_polygon(mouse, pts_2d):
                wall_hit = True
                break

        if wall_hit:
            # Compute view-space Z of wall centre; closer walls have higher (less
            # negative) Z in Blender view space (camera looks along -Z).
            cx = sum(p[0] for p in quad) / 4.0
            cy = sum(p[1] for p in quad) / 4.0
            center_3d = Vector((cx, cy, h / 2.0))
            view_z = (rv3d.view_matrix @ center_3d).z
            hits.append((view_z, wall.id))

    if hits:
        # Highest view_z = closest to camera.
        hits.sort(key=lambda item: -item[0])
        return ('wall', hits[0][1])

    # No wall hit — test room floor polygons (flat face at Z=0).
    room_hits = []  # (view_z, room_id)
    for room in rg.get_all_rooms():
        verts_2d = sg.get_cycle_vertices(room.cycle)
        if len(verts_2d) < 3:
            continue
        pts_2d = []
        skip = False
        for x, y in verts_2d:
            p2d = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector((x, y, 0.0)))
            if p2d is None:
                skip = True
                break
            pts_2d.append((p2d.x, p2d.y))
        if skip:
            continue
        if point_in_polygon(mouse, pts_2d):
            cx, cy = room.centroid
            view_z = (rv3d.view_matrix @ Vector((cx, cy, 0.0))).z
            room_hits.append((view_z, room.id))

    if room_hits:
        room_hits.sort(key=lambda item: -item[0])
        return ('room', room_hits[0][1])

    return None


class FLOORPLAN_OT_select_wall(bpy.types.Operator):
    bl_idname = "floorplan.select_wall"
    bl_label = "Select Wall / Room"
    bl_description = "Click a wall or room on the active floor plan object"

    @classmethod
    def poll(cls, context):
        from .. import find_floorplan_obj
        return find_floorplan_obj(context) is not None

    def invoke(self, context, event):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
        from ..ui.properties import set_wall_props_updating, populate_opening_items

        settings = context.scene.floorplan
        obj = find_floorplan_obj(context)
        if obj is None:
            return {'PASS_THROUGH'}

        # Auto-reconstruct graphs after addon reload / undo / file load.
        if obj.name not in _graph_store:
            sg, rg, mapper = reset_graphs_for_obj(obj)
            if not sg.get_all_walls():
                return {'PASS_THROUGH'}

        sg, rg, mapper = _graph_store[obj.name]
        result = _pick_element(context, sg, rg, event.mouse_region_x, event.mouse_region_y)

        if result is not None and result[0] == 'wall':
            wall_uuid = result[1]
            wall = sg.get_wall(wall_uuid)
            if wall is None:
                _clear_semantic_selection_ui(context, settings)
                return {'FINISHED'}

            _selection.select_wall(wall_uuid, context, object_name=obj.name)
            # Populate editable props without triggering the sync callback.
            set_wall_props_updating(True)
            try:
                settings.active_wall_thickness = wall.thickness
                settings.active_wall_height = wall.height
            finally:
                set_wall_props_updating(False)

            populate_opening_items(settings, sg, wall_uuid)
            context.area.tag_redraw()
            return {'FINISHED'}

        if result is not None and result[0] == 'room':
            room_uuid = result[1]
            room = rg.get_room(room_uuid)
            if room is None:
                _clear_semantic_selection_ui(context, settings)
                return {'FINISHED'}
            _selection.select_room(room_uuid, context, from_viewport=True, object_name=obj.name)
            # Populate active_room_name without triggering the sync callback.
            from ..ui.properties import set_room_props_updating
            set_room_props_updating(True)
            try:
                settings.active_room_name = room.name
            finally:
                set_room_props_updating(False)
            settings.active_wall_thickness = 0.0
            settings.active_wall_height = 0.0
            settings.opening_items.clear()
            context.area.tag_redraw()
            return {'FINISHED'}

        # Missed — clear selection and let Blender handle the click.
        _clear_semantic_selection_ui(context, settings)
        return {'PASS_THROUGH'}


def register_select_keymap():
    # LMB in Object Mode — fires before Blender's own selection so we can
    # intercept wall clicks.  Returns PASS_THROUGH on miss so normal Blender
    # selection still works.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(
        "floorplan.select_wall",
        type='LEFTMOUSE',
        value='PRESS',
    )
    return km, kmi


def unregister_select_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.get('Object Mode')
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == "floorplan.select_wall":
                km.keymap_items.remove(kmi)
                break
