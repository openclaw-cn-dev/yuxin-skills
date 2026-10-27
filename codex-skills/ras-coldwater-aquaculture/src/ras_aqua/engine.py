"""The ras_aqua engine ? orchestrates the full analysis pipeline.

``Engine.from_config()`` builds a fully-wired engine from validated settings:
skill registry, tool registry, species registry, hook bus, prompt builder,
context manager, and the chain-of-thought router. ``Engine.run`` executes the
routed skill plan in order with retry + quality-gate enforcement and returns an
``EngineReport``.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .errors import RasAquaError, SkillError, LLMUnavailable
from .schemas import EngineReport, SkillResult, Status, EvidenceItem
from .species import SpeciesRegistry
from .tools import ToolRegistry, ToolContext
from .hooks import HookBus, HookEvent
from .context import PromptBuilder, TokenBudget
from .router import ChainOfThoughtRouter
from .registry import SkillRegistry, SkillSpec
from .gates import evaluate_all, GateResult
from .logging_config import get_logger
from .skills import all_skills
from .skills.base import SkillContext, SkillState
from .llm_adapter import NoOpAdapter


class Engine:
    """Production-grade orchestrator for the ras-coldwater-aquaculture skill."""

    def __init__(self, settings, *, skill_registry: Optional[SkillRegistry] = None,
                 tool_registry: Optional[ToolRegistry] = None,
                 species_registry: Optional[SpeciesRegistry] = None,
                 hooks: Optional[HookBus] = None,
                 prompt_builder: Optional[PromptBuilder] = None,
                 router: Optional[ChainOfThoughtRouter] = None,
                 llm_adapter: Any = None,
                 logger: Any = None) -> None:
        self.settings = settings
        self.logger = logger or get_logger("ras_aqua", settings)
        self.skill_registry = skill_registry or SkillRegistry()
        self.tool_registry = tool_registry or ToolRegistry()
        self.species_registry = species_registry or SpeciesRegistry.from_settings(settings)
        self.hooks = hooks or HookBus(self.logger)
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm_adapter = llm_adapter or NoOpAdapter()
        self.router = router or ChainOfThoughtRouter(settings, self.prompt_builder, self.llm_adapter)
        self.token_budget = TokenBudget(
            max_context_tokens=settings.features.max_context_tokens,
            reserved_output_tokens=settings.features.reserved_output_tokens,
        )
        self._register_default_skills()

    # ----- construction -----
    @classmethod
    def from_config(cls, settings=None, **kwargs) -> "Engine":
        if settings is None:
            from config import load_settings
            settings = load_settings()
        return cls(settings, **kwargs)

    def _register_default_skills(self) -> None:
        for skill in all_skills():
            self.skill_registry.register(SkillSpec(
                name=skill.name, step=skill.step, description=skill.description,
                executor=skill.run, depends_on=list(skill.depends_on),
                input_schema=skill.input_schema, output_schema=skill.output_schema,
                prompt_template=skill.prompt_template, tags=list(skill.tags),
                retryable=skill.retryable,
            ))
        self.skill_registry.validate_dag()

    # ----- knowledge base -----
    def _load_knowledge_text(self) -> str:
        path = self.settings.knowledge_base_file
        if not path.is_file():
            self.logger.warning("knowledge_base.missing", path=str(path))
            return ""
        try:
            return path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            self.logger.warning("knowledge_base.read_failed", error=str(exc))
            return ""

    # ----- execution -----
    def run(self, user_message: str = "", *,
            requirements: Optional[Dict[str, Any]] = None,
            attached_log: Optional[str] = None,
            language: Optional[str] = None) -> EngineReport:
        t0 = time.perf_counter()
        if requirements and language:
            requirements = dict(requirements)
            requirements.setdefault("language", language)
        decision = self.router.route(user_message, requirements, attached_log)
        self.logger.info("engine.route", intent=decision.intent,
                         language=decision.language, plan=decision.plan,
                         est_tokens=decision.estimated_tokens)
        self.hooks.emit(HookEvent.PRE_ENGINE, intent=decision.intent,
                        language=decision.language, plan=decision.plan)

        state = SkillState()
        kb_text = self._load_knowledge_text()
        tool_ctx = ToolContext(
            settings=self.settings, species_registry=self.species_registry,
            knowledge_base_text=kb_text, logger=self.logger,
        )
        ctx = SkillContext(
            state=state, settings=self.settings,
            species_registry=self.species_registry,
            tool_registry=self.tool_registry, tool_context=tool_ctx,
            prompt_builder=self.prompt_builder, hooks=self.hooks,
            logger=self.logger, llm_adapter=self.llm_adapter,
            token_budget=self.token_budget,
            user_message=user_message, attached_log=attached_log,
        )
        ctx.pre_parsed_requirements = requirements  # type: ignore[attr-defined]

        results: List[SkillResult] = []
        for skill_name in decision.plan:
            if skill_name not in self.skill_registry.list():
                self.logger.warning("engine.skill_unknown", skill=skill_name)
                continue
            res = self._run_skill(skill_name, ctx)
            results.append(res)
            # If intake failed with clarification needed, stop the pipeline.
            if skill_name == "gather_requirements" and res.status != Status.OK:
                self.logger.info("engine.intake_incomplete",
                                 clarifying=bool(res.data.get("clarifying_questions")))
                break

        # Quality gates with auto-fix + retry.
        gate_results = self._enforce_gates(ctx, results)

        report = EngineReport(
            requirements=state.requirements,  # may be None if intake failed
            scorecard=state.scorecard,
            biofilter_risk=state.biofilter_risk,
            verdict=state.verdict,
            knowledge_citations=state.knowledge_citations,
            quality_gate_results={g.gate: ("pass" if g.passed else "fail") for g in gate_results},
            degradation_level=state.degradation_level,
            limitations=state.limitations,
            language=decision.language,
        )
        self.hooks.emit(HookEvent.POST_ENGINE, degradation=state.degradation_level,
                        verdict=state.verdict.verdict.value if state.verdict else None,
                        duration_ms=round((time.perf_counter() - t0) * 1000, 2))
        self.logger.info("engine.complete",
                         duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                         degradation=state.degradation_level,
                         gates=report.quality_gate_results)
        return report

    def _run_skill(self, name: str, ctx: SkillContext) -> SkillResult:
        spec = self.skill_registry.get(name)
        max_retries = self.settings.features.max_skill_retries if spec.retryable else 0
        last: Optional[SkillResult] = None
        for attempt in range(max_retries + 1):
            self.hooks.emit(HookEvent.PRE_SKILL, skill=name, attempt=attempt)
            t0 = time.perf_counter()
            try:
                result = spec.executor(ctx)
                if result.duration_ms == 0.0:
                    result.duration_ms = (time.perf_counter() - t0) * 1000
                self.hooks.emit(HookEvent.POST_SKILL, skill=name,
                                status=result.status.value,
                                degradation=result.degradation_level,
                                duration_ms=round(result.duration_ms, 2))
                self.logger.info("skill.complete", skill=name,
                                 status=result.status.value,
                                 degradation=result.degradation_level,
                                 attempt=attempt)
                return result
            except RasAquaError as exc:
                last = SkillResult(skill=name, status=Status.ERROR, data={},
                                   limitations=[str(exc)],
                                   evidence=[], degradation_level=exc.degradation_level,
                                   duration_ms=(time.perf_counter() - t0) * 1000)
                self.hooks.emit(HookEvent.ON_ERROR, skill=name, error=str(exc),
                                attempt=attempt, code=exc.code)
                self.logger.error("skill.error", skill=name, error=str(exc),
                                  attempt=attempt, code=exc.code)
                ctx.state.degradation_level = max(ctx.state.degradation_level,
                                                  exc.degradation_level)
                ctx.state.limitations.append(f"[{name}] {exc.message}")
            except Exception as exc:  # never let an unexpected error abort the pipeline
                last = SkillResult(skill=name, status=Status.ERROR, data={},
                                   limitations=[f"unexpected error: {exc}"],
                                   evidence=[], degradation_level=3,
                                   duration_ms=(time.perf_counter() - t0) * 1000)
                self.hooks.emit(HookEvent.ON_ERROR, skill=name, error=str(exc),
                                attempt=attempt, code="UNEXPECTED")
                self.logger.error("skill.unexpected_error", skill=name, error=str(exc),
                                  attempt=attempt)
                ctx.state.degradation_level = max(ctx.state.degradation_level, 3)
                ctx.state.limitations.append(f"[{name}] unexpected error: {exc}")
            if attempt < max_retries:
                time.sleep(min(2 ** attempt * 0.1, 1.0))
        return last or SkillResult(skill=name, status=Status.ERROR, data={},
                                   limitations=["skill produced no result"],
                                   degradation_level=3)

    def _enforce_gates(self, ctx: SkillContext,
                       results: List[SkillResult]) -> List[GateResult]:
        if ctx.state.verdict is None:
            # No verdict (e.g. intake incomplete); evaluate gates anyway for reporting.
            gates = evaluate_all(ctx.state)
            self.hooks.emit(HookEvent.PRE_GATE, count=len(gates))
            return gates
        max_retries = self.settings.features.max_skill_retries
        gates: List[GateResult] = []
        for _ in range(max_retries + 1):
            gates = evaluate_all(ctx.state)
            self.hooks.emit(HookEvent.PRE_GATE, count=len(gates))
            failed = [g for g in gates if not g.passed]
            if not failed:
                break
            if not self.settings.features.enable_quality_gate_autofix:
                break
            # Auto-fix: re-run the relevant synthesis skills once.
            self._autofix(failed, ctx)
        self.hooks.emit(HookEvent.POST_GATE,
                        passed=sum(1 for g in gates if g.passed),
                        failed=sum(1 for g in gates if not g.passed))
        return gates

    def _autofix(self, failed: List[GateResult], ctx: SkillContext) -> None:
        for g in failed:
            self.logger.info("gate.autofix", gate=g.gate, message=g.message)
            if g.gate in ("U2", "U5") and ctx.state.verdict:
                # Re-run advisor to regenerate disclosure/sections.
                self.skill_registry.get("ras_advisor").executor(ctx)
            elif g.gate in ("G2", "G3"):
                self.skill_registry.get("water_quality_analysis").executor(ctx)
            elif g.gate == "G4":
                self.skill_registry.get("biofilter_disease").executor(ctx)
            elif g.gate == "G1":
                self.skill_registry.get("evidence_collector").executor(ctx)
            ctx.state.degradation_level = max(ctx.state.degradation_level, 1)

    # ----- introspection -----
    def describe(self) -> Dict[str, Any]:
        return {
            "skill_name": self.settings.skill_name,
            "version": self.settings.version,
            "skills": self.skill_registry.specs(),
            "tools": self.tool_registry.schemas(),
            "species": self.species_registry.list_species(),
            "biofilter_media": self.species_registry.list_media(),
            "features": {
                "enable_chain_of_thought_routing": self.settings.features.enable_chain_of_thought_routing,
                "max_context_tokens": self.settings.features.max_context_tokens,
                "max_skill_retries": self.settings.features.max_skill_retries,
            },
        }
