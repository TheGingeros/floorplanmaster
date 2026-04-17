# Geometry Nodes tree builder for FloorPlanMaster.
# Creates a GN modifier that reads the 2D base mesh (edges + faces with named
# attributes) and generates 3D wall geometry.
#
# Strategy (step 3.1): per-edge instance box.
#   Phase 2 of Layer 3 sync pre-computes fp_direction (FLOAT_VECTOR) and
#   fp_length (FLOAT) for each edge and stores them via mesh.attributes API.
#   The GN tree reads those attributes via Named Attribute nodes, instances a
#   unit cube per edge, and scales/rotates it to (length x thickness x height).
#   Faces (rooms) from the original mesh pass through as floor polygons.

import bpy


TREE_NAME = "FloorPlanMaster_WallGen"
MODIFIER_NAME = "FPM_Geometry"
# Bump this whenever the GN tree structure changes. Trees with a lower
# version (or no version at all) are automatically rebuilt.
_TREE_VERSION = 2


def ensure_gn_modifier(obj):
    # Add GN modifier to obj if not already present. Returns the modifier.
    # Wall dimensions are read per-edge from named attributes so no global
    # modifier inputs are needed.
    mod = obj.modifiers.get(MODIFIER_NAME)
    if mod is None:
        mod = obj.modifiers.new(name=MODIFIER_NAME, type='NODES')
    tree = get_or_create_tree()
    mod.node_group = tree
    return mod


def get_or_create_tree():
    # Return existing tree, rebuilding if it uses the old global-socket
    # architecture, or build a new one when none exists yet.
    tree = bpy.data.node_groups.get(TREE_NAME)
    if tree is not None:
        if _needs_rebuild(tree):
            return rebuild_tree()
        return tree
    return _build_tree()


def _needs_rebuild(tree):
    # Rebuild when: (a) tree has the old global-socket architecture, or
    # (b) tree version is outdated (code changed since last build).
    if tree.get("_version", 0) < _TREE_VERSION:
        return True
    for item in tree.interface.items_tree:
        if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
            if item.socket_type != 'NodeSocketGeometry':
                return True
    return False


def rebuild_tree():
    # Force rebuild of the GN tree (e.g. after addon update).
    old = bpy.data.node_groups.get(TREE_NAME)
    if old:
        bpy.data.node_groups.remove(old)
    return _build_tree()


