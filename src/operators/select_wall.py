# FP2 — Select Wall operator
# Click anywhere in the viewport to select a wall (or deselect if clicking empty space).
# Projects wall 3D boxes to 2D screen space and tests mouse against those polygons.
# Works in any view (ortho, perspective, any angle).
# Future: extend _pick_element() to also return room hits for context menu (FP5).
# References: 04_features_fp2.md

import bpy
from bpy_extras import view3d_utils

from mathutils import Vector

from ..core.sync import _compute_wall_quad
from ..utils.math_helpers import point_in_polygon


def _pick_element(context, sg, mx, my):
    # Project wall 3D box faces to 2D screen space, collect all walls whose
    # screen projection contains the mouse, then return the one closest to the
    # camera (highest view-space Z) so occluded walls behind visible ones are
    # never accidentally selected.
    # Returns ('wall', wall_uuid) or None.
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

    if not hits:
        return None

    # Highest view_z = closest to camera.
    hits.sort(key=lambda item: -item[0])
    return ('wall', hits[0][1])


class FLOORPLAN_OT_select_wall(bpy.types.Operator):
    bl_idname = "floorplan.select_wall"
    bl_label = "Select Wall"
    bl_description = "Click a wall to select it and show its properties"

    def invoke(self, context, event):
        from .. import find_floorplan_obj, _graph_store, reset_graphs_for_obj
        import sys
        _addon = sys.modules[__package__.rsplit('.', 1)[0]]

        obj = find_floorplan_obj(context)
        if obj is None:
            return {'PASS_THROUGH'}

        # Auto-reconstruct graphs after addon reload / undo / file load.
        if obj.name not in _graph_store:
            sg, rg, mapper = reset_graphs_for_obj(obj)
            if not sg.get_all_walls():
                return {'PASS_THROUGH'}

        sg, rg, mapper = _graph_store[obj.name]
        result = _pick_element(context, sg, event.mouse_region_x, event.mouse_region_y)

        settings = context.scene.floorplan

        if result is not None and result[0] == 'wall':
            wall_uuid = result[1]
            wall = sg.get_wall(wall_uuid)
            if wall is None:
                settings.active_wall_id = ""
                return {'FINISHED'}

            # Populate active wall props without triggering the sync callback.
            _addon._updating_wall_props = True
            try:
                settings.active_wall_id = wall_uuid
                settings.active_wall_thickness = wall.thickness
                settings.active_wall_height = wall.height
            finally:
                _addon._updating_wall_props = False

            context.area.tag_redraw()
            return {'FINISHED'}

        # Missed — clear selection and let Blender handle the click.
        settings.active_wall_id = ""
        context.area.tag_redraw()
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
