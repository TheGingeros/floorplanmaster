# Geometry Nodes tree builder for FloorPlanMaster.
# Creates a GN modifier that reads the 2D base mesh (edges + faces with named
# attributes) and generates 3D wall geometry.
#
# Strategy: for each edge (wall axis), build a rectangular wall volume by
# offsetting perpendicular to the edge direction by thickness/2, then
# extruding up by wall_height.  Faces (rooms) become floor polygons.

import bpy


TREE_NAME = "FloorPlanMaster_WallGen"
MODIFIER_NAME = "FPM_Geometry"


def ensure_gn_modifier(obj, thickness=0.3, height=2.5):
    # Add GN modifier to obj if not already present. Returns the modifier.
    mod = obj.modifiers.get(MODIFIER_NAME)
    if mod is None:
        mod = obj.modifiers.new(name=MODIFIER_NAME, type='NODES')
    tree = get_or_create_tree()
    mod.node_group = tree
    _set_modifier_inputs(mod, tree, thickness, height)
    return mod


def _set_modifier_inputs(mod, tree, thickness, height):
    # Write group-input values into the modifier's custom properties.
    for item in tree.interface.items_tree:
        if item.item_type != 'SOCKET':
            continue
        if item.in_out != 'INPUT':
            continue
        if item.socket_type == 'NodeSocketGeometry':
            continue
        if item.name == "Wall Thickness":
            mod[item.identifier] = thickness
        elif item.name == "Wall Height":
            mod[item.identifier] = height


def get_or_create_tree():
    # Return existing tree or build a new one.
    tree = bpy.data.node_groups.get(TREE_NAME)
    if tree is not None:
        return tree
    return _build_tree()


def rebuild_tree():
    # Force rebuild of the GN tree (e.g. after addon update).
    old = bpy.data.node_groups.get(TREE_NAME)
    if old:
        bpy.data.node_groups.remove(old)
    return _build_tree()


def _build_tree():
    tree = bpy.data.node_groups.new(name=TREE_NAME, type='GeometryNodeTree')

    tree.nodes.clear()

    # Interface: geometry in/out + wall dimension inputs.
    tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    sock_thick = tree.interface.new_socket("Wall Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    sock_thick.default_value = 0.3
    sock_thick.min_value = 0.05
    sock_thick.max_value = 1.0
    sock_height = tree.interface.new_socket("Wall Height", in_out='INPUT', socket_type='NodeSocketFloat')
    sock_height.default_value = 2.5
    sock_height.min_value = 1.0
    sock_height.max_value = 10.0
    tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # --- Create nodes ---

    group_in = tree.nodes.new('NodeGroupInput')
    group_in.location = (-800, 0)

    group_out = tree.nodes.new('NodeGroupOutput')
    group_out.location = (800, 0)

    # Wall branch: convert edges to curves, sweep rectangular profile along them.

    mesh_to_curve = tree.nodes.new('GeometryNodeMeshToCurve')
    mesh_to_curve.location = (-400, 200)

    # Rectangular cross-section driven by group inputs (not named attributes).
    curve_rect = tree.nodes.new('GeometryNodeCurvePrimitiveQuadrilateral')
    curve_rect.mode = 'RECTANGLE'
    curve_rect.location = (-400, -200)

    # Sweep profile along wall curves to produce 3D wall boxes.
    curve_to_mesh = tree.nodes.new('GeometryNodeCurveToMesh')
    curve_to_mesh.location = (-100, 200)
    curve_to_mesh.inputs['Fill Caps'].default_value = True

    # Z-offset: the profile is centred on the curve; shift walls up by
    # height / 2 so the bottom face sits on the ground plane.
    set_position = tree.nodes.new('GeometryNodeSetPosition')
    set_position.location = (100, 200)

    math_div = tree.nodes.new('ShaderNodeMath')
    math_div.operation = 'DIVIDE'
    math_div.inputs[1].default_value = 2.0
    math_div.location = (-100, -100)

    combine_z = tree.nodes.new('ShaderNodeCombineXYZ')
    combine_z.location = (100, -100)

    # Join wall boxes with the original mesh (floor faces at Z = 0).
    join_geo = tree.nodes.new('GeometryNodeJoinGeometry')
    join_geo.location = (400, 0)

    # Shade flat for cleaner viewport look.
    set_shade = tree.nodes.new('GeometryNodeSetShadeSmooth')
    set_shade.location = (600, 0)
    set_shade.inputs['Shade Smooth'].default_value = False

    # --- Links ---

    # Wall branch
    tree.links.new(group_in.outputs['Geometry'], mesh_to_curve.inputs['Mesh'])
    tree.links.new(group_in.outputs['Wall Thickness'], curve_rect.inputs['Width'])
    tree.links.new(group_in.outputs['Wall Height'], curve_rect.inputs['Height'])
    tree.links.new(mesh_to_curve.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    tree.links.new(curve_rect.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])
    tree.links.new(curve_to_mesh.outputs['Mesh'], set_position.inputs['Geometry'])

    # Z offset
    tree.links.new(group_in.outputs['Wall Height'], math_div.inputs[0])
    tree.links.new(math_div.outputs['Value'], combine_z.inputs['Z'])
    tree.links.new(combine_z.outputs['Vector'], set_position.inputs['Offset'])

    # Join walls (from extrusion) + original input (floor faces at Z=0)
    tree.links.new(set_position.outputs['Geometry'], join_geo.inputs['Geometry'])
    tree.links.new(group_in.outputs['Geometry'], join_geo.inputs['Geometry'])

    # Output
    tree.links.new(join_geo.outputs['Geometry'], set_shade.inputs['Geometry'])
    tree.links.new(set_shade.outputs['Geometry'], group_out.inputs['Geometry'])

    return tree
