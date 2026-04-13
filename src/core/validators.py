from ..utils.constants import (
    MIN_THICKNESS, MAX_THICKNESS,
    MIN_HEIGHT, MAX_HEIGHT,
    MIN_ROOM_AREA,
    MIN_ASPECT_RATIO, MAX_ASPECT_RATIO,
    MIN_ROOM_VERTICES,
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
