"""Integration tests for the full engine pipeline (engine.py)."""
import unittest

from ras_aqua import Engine
from ras_aqua.schemas import VerdictCategory


def _critical_req():
    return {
        "species": "rainbow_trout", "life_stage": "growout",
        "wq": {"T_C": 15, "DO_mgL": 5.5, "pH": 7.8, "TAN_mgL": 1.2,
               "NO2_mgL": 0.05, "NO3_mgL": 30, "alkalinity_mgL": 60, "CO2_mgL": 18},
        "ras_config": {"tank_volume_m3": 50, "makeup_pct": 5,
                       "biofilter_type": "mbbr_kaldnes_k1", "biofilter_area_m2": 300,
                       "flow_lpm": 500},
        "biomass_kg": 2000, "feed_kg_day": 25, "feed_protein_pct": 42,
        "target_objective": "health_assessment", "language": "en",
    }


def _optimal_req():
    return {
        "species": "rainbow_trout", "life_stage": "growout",
        "wq": {"T_C": 13, "DO_mgL": 8.5, "pH": 7.0, "TAN_mgL": 0.3,
               "NO2_mgL": 0.02, "NO3_mgL": 15, "alkalinity_mgL": 95, "CO2_mgL": 10},
        "ras_config": {"tank_volume_m3": 100, "makeup_pct": 2,
                       "biofilter_type": "mbbr_kaldnes_k3", "biofilter_area_m2": 2000,
                       "flow_lpm": 1000},
        "biomass_kg": 3000, "feed_kg_day": 15, "feed_protein_pct": 40,
        "target_objective": "general_advice", "language": "en",
    }


class TestEnginePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine.from_config()

    def test_critical_scenario(self):
        r = self.engine.run(requirements=_critical_req())
        self.assertIsNotNone(r.verdict)
        self.assertEqual(r.verdict.verdict, VerdictCategory.CRITICAL)
        self.assertEqual(r.scorecard.nh3_status, "elevated")
        self.assertEqual(r.scorecard.do_status, "low")
        self.assertEqual(r.biofilter_risk.biofilter_capacity_status, "overloaded")
        # All gates pass.
        self.assertTrue(all(v == "pass" for v in r.quality_gate_results.values()),
                        f"gates: {r.quality_gate_results}")

    def test_optimal_scenario(self):
        r = self.engine.run(requirements=_optimal_req())
        self.assertEqual(r.verdict.verdict, VerdictCategory.OPTIMAL)
        self.assertTrue(all(v == "pass" for v in r.quality_gate_results.values()))

    def test_report_serializes(self):
        import json
        r = self.engine.run(requirements=_critical_req())
        d = r.to_dict()
        # Round-trip JSON.
        json.dumps(d, default=str)
        self.assertIn("verdict", d)
        self.assertIn("scorecard", d)

    def test_clarification_when_no_payload(self):
        r = self.engine.run(user_message="my trout look sick what do I do?")
        # No structured payload -> intake incomplete -> no verdict.
        self.assertIsNone(r.verdict)
        self.assertGreaterEqual(r.degradation_level, 3)
        self.assertGreater(len(r.limitations), 0)

    def test_warm_water_rejected(self):
        r = self.engine.run(requirements={
            "species": "tilapia", "life_stage": "growout",
            "wq": {"T_C": 28, "DO_mgL": 5, "pH": 7.5, "TAN_mgL": 1.0},
            "target_objective": "general_advice", "language": "en"})
        # Intake rejects warm-water species -> no verdict, degradation.
        self.assertIsNone(r.verdict)
        self.assertGreaterEqual(r.degradation_level, 3)

    def test_vietnamese_language(self):
        r = self.engine.run(requirements={
            "species": "rainbow_trout", "life_stage": "growout",
            "wq": {"T_C": 13, "DO_mgL": 8.5, "pH": 7.0, "TAN_mgL": 0.3},
            "ras_config": {"biofilter_type": "mbbr_kaldnes_k3",
                           "biofilter_area_m2": 2000, "tank_volume_m3": 100},
            "biomass_kg": 3000, "feed_kg_day": 15,
            "target_objective": "general_advice", "language": "vi"})
        self.assertEqual(r.language, "vi")
        # Gate U4 (language) passes.
        self.assertEqual(r.quality_gate_results.get("U4"), "pass")

    def test_hooks_emitted(self):
        from ras_aqua.hooks import HookEvent
        events = []
        self.engine.hooks.subscribe(HookEvent.POST_SKILL,
                                    lambda ctx: events.append(ctx.payload["skill"]))
        try:
            self.engine.run(requirements=_optimal_req())
            # All 6 skills should have emitted.
            self.assertEqual(events[:6],
                             ["gather_requirements", "evidence_collector",
                              "water_quality_analysis", "biofilter_disease",
                              "knowledge_updater", "ras_advisor"])
        finally:
            self.engine.hooks.event_log.clear()

    def test_describe(self):
        d = self.engine.describe()
        self.assertEqual(d["skill_name"], "ras-coldwater-aquaculture")
        self.assertEqual(len(d["skills"]), 6)
        self.assertGreaterEqual(len(d["tools"]), 6)

    def test_inconclusive_when_sizing_without_config(self):
        # biofilter_sizing objective but no biofilter config -> Inconclusive.
        r = self.engine.run(requirements={
            "species": "rainbow_trout", "life_stage": "growout",
            "wq": {"T_C": 14, "DO_mgL": 8.5, "pH": 7.0, "TAN_mgL": 0.3},
            "target_objective": "biofilter_sizing", "language": "en"})
        self.assertEqual(r.verdict.verdict, VerdictCategory.INCONCLUSIVE)

    def test_health_check_without_biofilter_is_optimal(self):
        # Water quality within envelope, no biofilter config, health objective
        # -> Optimal on water quality (biofilter simply not assessed).
        r = self.engine.run(requirements={
            "species": "rainbow_trout", "life_stage": "growout",
            "wq": {"T_C": 14, "DO_mgL": 8.5, "pH": 7.0, "TAN_mgL": 0.3},
            "target_objective": "health_assessment", "language": "en"})
        self.assertEqual(r.verdict.verdict, VerdictCategory.OPTIMAL)

    def test_all_four_verdict_categories_reachable(self):
        seen = set()
        cases = [
            _critical_req(),    # Critical Alert
            _optimal_req(),     # Optimal
            {"species": "rainbow_trout", "life_stage": "growout",
             "wq": {"T_C": 14, "DO_mgL": 6.5, "pH": 7.0, "TAN_mgL": 0.4,
                     "NO2_mgL": 0.02, "NO3_mgL": 15, "alkalinity_mgL": 90, "CO2_mgL": 12},
             "ras_config": {"biofilter_type": "mbbr_kaldnes_k3",
                            "biofilter_area_m2": 1500, "tank_volume_m3": 80, "flow_lpm": 600},
             "biomass_kg": 2000, "feed_kg_day": 12,
             "target_objective": "health_assessment", "language": "en"},  # Adjust Required
            {"species": "rainbow_trout", "life_stage": "growout",
             "wq": {"T_C": 14, "DO_mgL": 8.5, "pH": 7.0, "TAN_mgL": 0.3},
             "target_objective": "biofilter_sizing", "language": "en"},  # Inconclusive
        ]
        for req in cases:
            r = self.engine.run(requirements=req)
            self.assertIsNotNone(r.verdict)
            seen.add(r.verdict.verdict)
        self.assertEqual(seen, {VerdictCategory.OPTIMAL, VerdictCategory.ADJUST,
                                 VerdictCategory.CRITICAL, VerdictCategory.INCONCLUSIVE})


class TestGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine.from_config()

    def test_all_gates_defined(self):
        from ras_aqua.gates import ALL_GATES
        names = [g for g, _ in ALL_GATES]
        for g in ("U1", "U2", "U3", "U4", "U5", "U6",
                  "G1", "G2", "G3", "G4", "G5"):
            self.assertIn(g, names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
