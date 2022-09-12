# Constants for all the supported the units.
CENTIMETER = "cm"
FOOT = "ft"
METER = "m"


SUPPORTED_UNITS = [
    CENTIMETER,
    FOOT,
    METER,
]


_no_conv = lambda v: v

_cm_to_m = lambda v: v * 0.01

_cm_to_ft = lambda v: v * 0.0328084

_m_to_cm = lambda v: v * 100.0

_m_to_ft = lambda v: v * 3.28084

_ft_to_cm = lambda v: v * 30.48

_ft_to_m = lambda v: v * 0.3048


CONVERTERS = {
    CENTIMETER: {
        CENTIMETER: _no_conv,
        METER: _cm_to_m,
        FOOT: _cm_to_ft,
    },
    METER: {
        CENTIMETER: _m_to_cm,
        METER: _no_conv,
        FOOT: _m_to_ft,
    },
    FOOT: {
        CENTIMETER: _ft_to_cm,
        METER: _ft_to_m,
        FOOT: _no_conv,
    },
}


def conv(
    value: float,
    from_unit: str,
    to_unit: str,
):
    if from_unit not in SUPPORTED_UNITS:
        raise ValueError(
            f"Unsupported unit '{from_unit}'"
        )

    if to_unit not in SUPPORTED_UNITS:
        raise ValueError(
            f"Unsupported unit '{to_unit}'"
        )

    conv = CONVERTERS[from_unit][to_unit]

    return conv(value)
