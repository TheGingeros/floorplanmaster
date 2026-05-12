"""
Validation functions and error codes for FloorPlanMaster graph layers.

All validators raise :class:`ValidationError` with a structured error code
when a constraint is violated.  They are called at CRUD boundaries in the
graph modules so the invalid state is never allowed to enter the data model.

No bpy dependency — safe to import in unit tests without Blender.
"""

from ..utils.constants import (
    MIN_THICKNESS, MAX_THICKNESS,
    MIN_HEIGHT, MAX_HEIGHT,
    MIN_ROOM_AREA,
    MIN_ASPECT_RATIO, MAX_ASPECT_RATIO,
    MIN_ROOM_VERTICES,
    MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
    MIN_OPENING_HEIGHT,
    MIN_OPENING_CLEARANCE,
)
import math

# Error codes
E_WALL_TOO_SHORT = "E_WALL_TOO_SHORT"
E_WALL_DUPLICATE = "E_WALL_DUPLICATE"
E_WALL_SELF_LOOP = "E_WALL_SELF_LOOP"
E_THICKNESS_OUT_OF_RANGE = "E_THICKNESS_OUT_OF_RANGE"
E_HEIGHT_OUT_OF_RANGE = "E_HEIGHT_OUT_OF_RANGE"
E_ROOM_TOO_SMALL = "E_ROOM_TOO_SMALL"
E_ROOM_BAD_ASPECT = "E_ROOM_BAD_ASPECT"
E_ROOM_TOO_FEW_VERTICES = "E_ROOM_TOO_FEW_VERTICES"
E_JUNCTION_DUPLICATE = "E_JUNCTION_DUPLICATE"
E_OPENING_TOO_LARGE = "E_OPENING_TOO_LARGE"
E_OPENING_OVERLAP = "E_OPENING_OVERLAP"
E_OPENING_EXCEEDS_WALL = "E_OPENING_EXCEEDS_WALL"
E_OPENING_WIDTH_OUT_OF_RANGE = "E_OPENING_WIDTH_OUT_OF_RANGE"
E_OPENING_HEIGHT_OUT_OF_RANGE = "E_OPENING_HEIGHT_OUT_OF_RANGE"
E_PLANARITY_VIOLATION = "E_PLANARITY_VIOLATION"


# Define own class for expection handling
# Enables to try and catch only these defined errors and also custom error messaging
class ValidationError(Exception):
    """Raised when a FloorPlanMaster validation rule is violated.

    Attributes:
        code (str): Machine-readable error code (one of the ``E_*`` constants).
        message (str): Human-readable description of the violation.
    """

    def __init__(self, code, message=""):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}" if message else code)


# Validators — called at CRUD boundaries in graph modules.
def validate_thickness(value):
    """Raise :class:`ValidationError` if *value* is outside the allowed wall thickness range.

    Args:
        value (float): Proposed thickness in metres.

    Raises:
        ValidationError: Code ``E_THICKNESS_OUT_OF_RANGE``.
    """
    if not (MIN_THICKNESS <= value <= MAX_THICKNESS):
        raise ValidationError(
            E_THICKNESS_OUT_OF_RANGE,
            f"Thickness {value} not in [{MIN_THICKNESS}, {MAX_THICKNESS}]",
        )


def validate_height(value):
    """Raise :class:`ValidationError` if *value* is outside the allowed wall height range.

    Args:
        value (float): Proposed height in metres.

    Raises:
        ValidationError: Code ``E_HEIGHT_OUT_OF_RANGE``.
    """
    if not (MIN_HEIGHT <= value <= MAX_HEIGHT):
        raise ValidationError(
            E_HEIGHT_OUT_OF_RANGE,
            f"Height {value} not in [{MIN_HEIGHT}, {MAX_HEIGHT}]",
        )


def validate_room_area(area):
    """Raise :class:`ValidationError` if the room area is below the minimum.

    Args:
        area (float): Room area in square metres.

    Raises:
        ValidationError: Code ``E_ROOM_TOO_SMALL``.
    """
    if area < MIN_ROOM_AREA:
        raise ValidationError(
            E_ROOM_TOO_SMALL,
            f"Room area {area:.2f} m² is below minimum {MIN_ROOM_AREA} m²",
        )


