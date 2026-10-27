# SKILL.md — Skill Registry Documentation

> `ras-coldwater-aquaculture` v2.0.0 — production-grade, open-source skill
> engine for **Recirculating Aquaculture Systems & Cold-Water Fish Health
> Management**. This document is the canonical reference for how skills are
> registered, resolved, executed, validated, and extended.

This project ships TWO complementary layers:

1. **Prompt-layer skills** (`skills/*.md`) — markdown prompt files consumed by
   Claude Code when the skill is invoked interactively (`/ras-coldwater-aquaculture`).
   These document the harness flow, persona, quality gates, and output template
   for an LLM-driven run.
2. **Engine-layer skills** (`src/ras_aqua/skills/*.py`) — a modular, registry-based
   Python engine that executes the **same** 6-step pipeline deterministically with
   real domain computations (Emerson NH3 equilibrium, Benson-Krause DO saturation,
   cold-water nitrification derating, WOAH disease matching). The engine degrades
   gracefully without an LLM and is the backbone for CI, cron, and batch analysis.

Both layers share the same skill boundaries, input/output JSON schemas
(`assets/schemas/`), prompt templates (`references/prompt_templates/`), and
quality gates (U1–U6 + G1–G5).

---

## 1. Architecture

```
config/      type-safe settings + species envelopes + feature flags
references/  prompt templates + domain guidelines + citation tiers
assets/      JSON schemas (input/output) + architecture diagram
scripts/     setup, pipeline runner, water-log ingestion, KB seeding
src/ras_aqua/        the engine (registry + router + hooks + tools + skills)
  chemistry.py       real water-chemistry (Emerson, Benson-Krause, alkalinity)
  biofilter.py       TAN production, cold derating, capacity & loading
  diseases.py        WOAH disease early-warning rule table + matcher
  species.py         species envelope registry + name normalization
  registry.py        SkillRegistry (register / resolve / validate DAG)
  router.py          chain-of-thought router (intent + plan + token budget)
  hooks.py           lifecycle hook bus (pre/post skill/engine/gate/error)
  tools.py           Tool registry (schema + validated handler per tool)
  context.py         token budget + prompt builder (template rendering)
  gates.py           U1-U6 + G1-G5 quality gates with auto-fix
  engine.py          orchestrator (run -> report)
  skills/            6 concrete skill executors
skills/      markdown prompt-layer skills (Claude Code interactive)
tools/       knowledge crawl pipeline + project validators
tests/       scenarios + engine unit/integration tests
```

See `assets/diagrams/architecture.mmd` for the full data-flow diagram.

---

## 2. Skill Registry

### 2.1 Registration

Skills are registered declaratively as `SkillSpec` objects in
`src/ras_aqua/engine.py` via `Engine._register_default_skills()`. Each spec
binds a skill name to an executor callable (`Skill.run`), a step order,
declared dependencies, input/output schema paths, a prompt template, and tags.

```python
from ras_aqua import SkillRegistry, SkillSpec
from ras_aqua.skills import WaterQualityAnalysisSkill

reg = SkillRegistry()
skill = WaterQualityAnalysisSkill()
reg.register(SkillSpec(
    name=skill.name, step=skill.step, description=skill.description,
    executor=skill.run, depends_on=list(skill.depends_on),
    input_schema=skill.input_schema, output_schema=skill.output_schema,
    prompt_template=skill.prompt_template, tags=list(skill.tags),
))
reg.validate_dag()   # catches dangling dependencies
```

### 2.2 Resolution & Execution Order

`SkillRegistry.ordered()` returns skills sorted by `step`. The engine executes
the plan returned by the chain-of-thought router (`ChainOfThoughtRouter.route`)
in order. A skill only runs if all `depends_on` skills have produced output in
the shared `SkillState`.

### 2.3 Validation

* **DAG validation** — `SkillRegistry.validate_dag()` ensures every
  `depends_on` references a registered skill.
* **Input validation** — the intake skill validates the species via
  `SpeciesRegistry.normalize_species` (rejects warm-water species, per gate G5)
  and the minimum reading set (T, DO, pH, TAN).
* **Output validation** — every skill returns a `SkillResult` with a `status`
  (`ok`/`degraded`/`error`), `degradation_level`, `limitations`, and `evidence`.
