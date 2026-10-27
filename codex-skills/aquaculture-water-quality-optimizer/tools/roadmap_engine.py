# -*- coding: utf-8 -*-
"""
roadmap_engine.py — Generate a prioritized, evidence-based improvement roadmap.

Rules map low dimension scores (or flagged parameters) to concrete actions.
Actions are ranked by a mortality-risk urgency index:
  urgency = (100 - dimension_score) × impact_coefficient × hours_to_harm_coefficient
where acute toxicants (NH3, NO2, low DO) get higher hours-to-harm weights.
"""
from __future__ import annotations

from typing import List, Optional

from schemas import (
    CompositeScore,
    DimensionScore,
    Framework,
    IntakeProfile,
    Roadmap,
    RoadmapItem,
)


# Action templates keyed by target parameter / situation.
ACTION_CATALOG = {
    "do_mg_l": [
        {
            "action": "Increase mechanical aeration or emergency oxygenation immediately",
            "effort": "medium",
            "impact": "high",
            "target_dimension": "Oxygen status",
            "rationale": "Low DO causes rapid mortality; dawn minima are the most dangerous period.",
            "owner": "Farm manager / technician",
            "expected_effect": "DO > 4 mg/L within hours; reduced hypoxia stress",
            "urgency_hours": 4,
            "framework_source": "Boyd & Tucker (1998); Timmons & Guerdat (2017)",
        },
        {
            "action": "Reduce feeding until DO stabilizes",
            "effort": "low",
            "impact": "medium",
            "target_dimension": "Oxygen status",
            "rationale": "Feeding consumes oxygen through digestion and uneaten feed decomposition.",
            "owner": "Feeding technician",
            "expected_effect": "Lower oxygen demand; 10–30% DO improvement",
            "urgency_hours": 12,
            "framework_source": "Boyd (2020)",
        },
        {
            "action": "Increase water exchange or partial flushing",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "Oxygen status",
            "rationale": "Replaces oxygen-depleted, high-BOD water with oxygenated source water.",
            "owner": "Operations team",
            "expected_effect": "DO boost and removal of organic load",
            "urgency_hours": 24,
            "framework_source": "FAO pond management manuals",
        },
    ],
    "unionized_nh3_mg_l": [
        {
            "action": "Stop feeding and reduce protein input until ammonia detoxified",
            "effort": "low",
            "impact": "high",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "NH3 is acutely toxic at high pH/temperature; every feed input adds ammonia.",
            "owner": "Feeding manager",
            "expected_effect": "Reduced TAN load; stops further NH3 accumulation",
            "urgency_hours": 2,
            "framework_source": "Emerson et al. (1975); Timmons & Guerdat (2017)",
        },
        {
            "action": "Verify/adjust biofilter function or floc activity (RAS/BFT)",
            "effort": "high",
            "impact": "high",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "In intensive systems nitrogen removal depends on nitrifying/heterotrophic bacterial performance.",
            "owner": "Biofilter technician / RAS engineer",
            "expected_effect": "TAN < 1 mg/L, NH3 < 0.05 mg/L within 24–48 h",
            "urgency_hours": 8,
            "framework_source": "Malone & Pfeiffer (2006); Avnimelech (2012)",
        },
        {
            "action": "Lower pH cautiously if NH3 fraction is high (pH > 8.5)",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "Emerson equilibrium: NH3 fraction rises with pH. Lowering pH shifts NH3 → NH4⁺.",
            "owner": "Water-quality technician",
            "expected_effect": "Immediate reduction in unionized NH3 fraction",
            "urgency_hours": 6,
            "framework_source": "Emerson et al. (1975)",
        },
    ],
    "tan_mg_l": [
        {
            "action": "Reduce stocking density or feed loading in overloaded systems",
            "effort": "high",
            "impact": "high",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "Chronic TAN elevation signals carrying-capacity exceedance.",
            "owner": "Farm manager",
            "expected_effect": "Sustainable nitrogen load matching system removal capacity",
            "urgency_hours": 72,
            "framework_source": "Timmons & Guerdat (2017); Boyd & Tucker (1998)",
        },
    ],
    "no2_mg_l": [
        {
            "action": "Add chloride source (NaCl) to mitigate nitrite toxicity",
            "effort": "low",
            "impact": "high",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "Chloride competitively inhibits nitrite uptake across gills; chloride:nitrite ratio > 10:1 is protective.",
            "owner": "Water-quality technician",
            "expected_effect": "Reduced methemoglobinemia risk within hours",
            "urgency_hours": 6,
            "framework_source": "Boyd & Tucker (1998)",
        },
        {
            "action": "Accelerate nitrification biofilter maturation or water exchange",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "NO2⁻ accumulates when nitrite-oxidizing bacteria lag; biofilter maturity or dilution removes it.",
            "owner": "RAS/pond technician",
            "expected_effect": "NO2⁻ < 0.5 mg/L",
            "urgency_hours": 24,
            "framework_source": "Malone & Pfeiffer (2006)",
        },
    ],
    "ph": [
        {
            "action": "Buffer pH with agricultural lime or sodium bicarbonate",
            "effort": "medium",
            "impact": "high",
            "target_dimension": "pH/alkalinity stability",
            "rationale": "Low pH/alkalinity destabilizes nitrification and increases stress; lime raises both.",
            "owner": "Water-quality technician",
            "expected_effect": "pH 7.5–8.5, alkalinity > 80 mg/L CaCO3",
            "urgency_hours": 24,
            "framework_source": "Boyd (2020); Avnimelech (2012)",
        },
        {
            "action": "Reduce afternoon pH spikes by managing algal bloom / aeration",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "pH/alkalinity stability",
            "rationale": "High pH raises NH3 toxicity; afternoon photosynthesis can push pH > 9 in ponds.",
            "owner": "Farm manager",
            "expected_effect": "Stabilized daily pH swing < 1 unit",
            "urgency_hours": 24,
            "framework_source": "Boyd & Tucker (1998)",
        },
    ],
    "alkalinity_mg_l_caCO3": [
        {
            "action": "Apply alkalinity amendment (CaCO3 / NaHCO3 / hydrated lime)",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "pH/alkalinity stability",
            "rationale": "Adequate alkalinity buffers pH and provides inorganic carbon for nitrification/photosynthesis.",
            "owner": "Water-quality technician",
            "expected_effect": "Alkalinity > 80 mg/L CaCO3, reduced pH swings",
            "urgency_hours": 48,
            "framework_source": "Boyd (2020); Timmons & Guerdat (2017)",
        },
    ],
    "temp_c": [
        {
            "action": "Install shade/insulation or regulate water source temperature",
            "effort": "high",
            "impact": "medium",
            "target_dimension": "Temperature/salinity fit",
            "rationale": "Temperature outside optimal range reduces growth and immune competence.",
            "owner": "Engineering / farm manager",
            "expected_effect": "Temperature within species optimum",
            "urgency_hours": 168,
            "framework_source": "Boyd (2020)",
        },
    ],
    "salinity_ppt": [
        {
            "action": "Adjust salinity gradually to species optimum",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "Temperature/salinity fit",
            "rationale": "Salinity mismatches cause osmotic stress and affect ammonia toxicity calculations.",
            "owner": "Water-quality technician",
            "expected_effect": "Salinity within optimum band",
            "urgency_hours": 72,
            "framework_source": "FAO species manuals",
        },
    ],
    "c_n_ratio": [
        {
            "action": "Add carbon source (molasses, starch, glycerol) to reach C:N 10–15",
            "effort": "medium",
            "impact": "high",
            "target_dimension": "Nitrogen toxicity risk",
            "rationale": "Biofloc heterotrophic bacteria need C:N ~10–15 to assimilate TAN into microbial protein.",
            "owner": "BFT technician",
            "expected_effect": "TAN draw-down, stable floc, C:N 10–15",
            "urgency_hours": 24,
            "framework_source": "Avnimelech (2012); Avnimelech (1999)",
        },
    ],
    "tss_mg_l": [
        {
            "action": "Thin or harvest excess floc if TSS > 500 mg/L",
            "effort": "high",
            "impact": "medium",
            "target_dimension": "Oxygen status",
            "rationale": "Excessive floc increases respiration demand and can settle, causing anoxic zones.",
            "owner": "BFT technician",
            "expected_effect": "TSS 300–500 mg/L, lower oxygen demand",
            "urgency_hours": 48,
            "framework_source": "Emerenciano et al. (2017)",
        },
    ],
    "biosecurity": [
        {
            "action": "Implement immediate mortality diagnostic sampling and quarantine",
            "effort": "high",
            "impact": "high",
            "target_dimension": "Biosecurity",
            "rationale": "Sudden mortality requires pathogen identification before any treatment; quarantine prevents spread.",
            "owner": "Veterinarian / diagnostic lab",
            "expected_effect": "Pathogen identification; containment of disease event",
            "urgency_hours": 4,
            "framework_source": "WOAH (2024) Aquatic Animal Health Code",
        },
        {
            "action": "Document health checks and establish veterinary oversight protocol",
            "effort": "low",
            "impact": "medium",
            "target_dimension": "Biosecurity",
            "rationale": "WOAH-aligned farms require routine health surveillance and documented corrective actions.",
            "owner": "Farm manager / veterinarian",
            "expected_effect": "Earlier disease detection and regulatory compliance",
            "urgency_hours": 168,
            "framework_source": "WOAH (2024) Aquatic Animal Health Code",
        },
        {
            "action": "Disinfect shared equipment and control predator/bird access",
            "effort": "medium",
            "impact": "medium",
            "target_dimension": "Biosecurity",
            "rationale": "Mechanical and vector transmission are common routes for aquatic pathogens.",
            "owner": "Operations team",
            "expected_effect": "Reduced cross-contamination risk",
            "urgency_hours": 48,
            "framework_source": "WOAH (2024) Aquatic Animal Health Code",
        },
    ],
}


