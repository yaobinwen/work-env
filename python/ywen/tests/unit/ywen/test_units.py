import unittest

import ywen.units as units


class TestImport(unittest.TestCase):
    def test_import(self):
        import ywen.units


class TestConversion(unittest.TestCase):
    def test_unsupported_unit(self):
        self.assertRaises(
            ValueError,
            units.conv,
            value=units.conv,
            from_unit="yard",
            to_unit=units.METER,
        )

        self.assertRaises(
            ValueError,
            units.conv,
            value=units.conv,
            from_unit=units.METER,
            to_unit="yard",
        )

    def test_cm_to_cm(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.CENTIMETER,
            to_unit=units.CENTIMETER,
        )
        self.assertAlmostEqual(result, v)

    def test_cm_to_m(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.CENTIMETER,
            to_unit=units.METER,
        )
        self.assertAlmostEqual(result, v * 0.01)

    def test_cm_to_ft(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.CENTIMETER,
            to_unit=units.FOOT,
        )
        self.assertAlmostEqual(result, v * 0.0328084)

    def test_m_to_cm(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.METER,
            to_unit=units.CENTIMETER,
        )
        self.assertAlmostEqual(result, v * 100)

    def test_m_to_m(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.METER,
            to_unit=units.METER,
        )
        self.assertAlmostEqual(result, v)

    def test_m_to_ft(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.METER,
            to_unit=units.FOOT,
        )
        self.assertAlmostEqual(result, v * 3.28084)

    def test_ft_to_cm(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.FOOT,
            to_unit=units.CENTIMETER,
        )
        self.assertAlmostEqual(result, v * 30.48)

    def test_ft_to_m(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.FOOT,
            to_unit=units.METER,
        )
        self.assertAlmostEqual(result, v * 0.3048)

    def test_ft_to_ft(self):
        v = 1.02
        result = units.conv(
            value=v,
            from_unit=units.FOOT,
            to_unit=units.FOOT,
        )
        self.assertAlmostEqual(result, v)