* **Gate validation** — `gates.py` enforces U1–U6 + G1–G5 with auto-fix and a
  2-retry limit before emitting an explicit limitation.

---

## 3. Skill Catalog

| Step | Skill (`skills/*.md` + `src/ras_aqua/skills/*.py`) | Input | Output schema |
|------|----------------------------------------------------|-------|---------------|
| 1 | `gather_requirements` | user message / structured dict / attached log | `requirements.schema.json` |
| 2 | `evidence_collector` | Requirements | evidence bundle (envelope + thresholds + disease refs) |
| 3 | `water_quality_analysis` | Requirements + envelope | `water_quality_scorecard.schema.json` |
| 4 | `biofilter_disease` | Scorecard + RAS config + biomass/feed + disease refs | `biofilter_risk.schema.json` |
| 5 | `knowledge_updater` | analysis keywords | tiered citations + knowledge gaps |
| 6 | `ras_advisor` | scorecard + biofilter risk + evidence bundle + KB citations | `verdict.schema.json` |

Each skill has a matching prompt template under
`references/prompt_templates/<name>.md` used by `PromptBuilder` when an LLM is
configured.

---

## 4. Tool Registry

Tools are pure, deterministic functions wrapped with explicit input/output JSON
schemas, validated before execution. Skills and the router invoke them via
`ToolRegistry.invoke(name, args, ctx)`. Available tools:

| Tool | Description | Tags |
|------|-------------|------|
| `compute_nh3` | Un-ionized ammonia NH3-N from TAN, T, pH (Emerson 1975) | chemistry, ammonia |
| `compute_do_saturation` | DO saturation mg/L + optional % sat (Benson-Krause/APHA) | chemistry, oxygen |
| `compute_tan_production` | Daily TAN production from feed load + protein | biofilter |
| `compute_biofilter_capacity` | Derated biofilter capacity + cold penalty | biofilter |
| `match_disease_signals` | Match condition tags vs WOAH disease rule table | disease |
| `query_knowledge_base` | Keyword search of SECOND-KNOWLEDGE-BRAIN.md | knowledge, rag |

To register a custom tool:

```python
from ras_aqua import Tool, ToolRegistry

def my_handler(args, ctx):
    return {"result": args["x"] * 2}

reg = ToolRegistry()
reg.register(Tool(
    name="double", description="Double a number",
    input_schema={"type": "object", "required": ["x"], "properties": {"x": {"type": "number"}}},
    output_schema={"type": "object", "properties": {"result": {"type": "number"}}},
    handler=my_handler, tags=["math"],
))
```

---

## 5. Hooks (Lifecycle Management)

A publish/subscribe `HookBus` emits structured events at well-defined points.
Subscribers receive a `HookContext` and must never raise (failures are logged
and swallowed). Events:

| Event | When |
|-------|------|
| `PRE_ENGINE` / `POST_ENGINE` | engine run start / end |
| `PRE_SKILL` / `POST_SKILL` | each skill execution |
| `PRE_GATE` / `POST_GATE` | quality-gate evaluation |
| `ON_ERROR` | any skill/gate error (with retry) |
| `ON_DEGRADATION` | degradation level escalates |
| `ON_TOOL_CALL` | tool invocation |

```python
from ras_aqua import Engine, HookEvent

engine = Engine.from_config()
engine.hooks.subscribe(HookEvent.POST_SKILL,
    lambda ctx: print(f"skill done: {ctx.payload['skill']}"))
```

---

## 6. Configuration

Type-safe, environment-driven configuration lives in `config/`:

* `config/settings.py` — frozen dataclasses (`Settings`, `LLMSettings`,
  `LoggingSettings`, `FeatureFlags`) validated at load time. Env overrides use
  the `RAS_` prefix (e.g. `RAS_LLM_MODEL`, `RAS_LOG_LEVEL`, `RAS_MAX_CONTEXT_TOKENS`).
