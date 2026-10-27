"""Skill 2 ? assemble the authoritative evidence bundle for the species+stage.

Pulls envelopes from the ``SpeciesRegistry`` (cached, Tier 1-3), augments with
biofilter media parameters, and emits the disease reference list from the
disease registry. Live web sources are attempted only when an
``llm_adapter``/web tool is available and the feature flag is set; otherwise
the bundle degrades to the cached envelopes with an explicit limitation flag.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

from ..diseases import DISEASE_REGISTRY
from ..schemas import EvidenceItem
from .base import Skill, SkillContext


class EvidenceCollectorSkill(Skill):
    name = "evidence_collector"
    step = 2
    description = ("Fetch authoritative species-specific water-quality envelopes, "
                   "biofilter nitrification parameters, and disease-risk references.")
    depends_on = ["gather_requirements"]
    prompt_template = "evidence_collector"
    input_schema = "assets/schemas/requirements.schema.json"
    output_schema = ""
    tags = ["evidence", "rag"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        req = ctx.state.requirements
        if req is None:
            return self._degraded_result(
                {"evidence_bundle": None},
                limitations=["No requirements available."], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)
        env = ctx.state.envelope or {}
        species = req.species
        stage = req.life_stage

        bundle: Dict[str, Any] = {
            "species": species,
            "life_stage": stage,
            "wq_envelope": env,
            "nh3_chronic_mgL": _get(env, "NH3N_mgL", "chronic"),
            "nh3_acute_mgL": _get(env, "NH3N_mgL", "acute"),
            "do_floor_mgL": _get(env, "DO_mgL", "floor"),
            "do_target_pct_sat": _get(env, "DO_mgL", "target_pct_sat"),
            "tan_alert_mgL": _get(env, "TAN_mgL", "alert"),
            "tan_critical_mgL": _get(env, "TAN_mgL", "critical"),
            "no2_alert_mgL": _get(env, "NO2N_mgL", "alert"),
            "co2_alert_mgL": _get(env, "CO2_mgL", "alert"),
            "alkalinity_floor_mgL": _get(env, "alkalinity_mgL_CaCO3", "floor"),
            "biofilter_media_options": ctx.species_registry.list_media(),
            "disease_references": [
                {"disease": d.disease, "woah_notifiable": d.woah_notifiable,
                 "predisposing": list(d.predisposing_conditions)}
                for d in DISEASE_REGISTRY
            ],
        }

        # Attempt live web gap-fill only if enabled & an adapter is present.
        live_used = False
        if (ctx.settings.features.enable_web_search and ctx.llm_adapter is not None
                and hasattr(ctx.llm_adapter, "web_search")):
            try:
                extra = ctx.llm_adapter.web_search(
                    f"{ctx.species_registry.common_name(species)} {stage} water quality envelope aquaculture")
                if extra:
                    bundle["web_supplement"] = extra
                    live_used = True
            except Exception as exc:
                ctx.state.limitations.append(f"Web evidence unavailable: {exc}")
                ctx.state.degradation_level = max(ctx.state.degradation_level, 1)

        ctx.state.evidence_bundle = bundle
        evidence = [
            EvidenceItem(
                claim=(f"Envelope for {ctx.species_registry.common_name(species)} "
                       f"({stage}) loaded from cached species registry (Tier 1-3)."),
                sources=["config/species_envelopes.json", "FAO/DFO/SRAC/Freshwater Institute"],
                tier="3"),
            EvidenceItem(
                claim=f"NH3-N chronic threshold = {bundle['nh3_chronic_mgL']} mg/L "
                      f"(cold-water species; acute {bundle['nh3_acute_mgL']} mg/L).",
                sources=["Emerson et al. 1975 (10.1139/f75-274)", "FAO species factsheet"],
                tier="2"),
            EvidenceItem(
                claim=f"{len(DISEASE_REGISTRY)} disease early-warning rules loaded "
                      f"(WOAH Aquatic Animal Health Code).",
                sources=["WOAH Aquatic Animal Health Code"], tier="1"),
        ]
        if not live_used:
            self._degrade(ctx, "Live web sources not used; relying on cached envelopes.", level=1)
        return self._ok_result(
            {"evidence_bundle": bundle}, evidence=evidence,
            duration_ms=(time.perf_counter() - t0) * 1000)


def _get(env: Dict[str, Any], param: str, key: str) -> Any:
    return env.get(param, {}).get(key)
