# FP2 — Insert Room operator
# Inserts a rectangular room at the 3D cursor position.
# References: 04_features_fp2.md (Vložení pravoúhlé místnosti z parametrů),
#             05_ui_ux_npanel.md (Sekce Nástroje — Vložit místnost)

import bpy
from bpy.props import FloatProperty

from ..core.sync import sync_graph_to_mesh, sync_room_name_props
from ..geometry.gn_setup import ensure_gn_modifier
from .pencil_tool import _get_floorplan_obj


class FLOORPLAN_OT_insert_room(bpy.types.Operator):
    bl_idname = "floorplan.insert_room"
    bl_label = "Insert Room"
    bl_description = "Insert a rectangular room at the 3D cursor position"
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name="Width",
        description="Room width (meters)",
        default=4.0,
        min=0.5,
        max=100.0,
        unit='LENGTH',
    )
    depth: FloatProperty(
        name="Depth",
        description="Room depth (meters)",
        default=3.0,
        min=0.5,
        max=100.0,
        unit='LENGTH',
    )
    wall_height: FloatProperty(
        name="Wall Height",
        description="Height of the walls (meters)",
        default=2.5,
        min=1.0,
        max=10.0,
        unit='LENGTH',
    )
    wall_thickness: FloatProperty(
        name="Wall Thickness",
        description="Thickness of the walls (meters)",
        default=0.3,
        min=0.05,
        max=1.0,
        unit='LENGTH',
    )

    def invoke(self, context, event):
        # Pre-fill from scene settings.
        settings = context.scene.floorplan
        self.wall_height = settings.default_height
        self.wall_thickness = settings.default_thickness
        return self.execute(context)

    def execute(self, context):
        from .. import reset_graphs_for_obj

        obj = _get_floorplan_obj(context)
        ensure_gn_modifier(obj)

        # Rebuild Python graphs from the current mesh so that Blender's undo
        # (which restores mesh data but not Python objects) is the source of
        # truth.  Without this, re-executing after a parameter change would
        # add a second room on top of the first.
        sg, rg, mapper = reset_graphs_for_obj(obj)

        # Room centred on 3D cursor (XY only).
        cursor = context.scene.cursor.location
        cx, cy = cursor.x, cursor.y
        hw = self.width / 2.0
        hd = self.depth / 2.0

        # Four corners: bottom-left, bottom-right, top-right, top-left.
        positions = [
            (cx - hw, cy - hd),
            (cx + hw, cy - hd),
            (cx + hw, cy + hd),
            (cx - hw, cy + hd),
        ]

        # Create four junctions.
        junctions = []
        for pos in positions:
            try:
                j = sg.add_junction(pos)
            except Exception:
                # Junction already exists at position — find it.
                nearby = sg.find_junctions_near(pos, radius=0.001)
                if nearby:
                    j = nearby[0][0]
                else:
                    self.report({'ERROR'}, f"Cannot place junction at {pos}")
                    return {'CANCELLED'}
            junctions.append(j)

        # Create four walls closing the rectangle.
        n = len(junctions)
        for i in range(n):
            j_start = junctions[i]
            j_end = junctions[(i + 1) % n]
            try:
                sg.add_wall(
                    j_start.id, j_end.id,
                    thickness=self.wall_thickness,
                    height=self.wall_height,
                )
            except Exception:
                # Wall may already exist — skip.
                pass

        # Sync L2 + L3.
        rg.sync_from_structural_graph()
        sync_graph_to_mesh(obj, sg, rg, id_mapper=mapper)
        sync_room_name_props(obj, rg)

        # Re-apply modifier inputs after mesh rebuild so GN dimensions are correct.
        ensure_gn_modifier(obj)

        return {'FINISHED'}
