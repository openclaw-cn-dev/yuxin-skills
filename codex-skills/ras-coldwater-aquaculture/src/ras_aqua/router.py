"""Chain-of-thought router for the ras_aqua engine.

Inspects the user request + available inputs, classifies intent, confirms the
canonical 6-step skill plan (or a reduced plan for degraded/troubleshoot
flows), and enforces the context-token budget before each skill runs. The
router is deterministic by default; an LLM adapter can override intent
classification when available, with a deterministic fallback.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .context import TokenBudget, count_tokens


@dataclass
class RoutingDecision:
    intent: str
    plan: List[str]              # ordered skill names to execute
    language: str
    needs_clarification: bool = False
    notes: List[str] = field(default_factory=list)
    estimated_tokens: int = 0


class ChainOfThoughtRouter:
    """Deterministic CoT router with optional LLM-assisted intent classification."""

    DEFAULT_PLAN = [
        "gather_requirements",
        "evidence_collector",
        "water_quality_analysis",
        "biofilter_disease",
        "knowledge_updater",
        "ras_advisor",
    ]

    def __init__(self, settings, prompt_builder=None, llm_adapter=None) -> None:
        self.settings = settings
        self.prompt_builder = prompt_builder
        self.llm_adapter = llm_adapter

    def route(self, user_message: str, pre_parsed: Optional[Dict[str, Any]] = None,
              attached_log: Optional[str] = None) -> RoutingDecision:
        msg = user_message or ""
        # 1. Language detection (pre-flight).
        language = self._detect_language(msg, pre_parsed)

        # 2. Intent classification (deterministic, with optional LLM assist).
        intent = self._classify_intent(msg, pre_parsed)

        # 3. Plan selection.
        plan = list(self.DEFAULT_PLAN)
        notes: List[str] = []

        if intent == "troubleshoot_excursion":
            notes.append("Troubleshoot flow: evidence + analysis prioritized; knowledge gap-fill enabled.")
        elif intent == "biofilter_sizing":
            notes.append("Biofilter sizing flow: derated capacity estimate is the primary output.")
        elif intent == "general_advice":
            notes.append("General advice flow: full 6-step analysis with lighter synthesis.")

        # 4. Needs clarification? (No structured payload and no JSON in message)
        needs_clar = pre_parsed is None and not self._looks_like_json(msg)
        if needs_clar:
            notes.append("No structured payload detected; gather_requirements will emit clarifying questions.")

        # 5. Token estimate.
        est = count_tokens(msg) + (count_tokens(attached_log) if attached_log else 0)
        if pre_parsed:
            import json
            est += count_tokens(json.dumps(pre_parsed, default=str))

        return RoutingDecision(
            intent=intent, plan=plan, language=language,
            needs_clarification=needs_clar, notes=notes, estimated_tokens=est,
        )

    # ----- helpers -----
    def _detect_language(self, msg: str, pre_parsed: Optional[Dict[str, Any]]) -> str:
        if pre_parsed and pre_parsed.get("language") in ("en", "vi"):
            return pre_parsed["language"]
        vi_chars = set("?????????????????????")
        if any(ch.lower() in vi_chars for ch in msg):
            return "vi"
        return self.settings.default_language

    def _classify_intent(self, msg: str, pre_parsed: Optional[Dict[str, Any]]) -> str:
        if pre_parsed and pre_parsed.get("target_objective"):
            return pre_parsed["target_objective"]
        low = msg.lower()
        if any(k in low for k in ("troubleshoot", "excursion", "spike", "emergency", "crash")):
            return "troubleshoot_excursion"
        if any(k in low for k in ("size", "sizing", "design", "new system", "capacity")):
            return "biofilter_sizing"
        if any(k in low for k in ("health", "disease", "sick", "mortalit")):
            return "health_assessment"
        if any(k in low for k in ("design check", "verify", "validate config")):
            return "design_check"
        return "general_advice"

    @staticmethod
    def _looks_like_json(msg: str) -> bool:
        s = msg.strip()
        return s.startswith("{") and s.endswith("}")