# Preventive / maintenance actions used when no acute flags are present.
PREVENTIVE_ACTIONS = {
    "new_farm": [
        {
            "action": "Verify carrying capacity before full stocking (feed-loading vs oxygen/biofilter capacity)",
            "effort": "medium",
            "impact": "high",
            "target_dimension": "Oxygen status",
            "rationale": "Overstocking is the root cause of most water-quality failures; match biomass to system capacity.",
            "owner": "Farm manager / aquaculture engineer",
            "expected_effect": "Sustainable stocking density aligned with system oxygen and waste-removal capacity",
            "urgency_hours": 168,
            "framework_source": "Boyd & Tucker (1998); Timmons & Guerdat (2017); Piedrahita (2003)",
        },
        {
            "action": "Establish daily water-quality monitoring protocol (DO dawn/dusk, pH, temp, NH3/NO2 weekly)",
            "effort": "low",
            "impact": "high",
            "target_dimension": "Oxygen status",
            "rationale": "Early detection of trends prevents acute crises.",
            "owner": "Technician",
            "expected_effect": "Trend detection 24–48 h before dangerous thresholds",
            "urgency_hours": 168,
            "framework_source": "FAO technical papers; Boyd (2020)",
        },
        {
            "action": "Install backup aeration / oxygenation and alarm system",
            "effort": "high",
            "impact": "high",
            "target_dimension": "Oxygen status",
            "rationale": "Power failures and dawn DO minima are common mortality events; redundancy saves crops.",
            "owner": "Engineering / farm manager",
            "expected_effect": "Uninterrupted DO supply during emergencies",
            "urgency_hours": 168,
            "framework_source": "Boyd & Tucker (1998); Timmons & Guerdat (2017)",
        },
        {
            "action": "Implement quarantine and health-documentation procedures before stocking",
            "effort": "medium",
            "impact": "high",
            "target_dimension": "Biosecurity",
            "rationale": "WOAH-aligned biosecurity starts before animals enter the farm.",
            "owner": "Veterinarian / farm manager",
            "expected_effect": "Reduced pathogen introduction risk",
            "urgency_hours": 168,
            "framework_source": "WOAH (2024) Aquatic Animal Health Code",
        },
    ],
    "all_clear": [
        {
            "action": "Continue routine monitoring and preventive maintenance",
            "effort": "low",
            "impact": "medium",
            "target_dimension": "Oxygen status",
            "rationale": "Stable water quality today does not guarantee stability tomorrow; maintain surveillance.",
            "owner": "Technician",
            "expected_effect": "Sustained water quality within optimal bands",
            "urgency_hours": 168,
            "framework_source": "FAO technical papers",
        },
    ],
}


