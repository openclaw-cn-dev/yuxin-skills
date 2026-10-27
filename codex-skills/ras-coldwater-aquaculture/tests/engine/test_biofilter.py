"""Unit tests for biofilter engineering computations (biofilter.py)."""
import unittest

from ras_aqua import biofilter as b


class TestTANProduction(unittest.TestCase):
    def test_default_protein(self):
        self.assertAlmostEqual(b.tan_production_from_feed(5.0), 175.0, places=1)

    def test_protein_scaling(self):
        # 50% protein vs 40% reference -> 1.25x.
        high = b.tan_production_from_feed(5.0, 50.0)
        self.assertAlmostEqual(high, 175.0 * 1.25, places=1)

    def test_protein_clamp(self):
        # Out-of-range protein is clamped to [25, 50].
        low = b.tan_production_from_feed(5.0, 5.0)
        self.assertAlmostEqual(low, b.tan_production_from_feed(5.0, 25.0), places=4)


class TestDerating(unittest.TestCase):
    def test_derating_at_reference(self):
        self.assertAlmostEqual(b.nitrification_derating_factor(25), 1.0, places=4)

    def test_derating_cold(self):
        # At 10 degC, ~35% of reference (within the documented 25-40% band).
        f = b.nitrification_derating_factor(10)
        self.assertGreaterEqual(f, 0.25)
        self.assertLessEqual(f, 0.45)

    def test_derating_warm_saturates(self):
        self.assertLessEqual(b.nitrification_derating_factor(35), 1.0)

    def test_penalty_pct(self):
        self.assertAlmostEqual(b.nitrification_penalty_pct(25), 0.0, places=1)
        self.assertGreater(b.nitrification_penalty_pct(10), 50.0)


class TestCapacityAndLoading(unittest.TestCase):
    def test_capacity_derated(self):
        cap = b.biofilter_capacity_derated(200, 1.5, 10)
        # 200 * 1.5 * ~0.354 ~ 106.
        self.assertAlmostEqual(cap, 106.0, places=0)

    def test_loading_ratio_none_when_no_capacity(self):
        self.assertIsNone(b.biofilter_loading_ratio(100, 0))

    def test_status_from_ratio(self):
        self.assertEqual(b.biofilter_status_from_ratio(0.5), "adequate")
        self.assertEqual(b.biofilter_status_from_ratio(0.85), "marginal")
        self.assertEqual(b.biofilter_status_from_ratio(1.5), "overloaded")
        self.assertEqual(b.biofilter_status_from_ratio(None), "unknown")


class TestAlkalinityFromFeed(unittest.TestCase):
    def test_returns_none_without_volume(self):
        self.assertIsNone(b.alkalinity_demand_from_feed(5.0, tank_volume_m3=None))

    def test_with_volume(self):
        d = b.alkalinity_demand_from_feed(5.0, 40, tank_volume_m3=50.0)
        self.assertIsNotNone(d)
        self.assertGreater(d, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