def validate_aspect_ratio(ratio):
    """Raise :class:`ValidationError` if the room aspect ratio is out of range.

    Args:
        ratio (float): Aspect ratio (bounding-box width / height, always ≥ 1).

    Raises:
        ValidationError: Code ``E_ROOM_BAD_ASPECT``.
    """
    if not (MIN_ASPECT_RATIO <= ratio <= MAX_ASPECT_RATIO):
        raise ValidationError(
            E_ROOM_BAD_ASPECT,
            f"Aspect ratio {ratio:.2f} not in [{MIN_ASPECT_RATIO}, {MAX_ASPECT_RATIO}]",
        )


def validate_room_vertex_count(count):
    """Raise :class:`ValidationError` if the room has too few vertices.

    Args:
        count (int): Number of polygon vertices.

    Raises:
        ValidationError: Code ``E_ROOM_TOO_FEW_VERTICES``.
    """
    if count < MIN_ROOM_VERTICES:
        raise ValidationError(
            E_ROOM_TOO_FEW_VERTICES,
            f"Room has {count} vertices, minimum is {MIN_ROOM_VERTICES}",
        )


def validate_opening_width(value):
    """Raise :class:`ValidationError` if *value* is outside the allowed opening width range.

    Args:
        value (float): Proposed opening width in metres.

    Raises:
        ValidationError: Code ``E_OPENING_WIDTH_OUT_OF_RANGE``.
    """
    if not (MIN_OPENING_WIDTH <= value <= MAX_OPENING_WIDTH):
        raise ValidationError(
            E_OPENING_WIDTH_OUT_OF_RANGE,
            f"Opening width {value} not in [{MIN_OPENING_WIDTH}, {MAX_OPENING_WIDTH}]",
        )


def validate_opening_height(value, wall_height=None):
    """Raise :class:`ValidationError` if the opening height is invalid.

    Checks both the absolute minimum height and, when *wall_height* is given,
    ensures the opening does not exceed the wall.

    Args:
        value (float): Proposed opening height in metres.
        wall_height (float | None): Height of the parent wall, or ``None`` to
            skip the wall-height check.

    Raises:
        ValidationError: Code ``E_OPENING_HEIGHT_OUT_OF_RANGE``.
    """
    if value < MIN_OPENING_HEIGHT:
        raise ValidationError(
            E_OPENING_HEIGHT_OUT_OF_RANGE,
            f"Opening height {value} below minimum {MIN_OPENING_HEIGHT}",
        )
    if wall_height is not None and value > wall_height:
        raise ValidationError(
            E_OPENING_HEIGHT_OUT_OF_RANGE,
            f"Opening height {value} exceeds wall height {wall_height}",
        )


def _opening_half_norm(width, wall_length):
    if wall_length <= 0:
        return 0.5
    return (width / 2.0) / wall_length


def _opening_interval(position, width, wall_length):
    half_norm = _opening_half_norm(width, wall_length)
    return position - half_norm, position + half_norm


def _opening_value(opening, attr):
    if isinstance(opening, dict):
        return opening.get(attr)
    return getattr(opening, attr)