def _urgency_coefficient(dimension: str, param: Optional[str]) -> float:
    """Acute toxicants and DO get higher urgency weights."""
    if dimension == "Oxygen status":
        return 3.0
    if dimension == "Nitrogen toxicity risk" and param in ("unionized_nh3_mg_l", "no2_mg_l"):
        return 3.5
    if dimension == "Nitrogen toxicity risk":
        return 2.0
    if dimension == "Biosecurity":
        return 2.5
    return 1.0


def build_roadmap(profile: IntakeProfile, score: CompositeScore, fw: Framework) -> Roadmap:
    """Build a ranked roadmap from flagged dimensions/parameters."""
    candidates: List[RoadmapItem] = []

    # Parameter-driven actions
    for dim in score.dimensions:
        for param in dim.flagged_params:
            templates = ACTION_CATALOG.get(param, [])
            if not templates and param.startswith("shared_"):
                templates = ACTION_CATALOG.get("biosecurity", [])
            for tpl in templates:
                if dim.value >= 85 and tpl["impact"] == "medium":
                    continue  # skip lower-impact actions when dimension is already good
                urgency = (100.0 - dim.value) * _urgency_coefficient(dim.dimension, param) / max(tpl.get("urgency_hours", 24), 1)
                candidates.append(
                    RoadmapItem(
                        rank=1,  # rank assigned after sorting
                        action=tpl["action"],
                        target_parameter=param,
                        target_dimension=tpl.get("target_dimension", dim.dimension),
                        effort=tpl["effort"],
                        impact=tpl["impact"],
                        rationale=tpl["rationale"],
                        owner=tpl["owner"],
                        expected_effect=tpl["expected_effect"],
                        framework_source=tpl["framework_source"],
                        urgency_hours=tpl.get("urgency_hours"),
                    )
                )

    # Dimension-driven biosecurity fallback when dimension is poor but no specific flag exists
    biosecurity_dim = next((d for d in score.dimensions if d.dimension == "Biosecurity"), None)
    if biosecurity_dim and biosecurity_dim.value < 70:
        for tpl in ACTION_CATALOG.get("biosecurity", []):
            urgency = (100.0 - biosecurity_dim.value) * _urgency_coefficient("Biosecurity", None) / max(tpl.get("urgency_hours", 24), 1)
            candidates.append(
                RoadmapItem(
                    rank=1,
                    action=tpl["action"],
                    target_dimension="Biosecurity",
                    effort=tpl["effort"],
                    impact=tpl["impact"],
                    rationale=tpl["rationale"],
                    owner=tpl["owner"],
                    expected_effect=tpl["expected_effect"],
                    framework_source=tpl["framework_source"],
                    urgency_hours=tpl.get("urgency_hours"),
                )
            )

    # Sort by urgency desc, then by impact, then by effort asc
    impact_order = {"high": 0, "medium": 1, "low": 2}
    effort_order = {"low": 0, "medium": 1, "high": 2}
    candidates.sort(key=lambda r: (
        -((100.0 - score.dimension_score(r.target_dimension)) * _urgency_coefficient(r.target_dimension, r.target_parameter) / max(r.urgency_hours or 24, 1)) if hasattr(score, "dimension_score") else -1,
        impact_order.get(r.impact, 1),
        effort_order.get(r.effort, 1),
    ))

    # Compute composite-based urgency for sort
    def _rank_key(item: RoadmapItem) -> float:
        dim_value = score.dimension_score(item.target_dimension or '')
        coeff = _urgency_coefficient(item.target_dimension, item.target_parameter)
        hours = max(item.urgency_hours or 24, 1)
        return (100.0 - dim_value) * coeff / hours

    candidates.sort(key=_rank_key, reverse=True)

    # Deduplicate by action text
    seen = set()
    deduped = []
    for c in candidates:
        if c.action.lower() in seen:
            continue
        seen.add(c.action.lower())
        deduped.append(c)

    # Fallback: if no acute actions generated, add preventive actions
    if not deduped:
        preventives = PREVENTIVE_ACTIONS.get("new_farm", PREVENTIVE_ACTIONS["all_clear"])
        for tpl in preventives:
            deduped.append(
                RoadmapItem(
                    rank=1,
                    action=tpl["action"],
                    target_dimension=tpl["target_dimension"],
                    effort=tpl["effort"],
                    impact=tpl["impact"],
                    rationale=tpl["rationale"],
                    owner=tpl["owner"],
                    expected_effect=tpl["expected_effect"],
                    framework_source=tpl["framework_source"],
                    urgency_hours=tpl.get("urgency_hours"),
                )
            )

    for idx, item in enumerate(deduped, start=1):
        item.rank = idx

    schedule = (
        "Monitor DO and NH3 every 2–4 h during acute events; resume daily routine once all dimensions > 75. "
        "Record pH/alkalinity, NO2, and temperature daily until stable; weekly thereafter."
    )
    stopgap = None
    if score.composite < 50:
        stopgap = (
            "CRITICAL: The system is in a high-risk state. Activate emergency aeration, stop or reduce feeding, "
            "and begin water exchange/biofilter diagnostics before any non-urgent work."
        )

    return Roadmap(items=deduped, monitoring_schedule=schedule, stopgap_note=stopgap)


# Attach helper to CompositeScore for roadmap use (monkey patch allowed because model already frozen).