* `config/species_envelopes.json` — cold-water species water-quality envelopes
  + biofilter media parameters (the engine's authoritative setpoint source).
* `config/feature_flags.json` — system-wide feature flags (knowledge crawl,
  web search, CoT routing, quality-gate auto-fix, token budget, retries).

```python
from ras_aqua import Engine
engine = Engine.from_config()           # loads + validates everything
print(engine.describe())                # skills, tools, species, features
```

---

## 7. Input / Output JSON Schemas

All schemas live in `assets/schemas/` (JSON Schema 2020-12):

* `requirements.schema.json` — intake object (species, life_stage, wq, ras_config,
  biomass/feed, objective, language).
* `water_quality_scorecard.schema.json` — NH3, DO % sat, nitrification,
  alkalinity, CO2, deviations, data-quality flags.
* `biofilter_risk.schema.json` — capacity status, loading ratio, disease
  warnings, treatments, advanced options.
* `verdict.schema.json` — verdict category, disclosure, alerts, treatment
  procedure, scenarios, key risks, evidence chain, remediation.

Example intake:

```json
{
  "species": "rainbow_trout", "life_stage": "growout",
  "wq": {"T_C": 15, "DO_mgL": 5.5, "pH": 7.8, "TAN_mgL": 1.2,
         "NO2_mgL": 0.05, "NO3_mgL": 30, "alkalinity_mgL": 60, "CO2_mgL": 18},
  "ras_config": {"tank_volume_m3": 50, "makeup_pct": 5,
                 "biofilter_type": "mbbr_kaldnes_k1", "biofilter_area_m2": 300,
                 "flow_lpm": 500},
  "biomass_kg": 2000, "feed_kg_day": 25, "feed_protein_pct": 42,
  "target_objective": "health_assessment", "language": "en"
}
```

---

## 8. Execution & Quality Standards

* **Context-window management** — `TokenBudget` tracks running token usage; the
  router estimates tokens and the engine enforces the configured budget
  (`RAS_MAX_CONTEXT_TOKENS` / `RAS_RESERVED_OUTPUT_TOKENS`).
* **Error handling** — every skill runs with retry + exponential backoff
  (`max_skill_retries`); recoverable errors degrade the run, unexpected errors
  are caught and never abort the pipeline.
* **Graceful fallback** — 5-level degradation (0–4) with explicit LIMITATION
  banners; missing data is flagged, never fabricated.
* **Structured logging** — one JSON event per line to stderr
  (`RAS_LOG_FORMAT=json|text`, `RAS_LOG_LEVEL`), so stdout stays clean for
  machine-readable output.
* **Quality gates** — U1–U6 (sources, disclosure, tiers, language, template,
  traceability) + G1–G5 (envelope source, NH3 computed, DO % sat, treatment
  mapping, cold-water species) with auto-fix and 2-retry enforcement.

---

## 9. Running

```bash
# Local setup + smoke test
python scripts/setup_env.py

# Run an analysis from a JSON requirements file
python scripts/run_pipeline.py --input requirements.json --pretty

# Ingest a water-quality CSV/JSON log first
python scripts/ingest_water_log.py --log water.csv --species rainbow_trout \
    --life-stage growout --out requirements.json

# Engine capabilities
python scripts/run_pipeline.py --describe

# Interactive (Claude Code)
/ras-coldwater-aquaculture analyze my trout RAS ...
```

---

## 10. Extension Guide

* **Add a species** — append an entry to `config/species_envelopes.json` and an
  alias in `src/ras_aqua/species.py::SPECIES_ALIASES`.
* **Add a biofilter media** — append to `biofilter_media` in the envelopes file.
* **Add a disease rule** — append a `DiseaseSignal` to `DISEASE_REGISTRY` in
  `src/ras_aqua/diseases.py`.
* **Add a skill** — subclass `Skill` in `src/ras_aqua/skills/`, add it to
  `all_skills()`, add a prompt template, and (if it emits structured output) a
  JSON schema in `assets/schemas/`.
* **Add a tool** — implement a handler + schemas and `ToolRegistry.register`.

## 11. Testing

```bash
python -m pytest tests/engine/ -q        # engine unit + integration tests
python tools/test_knowledge_updater.py   # crawl pipeline unit tests
python tools/run_test_scenarios.py --all # 8-File Contract + scenario validator
python tools/validate_project.py         # 8-File Contract validator
```

All tests are hermetic (no network) and exit non-zero on failure.
