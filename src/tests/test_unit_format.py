from src.utils.unit_format import format_length, format_area


def test_format_length_metric_units():
    assert format_length(2.5, 'M') == '2.50 m'
    assert format_length(2.5, 'CM') == '250.0 cm'
    assert format_length(2.5, 'MM') == '2500 mm'


def test_format_length_imperial_units():
    assert format_length(1.0, 'FT') == '3.28 ft'
    assert format_length(1.0, 'IN') == '39.4 in'


def test_format_area_uses_selected_unit_squared():
    assert format_area(1.0, 'M') == '1.00 m²'
    assert format_area(1.0, 'CM') == '10000 cm²'
    assert format_area(1.0, 'MM') == '1000000 mm²'
    assert format_area(1.0, 'FT') == '10.76 ft²'
    assert format_area(1.0, 'IN') == '1550.0 in²'


def test_unknown_unit_falls_back_to_meters():
    assert format_length(1.23, 'X') == '1.23 m'
    assert format_area(1.23, 'X') == '1.23 m²'
