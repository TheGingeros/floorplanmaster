# Unit formatting helpers for UI/rendering.
# Internal model values remain in meters and square meters.


def _normalize_unit(unit):
    if unit in {'M', 'CM', 'MM', 'FT', 'IN'}:
        return unit
    return 'M'


def _length_scale(unit):
    unit = _normalize_unit(unit)
    if unit == 'CM':
        return 100.0
    if unit == 'MM':
        return 1000.0
    if unit == 'FT':
        return 3.28084
    if unit == 'IN':
        return 39.3701
    return 1.0


def _length_suffix(unit):
    unit = _normalize_unit(unit)
    if unit == 'CM':
        return 'cm'
    if unit == 'MM':
        return 'mm'
    if unit == 'FT':
        return 'ft'
    if unit == 'IN':
        return 'in'
    return 'm'


def _length_precision(unit):
    unit = _normalize_unit(unit)
    if unit == 'MM':
        return 0
    if unit == 'CM':
        return 1
    if unit == 'IN':
        return 1
    return 2


def _area_precision(unit):
    unit = _normalize_unit(unit)
    if unit == 'MM':
        return 0
    if unit == 'CM':
        return 0
    if unit == 'IN':
        return 1
    return 2


def _area_suffix(unit):
    unit = _normalize_unit(unit)
    if unit == 'CM':
        return 'cm²'
    if unit == 'MM':
        return 'mm²'
    if unit == 'FT':
        return 'ft²'
    if unit == 'IN':
        return 'in²'
    return 'm²'


def format_length(meters, unit='M'):
    unit = _normalize_unit(unit)
    value = meters * _length_scale(unit)
    precision = _length_precision(unit)
    return f"{value:.{precision}f} {_length_suffix(unit)}"


def format_area(square_meters, unit='M'):
    unit = _normalize_unit(unit)
    scale = _length_scale(unit)
    value = square_meters * scale * scale
    precision = _area_precision(unit)
    return f"{value:.{precision}f} {_area_suffix(unit)}"
