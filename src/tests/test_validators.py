import pytest

from src.core.validators import (
    ValidationError,
    validate_thickness,
    validate_height,
    validate_room_area,
    validate_aspect_ratio,
    validate_room_vertex_count,
    validate_opening_width,
    validate_opening_height,
    validate_opening_placement,
    validate_opening_sill,
    E_THICKNESS_OUT_OF_RANGE,
    E_HEIGHT_OUT_OF_RANGE,
    E_ROOM_TOO_SMALL,
    E_ROOM_BAD_ASPECT,
    E_ROOM_TOO_FEW_VERTICES,
    E_OPENING_TOO_LARGE,
    E_OPENING_OVERLAP,
    E_OPENING_EXCEEDS_WALL,
    E_OPENING_WIDTH_OUT_OF_RANGE,
    E_OPENING_HEIGHT_OUT_OF_RANGE,
)


class TestValidateThickness:
    def test_valid_minimum(self):
        validate_thickness(0.05)

    def test_valid_maximum(self):
        validate_thickness(1.0)

    def test_valid_default(self):
        validate_thickness(0.2)

    def test_too_thin(self):
        with pytest.raises(ValidationError, match=E_THICKNESS_OUT_OF_RANGE):
            validate_thickness(0.01)

    def test_too_thick(self):
        with pytest.raises(ValidationError, match=E_THICKNESS_OUT_OF_RANGE):
            validate_thickness(1.5)

    def test_zero(self):
        with pytest.raises(ValidationError, match=E_THICKNESS_OUT_OF_RANGE):
            validate_thickness(0.0)

    def test_negative(self):
        with pytest.raises(ValidationError, match=E_THICKNESS_OUT_OF_RANGE):
            validate_thickness(-0.1)


class TestValidateHeight:
    def test_valid_minimum(self):
        validate_height(1.0)

    def test_valid_maximum(self):
        validate_height(10.0)

    def test_valid_default(self):
        validate_height(3.0)

    def test_too_low(self):
        with pytest.raises(ValidationError, match=E_HEIGHT_OUT_OF_RANGE):
            validate_height(0.5)

    def test_too_high(self):
        with pytest.raises(ValidationError, match=E_HEIGHT_OUT_OF_RANGE):
            validate_height(15.0)


class TestValidateRoomArea:
    def test_valid(self):
        validate_room_area(5.0)

    def test_exactly_minimum(self):
        validate_room_area(1.0)

    def test_too_small(self):
        with pytest.raises(ValidationError, match=E_ROOM_TOO_SMALL):
            validate_room_area(0.5)


class TestValidateAspectRatio:
    def test_valid_square(self):
        validate_aspect_ratio(1.0)

    def test_valid_bounds(self):
        validate_aspect_ratio(0.1)
        validate_aspect_ratio(10.0)

    def test_too_narrow(self):
        with pytest.raises(ValidationError, match=E_ROOM_BAD_ASPECT):
            validate_aspect_ratio(0.05)

    def test_too_wide(self):
        with pytest.raises(ValidationError, match=E_ROOM_BAD_ASPECT):
            validate_aspect_ratio(15.0)


class TestValidateRoomVertexCount:
    def test_valid_triangle(self):
        validate_room_vertex_count(3)

    def test_valid_quad(self):
        validate_room_vertex_count(4)

    def test_too_few(self):
        with pytest.raises(ValidationError, match=E_ROOM_TOO_FEW_VERTICES):
            validate_room_vertex_count(2)

    def test_zero(self):
        with pytest.raises(ValidationError, match=E_ROOM_TOO_FEW_VERTICES):
            validate_room_vertex_count(0)


class TestValidationErrorAttributes:
    def test_error_code(self):
        try:
            validate_thickness(0.0)
        except ValidationError as e:
            assert e.code == E_THICKNESS_OUT_OF_RANGE
            assert E_THICKNESS_OUT_OF_RANGE in str(e)


