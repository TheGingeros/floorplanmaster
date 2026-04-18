from ..utils.constants import (
    MIN_THICKNESS, MAX_THICKNESS,
    MIN_HEIGHT, MAX_HEIGHT,
    MIN_ROOM_AREA,
    MIN_ASPECT_RATIO, MAX_ASPECT_RATIO,
    MIN_ROOM_VERTICES,
    MIN_OPENING_WIDTH, MAX_OPENING_WIDTH,
    MIN_OPENING_HEIGHT,
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


def validate_opening_placement(position, width, wall_length, existing_openings=None):
    # Check that opening fits within the wall.
    half_norm = (width / 2.0) / wall_length if wall_length > 0 else 0.5
    t_start = position - half_norm
    t_end = position + half_norm
    if t_start < -1e-6 or t_end > 1.0 + 1e-6:
        raise ValidationError(
            E_OPENING_TOO_LARGE,
            f"Opening (t={position}, w={width}) extends beyond wall (length={wall_length:.3f})",
        )

    # Check overlap with existing openings.
    if existing_openings:
        for other in existing_openings:
            o_half = (other.width / 2.0) / wall_length if wall_length > 0 else 0.5
            o_start = other.position - o_half
            o_end = other.position + o_half
            if t_start < o_end - 1e-6 and t_end > o_start + 1e-6:
                raise ValidationError(
                    E_OPENING_OVERLAP,
                    f"Opening overlaps with existing opening {other.id[:8]}",
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
