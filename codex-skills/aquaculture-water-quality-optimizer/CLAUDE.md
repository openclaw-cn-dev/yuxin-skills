# CLAUDE.md — Aquaculture Water Quality & Environment Optimizer (idea 118)

## Skill Identity
- **Name / slug:** `aquaculture-water-quality-optimizer`
- **Tagline:** Aquaculture Water Quality & Environment Optimizer
- **Source idea:** #118 (`ideas.md`)
- **Cluster:** Science, Engineering & Industry (`science-industry`)
- **Current phase:** Phase 5 — Integration & Cross-Skill Wiring **DONE**
- **Status:** Production-ready. All phases 0–5 complete.

## Problem This Skill Solves
Fish/shrimp farmers must keep water-quality parameters in safe ranges for species health and growth, but interactions (DO, ammonia, nitrite, pH, temperature, salinity) and biosecurity are complex and failures are costly.

This skill becomes **an aquaculture systems specialist who reads water-chemistry and stocking data the way a fisheries scientist and farm manager would**. It is research-first, grounds every score in named world-renowned frameworks, challenges its own assumptions before concluding, and produces a professional artifact: a multi-dimensional score plus a prioritized improvement roadmap.

## Harness Flow Summary
1. **Intake** → `sub-profile-intake` gathers structured inputs (`tools/schemas.py::IntakeProfile`).
2. **Gate / framework** → `sub-framework-selector` chooses a named framework (`tools/frameworks.py`).
3. **Research** → WebSearch/WebFetch enrich evidence from authoritative sources (graceful degradation to `SECOND-KNOWLEDGE-BRAIN.md` if unavailable).
4. **Scoring** → `sub-scoring-engine` produces a 0–100 multi-dimensional score (`tools/scoring_engine.py`).
5. **Roadmap** → `sub-improvement-roadmap` builds a prioritized plan (`tools/roadmap_engine.py`).
6. **Quality gate** → devil's-advocate review before final output.

_No hard safety/compliance gate; standard quality gates apply._

## Sub-skills
- `skills/sub-profile-intake.md` — Capture species, system type (pond/RAS/biofloc), stocking density, and measured parameters.
- `skills/sub-framework-selector.md` — Select species-specific water-quality envelopes and system-management model.
- `skills/sub-scoring-engine.md` — Score each parameter vs safe envelope and compute an overall water-health + biosecurity index.
- `skills/sub-improvement-roadmap.md` — Recommend aeration, water-exchange, feeding, and biosecurity actions ranked by mortality-risk reduction.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence gathering
- `Read`, `Write` — artifact production
- `Bash`/`python` — run `tools/knowledge_updater.py`, `tools/scoring_engine.py`, `tools/roadmap_engine.py`

## Knowledge Sources (crawl targets)
- *Aquaculture* (Elsevier)
- *Aquacultural Engineering*
- WOAH (OIE) Aquatic Animal Health Code
- FAO aquaculture technical papers
- PubMed, Crossref, Semantic Scholar, arXiv (via `tools/knowledge_updater.py`)

## Supporting Tools
- `tools/schemas.py` — Pydantic models for intake, framework, scoring, and roadmap.
- `tools/frameworks.py` — Named, citable water-quality envelopes and framework selection.
- `tools/scoring_engine.py` — Deterministic 5-dimension scoring engine.
- `tools/roadmap_engine.py` — Urgency-ranked improvement roadmap generator.
- `tools/knowledge_updater.py` — Scholarly-API crawler that grows `SECOND-KNOWLEDGE-BRAIN.md`.
- `tests/test_scenarios.py` — Automated regression harness for the 5 canonical scenarios.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Author main harness + 4 sub-skills
- [x] Define scoring dimensions: Oxygen status, Nitrogen toxicity risk, pH/alkalinity stability, Temperature/salinity fit, Biosecurity
- [x] Implement production Python tools (schemas, frameworks, scoring, roadmap, knowledge updater)
- [x] Seed SECOND-KNOWLEDGE-BRAIN with real, citable entries
- [x] Add automated regression scenarios (pytest, 7 tests, all passing)
- [x] Cross-skill wiring and framework alignment complete

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap (all phases done)
- `SECOND-KNOWLEDGE-BRAIN.md` — living knowledge base
- `tests/test-scenarios.md` — manual and automated scenario definitions

## How to Validate
```bash
pytest tests/test_scenarios.py -v
python tools/knowledge_updater.py --dry-run
```