def get_opening_free_spans(wall_length, existing_openings=None,
                           inset_start=0.0, inset_end=0.0,
                           min_gap=MIN_OPENING_CLEARANCE):
    """Return a list of free (start, end) spans along the wall as normalised fractions.

    Accounts for the junction inset at each end and a minimum clearance gap
    around every existing opening.

    Args:
        wall_length (float): Total wall length in metres.
        existing_openings: Iterable of opening objects/dicts that have
            ``position`` and ``width`` attributes.  ``None`` means no openings.
        inset_start (float): Reserved length (metres) at the start end.
        inset_end (float): Reserved length (metres) at the end.
        min_gap (float): Minimum required clearance between openings (metres).

    Returns:
        list[tuple[float, float]]: Sorted, non-overlapping free spans expressed
        as normalised fractions [0.0, 1.0] along the wall.
    """
    if wall_length <= 0:
        return []

    t_min = inset_start / wall_length
    t_max = 1.0 - (inset_end / wall_length)
    if t_min > t_max:
        return []

    gap_norm = (min_gap / wall_length) + 1e-6
    blocked = []
    for other in existing_openings or []:
        o_start, o_end = _opening_interval(
            _opening_value(other, "position"),
            _opening_value(other, "width"),
            wall_length,
        )
        o_start -= gap_norm
        o_end += gap_norm
        if o_end <= t_min or o_start >= t_max:
            continue
        blocked.append((max(t_min, o_start), min(t_max, o_end)))

    if not blocked:
        return [(t_min, t_max)]

    blocked.sort(key=lambda span: span[0])
    merged = [blocked[0]]
    for start, end in blocked[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 1e-9:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))

    free = []
    cursor = t_min
    for start, end in merged:
        if start > cursor + 1e-9:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < t_max - 1e-9:
        free.append((cursor, t_max))
    return free


def get_opening_center_intervals(width, wall_length, existing_openings=None,
                                 inset_start=0.0, inset_end=0.0,
                                 min_gap=MIN_OPENING_CLEARANCE):
    """Return valid centre-position intervals for a new opening of the given width.

    Shrinks each free span by ``width/2`` on each side so that any position
    within the returned intervals will place the opening without collision.

    Args:
        width (float): Width of the new opening in metres.
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings (same format as
            :func:`get_opening_free_spans`).
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Returns:
        list[tuple[float, float]]: Sorted centre-position intervals as
        normalised fractions.
    """
    half_norm = _opening_half_norm(width, wall_length)
    intervals = []
    for span_start, span_end in get_opening_free_spans(
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    ):
        center_start = span_start + half_norm
        center_end = span_end - half_norm
        if center_start <= center_end + 1e-9:
            intervals.append((center_start, center_end))
    return intervals


