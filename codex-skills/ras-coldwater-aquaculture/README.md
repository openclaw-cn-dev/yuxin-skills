# ras-coldwater-aquaculture

**Cold-Water Recirculating Aquaculture System (RAS) Design & Operation**

[![Claude Skill](https://img.shields.io/badge/Claude-Skill-blue)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![8-File Contract](https://img.shields.io/badge/8--File%20Contract-passing-brightgreen)](#testing)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](#roadmap)
[![Status](https://img.shields.io/badge/status-production--ready-success)](#roadmap)
[![Engine](https://img.shields.io/badge/engine-skill--registry-orange)](#architecture)

A professional-grade Claude Code harness for **Recirculating Aquaculture
Systems & Cold-Water Fish Health Management**. It gathers authoritative
real-time data, applies recognized domain methods (un-ionized ammonia
equilibrium, DO saturation, cold-water nitrification derating, WOAH
disease early-warning), integrates academic research, and delivers
evidence-backed, risk-disclosed operational verdicts.

## Overview

`ras-coldwater-aquaculture` turns Claude into a senior cold-water RAS
operations advisor. Given a facility snapshot (species, life stage, RAS
configuration, water-quality readings, biomass/feed load), it produces a
structured report containing a water-quality scorecard, a biofilter & disease
risk assessment, an automated water-treatment procedure, and a
risk-disclosed verdict. Every claim is traceable to a tiered source, every
limitation is disclosed before the recommendation, and the knowledge base
self-updates through a weekly crawl pipeline.

The harness enforces 6 universal quality gates (U1-U6) plus 5 domain gates
(G1-G5), degrades gracefully when sources are unreachable, and never
fabricates missing data.

## Features

<details>
<summary><b>Domain analysis</b></summary>

- Un-ionized ammonia (NH3-N) from temperature + pH via the Emerson (1975) equilibrium.
- Dissolved oxygen reported as both mg/L and % saturation vs temperature.
- Cold-water nitrification derating for biofilter capacity estimates.
- Alkalinity demand and CO2 accumulation assessment.
- Per-parameter deviation scorecards against species-specific envelopes.
- TAN production from feed load vs biofilter nitrification capacity.
- WOAH notifiable disease early-warning signal matching for cold-water salmonids.
- Advanced water-treatment recommendations (MBBR, denitrification, ozone, UV, CO2 stripping) with magnitude.

</details>

<details>
<summary><b>Harness &amp; quality discipline</b></summary>

- 7-step orchestrated harness (requirements -> evidence -> analysis -> biofilter/disease -> knowledge -> advisor -> gate).
- 6 universal + 5 domain quality gates with auto-fix and 2-retry enforcement.
- 5-level graceful degradation with explicit LIMITATION banners.
- Pre-flight Vietnamese/English language detection with label translation table.
- Risk-disclosed verdicts in exactly one of four categories: Optimal / Adjust Required / Critical Alert / Inconclusive.
- Best / base / worst scenario projection for borderline cases.

</details>

<details>
<summary><b>Self-improving knowledge base</b></summary>

- `SECOND-KNOWLEDGE-BRAIN.md` living knowledge base with evidence tiers (1-4).
- `tools/knowledge_updater.py` crawl pipeline: ArXiv + Semantic Scholar + RSS.
- SHA256 dedup of DOI/URL across both the update log and the existing reference table.
- Composite scoring (recency + keyword relevance + citation count).
- Weekly academic + daily news cron schedule with dry-run mode.

</details>

<details>
<summary><b>Programmatic skill-registry engine (v2.0)</b></summary>

- Modular, registry-based engine in `src/ras_aqua/` (pure stdlib; no hard deps).
- Chain-of-thought router: intent classification, plan selection, token budget.
- Real domain computation: Emerson (1975) NH3 equilibrium, Benson-Krause/APHA
  DO saturation, cold-water nitrification derating (Q10), WOAH disease matching.
- Lifecycle hooks (pre/post skill/engine/gate/error/degradation) for state sync,
  metrics, and audit. Rich tool registry with validated JSON-schema handlers.
- Type-safe, env-driven config (`config/`): settings, species envelopes, flags.
- Structured JSON logging to stderr; clean JSON reports on stdout.
- Graceful 5-level degradation; deterministic fallback when no LLM is configured.
- JSON Schema input/output contracts in `assets/schemas/`.

</details>

## Why This Skill

Recirculating Aquaculture Systems & Cold-Water Fish Health Management
practitioners face fragmented data, inconsistent methodology, and tools
that do not self-improve. This skill unifies authoritative real-time data,
recognized domain methods, and a continuously-updated academic knowledge
base into one evidence-backed, risk-disclosed workflow.

## Installation

```bash
pip install -r requirements.txt
```

Install the skill files to `~/.claude/skills/` or use them in place via the
project `CLAUDE.md`. Python 3.9+ is required for the tooling; the skill
files themselves are pure Markdown and require no runtime.

The core engine (`src/ras_aqua/`) is pure standard-library Python and has **no
hard runtime dependencies** ? the packages in `requirements.txt` are optional
and only enable the crawl pipeline, precise token counting, and pytest. Run the
local setup + smoke test:

```bash
python scripts/setup_env.py
```

## Quick Start

```bash
# 0. Local setup + engine smoke test
python scripts/setup_env.py

# 1. Validate the 8-File Contract (CI-safe, no network, no side effects)
python tools/validate_project.py

# 2. Run the structural & content validator
python tools/run_test_scenarios.py --all

# 3. Run the knowledge-updater unit tests
python tools/test_knowledge_updater.py

# 4. (Optional) Preview a knowledge crawl without writing anything
python tools/knowledge_updater.py --dry-run
```

Invoke the skill inside Claude Code:

```
/ras-coldwater-aquaculture Analyze my rainbow trout RAS: T 14C, DO 6.2 mg/L, pH 7.4, TAN 0.8 mg/L, NO2 0.15 mg/L, NO3 60 mg/L, alk 90 mg/L, CO2 12 mg/L, MBBR 8 m2, flow 200 lpm, biomass 120 kg, feed 1.5 kg/day
```

## Usage

```bash
/ras-coldwater-aquaculture [your query]


### Programmatic engine (batch / CI / cron)

```bash
# Run a full analysis from a JSON requirements file
python scripts/run_pipeline.py --input requirements.json --pretty

# Ingest a water-quality CSV/JSON log into a requirements file first
python scripts/ingest_water_log.py --log water.csv --species rainbow_trout \
    --life-stage growout --out requirements.json

# Print engine capabilities (skills, tools, species, features)
python scripts/run_pipeline.py --describe
```

A minimal requirements JSON:

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

Supported analysis types (auto-detected, default `combined`):

| Analysis type | Trigger keywords | Output |
|--------------|------------------|--------|
| `water-quality` | "water quality", "ammonia", "DO" | Water-quality scorecard + NH3/DO deviations |
| `biofilter-disease` | "biofilter", "disease", "nitrification" | Biofilter loading + disease early-warning |
| `combined` | default | Full scorecard + risk assessment + verdict |
| `comparison` | "compare", "versus", "vs" | Side-by-side scorecards for two cases |

## Architecture

```
USER INPUT
   |
[skills/main.md - ras-coldwater-aquaculture]
   |
   +-> sub-gather-requirements        -> structured requirements
   +-> sub-evidence-collector         -> species envelopes + disease refs
   +-> sub-water-quality-analysis     -> NH3, DO% sat, nitrification, CO2 scorecard
   +-> sub-biofilter-disease-assessment-> biofilter loading + disease risk
   +-> sub-knowledge-updater          -> tiered knowledge-base citations
   +-> sub-ras-advisor                -> risk-disclosed verdict + procedure
   |
   +-> [QUALITY GATE - main.md]
         U1-U6 + G1, G2, G3, G4, G5 -> deliver or flag limitation
```

The same 6-step pipeline runs in two layers: the **prompt layer**
(`skills/*.md`, interactive Claude Code) and the **engine layer**
(`src/ras_aqua/`, deterministic Python). Both share schemas, prompt templates,
and quality gates. See `SKILL.md` for the full skill-registry contract and
`assets/diagrams/architecture.mmd` for the data-flow diagram.

Project layout (8-File Contract + v2.0 modular architecture):

```
ras-coldwater-aquaculture/
+- CLAUDE.md, PROJECT-detail.md, PROJECT-DEVELOPMENT-PHASE-TRACKING.md
+- README.md, SKILL.md, SECOND-KNOWLEDGE-BRAIN.md, requirements.txt, .gitignore, LICENSE
+- skills/        main.md + 6 sub-*.md (prompt layer)
+- src/ras_aqua/  engine: registry, router, hooks, tools, gates, skills,
|                 chemistry, biofilter, diseases, species, schemas, context
+- config/        type-safe settings + species envelopes + feature flags
+- references/    prompt templates + domain guidelines + citation tiers
+- assets/        JSON schemas (input/output) + architecture diagram
+- scripts/       setup, run_pipeline, ingest_water_log, seed_knowledge_base
+- tools/         knowledge_updater.py, test_knowledge_updater.py,
|                 run_test_scenarios.py, validate_project.py
+- tests/         test-scenarios.md, TEST_RESULTS.md, engine/ (unit + integration)
+- logs/          crawl + engine logs (gitignored)
```

## Quality Gates

Universal gates U1-U6 (mandatory, library-wide) plus the domain gates defined
in `skills/main.md`:

| Gate | Check |
|------|-------|
| G1 | Water-quality setpoints cite >=1 authoritative aquaculture source per species+stage |
| G2 | Un-ionized ammonia (NH3) computed from T+pH via Emerson formula with units (mg/L NH3-N) |
| G3 | DO reported as % saturation vs temperature; flagged if below species floor |
| G4 | Each out-of-envelope parameter maps to a concrete water-treatment action; cold-T derating applied |
| G5 | Cold-water species envelopes kept distinct (e.g. salmonids T<18C); no warm-water setpoints applied |

Enforcement: apply each gate in order; on failure run the Auto-Fix; after 2
failed retries, emit an explicit limitation notice for that gate and continue.

## Data Sources

- FAO Aquaculture Department - fao.org/fishery (RAS & water-quality guidelines, cultured species factsheets)
- DFO Canada (Fisheries & Oceans) - dfo-mpo.gc.ca (cold-water salmonid/char culture)
- The Freshwater Institute (RAS research, biofilter & water reuse) - freshwaterinstitute.org
- SRAC / US Regional Aquaculture Centers - extension factsheets (water-quality tables)
- World Organisation for Animal Health (WOAH) - woah.org (Aquatic Animal Health Code & notifiable diseases)
- USDA APHIS Aquaculture - aphis.usda.gov (disease surveillance)
- US EPA - Water Quality Criteria (ammonia criteria for aquatic life)
- YSI / Xylem - ysi.com (DO, pH, conductivity sensor specs)
- Hach - hach.com (colorimetric NH3/NO2/NO3/alkalinity methods & sensor specs)
- NOAA Fisheries Aquaculture - fisheries.noaa.gov (aquaculture regulations & health)
- NIWA (NZ) - cold-water aquaculture references

## Testing

```bash
# 8-File Contract validator (CI-safe)
python tools/validate_project.py           # human report
python tools/validate_project.py --json   # machine-readable report

# Structural & content validator (90+ checks)
python tools/run_test_scenarios.py --all

# Knowledge-updater unit tests
python tools/test_knowledge_updater.py

# Engine unit + integration tests (stdlib unittest; pytest also works)
python -m unittest discover -s tests/engine -p "test_*.py"
# or: python -m pytest tests/engine -q
```

All three suites must exit 0. `tests/test-scenarios.md` defines 5+ end-to-end
scenarios (standard, minimal-input, comparison, risk/conflict, degraded-mode)
exercising every gate and every verdict category. Results are summarised in
`tests/TEST_RESULTS.md`.

## Knowledge Base

`SECOND-KNOWLEDGE-BRAIN.md` is the living knowledge base, organised into 7
sections (core methods, key papers with DOIs, state-of-the-art, data sources,
analytical frameworks, self-update protocol, update log). Evidence is tiered
1 (systematic review / standard) through 4 (news / vendor material).

The base auto-updates via `tools/knowledge_updater.py`:

```bash
python tools/knowledge_updater.py --dry-run            # preview, no writes
python tools/knowledge_updater.py --news-only          # daily news crawl only
python tools/knowledge_updater.py --keywords "..."    # override keywords
python tools/knowledge_updater.py --json              # emit JSON summary
```

Cron schedule (documented in `CLAUDE.md`): weekly academic (Mondays 08:00) +
daily news (07:00). Dedup is SHA256 of DOI/URL, case/whitespace-insensitive,
checked against both the existing reference table and the update log.

## Development

This project follows the 8-File Contract from `D:\972026\SKILL-STANDARD.md`.
Development is tracked phase-by-phase in
`PROJECT-DEVELOPMENT-PHASE-TRACKING.md` (Phases 0-5). When extending the
domain methods, update the corresponding `skills/sub-*.md`, the relevant
section of `SECOND-KNOWLEDGE-BRAIN.md`, and add a scenario to
`tests/test-scenarios.md`. Re-run all three validator suites before opening a
change.

```bash
# Local pre-flight gate before any change
python tools/validate_project.py && python tools/run_test_scenarios.py --all && python tools/test_knowledge_updater.py
```

## Roadmap

- [x] Phase 0: Architecture & source map
- [x] Phase 1: Core sub-skills (6)
- [x] Phase 2: Main harness + quality gates + degradation
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation
- [x] Phase 5: Integration & polish - PRODUCTION READY v1.0.0
- [x] Phase 6: Skill-registry engine + modular dirs (config/references/assets/scripts) + hooks/tools + SKILL.md - PRODUCTION READY v2.0.0

## Contributing

Contributions are welcome. Please:

1. Open an issue describing the proposed change and the evidence it rests on.
2. Keep sub-skill boundaries intact (one concern per `sub-*.md`).
3. Cite every new claim to a tiered source in `SECOND-KNOWLEDGE-BRAIN.md`.
4. Add or update a `tests/test-scenarios.md` scenario that exercises the change.
5. Ensure `python tools/validate_project.py`, `python tools/run_test_scenarios.py --all`,
   and `python tools/test_knowledge_updater.py` all exit 0 before submitting.

## License

MIT - see [LICENSE](LICENSE).

## Acknowledgments

- Emerson et al. (1975) for the un-ionized ammonia equilibrium.
- Benson & Krause (1984) and APHA Standard Methods for dissolved oxygen saturation.
- Timmons & Ebeling, *Recirculating Aquaculture* (3rd ed.) for RAS engineering.
- WOAH Aquatic Animal Health Code for notifiable-disease references.
- Eding et al. (2006) and Zhu & Chen (2002) for nitrification kinetics in biofilters.
- The Freshwater Institute and SRAC extension factsheets for cold-water envelopes.

## Citation

```bibtex
@software{ras-coldwater-aquaculture,
  title  = {ras-coldwater-aquaculture: Cold-Water Recirculating Aquaculture System (RAS) Design & Operation},
  year   = {2026},
  version= {2.0.0},
  url    = {https://github.com/your-org/ras-coldwater-aquaculture}
}
```
