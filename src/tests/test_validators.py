import pytest

from src.core.validators import (
    ValidationError,
    validate_thickness,
    validate_height,
    validate_room_area,
    validate_aspect_ratio,
    validate_room_vertex_count,
    E_THICKNESS_OUT_OF_RANGE,
    E_HEIGHT_OUT_OF_RANGE,
    E_ROOM_TOO_SMALL,
    E_ROOM_BAD_ASPECT,
    E_ROOM_TOO_FEW_VERTICES,
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
