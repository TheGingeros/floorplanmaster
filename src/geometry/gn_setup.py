# Geometry Nodes tree builder for FloorPlanMaster.
# Creates a GN modifier that reads the 2D base mesh (wall quad faces + room
# faces with named attributes) and generates 3D wall geometry.
#
# Strategy: quad-polygon + extrude.
#   Phase 1 of Layer 3 sync computes the actual 2D wall outline polygon for
#   each wall (4 verts with corner intersections resolved per junction) and
#   stores it as a mesh face with is_wall=1.  Room centerline faces have
#   is_wall=0.  The GN tree separates the two sets, extrudes wall faces by
#   their per-face wall_height named attribute, and joins the result with the
#   room floor faces.  No instancing, no trimming math in GN.

import bpy


TREE_NAME = "FloorPlanMaster_WallGen"
MODIFIER_NAME = "FPM_Geometry"
_TREE_VERSION = 10


def ensure_gn_modifier(obj):
    mod = obj.modifiers.get(MODIFIER_NAME)
    if mod is None:
        mod = obj.modifiers.new(name=MODIFIER_NAME, type='NODES')
    tree = get_or_create_tree()
    mod.node_group = tree
    return mod


def get_or_create_tree():
    tree = bpy.data.node_groups.get(TREE_NAME)
    if tree is not None:
        if _needs_rebuild(tree):
            return rebuild_tree()
        return tree
    return _build_tree()


def _needs_rebuild(tree):
    return tree.get("_version", 0) < _TREE_VERSION


def rebuild_tree():
    old = bpy.data.node_groups.get(TREE_NAME)
    if old:
        bpy.data.node_groups.remove(old)
    return _build_tree()


def _build_tree():
    tree = bpy.data.node_groups.new(name=TREE_NAME, type='GeometryNodeTree')
    tree.nodes.clear()

    tree.interface.new_socket("Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
    tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = tree.nodes
    links = tree.links

    group_in  = nodes.new('NodeGroupInput');  group_in.location  = (-1200, 0)
    group_out = nodes.new('NodeGroupOutput'); group_out.location = (1400, 0)

    # --- Step 1: Separate wall faces (is_wall == 1) from the rest ---
    named_is_wall = nodes.new('GeometryNodeInputNamedAttribute')
    named_is_wall.data_type = 'INT'
    named_is_wall.inputs['Name'].default_value = 'is_wall'
    named_is_wall.location = (-1000, -200)

    compare_wall = nodes.new('FunctionNodeCompare')
    compare_wall.data_type = 'INT'
    compare_wall.operation = 'EQUAL'
    compare_wall.inputs[3].default_value = 1
    compare_wall.location = (-800, -200)

    sep_wall = nodes.new('GeometryNodeSeparateGeometry')
    sep_wall.domain = 'FACE'
    sep_wall.location = (-600, 0)

    # --- Step 2: From the rest, separate opening cutters (is_opening == 1) ---
    named_is_opening = nodes.new('GeometryNodeInputNamedAttribute')
    named_is_opening.data_type = 'INT'
    named_is_opening.inputs['Name'].default_value = 'is_opening'
    named_is_opening.location = (-600, -400)

    compare_opening = nodes.new('FunctionNodeCompare')
    compare_opening.data_type = 'INT'
    compare_opening.operation = 'EQUAL'
    compare_opening.inputs[3].default_value = 1
    compare_opening.location = (-400, -400)

    sep_opening = nodes.new('GeometryNodeSeparateGeometry')
    sep_opening.domain = 'FACE'
    sep_opening.location = (-200, -200)

    # --- Step 3: Extrude wall faces by wall_height ---
    named_height = nodes.new('GeometryNodeInputNamedAttribute')
    named_height.data_type = 'FLOAT'
    named_height.inputs['Name'].default_value = 'wall_height'
    named_height.location = (-200, 300)

    extrude_walls = nodes.new('GeometryNodeExtrudeMesh')
    extrude_walls.mode = 'FACES'
    extrude_walls.location = (100, 150)

    set_shade = nodes.new('GeometryNodeSetShadeSmooth')
    set_shade.inputs['Shade Smooth'].default_value = False
    set_shade.location = (350, 150)

    # --- Step 4: Mesh Boolean (DIFFERENCE) — walls minus cutters ---
    # Cutter boxes are built as watertight 6-face solids in Python (sync.py)
    # with consistent outward normals.  No extrusion needed here.
    boolean_node = nodes.new('GeometryNodeMeshBoolean')
    boolean_node.operation = 'DIFFERENCE'
    boolean_node.solver = 'EXACT'
    boolean_node.location = (600, 0)

    # --- Step 5: Join walls-with-holes + floor faces ---
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (1000, 0)

    # --- Links ---
    # Step 1: Separate wall faces.
    links.new(group_in.outputs['Geometry'], sep_wall.inputs['Geometry'])
    links.new(named_is_wall.outputs[0], compare_wall.inputs[2])
    links.new(compare_wall.outputs['Result'], sep_wall.inputs['Selection'])

    # Step 2: Separate opening cutters from floor faces.
    links.new(sep_wall.outputs['Inverted'], sep_opening.inputs['Geometry'])
    links.new(named_is_opening.outputs[0], compare_opening.inputs[2])
    links.new(compare_opening.outputs['Result'], sep_opening.inputs['Selection'])

    # Step 3: Extrude wall faces.
    links.new(sep_wall.outputs['Selection'], extrude_walls.inputs['Mesh'])
    links.new(named_height.outputs[0], extrude_walls.inputs['Offset Scale'])
    links.new(extrude_walls.outputs['Mesh'], set_shade.inputs['Geometry'])

    # Step 4: Mesh Boolean — extruded walls minus 3D cutter boxes.
    links.new(set_shade.outputs['Geometry'], boolean_node.inputs['Mesh 1'])
    links.new(sep_opening.outputs['Selection'], boolean_node.inputs['Mesh 2'])

    # Step 5: Join result + floor faces.
    links.new(boolean_node.outputs['Mesh'], join.inputs['Geometry'])
    links.new(sep_opening.outputs['Inverted'], join.inputs['Geometry'])

    links.new(join.outputs['Geometry'], group_out.inputs['Geometry'])

    tree["_version"] = _TREE_VERSION
    return tree
