# Geometry Nodes tree builder for FloorPlanMaster.
# Creates a GN modifier that reads the 2D base mesh (wall quad faces + room
# faces with named attributes) and generates 3D wall geometry.
#
# Strategy (Option C, step 3.2): quad-polygon + extrude.
#   Phase 1 of Layer 3 sync computes the actual 2D wall outline polygon for
#   each wall (4 verts with corner intersections resolved per junction) and
#   stores it as a mesh face with is_wall=1.  Room centerline faces have
#   is_wall=0.  The GN tree separates the two sets, extrudes wall faces by
#   their per-face wall_height named attribute, and joins the result with the
#   room floor faces.  No instancing, no trimming math in GN.

import bpy


TREE_NAME = "FloorPlanMaster_WallGen"
MODIFIER_NAME = "FPM_Geometry"
_TREE_VERSION = 4


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

    group_in  = nodes.new('NodeGroupInput');  group_in.location  = (-900, 0)
    group_out = nodes.new('NodeGroupOutput'); group_out.location = (1000, 0)

    # Separate wall faces (is_wall == 1) from room floor faces (is_wall == 0).
    named_is_wall = nodes.new('GeometryNodeInputNamedAttribute')
    named_is_wall.data_type = 'INT'
    named_is_wall.inputs['Name'].default_value = 'is_wall'
    named_is_wall.location = (-700, -200)

    # Compare: is_wall == 1  ->  Selection socket for SeparateGeometry.
    compare = nodes.new('FunctionNodeCompare')
    compare.data_type = 'INT'
    compare.operation = 'EQUAL'
    compare.inputs[3].default_value = 1   # B = 1
    compare.location = (-500, -200)

    sep_geo = nodes.new('GeometryNodeSeparateGeometry')
    sep_geo.domain = 'FACE'
    sep_geo.location = (-300, 0)

    # Extrude wall faces by per-face wall_height named attribute.
    named_height = nodes.new('GeometryNodeInputNamedAttribute')
    named_height.data_type = 'FLOAT'
    named_height.inputs['Name'].default_value = 'wall_height'
    named_height.location = (-300, 300)

    extrude = nodes.new('GeometryNodeExtrudeMesh')
    extrude.mode = 'FACES'
    extrude.location = (100, 150)
    # Individual = False so all wall faces extrude independently per their
    # own height value (per-face attribute, read by the Extrude node socket).

    # Delete the original (Z=0) wall quad top-faces after extrusion so only
    # the extruded solid remains (optional cosmetic — keeps mesh clean).
    # We skip this for now; the base quads at Z=0 are covered by room floors.

    # Shade flat.
    set_shade = nodes.new('GeometryNodeSetShadeSmooth')
    set_shade.inputs['Shade Smooth'].default_value = False
    set_shade.location = (400, 150)

    # Join walls + room floors.
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (700, 0)

    # --- Links ---
    links.new(group_in.outputs['Geometry'], sep_geo.inputs['Geometry'])
    links.new(named_is_wall.outputs[0], compare.inputs[2])   # A
    links.new(compare.outputs['Result'], sep_geo.inputs['Selection'])

    # Wall branch: selection → extrude → shade → join
    links.new(sep_geo.outputs['Selection'], extrude.inputs['Mesh'])
    links.new(named_height.outputs[0], extrude.inputs['Offset Scale'])
    links.new(extrude.outputs['Mesh'], set_shade.inputs['Geometry'])
    links.new(set_shade.outputs['Geometry'], join.inputs['Geometry'])

    # Floor branch: inverted selection → join
    links.new(sep_geo.outputs['Inverted'], join.inputs['Geometry'])

    links.new(join.outputs['Geometry'], group_out.inputs['Geometry'])

    tree["_version"] = _TREE_VERSION
    return tree
