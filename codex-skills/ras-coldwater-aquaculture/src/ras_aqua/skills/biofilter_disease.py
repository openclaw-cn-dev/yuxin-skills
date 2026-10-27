"""Skill 4 ? biofilter & disease early-warning risk assessment.

Combines the water-quality scorecard, RAS config, biomass/feed, and disease
references to estimate derated biofilter capacity vs TAN load, quantify the
cold-temperature nitrification penalty, match disease early-warning signals,
and recommend treatments with magnitude + category + rationale (gate G4).
"""
from __future__ import annotations

import time
from typing import Any, List, Optional

from ..biofilter import (
    tan_production_from_feed, nitrification_derating_factor,
    nitrification_penalty_pct, biofilter_capacity_derated,
    biofilter_loading_ratio, biofilter_status_from_ratio,
)
from ..diseases import match_disease_signals
from ..schemas import (
    BiofilterRisk, DiseaseWarning, Treatment, Severity, EvidenceItem,
)
from .base import Skill, SkillContext


class BiofilterDiseaseSkill(Skill):
    name = "biofilter_disease"
    step = 4
    description = ("Assess biofilter loading/performance and disease early-warning "
                   "risk with cold-temperature derating and treatment recommendations.")
    depends_on = ["water_quality_analysis"]
    prompt_template = "biofilter_disease"
    input_schema = "assets/schemas/water_quality_scorecard.schema.json"
    output_schema = "assets/schemas/biofilter_risk.schema.json"
    tags = ["biofilter", "disease"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        req = ctx.state.requirements
        sc = ctx.state.scorecard
        if req is None or sc is None:
            return self._degraded_result(
                {"biofilter_risk": None},
                limitations=["Requirements or scorecard missing."], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        T = req.wq.T_C
        cfg = req.ras_config

        # --- TAN production ---
        tan_g_day: Optional[float] = None
        if req.feed_kg_day is not None:
            tan_g_day = tan_production_from_feed(req.feed_kg_day, req.feed_protein_pct)

        # --- Biofilter capacity (derated) ---
        capacity_g_day: Optional[float] = None
        penalty_pct: Optional[float] = None
        media_area: Optional[float] = cfg.biofilter_area_m2
        if cfg.biofilter_type and media_area is None and cfg.biofilter_media_volume_m3:
            # Derive surface area from media volume * specific surface area.
            try:
                media = ctx.species_registry.media(cfg.biofilter_type)
                media_area = cfg.biofilter_media_volume_m3 * media["specific_surface_area_m2_per_m3"]
            except Exception:
                media_area = None
        if cfg.biofilter_type and media_area is not None and media_area > 0:
            try:
                media = ctx.species_registry.media(cfg.biofilter_type)
            except Exception:
                media = {"ref_tan_capacity_g_per_m2_day": 1.0}
            capacity_g_day = biofilter_capacity_derated(
                media_area, media["ref_tan_capacity_g_per_m2_day"], T)
            penalty_pct = nitrification_penalty_pct(T)

        # --- Loading ratio & status ---
        ratio = biofilter_loading_ratio(tan_g_day, capacity_g_day) if tan_g_day else None
        bf_status = biofilter_status_from_ratio(ratio)

        # --- Disease early-warning ---
        warnings = match_disease_signals(ctx.state.conditions)
        # Always surface ammonia toxicity if NH3 elevated/toxic.
        if sc.nh3_status in ("elevated", "toxic") and not any(
                w.disease == "Ammonia toxicity" for w in warnings):
            warnings.insert(0, DiseaseWarning(
                disease="Ammonia toxicity",
                signal=f"NH3-N {sc.nh3_mgL} mg/L above species threshold.",
                matched_conditions=["high_NH3"],
                severity=Severity.CRITICAL if sc.nh3_status == "toxic" else Severity.ALERT,
                woah_notifiable=False))

        # --- Treatments (magnitude + category) ---
        treatments = self._build_treatments(ctx, sc, bf_status, ratio, penalty_pct)

        # --- Advanced options ---
        advanced = self._advanced_options(sc, bf_status, penalty_pct)

        risk = BiofilterRisk(
            biofilter_capacity_status=bf_status,
            disease_early_warning=warnings,
            recommended_treatments=treatments,
            tan_production_g_day=round(tan_g_day, 2) if tan_g_day is not None else None,
            biofilter_capacity_g_day=round(capacity_g_day, 2) if capacity_g_day is not None else None,
            loading_ratio=round(ratio, 3) if ratio is not None else None,
            nitrification_penalty_pct=penalty_pct,
            advanced_biofiltration_options=advanced,
        )
        ctx.state.biofilter_risk = risk

        evidence: List[EvidenceItem] = []
        if tan_g_day is not None:
            evidence.append(EvidenceItem(
                claim=f"TAN production ~{round(tan_g_day,1)} g/day from "
                      f"{req.feed_kg_day} kg feed/day at {req.feed_protein_pct or 40}% protein.",
                sources=["Timmons & Ebeling 2013 (ISBN 9780971264660)"], tier="2"))
        if penalty_pct is not None:
            evidence.append(EvidenceItem(
                claim=f"Cold-water nitrification penalty {penalty_pct}% at {T}C "
                      f"(derating factor {round(nitrification_derating_factor(T),3)}).",
                sources=["Zhu & Chen 2002 (10.1016/S0044-8486(02)00051-8)",
                         "Eding et al. 2006 (10.1016/j.aquaeng.2005.09.003)"], tier="2"))
        evidence.append(EvidenceItem(
            claim=f"{len(warnings)} disease early-warning signal(s) matched "
                  f"(WOAH Aquatic Animal Health Code).",
            sources=["WOAH Aquatic Animal Health Code"], tier="1"))

        if cfg.biofilter_type is None or media_area is None:
            self._degrade(ctx, "Biofilter config incomplete; capacity not estimated.", level=1)
        return self._ok_result(
            {"biofilter_risk": risk.to_dict()}, evidence=evidence,
            duration_ms=(time.perf_counter() - t0) * 1000)

    # ----- helpers -----
    def _build_treatments(self, ctx, sc, bf_status, ratio, penalty_pct) -> List[Treatment]:
        tx: List[Treatment] = []
        req = ctx.state.requirements
        # Ammonia emergency
        if sc.nh3_status == "toxic":
            tx.append(Treatment(
                action="Emergency ammonia control: stop feeding, lower pH toward species floor, "
                       "maximize aeration, 30-50% water exchange.",
                rationale="NH3-N above acute threshold; reduce TAN input and toxic fraction.",
                magnitude="Stop feeding 24-48h; pH toward 6.5-7.0; exchange 30-50% tank volume",
                category="operational"))
        elif sc.nh3_status == "elevated":
            tx.append(Treatment(
                action="Reduce feeding 50%, increase aeration, partial water exchange 20%.",
                rationale="NH3-N above chronic threshold; lower TAN load.",
                magnitude="Feed -50%; exchange 20% volume; recheck in 6h",
                category="operational"))
        # DO
        if sc.do_status == "critical":
            tx.append(Treatment(
                action="Increase oxygenation: raise DO to >species floor via pure O2 or "
                       "additional aeration; reduce feeding.",
                rationale="DO below critical floor; fish stress + biofilter DO collapse risk.",
                magnitude="DO to >6 mg/L; feed -50%",
                category="physical"))
        elif sc.do_status == "low":
            tx.append(Treatment(
                action="Increase aeration; verify DO sensor calibration.",
                rationale="DO below target saturation.",
                magnitude="Aeration +20%; calibrate probe",
                category="physical"))
        # Alkalinity
        if sc.alkalinity_status == "deficient":
            tx.append(Treatment(
                action="Add alkalinity: sodium bicarbonate (NaHCO3) to restore buffer.",
                rationale="Nitrification consumes ~7.14 mg CaCO3 per mg TAN; buffer depleted.",
                magnitude=f"NaHCO3 to raise alkalinity to "
                          f"{ctx.state.envelope.get('alkalinity_mgL_CaCO3',{}).get('target','100')} mg/L CaCO3",
                category="chemical"))
        # CO2
        if sc.co2_status in ("elevated", "critical"):
            tx.append(Treatment(
                action="Increase CO2 stripping: raise packed-column airflow / increase gas exchange.",
                rationale="CO2 accumulation depresses blood pH and stresses fish.",
                magnitude="Stripper airflow +50%; verify off-gas",
                category="physical"))
        # Biofilter overload
        if bf_status == "overloaded":
            tx.append(Treatment(
                action="Reduce feed load to <= derated biofilter capacity; consider supplemental "
                       "biofilter media or partial water exchange.",
                rationale=f"Loading ratio {round(ratio,2)} exceeds derated capacity "
                          f"(cold penalty {penalty_pct}%).",
                magnitude=f"Feed to load ratio <1.0 (currently {round(ratio,2)})",
                category="biofilter"))
        elif bf_status == "marginal":
            tx.append(Treatment(
                action="Monitor TAN/NO2 hourly; pre-stage supplemental media; avoid feed spikes.",
                rationale="Loading ratio near 1.0 with cold derating; limited headroom.",
                magnitude="Hourly TAN/NO2; feed steady-state",
                category="biofilter"))
        # Nitrification failure
        if sc.nitrification_status == "failing":
            tx.append(Treatment(
                action="Nitrification failure: reduce feeding 70%, partial exchange 30%, "
                       "add alkalinity, reseed biofilter from a healthy system.",
                rationale="NO2 spike + TAN rising indicates NOB collapse / cold shock.",
                magnitude="Feed -70%; exchange 30%; reseed biofilter",
                category="biofilter"))
        return tx

    def _advanced_options(self, sc, bf_status, penalty_pct) -> List[str]:
        opts: List[str] = []
        if penalty_pct and penalty_pct >= 40:
            opts.append("Oversize MBBR/fluidized-sand biofilter and pre-seed for low-T nitrification.")
        if sc.nh3_status in ("elevated", "toxic"):
            opts.append("Deploy denitrification reactor for NO3 control and reduce TAN load.")
        if sc.co2_status in ("elevated", "critical"):
            opts.append("Add/increase CO2 stripper (packed column, forced air).")
        if sc.do_status in ("low", "critical"):
            opts.append("Add ozone + UV treatment train (ozone requires off-gas destruction + ORP control).")
        opts.append("Consider UV disinfection for pathogen control (dose per WOAH guidance).")
        return opts
