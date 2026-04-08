import math

# All coordinates are 2D tuples: (x, y).
# All units are meters internally.

# Cool source for calculating area and centroid of polygon and many more fancy things:
# https://paulbourke.net/geometry/polygonmesh/ - section: Calculating the area and centroid of a polygon

# https://en.wikipedia.org/wiki/Shoelace_formula
def polygon_area(vertices):
    # Shoelace / Gauss formula for the signed area of a simple polygon.
    # Returns absolute area. Vertices are a list of (x, y) tuples in order.
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
    # Centroid of a simple polygon using the shoelace-weighted formula.
    # Returns (cx, cy). Assumes non-zero area.
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
    # Sum of edge lengths around a polygon.
    n = len(vertices)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        total += point_distance(vertices[i], vertices[(i + 1) % n])
    return total


def point_distance(p1, p2):
    # Euclidean distance between two 2D points.
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.hypot(dx, dy)


def edge_length(p1, p2):
    # Alias for point_distance — length of a wall between two junctions.
    return point_distance(p1, p2)

# https://docs.python.org/3/library/math.html#math.atan2
def edge_angle(p1, p2):
    # Angle of the edge p1→p2 in radians, measured counter-clockwise from the +X axis.
    # Returns value in (-π, π].
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.atan2(dy, dx)

# https://docs.python.org/3/library/math.html#math.atan2
def angle_between_edges(p_common, p1, p2):
    # Interior angle at p_common formed by edges p_common→p1 and p_common→p2.
    # Returns value in (0, 2π). Uses atan2 difference.
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
    # Approximate aspect ratio of a polygon via its axis-aligned bounding box.
    # Returns width/height (or height/width if height > width to keep ratio ≥ 1).
    if len(vertices) < 3:
        return 1.0
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    if width < 1e-12 or height < 1e-12:
        return 1.0
    return width / height