class TestValidateOpeningWidth:
    def test_valid(self):
        validate_opening_width(0.9)

    def test_minimum(self):
        validate_opening_width(0.3)

    def test_maximum(self):
        validate_opening_width(5.0)

    def test_too_narrow(self):
        with pytest.raises(ValidationError, match=E_OPENING_WIDTH_OUT_OF_RANGE):
            validate_opening_width(0.1)

    def test_too_wide(self):
        with pytest.raises(ValidationError, match=E_OPENING_WIDTH_OUT_OF_RANGE):
            validate_opening_width(6.0)


class TestValidateOpeningHeight:
    def test_valid(self):
        validate_opening_height(2.1)

    def test_minimum(self):
        validate_opening_height(0.3)

    def test_too_short(self):
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            validate_opening_height(0.1)

    def test_exceeds_wall(self):
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            validate_opening_height(4.0, wall_height=3.0)

    def test_no_wall_height_check(self):
        validate_opening_height(4.0)  # no wall_height -> no limit check


class TestValidateOpeningPlacement:
    def test_valid_center(self):
        validate_opening_placement(0.5, 0.9, 2.0)

    def test_extends_past_start(self):
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            validate_opening_placement(0.1, 0.9, 2.0)

    def test_extends_past_end(self):
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            validate_opening_placement(0.9, 0.9, 2.0)

    def test_exactly_full_wall(self):
        # Opening = wall length, position centered -> should pass (within tolerance).
        validate_opening_placement(0.5, 2.0, 2.0)

    def test_overlap_detected(self):
        from src.core.structural_graph import Opening
        existing = Opening("w1", position=0.3, width=0.8)
        with pytest.raises(ValidationError, match=E_OPENING_OVERLAP):
            validate_opening_placement(0.5, 0.8, 2.0, existing_openings=[existing])

    def test_no_overlap(self):
        from src.core.structural_graph import Opening
        existing = Opening("w1", position=0.2, width=0.5)
        validate_opening_placement(0.8, 0.5, 2.0, existing_openings=[existing])

    def test_inset_blocks_placement_at_start(self):
        # inset_start = 0.2 on a 2m wall -> t_min = 0.1
        # opening at position=0.15 with half_norm=0.1 -> t_start=0.05 < 0.1
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            validate_opening_placement(0.15, 0.4, 2.0, inset_start=0.2)

    def test_inset_blocks_placement_at_end(self):
        # inset_end = 0.2 on a 2m wall -> t_max = 0.9
        # opening at position=0.85 with half_norm=0.1 -> t_end=0.95 > 0.9
        with pytest.raises(ValidationError, match=E_OPENING_TOO_LARGE):
            validate_opening_placement(0.85, 0.4, 2.0, inset_end=0.2)

    def test_inset_allows_placement_inside_usable_span(self):
        # inset_start=0.2, inset_end=0.2 on a 2m wall -> usable [0.1, 0.9]
        # opening at 0.5 with half_norm=0.1 -> [0.4, 0.6] fully inside
        validate_opening_placement(0.5, 0.4, 2.0, inset_start=0.2, inset_end=0.2)

    def test_inset_zero_behaves_like_original(self):
        # Explicitly passing zero insets should behave identically to omitting them.
        validate_opening_placement(0.5, 0.9, 2.0, inset_start=0.0, inset_end=0.0)


class TestValidateOpeningSill:
    def test_valid_door(self):
        validate_opening_sill(0.0, 2.1, 3.0)

    def test_valid_window(self):
        validate_opening_sill(0.9, 1.2, 3.0)

    def test_exceeds_wall(self):
        with pytest.raises(ValidationError, match=E_OPENING_EXCEEDS_WALL):
            validate_opening_sill(2.0, 2.0, 3.0)

    def test_negative_sill(self):
        with pytest.raises(ValidationError, match=E_OPENING_HEIGHT_OUT_OF_RANGE):
            validate_opening_sill(-0.5, 2.0, 3.0)

    def test_exact_fit(self):
        validate_opening_sill(1.0, 2.0, 3.0)  # 1.0 + 2.0 = 3.0 exactly
