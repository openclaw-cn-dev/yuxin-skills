"""Exception hierarchy and structured error handling for ras_aqua.

The engine never lets an unexpected exception bubble to the user silently:
every recoverable failure is wrapped in a domain error carrying a stable
``code``, a human-readable ``message``, optional ``cause``, and a
``degradation_level`` hint that the orchestrator uses to decide whether to
continue with reduced data or abort.
"""
from __future__ import annotations

from typing import Optional


class RasAquaError(Exception):
    """Base class for all ras_aqua errors."""

    code: str = "RAS_AQUA_ERROR"
    degradation_level: int = 0

    def __init__(self, message: str, *, cause: Optional[BaseException] = None,
                 degradation_level: Optional[int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause
        if degradation_level is not None:
            self.degradation_level = degradation_level

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "degradation_level": self.degradation_level,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigError(RasAquaError):
    code = "CONFIG_ERROR"
    degradation_level = 4


class SkillError(RasAquaError):
    code = "SKILL_ERROR"
    degradation_level = 3


class SkillNotFoundError(SkillError):
    code = "SKILL_NOT_FOUND"
    degradation_level = 4


class QualityGateError(RasAquaError):
    code = "QUALITY_GATE_ERROR"
    degradation_level = 2

    def __init__(self, message: str, *, gate: str = "",
                 cause: Optional[BaseException] = None,
                 degradation_level: Optional[int] = None) -> None:
        super().__init__(message, cause=cause, degradation_level=degradation_level)
        self.gate = gate

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["gate"] = self.gate
        return d


class ToolError(RasAquaError):
    code = "TOOL_ERROR"
    degradation_level = 3


class ContextBudgetError(RasAquaError):
    code = "CONTEXT_BUDGET_ERROR"
    degradation_level = 2


class LLMUnavailable(RasAquaError):
    """Raised when the LLM adapter cannot produce output after retries."""
    code = "LLM_UNAVAILABLE"
    degradation_level = 2


class InputValidationError(RasAquaError):
    code = "INPUT_VALIDATION_ERROR"
    degradation_level = 3


def safe_call(func, *args, on_error=None, **kwargs):
    """Invoke ``func``; on any exception return ``on_error`` (default None).

    Used to wrap non-critical computations so a single bad reading cannot
    abort the whole pipeline. The original exception is swallowed intentionally
    because the caller is expected to record a data-quality flag instead.
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return on_error
