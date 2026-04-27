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


# Define own class for expection handling
# Enables to try and catch only these defined errors and also custom error messaging
class ValidationError(Exception):
    # Raised when a validation rule is violated.
    def __init__(self, code, message=""):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}" if message else code)


# Validators — called at CRUD boundaries in graph modules.
def validate_thickness(value):
    if not (MIN_THICKNESS <= value <= MAX_THICKNESS):
        raise ValidationError(
            E_THICKNESS_OUT_OF_RANGE,
            f"Thickness {value} not in [{MIN_THICKNESS}, {MAX_THICKNESS}]",
        )


def validate_height(value):
    if not (MIN_HEIGHT <= value <= MAX_HEIGHT):
        raise ValidationError(
            E_HEIGHT_OUT_OF_RANGE,
            f"Height {value} not in [{MIN_HEIGHT}, {MAX_HEIGHT}]",
        )


def validate_room_area(area):
    if area < MIN_ROOM_AREA:
        raise ValidationError(
            E_ROOM_TOO_SMALL,
            f"Room area {area:.2f} m² is below minimum {MIN_ROOM_AREA} m²",
        )


def validate_aspect_ratio(ratio):
    if not (MIN_ASPECT_RATIO <= ratio <= MAX_ASPECT_RATIO):
        raise ValidationError(
            E_ROOM_BAD_ASPECT,
            f"Aspect ratio {ratio:.2f} not in [{MIN_ASPECT_RATIO}, {MAX_ASPECT_RATIO}]",
        )


def validate_room_vertex_count(count):
    if count < MIN_ROOM_VERTICES:
        raise ValidationError(
            E_ROOM_TOO_FEW_VERTICES,
            f"Room has {count} vertices, minimum is {MIN_ROOM_VERTICES}",
        )


def validate_opening_width(value):
    if not (MIN_OPENING_WIDTH <= value <= MAX_OPENING_WIDTH):
        raise ValidationError(
            E_OPENING_WIDTH_OUT_OF_RANGE,
            f"Opening width {value} not in [{MIN_OPENING_WIDTH}, {MAX_OPENING_WIDTH}]",
        )


def validate_opening_height(value, wall_height=None):
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
