"""Skill 3 ? compute the water-quality scorecard.

Deterministically computes un-ionized ammonia (Emerson 1975), DO % saturation
(Benson-Krause/APHA), nitrification status from the TAN/NO2/NO3 pattern,
alkalinity demand, CO2 status, and per-parameter deviations against the
species envelope. Every formula and unit is stated explicitly in the output to
satisfy gates G2 and G3.
"""
from __future__ import annotations

import time
from typing import Any, List, Optional

from ..chemistry import (
    ammonia_pka, unionized_ammonia_mgL, do_saturation_freshwater,
    do_percent_saturation, alkalinity_demand_for_tan,
    severity_for_value, severity_in_range,
)
from ..schemas import (
    WaterQualityScorecard, Deviation, Severity, EvidenceItem,
)
from ..species import SpeciesRegistry
from .base import Skill, SkillContext


class WaterQualityAnalysisSkill(Skill):
    name = "water_quality_analysis"
    step = 3
    description = ("Compute derived water-quality metrics and quantify deviations "
                   "from the species envelope (NH3, DO % sat, nitrification, "
                   "alkalinity, CO2).")
    depends_on = ["evidence_collector"]
    prompt_template = "water_quality_analysis"
    input_schema = "assets/schemas/requirements.schema.json"
    output_schema = "assets/schemas/water_quality_scorecard.schema.json"
    tags = ["analysis", "chemistry"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        req = ctx.state.requirements
        env = ctx.state.envelope
        if req is None or env is None:
            return self._degraded_result(
                {"scorecard": None},
                limitations=["Requirements or envelope missing."], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        wq = req.wq
        reg = ctx.species_registry
        flags: List[str] = []
        deviations: List[Deviation] = []

        # --- Temperature ---
        T = wq.T_C
        t_opt = reg.optimal_range(env, "T_C")
        t_safe = reg.safe_range(env, "T_C")
        t_lethal = reg.threshold(env, "T_C", "lethal_above")
        sev_T = severity_in_range(T, t_opt, t_safe)
        if t_lethal and T >= t_lethal:
            sev_T = Severity.CRITICAL
        deviations.append(Deviation("T", T, self._fmt_range(t_opt, t_safe, t_lethal), sev_T))

        # --- pH ---
        ph_status = "ok"
        if wq.pH is not None:
            ph_opt = reg.optimal_range(env, "pH")
            ph_safe = reg.safe_range(env, "pH")
            sev_pH = severity_in_range(wq.pH, ph_opt, ph_safe)
            deviations.append(Deviation("pH", wq.pH, self._fmt_range(ph_opt, ph_safe), sev_pH))
        else:
            flags.append("pH missing; NH3 cannot be computed (gate G2 unmet).")

        # --- Un-ionized ammonia (Emerson 1975) ---
        nh3_mgL: Optional[float] = None
        nh3_f: Optional[float] = None
        nh3_status = "unknown"
        nh3_chronic = reg.threshold(env, "NH3N_mgL", "chronic")
        nh3_acute = reg.threshold(env, "NH3N_mgL", "acute")
        if wq.pH is not None and wq.TAN_mgL is not None:
            nh3_mgL, nh3_f = unionized_ammonia_mgL(wq.TAN_mgL, T, wq.pH)
            pKa = ammonia_pka(T)
            if nh3_acute and nh3_mgL >= nh3_acute:
                nh3_status = "toxic"
            elif nh3_chronic and nh3_mgL >= nh3_chronic:
                nh3_status = "elevated"
            else:
                nh3_status = "safe"
            sev_TAN = severity_for_value(nh3_mgL, nh3_chronic, nh3_acute)
            deviations.append(Deviation(
                "NH3-N", round(nh3_mgL, 6),
                f"chronic {nh3_chronic} / acute {nh3_acute} mg/L NH3-N "
                f"(Emerson 1975; pKa={round(pKa,3)} at {T}C, f={round(nh3_f,5)})",
                sev_TAN))
        else:
            flags.append("TAN or pH missing; NH3 not computed.")

        # --- DO saturation (Benson-Krause/APHA) ---
        do_sat_pct: Optional[float] = None
        do_status = "unknown"
        do_floor = reg.threshold(env, "DO_mgL", "floor")
        do_target_pct = reg.threshold(env, "DO_mgL", "target_pct_sat")
        if wq.DO_mgL is not None:
            do_sat_pct = do_percent_saturation(wq.DO_mgL, T, wq.salinity_ppt or 0.0)
            do_sat_mgL = do_saturation_freshwater(T, wq.salinity_ppt or 0.0)
            if do_floor and wq.DO_mgL <= do_floor * 0.7:
                do_status = "critical"
            elif do_floor and wq.DO_mgL <= do_floor:
                do_status = "low"
            elif do_target_pct and do_sat_pct < do_target_pct:
                do_status = "low"
            else:
                do_status = "adequate"
            sev_DO = Severity.CRITICAL if do_status == "critical" else (
                Severity.ALERT if do_status == "low" else Severity.OK)
            deviations.append(Deviation(
                "DO", wq.DO_mgL,
                f"floor {do_floor} mg/L; sat {round(do_sat_mgL,2)} mg/L @ {T}C "
                f"(sal {wq.salinity_ppt or 0}ppt) -> {round(do_sat_pct,1)}% sat",
                sev_DO))
        else:
            flags.append("DO missing; % saturation cannot be reported (gate G3 unmet).")

        # --- Nitrification status (TAN/NO2/NO3 pattern) ---
        nit_status = self._nitrification_status(wq)
        if nit_status in ("failing", "stressed"):
            flags.append(f"Nitrification status: {nit_status}.")

        # --- Alkalinity ---
        alk_status = "unknown"
        alk_demand: Optional[float] = None
        alk_floor = reg.threshold(env, "alkalinity_mgL_CaCO3", "floor")
        exchange = (req.ras_config.makeup_pct or 0) / 100.0 / 30.0 if req.ras_config.makeup_pct else 0.0
        if wq.TAN_mgL is not None:
            alk_demand = alkalinity_demand_for_tan(wq.TAN_mgL, exchange)
        if wq.alkalinity_mgL is not None:
            if alk_floor and wq.alkalinity_mgL < alk_floor:
                alk_status = "deficient"
            elif alk_demand is not None and wq.alkalinity_mgL < alk_demand:
                alk_status = "deficient"
            else:
                alk_status = "sufficient"
            sev_alk = Severity.ALERT if alk_status == "deficient" else Severity.OK
            deviations.append(Deviation(
                "Alkalinity", wq.alkalinity_mgL,
                f"floor {alk_floor} mg/L CaCO3; nitrification demand "
                f"{round(alk_demand,2) if alk_demand is not None else 'n/a'} mg/L/d",
                sev_alk))
        else:
            flags.append("Alkalinity missing; demand reported but buffer status unknown.")

        # --- CO2 ---
        co2_status = "unknown"
        co2_alert = reg.threshold(env, "CO2_mgL", "alert")
        co2_crit = reg.threshold(env, "CO2_mgL", "critical")
        if wq.CO2_mgL is not None:
            if co2_crit and wq.CO2_mgL >= co2_crit:
                co2_status = "critical"
            elif co2_alert and wq.CO2_mgL >= co2_alert:
                co2_status = "elevated"
            else:
                co2_status = "ok"
            sev_CO2 = severity_for_value(wq.CO2_mgL, co2_alert, co2_crit)
            deviations.append(Deviation("CO2", wq.CO2_mgL,
                                        f"alert {co2_alert} / critical {co2_crit} mg/L",
                                        sev_CO2))
        else:
            flags.append("CO2 missing; accumulation status unknown.")

        # --- NO2 / NO3 deviations ---
        no2_alert = reg.threshold(env, "NO2N_mgL", "alert")
        no2_crit = reg.threshold(env, "NO2N_mgL", "critical")
        if wq.NO2_mgL is not None:
            sev = severity_for_value(wq.NO2_mgL, no2_alert, no2_crit)
            deviations.append(Deviation("NO2-N", wq.NO2_mgL,
                                        f"alert {no2_alert} / critical {no2_crit} mg/L", sev))
        no3_alert = reg.threshold(env, "NO3N_mgL", "alert")
        no3_crit = reg.threshold(env, "NO3N_mgL", "critical")
        if wq.NO3_mgL is not None:
            sev = severity_for_value(wq.NO3_mgL, no3_alert, no3_crit)
            deviations.append(Deviation("NO3-N", wq.NO3_mgL,
                                        f"alert {no3_alert} / critical {no3_crit} mg/L", sev))

        scorecard = WaterQualityScorecard(
            nh3_mgL=round(nh3_mgL, 6) if nh3_mgL is not None else None,
            nh3_fraction=round(nh3_f, 6) if nh3_f is not None else None,
            nh3_status=nh3_status,
            do_sat_pct=round(do_sat_pct, 1) if do_sat_pct is not None else None,
            do_status=do_status,
            nitrification_status=nit_status,
            alkalinity_status=alk_status,
            alkalinity_demand_mgL_CaCO3_per_day=(round(alk_demand, 2)
                                                  if alk_demand is not None else None),
            co2_status=co2_status,
            deviations=deviations,
            trend=None,
            data_quality_flags=flags,
        )
        ctx.state.scorecard = scorecard
        # Populate condition tags for the disease matcher.
        from ..diseases import conditions_from_scorecard
        ctx.state.conditions = conditions_from_scorecard(scorecard, req.ras_config)
        # Add crowding condition if biomass density is high.
        if req.biomass_kg and req.ras_config.tank_volume_m3 and req.ras_config.tank_volume_m3 > 0:
            density = req.biomass_kg / req.ras_config.tank_volume_m3
            if density > 60:
                ctx.state.conditions.append("crowding")

        evidence = [
            EvidenceItem(claim=(f"NH3-N = {nh3_mgL} mg/L via Emerson (1975) "
                                f"(TAN={wq.TAN_mgL}, T={T}, pH={wq.pH})."),
                         sources=["Emerson et al. 1975 (10.1139/f75-274)"], tier="2"),
            EvidenceItem(claim=(f"DO {wq.DO_mgL} mg/L = {do_sat_pct}% sat @ {T}C "
                                f"(Benson-Krause/APHA)."),
                         sources=["Benson & Krause 1984 (10.4319/lo.1984.29.3.0620)",
                                  "APHA Standard Methods (2017)"], tier="2"),
        ]
        if flags:
            self._degrade(ctx, "Some readings missing; affected metrics flagged.", level=1)
        return self._ok_result(
            {"scorecard": scorecard.to_dict()}, evidence=evidence,
            duration_ms=(time.perf_counter() - t0) * 1000)

    # ----- helpers -----
    @staticmethod
    def _nitrification_status(wq) -> str:
        tan, no2, no3 = wq.TAN_mgL, wq.NO2_mgL, wq.NO3_mgL
        if tan is None:
            return "unknown"
        if no2 is not None and no2 > 0.5 and (no3 is None or no3 < 5):
            return "new"  # NOB lag
        if tan > 1.0 and no2 is not None and no2 > 0.3:
            return "failing"
        if tan > 0.5 and no2 is not None and no2 > 0.1:
            return "stressed"
        if tan < 0.5 and (no3 is None or no3 >= 5):
            return "mature"
        return "mature"

    @staticmethod
    def _fmt_range(opt, safe, lethal=None) -> str:
        parts = []
        if opt:
            parts.append(f"optimal {opt[0]}-{opt[1]}")
        if safe:
            parts.append(f"safe {safe[0]}-{safe[1]}")
        if lethal:
            parts.append(f"lethal >{lethal}")
        return "; ".join(parts) + " C" if parts else "n/a"
