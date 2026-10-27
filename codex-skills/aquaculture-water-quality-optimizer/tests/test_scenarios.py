# -*- coding: utf-8 -*-
"""
test_scenarios.py — Automated regression harness for the five canonical scenarios.

Run: pytest tests/test_scenarios.py -v

Each scenario builds an IntakeProfile, selects a framework, computes a score, and builds
a roadmap. Assertions validate:
  * framework is selected from the registry
  * all five dimensions are scored
  * expected low dimensions are flagged
  * top roadmap actions match the scenario's acute risk
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add tools/ to import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from schemas import BiosecurityFlags, IntakeProfile, StockingInfo, SystemType, WaterParameters
from frameworks import FRAMEWORK_REGISTRY, select_framework
from scoring_engine import compute_score
from roadmap_engine import build_roadmap

DIMENSIONS = {
    "Oxygen status",
    "Nitrogen toxicity risk",
    "pH/alkalinity stability",
    "Temperature/salinity fit",
    "Biosecurity",
}


def _assert_dimensions(score):
    names = {d.dimension for d in score.dimensions}
    assert names == DIMENSIONS, f"missing dimensions: {DIMENSIONS - names}"


def test_scenario_1_shrimp_pond_low_do():
    """Shrimp pond: DO 2.5 mg/L at dawn. Expect oxygen and biosecurity actions."""
    profile = IntakeProfile(
        stocking=StockingInfo(species="whiteleg shrimp", system_type=SystemType.POND),
        water=WaterParameters(
            do_mg_l=2.5,
            tan_mg_l=1.2,
            ph=8.0,
            temp_c=29.0,
            salinity_ppt=15.0,
        ),
        biosecurity=BiosecurityFlags(recent_mortality=False),
    )
    framework = select_framework(profile.stocking.species, profile.stocking.system_type)
    assert framework.name.startswith("Penaeid shrimp pond")
    score = compute_score(profile, framework)
    _assert_dimensions(score)

    oxygen = next(d for d in score.dimensions if d.dimension == "Oxygen status")
    assert oxygen.value < 50, "DO 2.5 mg/L should score below 50"
    assert "do_mg_l" in oxygen.flagged_params

    roadmap = build_roadmap(profile, score, framework)
    top_actions = [r.action.lower() for r in roadmap.items]
    assert any("aeration" in a or "oxygenation" in a for a in top_actions), "aeration should be top action"


def test_scenario_2_ammonia_spike_in_ras():
    """RAS: TAN high, pH 8.2, warm. Expect un-ionized ammonia calc and mitigation."""
    profile = IntakeProfile(
        stocking=StockingInfo(species="atlantic salmon", system_type=SystemType.RAS),
        water=WaterParameters(
            do_mg_l=6.5,
            tan_mg_l=2.5,
            ph=8.2,
            temp_c=18.0,
            salinity_ppt=0.0,
        ),
        biosecurity=BiosecurityFlags(),
    )
    framework = select_framework(profile.stocking.species, profile.stocking.system_type)
    assert framework.name.startswith("Recirculating Aquaculture Systems")
    score = compute_score(profile, framework)
    _assert_dimensions(score)

    nitrogen = next(d for d in score.dimensions if d.dimension == "Nitrogen toxicity risk")
    assert nitrogen.value < 40, f"RAS TAN 2.5 + pH 8.2 should yield very low nitrogen score, got {nitrogen.value}"
    assert "unionized_nh3_mg_l" in nitrogen.flagged_params

    roadmap = build_roadmap(profile, score, framework)
    top_actions = [r.action.lower() for r in roadmap.items]
    assert any("biofilter" in a for a in top_actions), "biofilter action expected"
    assert any("feeding" in a or "protein" in a for a in top_actions), "feed reduction expected"


def test_scenario_3_new_tilapia_farm_setup():
    """New tilapia farm: plans stocking density. Expect carrying-capacity targets."""
    profile = IntakeProfile(
        stocking=StockingInfo(
            species="tilapia",
            system_type=SystemType.POND,
            stocking_count_m2=5.0,
            water_volume_m3=1000.0,
        ),
        water=WaterParameters(
            do_mg_l=5.5,
            ph=7.5,
            temp_c=28.0,
            salinity_ppt=0.0,
            alkalinity_mg_l_caCO3=80.0,
        ),
        biosecurity=BiosecurityFlags(health_checks_documented=True),
    )
    framework = select_framework(profile.stocking.species, profile.stocking.system_type)
    assert framework.name.startswith("Warm-water finfish pond")
    score = compute_score(profile, framework)
    _assert_dimensions(score)

    # New farms start in decent chemical state but need a preventive roadmap
    assert score.composite >= 60
    roadmap = build_roadmap(profile, score, framework)
    assert len(roadmap.items) >= 1


def test_scenario_4_disease_outbreak_biosecurity():
    """Sudden mortality. Expect WOAH-aligned biosecurity and diagnostic referral."""
    profile = IntakeProfile(
        stocking=StockingInfo(species="whiteleg shrimp", system_type=SystemType.POND),
        water=WaterParameters(
            do_mg_l=4.2,
            tan_mg_l=0.8,
            ph=8.0,
            temp_c=29.0,
            salinity_ppt=15.0,
        ),
        biosecurity=BiosecurityFlags(
            recent_mortality=True,
            shared_equipment_between_ponds=True,
            untreated_water_source=True,
        ),
    )
    framework = select_framework(profile.stocking.species, profile.stocking.system_type)
    score = compute_score(profile, framework)
    _assert_dimensions(score)

    bio = next(d for d in score.dimensions if d.dimension == "Biosecurity")
    assert bio.value < 60, "Multiple biosecurity flags should drive score below 60"

    roadmap = build_roadmap(profile, score, framework)
    top_actions = [r.action.lower() for r in roadmap.items]
    assert any("diagnostic" in a or "quarantine" in a for a in top_actions), "diagnostic/quarantine expected"


def test_scenario_5_biofloc_balance():
    """Biofloc C:N ratio management. Expect floc and carbon-source actions."""
    profile = IntakeProfile(
        stocking=StockingInfo(species="whiteleg shrimp", system_type=SystemType.BIOFLOC),
        water=WaterParameters(
            do_mg_l=4.0,
            tan_mg_l=1.8,
            ph=8.0,
            temp_c=29.0,
            salinity_ppt=20.0,
            c_n_ratio=6.0,
            tss_mg_l=650.0,
        ),
        biosecurity=BiosecurityFlags(),
    )
    framework = select_framework(profile.stocking.species, profile.stocking.system_type)
    assert framework.name.startswith("Biofloc Technology")
    score = compute_score(profile, framework)
    _assert_dimensions(score)

    # C:N too low → nitrogen not being assimilated
    nitrogen = next(d for d in score.dimensions if d.dimension == "Nitrogen toxicity risk")
    assert nitrogen.value < 60 or "c_n_ratio" in [p for d in score.dimensions for p in d.flagged_params]

    roadmap = build_roadmap(profile, score, framework)
    top_actions = [r.action.lower() for r in roadmap.items]
    assert any("carbon" in a or "c:n" in a for a in top_actions), "carbon-source/C:N action expected"


def test_framework_registry_complete():
    """Sanity: the framework registry contains the expected named frameworks."""
    names = {fw.name.split()[0] for fw in FRAMEWORK_REGISTRY}
    assert names >= {"Warm-water", "Penaeid", "Recirculating", "Biofloc", "Flow-through"}, names


def test_nh3_equilibrium_calculation():
    """Emerson equilibrium sanity check at 30 °C, pH 8.2, TAN 2.0."""
    water = WaterParameters(tan_mg_l=2.0, ph=8.2, temp_c=30.0)
    nh3 = water.unionized_nh3_mg_l
    assert nh3 is not None
    assert 0.1 < nh3 < 0.3, f"expected NH3 ~0.2 mg/L, got {nh3}"


if __name__ == "__main__":
    # Lightweight manual runner if pytest is not installed
    tests = [
        test_scenario_1_shrimp_pond_low_do,
        test_scenario_2_ammonia_spike_in_ras,
        test_scenario_3_new_tilapia_farm_setup,
        test_scenario_4_disease_outbreak_biosecurity,
        test_scenario_5_biofloc_balance,
        test_framework_registry_complete,
        test_nh3_equilibrium_calculation,
    ]
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as exc:
            print(f"FAIL {t.__name__}: {exc}")