def clamp_opening_position(position, width, wall_length, existing_openings=None,
                           inset_start=0.0, inset_end=0.0,
                           min_gap=MIN_OPENING_CLEARANCE):
    """Return the nearest valid centre position for an opening, or ``None`` if it cannot fit.

    If *position* already lies within a valid interval it is returned unchanged
    (clamped to interval boundaries).  Otherwise the closest interval boundary
    is returned.

    Args:
        position (float): Desired normalised centre position [0.0, 1.0].
        width (float): Opening width in metres.
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings (same format as
            :func:`get_opening_free_spans`).
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Returns:
        float | None: Clamped centre position, or ``None`` if the opening
        cannot fit anywhere.
    """
    intervals = get_opening_center_intervals(
        width,
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    if not intervals:
        return None

    for start, end in intervals:
        if start - 1e-9 <= position <= end + 1e-9:
            return max(start, min(position, end))

    best = None
    best_dist = None
    for start, end in intervals:
        candidate = start if position < start else end
        distance = abs(candidate - position)
        if best_dist is None or distance < best_dist:
            best = candidate
            best_dist = distance
    return best


def max_opening_width(wall_length, existing_openings=None,
                      inset_start=0.0, inset_end=0.0,
                      min_gap=MIN_OPENING_CLEARANCE):
    """Return the largest opening width that can still be placed anywhere on the wall.

    Args:
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings (same format as
            :func:`get_opening_free_spans`).
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Returns:
        float: Maximum fitting width in metres, or 0.0 if nothing fits.
    """
    spans = get_opening_free_spans(
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    if not spans:
        return 0.0
    return max((end - start) * wall_length for start, end in spans)


def max_opening_width_at_position(position, wall_length, existing_openings=None,
                                  inset_start=0.0, inset_end=0.0,
                                  min_gap=MIN_OPENING_CLEARANCE):
    """Return the maximum opening width centred at *position* that fits without collision.

    Args:
        position (float): Normalised centre position [0.0, 1.0].
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings (same format as
            :func:`get_opening_free_spans`).
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Returns:
        float: Maximum width in metres, or 0.0 if the position is blocked.
    """
    spans = get_opening_free_spans(
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    if not spans:
        return 0.0

    for start, end in spans:
        if start - 1e-9 <= position <= end + 1e-9:
            return max(0.0, 2.0 * min(position - start, end - position) * wall_length)
    return 0.0


def can_fit_opening(width, wall_length, existing_openings=None,
                    inset_start=0.0, inset_end=0.0,
                    min_gap=MIN_OPENING_CLEARANCE):
    """Return ``True`` if an opening of *width* can be placed anywhere on the wall.

    Args:
        width (float): Opening width in metres.
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings (same format as
            :func:`get_opening_free_spans`).
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Returns:
        bool: ``True`` if the opening fits, ``False`` otherwise.
    """
    intervals = get_opening_center_intervals(
        width,
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    return bool(intervals)


def validate_opening_placement(position, width, wall_length, existing_openings=None,
                               inset_start=0.0, inset_end=0.0,
                               min_gap=MIN_OPENING_CLEARANCE):
    """Raise :class:`ValidationError` if the opening placement is invalid.

    Checks that the opening fits within the usable wall span and does not
    overlap or touch an existing opening.

    Args:
        position (float): Normalised centre position [0.0, 1.0].
        width (float): Opening width in metres.
        wall_length (float): Total wall length in metres.
        existing_openings: Existing openings to check against.
        inset_start (float): Reserved length at the start end (metres).
        inset_end (float): Reserved length at the end (metres).
        min_gap (float): Minimum clearance between openings (metres).

    Raises:
        ValidationError: Code ``E_OPENING_TOO_LARGE`` or ``E_OPENING_OVERLAP``.
    """
    # Check that opening fits within the usable wall span and does not overlap or touch.
    # inset_start / inset_end are the miter-inset distances (in meters) at each end.
    base_intervals = get_opening_center_intervals(
        width,
        wall_length,
        existing_openings=None,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    if not base_intervals:
        raise ValidationError(
            E_OPENING_TOO_LARGE,
            f"Opening (t={position}, w={width}) extends beyond usable wall span (length={wall_length:.3f})",
        )

    in_base = any(start - 1e-9 <= position <= end + 1e-9 for start, end in base_intervals)
    if not in_base:
        raise ValidationError(
            E_OPENING_TOO_LARGE,
            f"Opening (t={position}, w={width}) extends beyond usable wall span (length={wall_length:.3f})",
        )

    constrained_intervals = get_opening_center_intervals(
        width,
        wall_length,
        existing_openings=existing_openings,
        inset_start=inset_start,
        inset_end=inset_end,
        min_gap=min_gap,
    )
    in_constrained = any(start - 1e-9 <= position <= end + 1e-9 for start, end in constrained_intervals)
    if not in_constrained:
        raise ValidationError(
            E_OPENING_OVERLAP,
            "Opening overlaps or touches an existing opening",
        )


def validate_opening_sill(sill_height, opening_height, wall_height):
    """Raise :class:`ValidationError` if the sill + opening height exceeds the wall.

    Args:
        sill_height (float): Distance from floor to bottom of opening (metres).
        opening_height (float): Height of the opening (metres).
        wall_height (float): Height of the parent wall (metres).

    Raises:
        ValidationError: Code ``E_OPENING_HEIGHT_OUT_OF_RANGE`` or
            ``E_OPENING_EXCEEDS_WALL``.
    """
    if sill_height < 0:
        raise ValidationError(
            E_OPENING_HEIGHT_OUT_OF_RANGE,
            f"Sill height {sill_height} cannot be negative",
        )
    if sill_height + opening_height > wall_height + 1e-6:
        raise ValidationError(
            E_OPENING_EXCEEDS_WALL,
            f"Opening top ({sill_height + opening_height:.2f}) exceeds wall height ({wall_height:.2f})",
        )


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p, eps=1e-9):
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def _segments_intersect(a, b, c, d, eps=1e-9):
    o1 = _orient(a, b, c)
    o2 = _orient(a, b, d)
    o3 = _orient(c, d, a)
    o4 = _orient(c, d, b)

    # Proper intersection.
    if (o1 > eps and o2 < -eps or o1 < -eps and o2 > eps) and (
        o3 > eps and o4 < -eps or o3 < -eps and o4 > eps
    ):
        return True

    # Collinear / touching cases.
    if abs(o1) <= eps and _on_segment(a, b, c, eps):
        return True
    if abs(o2) <= eps and _on_segment(a, b, d, eps):
        return True
    if abs(o3) <= eps and _on_segment(c, d, a, eps):
        return True
    if abs(o4) <= eps and _on_segment(c, d, b, eps):
        return True

    return False


def _point_segment_distance(p, a, b):
    abx = b[0] - a[0]
    aby = b[1] - a[1]
    apx = p[0] - a[0]
    apy = p[1] - a[1]
    denom = abx * abx + aby * aby
    if denom < 1e-12:
        return math.hypot(apx, apy)
    t = (apx * abx + apy * aby) / denom
    if t <= 0.0:
        return math.hypot(apx, apy)
    if t >= 1.0:
        return math.hypot(p[0] - b[0], p[1] - b[1])
    projx = a[0] + t * abx
    projy = a[1] + t * aby
    return math.hypot(p[0] - projx, p[1] - projy)


def _segment_distance(a, b, c, d):
    if _segments_intersect(a, b, c, d):
        return 0.0
    return min(
        _point_segment_distance(a, c, d),
        _point_segment_distance(b, c, d),
        _point_segment_distance(c, a, b),
        _point_segment_distance(d, a, b),
    )


def validate_planar_wall_layout(wall_segments, min_wall_length=1e-6, eps=1e-9):
    """Validate 2D planarity of the current wall layout.

    Checks that every wall has a non-zero length and that no pair of
    non-adjacent walls intersects or overlaps.

    Args:
        wall_segments (list[dict]): Each dict must contain keys
            ``'wall_id'``, ``'junction_start'``, ``'junction_end'``,
            ``'start'`` (x, y), and ``'end'`` (x, y).
        min_wall_length (float): Minimum acceptable wall length (metres).
        eps (float): Numerical epsilon for intersection tests.

    Raises:
        ValidationError: Code ``E_WALL_TOO_SHORT`` or ``E_PLANARITY_VIOLATION``.
    """
    # Validate geometry-level planarity in 2D:
    # - Every wall has non-zero usable length.
    # - No pair of non-adjacent walls intersects or touches.
    for seg in wall_segments:
        a = seg["start"]
        b = seg["end"]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if length < min_wall_length:
            raise ValidationError(
                E_WALL_TOO_SHORT,
                f"Wall {seg['wall_id'][:8]} is too short after edit",
            )

    count = len(wall_segments)
    for i in range(count):
        s1 = wall_segments[i]
        a = s1["start"]
        b = s1["end"]
        shared_1 = {s1["junction_start"], s1["junction_end"]}

        for j in range(i + 1, count):
            s2 = wall_segments[j]
            c = s2["start"]
            d = s2["end"]
            shared_2 = {s2["junction_start"], s2["junction_end"]}

            # Adjacent walls may meet at a shared junction.
            if shared_1 & shared_2:
                continue

            if _segments_intersect(a, b, c, d, eps=eps):
                raise ValidationError(
                    E_PLANARITY_VIOLATION,
                    (
                        f"Wall {s1['wall_id'][:8]} intersects wall "
                        f"{s2['wall_id'][:8]}"
                    ),
                )

            # Thickness-aware overlap check (offset footprint collision).
            # Even if centerlines do not intersect, the actual wall bodies can
            # still overlap when segment distance is less than combined half-thickness.
            t1 = float(s1.get("thickness", 0.0))
            t2 = float(s2.get("thickness", 0.0))
            clearance = (t1 + t2) * 0.5
            if clearance > 0.0:
                dist = _segment_distance(a, b, c, d)
                if dist <= clearance + eps:
                    raise ValidationError(
                        E_PLANARITY_VIOLATION,
                        (
                            f"Wall {s1['wall_id'][:8]} overlaps wall "
                            f"{s2['wall_id'][:8]} (thickness collision)"
                        ),
                    )
