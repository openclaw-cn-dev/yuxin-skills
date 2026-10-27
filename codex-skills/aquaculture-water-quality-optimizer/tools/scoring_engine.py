# -*- coding: utf-8 -*-
"""
scoring_engine.py — deterministic, cited scoring for the five aquaculture dimensions.

Every dimension score is computed against a named framework envelope and returns:
- value: 0–100
- justification: human-readable sentence with parameter values and bounds
- sources: named framework citations
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from schemas import (
    BiosecurityFlags,
    CompositeScore,
    DimensionScore,
    EnvelopeCriterion,
    Framework,
    IntakeProfile,
    LifeStage,
)


DEFAULT_WEIGHTS = {
    "Oxygen status": 0.25,
    "Nitrogen toxicity risk": 0.25,
    "pH/alkalinity stability": 0.20,
    "Temperature/salinity fit": 0.15,
    "Biosecurity": 0.15,
}


def _piecewise_score(
    value: Optional[float],
    crit: EnvelopeCriterion,
    dimension_name: str,
    extra_note: str = "",
) -> Tuple[float, str, List[str]]:
    """
    Map a measured value to a 0-100 score using the envelope bands.
    Bands (in priority order):
      lethal_below / lethal_above  → 0
      stress zone                  → 25–75 linear
      optimal zone                 → 75–100 linear, plateau at 100 inside optimal
    Missing value → score 50, low confidence.
    """
    if value is None:
        return (
            50.0,
            f"{dimension_name}: {crit.parameter} not measured; neutral score assumed.{extra_note}",
            [crit.source],
        )

    v = float(value)

    # Lethal zones
    if crit.lethal_below is not None and v < crit.lethal_below:
        return (
            0.0,
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is below lethal threshold ({crit.lethal_below}{crit.unit}).{extra_note}",
            [crit.source],
        )
    if crit.lethal_above is not None and v > crit.lethal_above:
        return (
            0.0,
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} exceeds lethal threshold ({crit.lethal_above}{crit.unit}).{extra_note}",
            [crit.source],
        )

    # Stress band (below optimal)
    if crit.min_optimal is not None and crit.min_stress is not None and v < crit.min_optimal:
        if v >= crit.min_stress:
            score = 25.0 + 50.0 * (v - crit.min_stress) / max(1e-9, crit.min_optimal - crit.min_stress)
        else:
            # Below stress but not lethal: severe stress
            score = max(0.0, 25.0 * (v - (crit.lethal_below or 0.0)) / max(1e-9, crit.min_stress - (crit.lethal_below or 0.0)))
        return (
            round(score, 1),
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is below optimal ({crit.min_optimal}{crit.unit}){extra_note}.",
            [crit.source],
        )

    # Stress band (above optimal)
    if crit.max_optimal is not None and crit.max_stress is not None and v > crit.max_optimal:
        if v <= crit.max_stress:
            score = 25.0 + 50.0 * (crit.max_stress - v) / max(1e-9, crit.max_stress - crit.max_optimal)
        else:
            score = max(0.0, 25.0 * ((crit.lethal_above or 1e9) - v) / max(1e-9, (crit.lethal_above or 1e9) - crit.max_stress))
        return (
            round(score, 1),
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is above optimal ({crit.max_optimal}{crit.unit}){extra_note}.",
            [crit.source],
        )

    # Optimal plateau
    if crit.min_optimal is not None and crit.max_optimal is not None and crit.min_optimal <= v <= crit.max_optimal:
        return (
            100.0,
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is within optimal range ({crit.min_optimal}–{crit.max_optimal}{crit.unit}).{extra_note}",
            [crit.source],
        )

    # Single-sided optimal (only max)
    if crit.max_optimal is not None and crit.min_optimal is None and v <= crit.max_optimal:
        return (
            100.0,
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is at or below optimal maximum ({crit.max_optimal}{crit.unit}).{extra_note}",
            [crit.source],
        )

    # Single-sided optimal (only min)
    if crit.min_optimal is not None and crit.max_optimal is None and v >= crit.min_optimal:
        return (
            100.0,
            f"{dimension_name}: {crit.parameter}={v}{crit.unit} is at or above optimal minimum ({crit.min_optimal}{crit.unit}).{extra_note}",
            [crit.source],
        )

    # Fallback (no clear bands)
    return (
        75.0,
        f"{dimension_name}: {crit.parameter}={v}{crit.unit}; envelope has no clear band for this value.{extra_note}",
        [crit.source],
    )


def _get_crit(fw: Framework, param: str) -> Optional[EnvelopeCriterion]:
    for c in fw.envelope:
        if c.parameter == param:
            return c
    return None


def score_oxygen(profile: IntakeProfile, fw: Framework) -> DimensionScore:
    """Oxygen status dimension using DO saturation where available."""
    crit = _get_crit(fw, "do_mg_l")
    if crit is None:
        return DimensionScore(
            dimension="Oxygen status",
            value=50.0,
            weight=DEFAULT_WEIGHTS["Oxygen status"],
            justification="Framework has no DO envelope; neutral score.",
            sources=[fw.name],
            confidence="low",
        )
    value, justif, sources = _piecewise_score(profile.water.do_mg_l, crit, "Oxygen status")
    flagged = []
    if profile.water.do_mg_l is not None and value < 75:
        flagged.append("do_mg_l")
    # Biofloc TSS: high floc concentration increases oxygen demand
    tss_crit = _get_crit(fw, "tss_mg_l")
    if tss_crit and profile.water.tss_mg_l is not None:
        s, j, src = _piecewise_score(profile.water.tss_mg_l, tss_crit, "Oxygen status", extra_note=" TSS/floc concentration")
        # Blend DO score and TSS score, giving DO 2/3 weight
        value = round((value * 2.0 + s) / 3.0, 1)
        justif += " | " + j
        sources.extend(src)
        if s < 75:
            flagged.append("tss_mg_l")

    # Saturation annotation
    if profile.water.percent_saturation is not None:
        justif += f" DO saturation ≈ {profile.water.percent_saturation}%."
    return DimensionScore(
        dimension="Oxygen status",
        value=value,
        weight=DEFAULT_WEIGHTS["Oxygen status"],
        justification=justif,
        sources=sources + fw.citations[:1],
        flagged_params=flagged,
        confidence="high" if profile.water.do_mg_l is not None else "low",
    )


def score_nitrogen(profile: IntakeProfile, fw: Framework) -> DimensionScore:
    """Nitrogen toxicity risk: TAN, NH3, NO2. NH3 is the dominant acute toxicant."""
    sources: List[str] = []
    notes: List[str] = []
    scores: List[float] = []
    flagged: List[str] = []

    # TAN
    tan_crit = _get_crit(fw, "tan_mg_l")
    if tan_crit and profile.water.tan_mg_l is not None:
        s, j, src = _piecewise_score(profile.water.tan_mg_l, tan_crit, "Nitrogen toxicity risk", extra_note=" TAN")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("tan_mg_l")

    # Un-ionized NH3 (acute toxicant)
    nh3 = profile.water.unionized_nh3_mg_l
    nh3_crit = _get_crit(fw, "unionized_nh3_mg_l")
    if nh3_crit and nh3 is not None:
        s, j, src = _piecewise_score(nh3, nh3_crit, "Nitrogen toxicity risk", extra_note=f" un-ionized NH3 (Emerson equilibrium)")
        # NH3 dominates when elevated
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("unionized_nh3_mg_l")

    # NO2
    no2_crit = _get_crit(fw, "no2_mg_l")
    if no2_crit and profile.water.no2_mg_l is not None:
        s, j, src = _piecewise_score(profile.water.no2_mg_l, no2_crit, "Nitrogen toxicity risk", extra_note=" NO2")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("no2_mg_l")

    if not scores:
        return DimensionScore(
            dimension="Nitrogen toxicity risk",
            value=50.0,
            weight=DEFAULT_WEIGHTS["Nitrogen toxicity risk"],
            justification="No nitrogen parameters measured; neutral score assumed.",
            sources=[fw.name],
            confidence="low",
        )

    # NH3 gets 1.5x influence when present because it is the acute toxicant
    weights = []
    for p in ["tan_mg_l", "unionized_nh3_mg_l", "no2_mg_l"]:
        if p == "unionized_nh3_mg_l" and profile.water.unionized_nh3_mg_l is not None:
            weights.append(1.5)
        elif getattr(profile.water, p, None) is not None:
            weights.append(1.0)
    # Biofloc C:N ratio: low C:N means insufficient carbon to assimilate TAN
    cn_crit = _get_crit(fw, "c_n_ratio")
    if cn_crit and profile.water.c_n_ratio is not None:
        s, j, src = _piecewise_score(profile.water.c_n_ratio, cn_crit, "Nitrogen toxicity risk", extra_note=" C:N ratio")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        weights.append(1.0)
        if s < 75:
            flagged.append("c_n_ratio")

    value = round(sum(s * w for s, w in zip(scores, weights)) / max(sum(weights), 1.0), 1)
    return DimensionScore(
        dimension="Nitrogen toxicity risk",
        value=value,
        weight=DEFAULT_WEIGHTS["Nitrogen toxicity risk"],
        justification=" | ".join(notes),
        sources=list(dict.fromkeys(sources + fw.citations[:1])),
        flagged_params=flagged,
        confidence="high" if len(scores) >= 2 else "medium",
    )


def score_ph_alkalinity(profile: IntakeProfile, fw: Framework) -> DimensionScore:
    """pH/alkalinity stability. Both must be in acceptable bands."""
    sources: List[str] = []
    notes: List[str] = []
    scores: List[float] = []
    flagged: List[str] = []

    ph_crit = _get_crit(fw, "ph")
    if ph_crit and profile.water.ph is not None:
        s, j, src = _piecewise_score(profile.water.ph, ph_crit, "pH/alkalinity stability", extra_note=" pH")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("ph")

    alk_crit = _get_crit(fw, "alkalinity_mg_l_caCO3")
    if alk_crit and profile.water.alkalinity_mg_l_caCO3 is not None:
        s, j, src = _piecewise_score(profile.water.alkalinity_mg_l_caCO3, alk_crit, "pH/alkalinity stability", extra_note=" alkalinity")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("alkalinity_mg_l_caCO3")

    if not scores:
        return DimensionScore(
            dimension="pH/alkalinity stability",
            value=50.0,
            weight=DEFAULT_WEIGHTS["pH/alkalinity stability"],
            justification="No pH/alkalinity data; neutral score assumed.",
            sources=[fw.name],
            confidence="low",
        )

    value = round(sum(scores) / len(scores), 1)
    return DimensionScore(
        dimension="pH/alkalinity stability",
        value=value,
        weight=DEFAULT_WEIGHTS["pH/alkalinity stability"],
        justification=" | ".join(notes),
        sources=list(dict.fromkeys(sources + fw.citations[:1])),
        flagged_params=flagged,
        confidence="high" if len(scores) == 2 else "medium",
    )


def score_temp_salinity(profile: IntakeProfile, fw: Framework) -> DimensionScore:
    """Temperature/salinity fit."""
    sources: List[str] = []
    notes: List[str] = []
    scores: List[float] = []
    flagged: List[str] = []

    temp_crit = _get_crit(fw, "temp_c")
    if temp_crit and profile.water.temp_c is not None:
        s, j, src = _piecewise_score(profile.water.temp_c, temp_crit, "Temperature/salinity fit", extra_note=" temperature")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("temp_c")

    sal_crit = _get_crit(fw, "salinity_ppt")
    if sal_crit and profile.water.salinity_ppt is not None:
        s, j, src = _piecewise_score(profile.water.salinity_ppt, sal_crit, "Temperature/salinity fit", extra_note=" salinity")
        scores.append(s)
        notes.append(j)
        sources.extend(src)
        if s < 75:
            flagged.append("salinity_ppt")

    if not scores:
        return DimensionScore(
            dimension="Temperature/salinity fit",
            value=50.0,
            weight=DEFAULT_WEIGHTS["Temperature/salinity fit"],
            justification="No temperature/salinity data; neutral score assumed.",
            sources=[fw.name],
            confidence="low",
        )

    value = round(sum(scores) / len(scores), 1)
    return DimensionScore(
        dimension="Temperature/salinity fit",
        value=value,
        weight=DEFAULT_WEIGHTS["Temperature/salinity fit"],
        justification=" | ".join(notes),
        sources=list(dict.fromkeys(sources + fw.citations[:1])),
        flagged_params=flagged,
        confidence="high" if len(scores) == 2 else "medium",
    )


def score_biosecurity(profile: IntakeProfile, fw: Framework) -> DimensionScore:
    """
    Biosecurity score from the BiosecurityFlags checklist, aligned with WOAH.
    More flags raised → lower score. Positive controls (documentation, vet) add back points.
    """
    b = profile.biosecurity
    flags = [
        (b.recent_mortality, 35, "recent mortality reported"),
        (b.recent_stocking_without_quarantine, 25, "stocking without quarantine"),
        (b.shared_equipment_between_ponds, 15, "shared equipment between units"),
        (b.predators_or_birds_observed, 10, "predators/birds observed"),
        (b.untreated_water_source, 15, "untreated water source"),
        (b.recent_weather_extreme, 10, "recent weather extreme"),
        (b.disease_history, 20, "prior disease history"),
    ]
    controls = [
        (b.health_checks_documented, -15, "documented health checks"),
        (b.veterinary_oversight, -20, "veterinary oversight"),
    ]
    deductions = sum(penalty for triggered, penalty, _ in flags if triggered)
    credits = sum(abs(penalty) for active, penalty, _ in controls if active)
    value = max(0.0, min(100.0, 100.0 - deductions + credits))

    notes = []
    for triggered, _, text in flags:
        if triggered:
            notes.append(text)
    for active, _, text in controls:
        if active:
            notes.append(text)

    if not notes:
        justif = "No biosecurity risk flags reported; score assumes basic controls are in place."
    else:
        justif = "Biosecurity status: " + ", ".join(notes) + f". Composite penalty {deductions}, credits {credits}."

    return DimensionScore(
        dimension="Biosecurity",
        value=round(value, 1),
        weight=DEFAULT_WEIGHTS["Biosecurity"],
        justification=justif,
        sources=["WOAH (2024) Aquatic Animal Health Code — biosecurity chapter"] + fw.citations[-1:],
        flagged_params=[text for triggered, _, text in flags if triggered],
        confidence="medium" if any([b.recent_mortality, b.recent_stocking_without_quarantine]) else "high",
    )


def compute_score(profile: IntakeProfile, fw: Framework, weights: Optional[dict] = None) -> CompositeScore:
    """Run the five-dimension scoring pipeline and return a composite."""
    dims = [
        score_oxygen(profile, fw),
        score_nitrogen(profile, fw),
        score_ph_alkalinity(profile, fw),
        score_temp_salinity(profile, fw),
        score_biosecurity(profile, fw),
    ]
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    total_weight = sum(d.weight for d in dims)
    composite = round(sum(d.value * d.weight for d in dims) / max(total_weight, 1e-9), 1)

    confidence_levels = [d.confidence for d in dims]
    if "low" in confidence_levels or profile.critical_missing:
        overall_confidence = "low"
    elif confidence_levels.count("medium") >= 2:
        overall_confidence = "medium"
    else:
        overall_confidence = "high"

    missing_note = None
    if profile.critical_missing:
        missing_note = f"Critical missing fields: {', '.join(profile.critical_missing)}; scores may change with complete data."

    return CompositeScore(
        dimensions=dims,
        composite=composite,
        confidence=overall_confidence,
        missing_data_note=missing_note,
    )
