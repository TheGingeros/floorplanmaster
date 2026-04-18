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
    # Project wall 3D faces (bottom quad at Z=0, top quad at Z=height, and
    # four side quads) to 2D screen space and test the mouse point against
    # those screen-space polygons.  Works in any view (ortho, perspective).
    # Returns ('wall', wall_uuid) or None.
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None

    mouse = (float(mx), float(my))

    walls = sg.get_all_walls()
    junctions = sg.get_all_junctions()
    junctions_by_id = {j.id: j for j in junctions}

    for wall in walls:
        quad = _compute_wall_quad(wall, junctions_by_id, sg)
        if quad is None:
            continue

        h = wall.height
        # 3D corners: bottom (Z=0) and top (Z=h)
        # quad = (p0, p1, p2, p3) — 2D tuples, CCW from above
        b = [Vector((p[0], p[1], 0.0)) for p in quad]
        t = [Vector((p[0], p[1], h)) for p in quad]

        # 6 faces of the wall box: bottom, top, 4 sides
        faces_3d = [
            b,                          # bottom
            t,                          # top
            [b[0], b[1], t[1], t[0]],   # side 0-1
            [b[1], b[2], t[2], t[1]],   # side 1-2
            [b[2], b[3], t[3], t[2]],   # side 2-3
            [b[3], b[0], t[0], t[3]],   # side 3-0
        ]

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
                return ('wall', wall.id)

    return None


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
        return {'PASS_THROUGH'}


class FLOORPLAN_OT_deselect_wall(bpy.types.Operator):
    bl_idname = "floorplan.deselect_wall"
    bl_label = "Deselect Wall"
    bl_description = "Clear the current wall selection"

    def execute(self, context):
        context.scene.floorplan.active_wall_id = ""
        return {'FINISHED'}


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
