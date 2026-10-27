# DEVELOPMENT-TRACKING.md ? Agent Memory (ras-coldwater-aquaculture v2.0)

> Working memory for the agent that upgraded this project. Mirrors the public
> `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` but records decisions, gotchas, and
> the verification trail so future work resumes cleanly.

## Mission
Upgrade, expand, and complete `161-ras-coldwater-aquaculture` to a bulletproof,
production-grade, open-source standard: flexible agent & skill architecture,
hooks & tools, SKILL.md registry, modular dirs (config/references/assets/
scripts), real-world best practices, no placeholders.

## Key decisions
- **Two-layer design**: keep the markdown `skills/*.md` as the prompt layer for
  interactive Claude Code; add a deterministic Python engine (`src/ras_aqua/`)
  as the executable backbone for CI/cron/batch. Both share schemas, templates,
  gates.
- **Skill-registry pattern** (`registry.py` + `skills/base.py`): declarative
  `SkillSpec`, DAG validation, ordered execution, retry + degradation. Chosen
  over a fixed chain for extensibility.
- **Chain-of-thought router** (`router.py`): deterministic intent + plan +
  token budget; LLM assist optional.
- **Real computation**: chemistry (Emerson 1975, Benson-Krause/APHA),
  biofilter (Q10 cold derating), diseases (WOAH rule table) are pure functions,
  unit-tested. The engine produces correct verdicts WITHOUT an LLM.
- **Graceful LLM-free fallback**: `NoOpAdapter`; LLM only polishes prose.
- **Type-safe config**: stdlib dataclasses (no pydantic) to keep zero hard deps.
- **JSON not YAML** for config (stdlib-only, no BOM issues).
- **Logging ? stderr** so `run_pipeline.py` stdout is clean machine JSON.

## Gotchas hit & fixed
- PowerShell `Set-Content -Encoding UTF8` adds a BOM ? JSON loads fail. Fixed by
  reading with `utf-8-sig` in `_load_json` and stripping BOM after writes.
- Piping non-ASCII (Vietnamese) through PowerShell stdin to Python mangles it
  (console code page). Used `Set-Content -Encoding UTF8` + BOM strip for
  non-ASCII files instead of the python-stdin writer.
- DO salinity correction coefficients were wrong (Standard Methods uses T in
  Kelvin with `(0.017674, -10.754, 2140.7)`); fixed and verified vs seawater.
- Hook callback passed `event=` kwarg colliding with `logger.debug(event=...)`;
  renamed to `hook_event=`.
- `tests/` needed `__init__.py` for `python -m unittest tests.engine.*`.

## Verification trail (all green)
- `python tools/validate_project.py` ? 164/164 (was 100; +64 v2 checks).
- `python tools/run_test_scenarios.py --all` ? 93/93.
- `python tools/test_knowledge_updater.py` ? all pass.
- `python -m unittest discover -s tests/engine` ? 62/62.
- `python scripts/setup_env.py` ? smoke test verdict produced, 11/11 gates pass.
- `python scripts/run_pipeline.py --input tests/engine/sample_req.json` ?
  Critical Alert, 11/11 gates, exit 0.
- Engine spot-checks: NH3 @ TAN1/15C/pH7.5 = 0.0087 mg/L; DOsat @15C =
  10.08 mg/L; derate @10C = 0.354; biofilter overload ratio computed correctly.

## File map added in v2
- `SKILL.md`, `config/` (3), `references/` (9), `assets/` (5), `scripts/` (4),
  `src/ras_aqua/` (16 modules + 7 skills), `tests/engine/` (5 test modules),
  updated: `tools/validate_project.py`, `requirements.txt`, `.gitignore`,
  `README.md`, `CLAUDE.md`, `PROJECT-detail.md`,
  `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`, `tests/TEST_RESULTS.md`,
  `skills/main.md`.

## Status
**PRODUCTION READY v2.0.0 ? all phases 0?6 at 100%.**
