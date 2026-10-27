"""Context-window management and prompt assembly for ras_aqua.

Two responsibilities:

1. ``TokenBudget`` ? tracks the running token budget across skills so the
   engine can decide whether to compact/summarize context before invoking the
   next skill (production-grade context-window discipline).
2. ``PromptBuilder`` ? loads the prompt templates under
   ``references/prompt_templates/`` and substitutes ``{{placeholder}}`` tokens,
   producing the final system+user prompt strings for the LLM adapter.

Token counting uses a deterministic, dependency-free heuristic (chars/4 +
whitespace bias) that is good enough for budget gating; a precise tokenizer is
plugged in when available (e.g. tiktoken) without changing the API.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from .errors import ContextBudgetError

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT_DIR / "references" / "prompt_templates"


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> int:
    """Heuristic token count (~chars/4 with a small whitespace bias).

    Good enough for budget gating. If ``tiktoken`` is installed and the text is
    large, fall back to it for accuracy.
    """
    if not text:
        return 0
    try:
        import tiktoken  # type: ignore
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Heuristic: English text averages ~4 chars/token.
        return max(1, int(len(text) / 4.0 + text.count(" ") * 0.0))


@dataclass
class TokenBudget:
    max_context_tokens: int
    reserved_output_tokens: int
    used_tokens: int = 0

    @property
    def available(self) -> int:
        return max(0, self.max_context_tokens - self.reserved_output_tokens - self.used_tokens)

    def consume(self, n: int) -> None:
        if n < 0:
            raise ContextBudgetError("cannot consume negative tokens")
        self.used_tokens += n
        if self.used_tokens > self.max_context_tokens - self.reserved_output_tokens:
            raise ContextBudgetError(
                f"context budget exhausted: used {self.used_tokens} > "
                f"{self.max_context_tokens - self.reserved_output_tokens} available",
                degradation_level=2,
            )

    def reset(self) -> None:
        self.used_tokens = 0


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class PromptBuilder:
    """Loads and renders prompt templates from ``references/prompt_templates``."""

    def __init__(self, templates_dir: Optional[Path] = None) -> None:
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self._cache: Dict[str, str] = {}

    def load(self, name: str) -> str:
        """Load template ``name`` (e.g. 'base', 'gather_requirements')."""
        if name in self._cache:
            return self._cache[name]
        path = self.templates_dir / f"{name}.md"
        if not path.is_file():
            raise FileNotFoundError(f"prompt template not found: {path}")
        text = path.read_text(encoding="utf-8-sig")
        self._cache[name] = text
        return text

    def render(self, name: str, variables: Dict[str, Any]) -> str:
        """Render template ``name`` substituting ``{{var}}`` tokens.

        Missing variables are left as-is and logged by the caller; dict/list
        values are JSON-serialized for compactness.
        """
        template = self.load(name)

        def repl(match: re.Match) -> str:
            key = match.group(1)
            if key not in variables:
                return match.group(0)
            val = variables[key]
            if isinstance(val, (dict, list)):
                import json
                return json.dumps(val, ensure_ascii=False, default=str)
            return str(val)

        return _PLACEHOLDER_RE.sub(repl, template)

    def build_skill_prompt(self, skill_template: str, base_vars: Dict[str, Any],
                           skill_vars: Dict[str, Any]) -> str:
        """Combine the base preamble with a skill template into one prompt."""
        base = self.render("base", base_vars)
        skill = self.render(skill_template, skill_vars)
        return f"{base}\n\n---\n{skill}"
