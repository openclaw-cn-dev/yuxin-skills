"""Skill 6 — RAS advisor: synthesize the final risk-disclosed verdict.

Deterministically derives the verdict category from the scorecard + biofilter
risk, assembles the ordered water-treatment procedure, builds best/base/worst
scenarios for borderline cases, deduplicates early-warning alerts, and
assembles the evidence chain from upstream evidence items. An LLM adapter, when
available, is used only to polish the disclosure prose; the structured verdict
is always produced from the deterministic computation so the engine degrades
gracefully without an LLM.
"""
from __future__ import annotations

import time
from typing import Any, List, Optional

from ..schemas import (
    Verdict, VerdictCategory, TreatmentStep, EvidenceItem, Severity,
)
from .base import Skill, SkillContext


class RasAdvisorSkill(Skill):
    name = "ras_advisor"
    step = 6
    description = ("Synthesize all prior analysis into a risk-disclosed verdict: "
                   "system status, early-warning alerts, water-treatment procedure, "
                   "and full evidence chain.")
    depends_on = ["knowledge_updater"]
    prompt_template = "ras_advisor"
    input_schema = "assets/schemas/biofilter_risk.schema.json"
    output_schema = "assets/schemas/verdict.schema.json"
    tags = ["synthesis"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        req = ctx.state.requirements
        sc = ctx.state.scorecard
        br = ctx.state.biofilter_risk
        if req is None or sc is None or br is None:
            return self._degraded_result(
                {"verdict": None},
                limitations=["Upstream analysis missing; cannot synthesize."], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        category = self._verdict_category(sc, br, req.target_objective)
        alerts = self._alerts(sc, br)
        procedure = self._procedure(br)
        scenarios = self._scenarios(sc, br, category)
        key_risks = self._key_risks(sc, br)
        remediation = self._remediation(br)
        evidence_chain = self._evidence_chain(ctx)
        disclosure = self._disclosure(ctx, category)

        verdict = Verdict(
            verdict=category,
            disclosure=disclosure,
            early_warning_alerts=alerts,
            water_treatment_procedure=procedure,
            key_risks=key_risks,
            evidence_chain=evidence_chain,
            remediation=remediation,
            scenarios=scenarios,
            degradation_level=ctx.state.degradation_level,
        )
        ctx.state.verdict = verdict
        return self._ok_result(
            {"verdict": verdict.to_dict()},
            evidence=evidence_chain, duration_ms=(time.perf_counter() - t0) * 1000)

    # ----- verdict logic -----
    @staticmethod
    def _verdict_category(sc, br, objective=None) -> VerdictCategory:
        # Critical if any toxicity, critical DO/CO2, failing nitrification, or overloaded biofilter.
        if (sc.nh3_status == "toxic" or sc.do_status == "critical"
                or sc.co2_status == "critical"
                or sc.nitrification_status == "failing"
                or br.biofilter_capacity_status == "overloaded"
                or any(w.severity == Severity.CRITICAL for w in br.disease_early_warning)):
            return VerdictCategory.CRITICAL
        # Inconclusive when an assessment dimension essential to the objective is
        # unknown and no critical signal forces action:
        #  - sizing/design objectives cannot conclude without biofilter config; or
        #  - all three core dimensions (NH3, DO, biofilter) are unknown.
        obj_val = objective.value if objective is not None else None
        if ((obj_val in ("biofilter_sizing", "design_check")
             and br.biofilter_capacity_status == "unknown")
                or (sc.nh3_status == "unknown" and sc.do_status == "unknown"
                    and br.biofilter_capacity_status == "unknown")):
            return VerdictCategory.INCONCLUSIVE
        # Adjust required if any alert/elevated/marginal.
        if (sc.nh3_status == "elevated" or sc.do_status == "low"
                or sc.co2_status == "elevated" or sc.alkalinity_status == "deficient"
                or sc.nitrification_status in ("stressed", "new")
                or br.biofilter_capacity_status == "marginal"
                or any(w.severity in (Severity.ALERT, Severity.WATCH)
                       for w in br.disease_early_warning)):
            return VerdictCategory.ADJUST
        return VerdictCategory.OPTIMAL

    @staticmethod
    def _alerts(sc, br) -> List[str]:
        alerts: List[str] = []
        if sc.nh3_status == "toxic":
            alerts.append(f"CRITICAL: NH3-N {sc.nh3_mgL} mg/L above acute threshold (toxic).")
        elif sc.nh3_status == "elevated":
            alerts.append(f"ALERT: NH3-N {sc.nh3_mgL} mg/L above chronic threshold.")
        if sc.do_status == "critical":
            alerts.append("CRITICAL: DO below critical floor.")
        elif sc.do_status == "low":
            alerts.append(f"ALERT: DO {sc.do_sat_pct}% sat below target.")
        if sc.co2_status == "critical":
            alerts.append("CRITICAL: CO2 above critical threshold.")
        elif sc.co2_status == "elevated":
            alerts.append("ALERT: CO2 elevated.")
        if sc.nitrification_status == "failing":
            alerts.append("CRITICAL: Nitrification failing (NO2 spike + TAN rising).")
        elif sc.nitrification_status == "stressed":
            alerts.append("ALERT: Nitrification stressed.")
        if br.biofilter_capacity_status == "overloaded":
            alerts.append(f"CRITICAL: Biofilter overloaded (ratio {br.loading_ratio}).")
        elif br.biofilter_capacity_status == "marginal":
            alerts.append("ALERT: Biofilter marginal headroom.")
        for w in br.disease_early_warning:
            tag = "WOAH-notifiable" if w.woah_notifiable else "non-notifiable"
            alerts.append(f"{w.severity.value.upper()}: {w.disease} ({tag}) - {w.signal}")
        seen = set()
        uniq = []
        for a in alerts:
            if a not in seen:
                seen.add(a)
                uniq.append(a)
        return uniq

    @staticmethod
    def _procedure(br) -> List[TreatmentStep]:
        steps: List[TreatmentStep] = []
        for i, t in enumerate(br.recommended_treatments, start=1):
            steps.append(TreatmentStep(
                step=i, action=t.action, magnitude=t.magnitude,
                safety_limit=("Ozone: off-gas destruction + ORP control; "
                              "chemicals: dose per manufacturer; verify fish safety."
                              if t.category in ("chemical", "physical") else "")))
        return steps

    @staticmethod
    def _scenarios(sc, br, category) -> dict:
        if category == VerdictCategory.OPTIMAL:
            return {"best": "Maintained within envelope; continue monitoring.",
                    "base": "Stable operation; routine checks.",
                    "worst": "A feed spike + 5C rise could push NH3 to chronic threshold."}
        if category == VerdictCategory.INCONCLUSIVE:
            return {"best": "Pending fresh readings; likely manageable.",
                    "base": "Cannot project without key readings.",
                    "worst": "Undetected excursion may already be harming fish."}
        return {
            "best": "Immediate corrective actions restore envelope within 24-48h.",
            "base": "Stabilize with corrective actions; recheck in 6-12h.",
            "worst": "Without intervention: ammonia/DO excursion escalates to mortality event.",
        }

    @staticmethod
    def _key_risks(sc, br) -> List[str]:
        risks: List[str] = []
        if sc.nh3_status in ("elevated", "toxic"):
            risks.append("Ammonia toxicity: gill damage, mortality at acute levels.")
        if sc.do_status in ("low", "critical"):
            risks.append("Hypoxia: reduced growth, stress-mediated disease susceptibility.")
        if sc.co2_status in ("elevated", "critical"):
            risks.append("CO2 narcosis + blood acidosis; reduces DO tolerance.")
        if sc.nitrification_status in ("failing", "stressed"):
            risks.append("Biofilter collapse: rapid TAN/NO2 accumulation.")
        if br.biofilter_capacity_status in ("overloaded", "marginal"):
            risks.append("Biofilter undersized for feed load (cold-derated).")
        for w in br.disease_early_warning:
            if w.severity in (Severity.CRITICAL, Severity.ALERT):
                risks.append(f"Disease risk: {w.disease}.")
        if not risks:
            risks.append("No acute risks identified; maintain routine monitoring.")
        return risks

    @staticmethod
    def _remediation(br) -> List[str]:
        remed = []
        for t in br.recommended_treatments:
            remed.append(t.action)
        remed.extend(br.advanced_biofiltration_options)
        return remed

    @staticmethod
    def _evidence_chain(ctx) -> List[EvidenceItem]:
        chain: List[EvidenceItem] = []
        chain.extend(ctx.state.knowledge_citations)
        sc = ctx.state.scorecard
        if sc and sc.nh3_mgL is not None:
            chain.append(EvidenceItem(
                claim=f"NH3-N {sc.nh3_mgL} mg/L computed via Emerson (1975).",
                sources=["10.1139/f75-274"], tier="2"))
        if sc and sc.do_sat_pct is not None:
            chain.append(EvidenceItem(
                claim=f"DO {sc.do_sat_pct}% sat via Benson-Krause/APHA.",
                sources=["10.4319/lo.1984.29.3.0620", "APHA Standard Methods (2017)"], tier="2"))
        br = ctx.state.biofilter_risk
        if br and br.nitrification_penalty_pct is not None:
            chain.append(EvidenceItem(
                claim=f"Cold-temperature nitrification penalty {br.nitrification_penalty_pct}%.",
                sources=["10.1016/S0044-8486(02)00051-8"], tier="2"))
        if br and br.disease_early_warning:
            chain.append(EvidenceItem(
                claim=f"{len(br.disease_early_warning)} disease early-warning signal(s).",
                sources=["WOAH Aquatic Animal Health Code"], tier="1"))
        seen = set()
        uniq = []
        for e in chain:
            if e.claim not in seen:
                seen.add(e.claim)
                uniq.append(e)
        return uniq

    def _disclosure(self, ctx, category) -> str:
        lang = ctx.state.requirements.language
        level = ctx.state.degradation_level
        if lang == "vi":
            base = ("CANH BAO / GIOI HAN: Phan tich dua tren du lieu hien co. "
                    "Day la huong dan van hanh, khong phai chan doan thu y thuy san. "
                    "Xac nhan benh can kham thu y thuy san. ")
        else:
            base = ("DISCLOSURE/LIMITATIONS: This analysis is operational guidance, not a "
                    "veterinary diagnosis. Disease signals require aquatic-vet confirmation. "
                    "Chemical/ozone interventions carry fish-safety limits (off-gas + ORP control). ")
        if level >= 1:
            base += (f"Generated at degradation level {level} (some sources/inputs "
                     "substituted or missing; flagged inline). ")
        base += f"Verdict category: {category.value}."
        return base
