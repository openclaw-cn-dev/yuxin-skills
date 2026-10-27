"""ras_aqua ? production-grade skill engine for ras-coldwater-aquaculture.

A modular, registry-based agent engine that turns a cold-water RAS facility
snapshot into an evidence-backed, risk-disclosed operational verdict. The
engine is pure-Python (stdlib only for the core) and computes the real
domain chemistry (Emerson NH3 equilibrium, Benson-Krause DO saturation,
cold-water nitrification derating) deterministically; LLM calls are isolated
behind a thin, fallback-protected adapter so the engine degrades gracefully
when a model is unavailable.

Public API::

    from ras_aqua import Engine
    engine = Engine.from_config()
    report = engine.run(user_message="...", attached_log=None)
"""
from __future__ import annotations

from .errors import (
    RasAquaError, ConfigError, SkillError, SkillNotFoundError,
    QualityGateError, ToolError, ContextBudgetError, LLMUnavailable,
    InputValidationError,
)
from .schemas import (
    Requirements, WaterQualityReading, RasConfig, WaterQualityScorecard,
    Deviation, BiofilterRisk, DiseaseWarning, Treatment, Verdict,
    EvidenceItem, SkillResult, EngineReport, Severity, VerdictCategory, Status,
)
from .chemistry import (
    ammonia_pka, unionized_ammonia_fraction, unionized_ammonia_mgL,
    do_saturation_freshwater, do_percent_saturation,
    alkalinity_demand_for_tan, severity_for_value, severity_in_range,
)
from .biofilter import (
    tan_production_from_feed, nitrification_derating_factor,
    biofilter_capacity_derated, biofilter_loading_ratio,
    biofilter_status_from_ratio, nitrification_penalty_pct,
    alkalinity_demand_from_feed,
)
from .diseases import DISEASE_REGISTRY, match_disease_signals, DiseaseSignal
from .species import SpeciesRegistry, EnvelopeLookup
from .registry import SkillRegistry, SkillSpec
from .hooks import HookBus, HookEvent, LifecycleHook
from .tools import ToolRegistry, Tool, ToolContext
from .context import PromptBuilder, TokenBudget, count_tokens
from .router import ChainOfThoughtRouter, RoutingDecision
from .engine import Engine

__all__ = [
    "Engine",
    "RasAquaError", "ConfigError", "SkillError", "SkillNotFoundError",
    "QualityGateError", "ToolError", "ContextBudgetError", "LLMUnavailable",
    "InputValidationError",
    "Requirements", "WaterQualityReading", "RasConfig", "WaterQualityScorecard",
    "Deviation", "BiofilterRisk", "DiseaseWarning", "Treatment", "Verdict",
    "EvidenceItem", "SkillResult", "EngineReport", "Severity", "VerdictCategory",
    "Status",
    "ammonia_pka", "unionized_ammonia_fraction", "unionized_ammonia_mgL",
    "do_saturation_freshwater", "do_percent_saturation",
    "alkalinity_demand_for_tan", "severity_for_value", "severity_in_range",
    "tan_production_from_feed", "nitrification_derating_factor",
    "biofilter_capacity_derated", "biofilter_loading_ratio",
    "biofilter_status_from_ratio", "nitrification_penalty_pct",
    "alkalinity_demand_from_feed",
    "DISEASE_REGISTRY", "match_disease_signals", "DiseaseSignal",
    "SpeciesRegistry", "EnvelopeLookup",
    "SkillRegistry", "SkillSpec", "HookBus", "HookEvent", "LifecycleHook",
    "ToolRegistry", "Tool", "ToolContext",
    "PromptBuilder", "TokenBudget", "count_tokens",
    "ChainOfThoughtRouter", "RoutingDecision",
]

__version__ = "2.0.0"
