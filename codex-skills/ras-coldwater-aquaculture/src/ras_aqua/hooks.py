"""Lifecycle hooks for the ras_aqua engine.

A lightweight publish/subscribe bus that emits structured events at well-defined
lifecycle points. Skills, tools, and external observers can subscribe to
``pre_skill``, ``post_skill``, ``pre_engine``, ``post_engine``, ``on_error``,
``gate_check``, and ``degradation`` events for state synchronization, event
emission, metrics, or audit logging ? without coupling to the orchestrator.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .logging_config import StructuredLogger


class HookEvent(str, Enum):
    PRE_ENGINE = "pre_engine"
    POST_ENGINE = "post_engine"
    PRE_SKILL = "pre_skill"
    POST_SKILL = "post_skill"
    PRE_GATE = "pre_gate"
    POST_GATE = "post_gate"
    ON_ERROR = "on_error"
    ON_DEGRADATION = "on_degradation"
    ON_TOOL_CALL = "on_tool_call"


@dataclass
class HookContext:
    """Payload passed to every hook callback."""
    event: HookEvent
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


LifecycleHook = Callable[[HookContext], None]


class HookBus:
    """In-process hook registry + dispatcher."""

    def __init__(self, logger: Optional[StructuredLogger] = None) -> None:
        self._subs: Dict[HookEvent, List[LifecycleHook]] = {e: [] for e in HookEvent}
        self._logger = logger
        self.event_log: List[Dict[str, Any]] = []

    def subscribe(self, event: HookEvent, callback: LifecycleHook) -> None:
        self._subs[event].append(callback)

    def unsubscribe(self, event: HookEvent, callback: LifecycleHook) -> None:
        try:
            self._subs[event].remove(callback)
        except ValueError:
            pass

    def emit(self, event: HookEvent, **payload: Any) -> None:
        ctx = HookContext(event=event, payload=payload)
        record = {"event": event.value, "payload": payload}
        self.event_log.append(record)
        if self._logger is not None:
            self._logger.debug("hook.emit", hook_event=event.value, **payload)
        for cb in list(self._subs[event]):
            try:
                cb(ctx)
            except Exception as exc:  # hooks must never break the pipeline
                if self._logger is not None:
                    self._logger.warning("hook.callback_failed",
                                         event=event.value, error=str(exc))

    def clear(self) -> None:
        self.event_log.clear()


# ---------------------------------------------------------------------------
# Built-in hooks (optional, registered by the engine)
# ---------------------------------------------------------------------------

def make_logging_hook(logger: StructuredLogger) -> LifecycleHook:
    def _hook(ctx: HookContext) -> None:
        logger.info("lifecycle", event=ctx.event.value, **ctx.payload)
    return _hook


def make_degradation_hook(collector: List[Dict[str, Any]]) -> LifecycleHook:
    def _hook(ctx: HookContext) -> None:
        if ctx.event is HookEvent.ON_DEGRADATION:
            collector.append(dict(ctx.payload))
    return _hook
