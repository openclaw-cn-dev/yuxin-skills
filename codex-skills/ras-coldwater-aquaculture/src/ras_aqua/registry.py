"""Skill registry: declarative registration, resolution, validation, and
execution of skills in the ras_aqua engine.

A ``SkillSpec`` is the metadata contract (name, step order, description,
input/output schema references, dependencies, prompt template). An executor is
a callable ``SkillContext -> SkillResult``. The registry resolves skills by
name, validates that required upstream outputs are present, and executes them
with retry + degradation handling driven by the engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .errors import SkillError, SkillNotFoundError
from .schemas import SkillResult


SkillExecutor = Callable[[Any], SkillResult]


@dataclass
class SkillSpec:
    name: str
    step: int
    description: str
    executor: SkillExecutor
    input_schema: str = ""           # path to JSON schema under assets/schemas
    output_schema: str = ""
    depends_on: List[str] = field(default_factory=list)
    prompt_template: str = ""
    tags: List[str] = field(default_factory=list)
    retryable: bool = True


class SkillRegistry:
    """Holds SkillSpecs; resolves by name and in execution order."""

    def __init__(self) -> None:
        self._skills: Dict[str, SkillSpec] = {}

    def register(self, spec: SkillSpec) -> None:
        if spec.name in self._skills:
            raise SkillError(f"skill '{spec.name}' already registered")
        self._skills[spec.name] = spec

    def get(self, name: str) -> SkillSpec:
        if name not in self._skills:
            raise SkillNotFoundError(f"skill '{name}' not registered")
        return self._skills[name]

    def has(self, name: str) -> bool:
        return name in self._skills

    def list(self) -> List[str]:
        return sorted(self._skills.keys())

    def ordered(self) -> List[SkillSpec]:
        """Return skills ordered by their declared step."""
        return sorted(self._skills.values(), key=lambda s: s.step)

    def validate_dag(self) -> None:
        """Ensure every declared dependency exists (no dangling refs)."""
        for spec in self._skills.values():
            for dep in spec.depends_on:
                if dep not in self._skills:
                    raise SkillError(
                        f"skill '{spec.name}' depends on unknown skill '{dep}'")

    def specs(self) -> List[Dict[str, Any]]:
        return [
            {"name": s.name, "step": s.step, "description": s.description,
             "depends_on": s.depends_on, "input_schema": s.input_schema,
             "output_schema": s.output_schema, "tags": s.tags}
            for s in self.ordered()
        ]
