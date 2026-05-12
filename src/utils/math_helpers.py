"""
2D geometry helpers for FloorPlanMaster.

All coordinates are 2D tuples (x, y).  All units are metres internally.
No bpy dependency — safe to import in unit tests without Blender.
"""

import math

# Cool source for calculating area and centroid of polygon and many more fancy things:
# https://paulbourke.net/geometry/polygonmesh/ - section: Calculating the area and centroid of a polygon

# https://en.wikipedia.org/wiki/Shoelace_formula
def polygon_area(vertices):
    """Return the absolute area of a simple polygon using the Shoelace (Gauss) formula.

    Args:
        vertices: Ordered list of (x, y) tuples representing polygon corners.

    Returns:
        float: Absolute area in square metres.  Returns 0.0 for degenerate
               input (fewer than 3 vertices).
    """
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    return abs(area) / 2.0

# https://en.wikipedia.org/wiki/Centroid#Of_a_polygon
def polygon_centroid(vertices):
    """Return the centroid of a simple polygon using the shoelace-weighted formula.

    Falls back to the arithmetic mean for degenerate polygons (fewer than 3
    vertices or near-zero area).

    Args:
        vertices: Ordered list of (x, y) tuples.

    Returns:
        tuple[float, float]: (cx, cy) centroid coordinates.
    """
    n = len(vertices)
    if n == 0:
        return (0.0, 0.0)
    if n < 3:
        # Degenerate: return arithmetic mean.
        cx = sum(v[0] for v in vertices) / n
        cy = sum(v[1] for v in vertices) / n
        return (cx, cy)

    signed_area = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        signed_area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    signed_area *= 0.5
    if abs(signed_area) < 1e-12:
        # Degenerate polygon; fall back to arithmetic mean.
        cx = sum(v[0] for v in vertices) / n
        cy = sum(v[1] for v in vertices) / n
        return (cx, cy)

    factor = 1.0 / (6.0 * signed_area)
    return (cx * factor, cy * factor)


# https://docs.python.org/3/library/math.html#math.hypot
# https://en.wikipedia.org/wiki/Euclidean_distance
def polygon_perimeter(vertices):
    """Return the total perimeter of a polygon (sum of all edge lengths).

    Args:
        vertices: Ordered list of (x, y) tuples.

    Returns:
        float: Perimeter in metres.
    """
    n = len(vertices)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        total += point_distance(vertices[i], vertices[(i + 1) % n])
    return total


def point_distance(p1, p2):
    """Return the Euclidean distance between two 2D points.

    Args:
        p1: (x, y) tuple.
        p2: (x, y) tuple.

    Returns:
        float: Distance in metres.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.hypot(dx, dy)


def edge_length(p1, p2):
    """Return the length of a wall edge between two junction positions.

    Alias for :func:`point_distance`.

    Args:
        p1: Start junction position (x, y).
        p2: End junction position (x, y).

    Returns:
        float: Edge length in metres.
    """
    return point_distance(p1, p2)

# https://docs.python.org/3/library/math.html#math.atan2
def edge_angle(p1, p2):
    """Return the angle of edge p1→p2 in radians, counter-clockwise from +X.

    Args:
        p1: Start point (x, y).
        p2: End point (x, y).

    Returns:
        float: Angle in radians, in the range (-π, π].
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.atan2(dy, dx)

# https://docs.python.org/3/library/math.html#math.atan2
def angle_between_edges(p_common, p1, p2):
    """Return the interior angle at *p_common* formed by edges p_common→p1 and p_common→p2.

    Args:
        p_common: Vertex shared by both edges (x, y).
        p1: Far end of the first edge (x, y).
        p2: Far end of the second edge (x, y).

    Returns:
        float: Angle in radians, normalised to (0, 2π).
    """
    a1 = edge_angle(p_common, p1)
    a2 = edge_angle(p_common, p2)
    angle = a2 - a1
    # Normalise to (0, 2π)
    angle = angle % (2.0 * math.pi)
    if angle <= 0:
        angle += 2.0 * math.pi
    return angle


# https://en.wikipedia.org/wiki/Minimum_bounding_box#Axis-aligned_minimum_bounding_box
def aspect_ratio(vertices):
    """Return an approximate aspect ratio of a polygon via its axis-aligned bounding box.

    Always returns a value ≥ 1 (swaps width and height when height > width).

    Args:
        vertices: List of (x, y) tuples.

    Returns:
        float: Aspect ratio ≥ 1.  Returns 1.0 for degenerate input.
    """
    if len(vertices) < 3:
        return 1.0
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    if width < 1e-12 or height < 1e-12:
        return 1.0
    return width / height


# https://en.wikipedia.org/wiki/Point_in_polygon — winding number / ray casting
def point_in_polygon(point, polygon):
    """Test whether *point* is inside *polygon* using the ray-casting algorithm.

    Casts a ray in the +X direction from *point* and counts edge crossings.

    Args:
        point: (x, y) query point.
        polygon: Ordered list of (x, y) tuples forming a simple polygon.

    Returns:
        bool: True if the point is strictly inside or on the boundary.
    """
    x, y = point
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        if ((y0 <= y < y1) or (y1 <= y < y0)):
            # X coordinate of the edge at height y.
            t = (y - y0) / (y1 - y0)
            x_intersect = x0 + t * (x1 - x0)
            if x < x_intersect:
                inside = not inside
    return inside
