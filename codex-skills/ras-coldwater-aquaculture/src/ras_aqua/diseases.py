"""Disease early-warning signal matching for cold-water RAS salmonids.

Reference-grounded in WOAH Aquatic Animal Health Code (Tier 1) and
SECOND-KNOWLEDGE-BRAIN.md ?1.4. This module NEVER diagnoses a disease ? it
raises EARLY-WARNING signals by matching observed stress/environmental
conditions against published predisposing factors, and recommends veterinary
follow-up. The engine only emits signals; a veterinarian confirms diagnosis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .schemas import DiseaseWarning, Severity


@dataclass(frozen=True)
class DiseaseSignal:
    """A disease early-warning rule: the predisposing conditions that, when
    matched, raise a watch/alert/critical signal."""
    disease: str
    signal: str
    predisposing_conditions: List[str]
    severity: Severity
    woah_notifiable: bool = False
    follow_up: str = ""


# Rule table. Conditions are matched against a normalized set of condition
# tags produced by the biofilter/disease skill from the scorecard + RAS config.
DISEASE_REGISTRY: List[DiseaseSignal] = [
    DiseaseSignal(
        disease="Viral hemorrhagic septicemia (VHS)",
        signal="Cold-water rhabdovirus reactivation risk; VHS is WOAH-notifiable.",
        predisposing_conditions=["low_DO", "thermal_shock_cold", "crowding"],
        severity=Severity.CRITICAL,
        woah_notifiable=True,
        follow_up="Isolate affected lot; contact aquatic vet for PCR confirmation; report to competent authority if confirmed.",
    ),
    DiseaseSignal(
        disease="Infectious pancreatic necrosis (IPN)",
        signal="Stress-triggered IPN reactivation in fry/smolt; WOAH-notifiable.",
        predisposing_conditions=["high_NH3", "crowding", "low_DO"],
        severity=Severity.ALERT,
        woah_notifiable=True,
        follow_up="Reduce stressors, submit kidney/spleen samples for virology.",
    ),
    DiseaseSignal(
        disease="Infectious salmon anemia (ISA)",
        signal="ISA risk in Atlantic salmon under chronic stress; WOAH-notifiable.",
        predisposing_conditions=["high_CO2", "low_DO", "crowding"],
        severity=Severity.CRITICAL,
        woah_notifiable=True,
        follow_up="Mandatory report; PCR confirmation; slaughter/disinfection per WOAH code on confirmation.",
    ),
    DiseaseSignal(
        disease="Furunculosis (Aeromonas salmonicida)",
        signal="Bacterial furunculosis flare under stress + warm excursion.",
        predisposing_conditions=["high_NH3", "thermal_shock_warm", "crowding", "elevated_TAN"],
        severity=Severity.ALERT,
        woah_notifiable=False,
        follow_up="Antibacterial treatment under vet prescription; biosecurity review.",
    ),
    DiseaseSignal(
        disease="Saprolegniosis (fungal)",
        signal="Stress-mediated fungal infection; cold water + skin trauma.",
        predisposing_conditions=["low_DO", "thermal_shock_cold", "handling_stress"],
        severity=Severity.WATCH,
        woah_notifiable=False,
        follow_up="Formalin/bath treatment under vet guidance; reduce handling stress.",
    ),
    DiseaseSignal(
        disease="Gyrodactylosis (Gyrodactylus spp.)",
        signal="Ectoparasite bloom under crowding + stress.",
        predisposing_conditions=["crowding", "high_NH3", "low_DO"],
        severity=Severity.WATCH,
        woah_notifiable=True,
        follow_up="Skin/gill smear; antiparasitic bath under vet guidance.",
    ),
    DiseaseSignal(
        disease="Nitrification failure / NOB collapse",
        signal="Biofilter nitrification failure (NO2 spike, TAN rising) ? fish-health risk not a pathogen.",
        predisposing_conditions=["nitrification_failing", "elevated_NO2", "cold_shock_filter"],
        severity=Severity.CRITICAL,
        woah_notifiable=False,
        follow_up="Reduce feeding, partial water exchange, reseed biofilter, add alkalinity; monitor TAN/NO2 hourly.",
    ),
    DiseaseSignal(
        disease="Ammonia toxicity",
        signal="Acute un-ionized ammonia exposure above species threshold.",
        predisposing_conditions=["high_NH3", "elevated_TAN", "high_pH"],
        severity=Severity.CRITICAL,
        woah_notifiable=False,
        follow_up="Emergency: stop feeding, lower pH toward species floor, maximize aeration, partial water exchange.",
    ),
]


def match_disease_signals(conditions: Sequence[str],
                          registry: Optional[Sequence[DiseaseSignal]] = None
                          ) -> List[DiseaseWarning]:
    """Match observed condition tags against the disease rule table.

    A signal fires when ALL of its predisposing conditions are present in the
    observed set (conservative AND-match to avoid false positives). Returns
    warnings ordered by severity (critical first).
    """
    reg = list(registry) if registry is not None else DISEASE_REGISTRY
    observed = {c for c in conditions}
    warnings: List[DiseaseWarning] = []
    for sig in reg:
        if all(cond in observed for cond in sig.predisposing_conditions):
            warnings.append(DiseaseWarning(
                disease=sig.disease,
                signal=sig.signal,
                matched_conditions=list(sig.predisposing_conditions),
                severity=sig.severity,
                woah_notifiable=sig.woah_notifiable,
            ))
    # Order: CRITICAL > ALERT > WATCH > OK
    sev_rank = {Severity.CRITICAL: 0, Severity.ALERT: 1, Severity.WATCH: 2, Severity.OK: 3}
    warnings.sort(key=lambda w: sev_rank.get(w.severity, 9))
    return warnings


def conditions_from_scorecard(scorecard, ras_config=None) -> List[str]:
    """Derive normalized condition tags from a WaterQualityScorecard + RAS config.

    This is the deterministic bridge between the chemistry scorecard and the
    disease rule table, keeping the disease matcher pure and testable.
    """
    conds: List[str] = []
    if scorecard is None:
        return conds
    if scorecard.nh3_status in ("elevated", "toxic"):
        conds.append("high_NH3")
    if scorecard.do_status in ("low", "critical"):
        conds.append("low_DO")
    if scorecard.co2_status in ("elevated", "critical"):
        conds.append("high_CO2")
    if scorecard.nitrification_status == "failing":
        conds.append("nitrification_failing")
    if scorecard.nitrification_status == "stressed":
        conds.append("cold_shock_filter")
    for dv in scorecard.deviations:
        if dv.parameter == "NO2" and dv.severity in (Severity.ALERT, Severity.CRITICAL):
            conds.append("elevated_NO2")
        if dv.parameter == "TAN" and dv.severity in (Severity.ALERT, Severity.CRITICAL):
            conds.append("elevated_TAN")
        if dv.parameter == "pH" and dv.value is not None and dv.value >= 8.5:
            conds.append("high_pH")
        if dv.parameter == "T" and dv.value is not None:
            # Thermal shock tags require the species envelope safe range; the
            # skill supplies them directly when available. Here we only flag
            # obvious warm excursions via the deviation severity.
            if dv.severity in (Severity.ALERT, Severity.CRITICAL):
                conds.append("thermal_shock_warm" if dv.value > 18 else "thermal_shock_cold")
    # Crowding is derived in the water-quality skill from biomass/tank density
    # (biomass_kg / tank_volume_m3 > 60), not here, to keep the matcher pure.
    return conds
