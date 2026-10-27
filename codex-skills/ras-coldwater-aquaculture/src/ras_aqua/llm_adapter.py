"""LLM adapter interface and a deterministic no-op fallback.

The engine never depends on a live model: when no adapter is configured it uses
``NoOpAdapter``, which returns structured "degraded" responses so the
deterministic skill pipeline still produces a complete, evidence-backed report.
A real adapter (OpenAI/Anthropic/local) can be plugged in by implementing the
``LLMAdapter`` protocol; all failures degrade to ``LLMUnavailable`` and the
engine continues with the deterministic path.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class LLMAdapter(Protocol):
    """Minimal protocol implemented by any LLM backend."""

    def complete(self, prompt: str, *, max_tokens: int = 2048,
                 temperature: float = 0.2) -> str: ...

    def web_search(self, query: str) -> List[str]: ...


class NoOpAdapter:
    """Deterministic fallback used when no LLM is configured.

    Returns a JSON string signalling that LLM synthesis was skipped; skills
    that only need the structured deterministic computation ignore this. Web
    search returns an empty list (no network).
    """

    name = "noop"

    def complete(self, prompt: str, *, max_tokens: int = 2048,
                 temperature: float = 0.2) -> str:
        return ('{"llm": "noop", "note": "No LLM configured; deterministic '
                'pipeline used."}')

    def web_search(self, query: str) -> List[str]:
        return []
