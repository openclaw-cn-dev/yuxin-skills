"""Unit tests for disease signal matching (diseases.py) and species registry."""
import unittest

from ras_aqua import diseases as d
from ras_aqua.schemas import Severity


class TestDiseaseMatching(unittest.TestCase):
    def test_no_match_when_conditions_empty(self):
        self.assertEqual(d.match_disease_signals([]), [])

    def test_ipn_match(self):
        w = d.match_disease_signals(["high_NH3", "crowding", "low_DO"])
        names = [x.disease for x in w]
        self.assertIn("Infectious pancreatic necrosis (IPN)", names)

    def test_vhs_critical_requires_all_conditions(self):
        # Missing one condition -> no VHS match.
        w = d.match_disease_signals(["low_DO", "thermal_shock_cold"])
        self.assertFalse(any("VHS" in x.disease for x in w))
        # All three -> VHS fires.
        w2 = d.match_disease_signals(["low_DO", "thermal_shock_cold", "crowding"])
        self.assertTrue(any("VHS" in x.disease for x in w2))

    def test_severity_ordering(self):
        w = d.match_disease_signals(["high_NH3", "crowding", "low_DO",
                                     "thermal_shock_cold"])
        # Critical signals come first.
        sev = [x.severity for x in w]
        self.assertEqual(sev, sorted(sev, key=lambda s: {
            Severity.CRITICAL: 0, Severity.ALERT: 1, Severity.WATCH: 2, Severity.OK: 3}[s]))

    def test_woah_flag(self):
        w = d.match_disease_signals(["low_DO", "thermal_shock_cold", "crowding"])
        vhs = next(x for x in w if "VHS" in x.disease)
        self.assertTrue(vhs.woah_notifiable)


class TestSpeciesRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from config import load_settings
        from ras_aqua.species import SpeciesRegistry
        cls.reg = SpeciesRegistry.from_settings(load_settings())

    def test_normalize_aliases(self):
        self.assertEqual(self.reg.normalize_species("Rainbow Trout"), "rainbow_trout")
        self.assertEqual(self.reg.normalize_species("salmo salar"), "atlantic_salmon")
        self.assertEqual(self.reg.normalize_species("char"), "arctic_char")

    def test_rejects_warm_water(self):
        from ras_aqua.errors import InputValidationError
        with self.assertRaises(InputValidationError):
            self.reg.normalize_species("tilapia")

    def test_resolve_envelope(self):
        e = self.reg.resolve_envelope("rainbow_trout", "growout")
        self.assertEqual(e.life_stage, "growout")
        self.assertIsNotNone(e.envelope)

    def test_default_life_stage(self):
        e = self.reg.resolve_envelope("arctic_char", None)
        self.assertEqual(e.life_stage, "growout")

    def test_list_species_and_media(self):
        self.assertIn("rainbow_trout", self.reg.list_species())
        self.assertGreaterEqual(len(self.reg.list_media()), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
