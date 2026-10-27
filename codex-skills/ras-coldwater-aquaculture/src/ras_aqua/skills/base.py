"""Base skill class and shared skill execution context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..schemas import (
    Requirements, WaterQualityScorecard, BiofilterRisk, Verdict,
    EvidenceItem, SkillResult, Status,
)


@dataclass
class SkillState:
    """Mutable shared state passed through the skill pipeline."""
    requirements: Optional[Requirements] = None
    envelope: Optional[Dict[str, Any]] = None
    evidence_bundle: Optional[Dict[str, Any]] = None
    scorecard: Optional[WaterQualityScorecard] = None
    biofilter_risk: Optional[BiofilterRisk] = None
    knowledge_citations: List[EvidenceItem] = field(default_factory=list)
    verdict: Optional[Verdict] = None
    degradation_level: int = 0
    limitations: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    raw_user_message: str = ""


@dataclass
class SkillContext:
    """Everything a skill needs at execution time."""
    state: SkillState
    settings: Any
    species_registry: Any
    tool_registry: Any
    tool_context: Any
    prompt_builder: Any
    hooks: Any = None
    logger: Any = None
    llm_adapter: Any = None
    token_budget: Any = None
    # The raw user input for the gather step.
    user_message: str = ""
    attached_log: Optional[str] = None


class Skill:
    """Abstract skill. Subclasses implement ``run``."""

    name: str = "base"
    step: int = 0
    description: str = ""
    depends_on: List[str] = []
    prompt_template: str = ""
    input_schema: str = ""
    output_schema: str = ""
    tags: List[str] = []
    retryable: bool = True

    def run(self, ctx: SkillContext) -> SkillResult:
        raise NotImplementedError

    # ----- helpers -----
    def _degrade(self, ctx: SkillContext, message: str, level: int = 1) -> None:
        ctx.state.degradation_level = max(ctx.state.degradation_level, level)
        ctx.state.limitations.append(message)
        if ctx.hooks is not None:
            from ..hooks import HookEvent
            ctx.hooks.emit(HookEvent.ON_DEGRADATION, skill=self.name,
                           level=level, message=message)

    def _ok_result(self, data: Dict[str, Any], evidence: List[EvidenceItem] = None,
                   duration_ms: float = 0.0) -> SkillResult:
        return SkillResult(
            skill=self.name, status=Status.OK, data=data,
            evidence=evidence or [], degradation_level=0, duration_ms=duration_ms,
        )

    def _degraded_result(self, data: Dict[str, Any], limitations: List[str],
                         level: int, evidence: List[EvidenceItem] = None,
                         duration_ms: float = 0.0) -> SkillResult:
        return SkillResult(
            skill=self.name, status=Status.DEGRADED, data=data,
            limitations=limitations, evidence=evidence or [],
            degradation_level=level, duration_ms=duration_ms,
        )