def _build_tree():
    tree = bpy.data.node_groups.new(name=TREE_NAME, type='GeometryNodeTree')
    tree.nodes.clear()

    # Interface: geometry in/out only. All wall dimensions come from per-edge
    # named attributes written by Layer 3 Phase 2 sync.
    tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = tree.nodes
    links = tree.links

    group_in = nodes.new('NodeGroupInput')
    group_in.location = (-800, 0)

    group_out = nodes.new('NodeGroupOutput')
    group_out.location = (1100, 0)

    # Convert each edge to a point at its midpoint (Z=0).
    # Named attributes on the EDGE domain are transferred automatically to
    # the resulting POINT domain by Mesh to Points.
    to_points = nodes.new('GeometryNodeMeshToPoints')
    to_points.mode = 'EDGES'
    to_points.location = (-600, 200)

    # Offset each point upward by wall_height / 2 so the cube sits on Z=0.
    named_height_z = nodes.new('GeometryNodeInputNamedAttribute')
    named_height_z.data_type = 'FLOAT'
    named_height_z.inputs['Name'].default_value = 'wall_height'
    named_height_z.location = (-400, -150)

    half_height = nodes.new('ShaderNodeMath')
    half_height.operation = 'DIVIDE'
    half_height.inputs[1].default_value = 2.0
    half_height.location = (-200, -150)

    # Build offset vector (0, 0, wall_height/2).
    comb_offset = nodes.new('ShaderNodeCombineXYZ')
    comb_offset.location = (0, -150)

    set_pos = nodes.new('GeometryNodeSetPosition')
    set_pos.location = (200, 200)

    # Per-instance scale: (fp_length, wall_thickness, wall_height).
    named_len = nodes.new('GeometryNodeInputNamedAttribute')
    named_len.data_type = 'FLOAT'
    named_len.inputs['Name'].default_value = 'fp_length'
    named_len.location = (-400, 500)

    named_thick = nodes.new('GeometryNodeInputNamedAttribute')
    named_thick.data_type = 'FLOAT'
    named_thick.inputs['Name'].default_value = 'wall_thickness'
    named_thick.location = (-400, 380)

    named_height = nodes.new('GeometryNodeInputNamedAttribute')
    named_height.data_type = 'FLOAT'
    named_height.inputs['Name'].default_value = 'wall_height'
    named_height.location = (-400, 260)

    scale_xyz = nodes.new('ShaderNodeCombineXYZ')
    scale_xyz.location = (-100, 380)

    # Per-instance rotation: align cube X-axis to wall direction.
    # Direction is stored as two scalar float edge layers (fp_dir_x, fp_dir_y)
    # to avoid FLOAT_VECTOR bmesh layer limitations; combined here into a vector.
    named_dir_x = nodes.new('GeometryNodeInputNamedAttribute')
    named_dir_x.data_type = 'FLOAT'
    named_dir_x.inputs['Name'].default_value = 'fp_dir_x'
    named_dir_x.location = (-400, 750)

    named_dir_y = nodes.new('GeometryNodeInputNamedAttribute')
    named_dir_y.data_type = 'FLOAT'
    named_dir_y.inputs['Name'].default_value = 'fp_dir_y'
    named_dir_y.location = (-400, 660)

    dir_combine = nodes.new('ShaderNodeCombineXYZ')
    dir_combine.inputs['Z'].default_value = 0.0
    dir_combine.location = (-150, 700)

    align_rot = nodes.new('FunctionNodeAlignRotationToVector')
    align_rot.axis = 'X'
    align_rot.pivot_axis = 'Z'
    align_rot.location = (-100, 700)

    # Unit cube (1x1x1) scaled per-instance.
    unit_cube = nodes.new('GeometryNodeMeshCube')
    unit_cube.inputs['Size'].default_value = (1.0, 1.0, 1.0)
    unit_cube.location = (-100, 900)

    inst_on_pts = nodes.new('GeometryNodeInstanceOnPoints')
    inst_on_pts.location = (400, 500)

    realize = nodes.new('GeometryNodeRealizeInstances')
    realize.location = (600, 300)

    # Join realized wall boxes with original mesh (room faces as floors).
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (800, 100)

    set_shade = nodes.new('GeometryNodeSetShadeSmooth')
    set_shade.inputs['Shade Smooth'].default_value = False
    set_shade.location = (950, 50)

    # --- Links ---

    # Edges to Points
    links.new(group_in.outputs['Geometry'], to_points.inputs['Mesh'])

    # Z offset: (0, 0, wall_height / 2)
    links.new(named_height_z.outputs[0], half_height.inputs[0])
    links.new(half_height.outputs['Value'], comb_offset.inputs['Z'])
    links.new(to_points.outputs['Points'], set_pos.inputs['Geometry'])
    links.new(comb_offset.outputs['Vector'], set_pos.inputs['Offset'])

    # Scale = (fp_length, wall_thickness, wall_height) per point
    links.new(named_len.outputs[0], scale_xyz.inputs['X'])
    links.new(named_thick.outputs[0], scale_xyz.inputs['Y'])
    links.new(named_height.outputs[0], scale_xyz.inputs['Z'])

    # Rotation aligned to fp_dir_x / fp_dir_y
    links.new(named_dir_x.outputs[0], dir_combine.inputs['X'])
    links.new(named_dir_y.outputs[0], dir_combine.inputs['Y'])
    links.new(dir_combine.outputs['Vector'], align_rot.inputs['Vector'])

    # Instance cube at each wall-centre point
    links.new(set_pos.outputs['Geometry'], inst_on_pts.inputs['Points'])
    links.new(unit_cube.outputs['Mesh'], inst_on_pts.inputs['Instance'])
    links.new(align_rot.outputs['Rotation'], inst_on_pts.inputs['Rotation'])
    links.new(scale_xyz.outputs['Vector'], inst_on_pts.inputs['Scale'])

    # Realize, join with floor faces, shade flat
    links.new(inst_on_pts.outputs['Instances'], realize.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], join.inputs['Geometry'])
    links.new(group_in.outputs['Geometry'], join.inputs['Geometry'])
    links.new(join.outputs['Geometry'], set_shade.inputs['Geometry'])
    links.new(set_shade.outputs['Geometry'], group_out.inputs['Geometry'])

    tree["_version"] = _TREE_VERSION
    return tree
