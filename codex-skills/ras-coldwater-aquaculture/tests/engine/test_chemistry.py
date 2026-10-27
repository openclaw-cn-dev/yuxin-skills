"""Unit tests for water-chemistry computations (chemistry.py)."""
import math
import unittest

from ras_aqua import chemistry as c


class TestAmmonia(unittest.TestCase):
    def test_pka_decreases_with_temperature(self):
        # pKa falls as temperature rises (endothermic dissociation).
        self.assertGreater(c.ammonia_pka(5), c.ammonia_pka(25))

    def test_pka_value_at_25c(self):
        # Emerson 1975: pKa ~9.24 at 25 degC.
        self.assertAlmostEqual(c.ammonia_pka(25), 9.24, places=2)

    def test_fraction_bounds(self):
        f = c.unionized_ammonia_fraction(15, 7.5)
        self.assertGreater(f, 0.0)
        self.assertLess(f, 1.0)

    def test_fraction_rises_with_pH(self):
        self.assertGreater(c.unionized_ammonia_fraction(15, 8.5),
                           c.unionized_ammonia_fraction(15, 7.0))

    def test_nh3_mgL(self):
        nh3, f = c.unionized_ammonia_mgL(1.0, 15, 7.5)
        self.assertAlmostEqual(nh3, f, places=6)
        self.assertGreater(nh3, 0.0)
        # Cross-check: TAN * f.
        self.assertAlmostEqual(nh3, 1.0 * f, places=8)

    def test_invalid_pH_raises(self):
        with self.assertRaises(ValueError):
            c.unionized_ammonia_fraction(15, 20)


class TestDOSaturation(unittest.TestCase):
    def test_do_saturation_decreases_with_temperature(self):
        self.assertGreater(c.do_saturation_freshwater(5),
                           c.do_saturation_freshwater(25))

    def test_do_saturation_at_15c(self):
        # Freshwater DO sat at 15 degC ~10.1 mg/L.
        self.assertAlmostEqual(c.do_saturation_freshwater(15), 10.08, places=1)

    def test_salinity_lowers_saturation(self):
        self.assertLess(c.do_saturation_freshwater(15, 5),
                        c.do_saturation_freshwater(15, 0))

    def test_seawater_saturation(self):
        # ~35 ppt should reduce DO sat by ~20%.
        fresh = c.do_saturation_freshwater(15, 0)
        sea = c.do_saturation_freshwater(15, 35)
        self.assertLess(sea, fresh * 0.85)

    def test_percent_saturation(self):
        pct = c.do_percent_saturation(6.0, 15)
        self.assertAlmostEqual(pct, 59.5, places=0)


class TestAlkalinityAndSeverity(unittest.TestCase):
    def test_alkalinity_demand(self):
        # 7.14 mg CaCO3 per mg TAN.
        self.assertAlmostEqual(c.alkalinity_demand_for_tan(2.0), 14.28, places=1)

    def test_alkalinity_demand_with_exchange(self):
        d = c.alkalinity_demand_for_tan(2.0, daily_water_exchange_frac=0.05)
        self.assertLess(d, 14.28)

    def test_severity_higher_is_worse(self):
        from ras_aqua.schemas import Severity
        self.assertEqual(c.severity_for_value(2.0, 1.0, 3.0), Severity.ALERT)
        self.assertEqual(c.severity_for_value(4.0, 1.0, 3.0), Severity.CRITICAL)
        self.assertEqual(c.severity_for_value(0.5, 1.0, 3.0), Severity.OK)

    def test_severity_lower_is_worse(self):
        from ras_aqua.schemas import Severity
        self.assertEqual(c.severity_for_value(4.0, 6.0, 4.0, lower_is_worse=True),
                         Severity.CRITICAL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
