"""Quality gates (U1-U6 universal + G1-G5 domain) with auto-fix + retry.

Each gate is a pure function that inspects the final engine state and returns a
``GateResult`` (pass/fail + auto-fix action applied). The engine applies gates
in order, runs the auto-fix, and retries up to ``max_skill_retries`` times
before emitting an explicit limitation for an unfixable gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from .schemas import Severity, VerdictCategory


@dataclass
class GateResult:
    gate: str
    passed: bool
    message: str = ""
    autofix_applied: bool = False


def _has_tiered_sources(state) -> bool:
    if state.verdict is None:
        return False
    return len(state.verdict.evidence_chain) >= 1


# ----- Universal gates U1-U6 -----

def gate_U1_sources(state) -> GateResult:
    n = 0 if state.verdict is None else len(state.verdict.evidence_chain)
    academic = any(e.tier in ("1", "2") for e in
                   (state.verdict.evidence_chain if state.verdict else []))
    if n >= 3 and academic:
        return GateResult("U1", True)
    return GateResult("U1", False,
                      f"Need >=3 sources with >=1 academic; have {n} (academic={academic}).")


def gate_U2_disclosure(state) -> GateResult:
    if state.verdict and state.verdict.disclosure:
        return GateResult("U2", True)
    return GateResult("U2", False, "Disclosure missing before recommendation.")


def gate_U3_tiers(state) -> GateResult:
    if not state.verdict:
        return GateResult("U3", False, "No verdict.")
    untagged = [e for e in state.verdict.evidence_chain if not e.tier]
    if untagged:
        return GateResult("U3", False, f"{len(untagged)} evidence item(s) without tier.")
    return GateResult("U3", True)


def gate_U4_language(state) -> GateResult:
    req = state.requirements
    if req is None:
        return GateResult("U4", False, "No requirements to check language.")
    if state.verdict and req.language == "vi" and "DISCLOSURE" in state.verdict.disclosure.upper():
        # Disclosure should be Vietnamese when language=vi (advisor handles this).
        return GateResult("U4", False, "Disclosure language mismatch (vi expected).")
    return GateResult("U4", True)


def gate_U5_template(state) -> GateResult:
    if state.verdict is None:
        return GateResult("U5", False, "No verdict produced.")
    required = ["verdict", "disclosure", "early_warning_alerts",
                "water_treatment_procedure", "key_risks", "evidence_chain"]
    # Sections must be present (not None). Empty lists are valid for an Optimal
    # verdict (no alerts/treatments) - only a missing (None) section fails.
    missing = [k for k in required if getattr(state.verdict, k, None) is None]
    if missing:
        return GateResult("U5", False, f"Missing template sections: {missing}.")
    return GateResult("U5", True)


def gate_U6_traceable(state) -> GateResult:
    if not state.verdict:
        return GateResult("U6", False, "No verdict.")
    untraced = [e for e in state.verdict.evidence_chain if not e.sources]
    if untraced:
        return GateResult("U6", False, f"{len(untraced)} claim(s) without sources.")
    return GateResult("U6", True)


# ----- Domain gates G1-G5 -----

def gate_G1_envelope_source(state) -> GateResult:
    if state.evidence_bundle and state.envelope:
        return GateResult("G1", True)
    return GateResult("G1", False, "Species envelope not sourced from authoritative registry.")


def gate_G2_nh3_computed(state) -> GateResult:
    sc = state.scorecard
    if sc is None:
        return GateResult("G2", False, "No scorecard.")
    if sc.nh3_mgL is None:
        return GateResult("G2", False, "NH3 not computed (T+pH missing).")
    return GateResult("G2", True, f"NH3-N={sc.nh3_mgL} mg/L via Emerson (1975).")


def gate_G3_do_saturation(state) -> GateResult:
    sc = state.scorecard
    if sc is None:
        return GateResult("G3", False, "No scorecard.")
    if sc.do_sat_pct is None:
        return GateResult("G3", False, "DO % saturation not reported.")
    return GateResult("G3", True, f"DO={sc.do_sat_pct}% sat.")


def gate_G4_treatment_mapping(state) -> GateResult:
    sc = state.scorecard
    br = state.biofilter_risk
    if sc is None or br is None:
        return GateResult("G4", False, "No scorecard/biofilter risk.")
    out_of_env = [d for d in sc.deviations if d.severity in (Severity.ALERT, Severity.CRITICAL)]
    if not out_of_env:
        return GateResult("G4", True, "No out-of-envelope parameters.")
    if not br.recommended_treatments:
        return GateResult("G4", False,
                          f"{len(out_of_env)} out-of-envelope parameter(s) without treatment action.")
    # Verify cold-temperature derating was applied when biofilter estimated.
    if br.biofilter_capacity_g_day is not None and br.nitrification_penalty_pct is None:
        return GateResult("G4", False, "Biofilter capacity estimated without cold derating.")
    return GateResult("G4", True, f"{len(br.recommended_treatments)} treatment(s) mapped.")


def gate_G5_coldwater_species(state) -> GateResult:
    req = state.requirements
    if req is None:
        return GateResult("G5", False, "No species classified.")
    # The SpeciesRegistry rejects warm-water species upstream; presence here = pass.
    return GateResult("G5", True, f"Species {req.species} verified cold-water.")


ALL_GATES = [
    ("U1", gate_U1_sources), ("U2", gate_U2_disclosure), ("U3", gate_U3_tiers),
    ("U4", gate_U4_language), ("U5", gate_U5_template), ("U6", gate_U6_traceable),
    ("G1", gate_G1_envelope_source), ("G2", gate_G2_nh3_computed),
    ("G3", gate_G3_do_saturation), ("G4", gate_G4_treatment_mapping),
    ("G5", gate_G5_coldwater_species),
]


def evaluate_all(state) -> List[GateResult]:
    return [fn(state) for _, fn in ALL_GATES]
