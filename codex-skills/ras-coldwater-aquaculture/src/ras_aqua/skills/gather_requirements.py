"""Skill 1 ? gather & validate structured requirements from user input.

Accepts either an explicit structured ``requirements`` dict (preferred) or a
JSON-encoded user message. Validates the cold-water species via the
``SpeciesRegistry``, ensures the minimum reading set (T, DO, pH, TAN) is
present, and returns a typed ``Requirements`` object ? or, when critical fields
are missing, returns a degraded result with explicit clarifying questions
(never fabricates data).
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from ..errors import InputValidationError
from ..schemas import Requirements, Status, EvidenceItem
from .base import Skill, SkillContext


MIN_READINGS = ("T_C", "DO_mgL", "pH", "TAN_mgL")


class GatherRequirementsSkill(Skill):
    name = "gather_requirements"
    step = 1
    description = ("Clarify cold-water species, life stage, RAS config, water-quality "
                   "readings, biomass/feed, objective, and language.")
    depends_on: List[str] = []
    prompt_template = "gather_requirements"
    input_schema = "assets/schemas/requirements.schema.json"
    output_schema = "assets/schemas/requirements.schema.json"
    tags = ["intake"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        data = self._extract(ctx)
        if data is None:
            qs = self._clarifying_questions(ctx)
            ctx.state.limitations.append("Requirements incomplete; clarifying questions emitted.")
            ctx.state.degradation_level = max(ctx.state.degradation_level, 3)
            return self._degraded_result(
                {"clarifying_questions": qs, "requirements": None},
                limitations=["Requirements incomplete."], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        # Normalize & validate species.
        try:
            species = ctx.species_registry.normalize_species(data.get("species", ""))
        except InputValidationError as exc:
            ctx.state.limitations.append(str(exc))
            ctx.state.degradation_level = max(ctx.state.degradation_level, 3)
            return self._degraded_result(
                {"requirements": None, "error": str(exc)},
                limitations=[str(exc)], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        data["species"] = species
        data["species_common_name"] = ctx.species_registry.common_name(species)

        # Resolve life stage (default if missing/unknown).
        try:
            lookup = ctx.species_registry.resolve_envelope(species, data.get("life_stage"))
        except InputValidationError:
            lookup = ctx.species_registry.resolve_envelope(species, None)
            data["life_stage"] = lookup.life_stage
            ctx.state.limitations.append(
                f"life_stage not provided; defaulted to '{lookup.life_stage}'.")
            ctx.state.degradation_level = max(ctx.state.degradation_level, 1)
        data["life_stage"] = lookup.life_stage

        # Validate minimum readings.
        wq = data.get("wq") or {}
        missing = [k for k in MIN_READINGS if wq.get(k) in (None, "")]
        if missing:
            qs = self._clarifying_questions(ctx, missing=missing)
            ctx.state.limitations.append(f"Missing minimum readings: {missing}")
            ctx.state.degradation_level = max(ctx.state.degradation_level, 3)
            return self._degraded_result(
                {"clarifying_questions": qs, "requirements": None},
                limitations=[f"Missing readings: {missing}"], level=3,
                duration_ms=(time.perf_counter() - t0) * 1000)

        # Build typed Requirements.
        req = Requirements.from_dict(data)
        ctx.state.requirements = req
        ctx.state.envelope = lookup.envelope
        ctx.state.raw_user_message = ctx.user_message

        evidence = [EvidenceItem(
            claim=f"Species classified as cold-water: {lookup.common_name} ({lookup.life_stage}).",
            sources=[lookup.common_name], tier="3")]
        return self._ok_result(
            {"requirements": req.to_dict()},
            evidence=evidence, duration_ms=(time.perf_counter() - t0) * 1000)

    # ----- helpers -----
    def _extract(self, ctx: SkillContext) -> Optional[Dict[str, Any]]:
        # Prefer an explicit structured payload attached to the context.
        pre = getattr(ctx, "pre_parsed_requirements", None)
        if isinstance(pre, dict):
            return pre
        msg = (ctx.user_message or "").strip()
        if not msg:
            return None
        # Try JSON first.
        if msg.startswith("{"):
            try:
                return json.loads(msg)
            except json.JSONDecodeError:
                pass
        # Attached log may contain a JSON snapshot.
        if ctx.attached_log:
            try:
                return json.loads(ctx.attached_log)
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    def _clarifying_questions(self, ctx: SkillContext,
                              missing: Optional[List[str]] = None) -> List[str]:
        qs = [
            "Which cold-water species? (rainbow_trout, atlantic_salmon, arctic_char, sturgeon)",
            "Which life stage? (fry, growout, parr, smolt ? depends on species)",
            "Provide water-quality readings: T (degC), DO (mg/L), pH, TAN (mg/L), "
            "and ideally NO2, NO3, alkalinity, CO2.",
            "RAS configuration: tank volume (m3), make-up water %, biofilter type "
            "(mbbr_kaldnes_k1/k3, fixed_film_trickling, fluidized_sand, rbc), "
            "media volume or surface area (m2), flow (lpm).",
            "Biomass (kg), feed (kg/day), feed protein %?",
            "Target objective? (health_assessment, design_check, troubleshoot_excursion, "
            "biofilter_sizing, general_advice)",
            "Output language? (en or vi)",
        ]
        if missing:
            qs.insert(0, f"Missing minimum readings required for analysis: {missing}.")
        return qs
