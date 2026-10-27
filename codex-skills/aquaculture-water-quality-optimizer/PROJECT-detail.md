# PROJECT-detail.md — Aquaculture Water Quality & Environment Optimizer

## Executive Summary
`aquaculture-water-quality-optimizer` is a Claude Skill that turns Claude into **an aquaculture systems specialist who reads water-chemistry and stocking data the way a fisheries scientist and farm manager would**. It ingests domain inputs, screens for safety/compliance where required, selects a world-renowned evaluation framework, gathers fresh evidence, scores the subject across 5 dimensions, and outputs a prioritized improvement roadmap. It is part of the **Science, Engineering & Industry** cluster.

**Current status:** Production-ready. All development phases 0–5 complete; automated scenario regression passes.

## Problem Statement
Fish/shrimp farmers must keep water-quality parameters in safe ranges for species health and growth, but interactions (DO, ammonia, nitrite, pH, temperature, salinity) and biosecurity are complex and failures are costly.

Domain context: practitioners need reproducible, evidence-graded evaluation rather than ad-hoc opinion. This skill enforces a research-first harness with explicit quality gates and a self-improving knowledge base.

## Target Users & Use Cases
- Primary: practitioners, learners, and decision-makers in this domain.
- Trigger examples:
1. **Shrimp pond low DO at dawn** — DO drops to 2.5 mg/L. Expect mortality-risk scoring and aeration/feeding-adjustment roadmap.
2. **Ammonia spike in RAS** — TAN high, pH 8.2, warm. Expect un-ionized ammonia calc and immediate mitigation steps.
3. **New tilapia farm setup** — User plans stocking density. Expect carrying-capacity reasoning and parameter targets.
4. **Disease outbreak biosecurity** — Sudden mortality. Expect WOAH-aligned biosecurity roadmap and diagnostic referral.
5. **Biofloc balance** — C:N ratio management. Expect floc-management guidance and monitoring schedule.

## Harness Architecture
```
/aquaculture-water-quality-optimizer  (skills/main.md)
   |
   v
[1] sub-profile-intake        -> structured IntakeProfile (tools/schemas.py)
   |
   v
[2] framework selection  -> choose named framework (tools/frameworks.py)
   |
   v
[3] research (WebSearch/WebFetch)        -> evidence (graceful deg: SECOND-KNOWLEDGE-BRAIN.md)
   |
   v
[4] scoring engine                       -> 0-100 multi-dimensional score (tools/scoring_engine.py)
   |
   v
[5] improvement roadmap                  -> effort x impact prioritized actions (tools/roadmap_engine.py)
   |
   v
[6] quality-gate / devil's advocate      -> final professional artifact
```

## Full Sub-Skill Catalog
#### `sub-profile-intake`
- **Purpose:** Capture species, system type (pond/RAS/biofloc), stocking density, and measured parameters.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated `IntakeProfile` (JSON)
- **Tools:** Read, Write; `tools/schemas.py`
- **Quality gate:** output schema validated before proceeding

#### `sub-framework-selector`
- **Purpose:** Select species-specific water-quality envelopes and system-management model.
- **Inputs:** `IntakeProfile`
- **Outputs:** selected `Framework` (JSON)
- **Tools:** Read, Write, WebSearch/WebFetch; `tools/frameworks.py`
- **Quality gate:** framework from registry, rationale cited

#### `sub-scoring-engine`
- **Purpose:** Score each parameter vs safe envelope and compute an overall water-health + biosecurity index.
- **Inputs:** `IntakeProfile` + `Framework`
- **Outputs:** `CompositeScore` (JSON)
- **Tools:** Read, Write, WebSearch/WebFetch; `tools/scoring_engine.py`
- **Quality gate:** every dimension cited, NH3 computed when possible

#### `sub-improvement-roadmap`
- **Purpose:** Recommend aeration, water-exchange, feeding, and biosecurity actions ranked by mortality-risk reduction.
- **Inputs:** `IntakeProfile` + `Framework` + `CompositeScore`
- **Outputs:** `Roadmap` (JSON)
- **Tools:** Read, Write; `tools/roadmap_engine.py`
- **Quality gate:** actions for low dimensions, monitoring schedule, stopgap note when composite < 50

## Evaluation Frameworks (world-renowned, citable)
- Water-quality parameter envelopes (DO, TAN/NH3, NO2, NO3, pH, alkalinity, temp, salinity)
- Total Ammonia Nitrogen / un-ionized ammonia equilibrium
- Carrying-capacity & stocking-density models
- Biosecurity / WOAH (OIE) aquatic health standards
- RAS & biofloc management principles
- FCR / growth performance benchmarking

## Scoring Model
| Dimension | Range | Default weight |
|-----------|-------|----------------|
| Oxygen status | 0–100 | 0.25 |
| Nitrogen toxicity risk | 0–100 | 0.25 |
| pH/alkalinity stability | 0–100 | 0.20 |
| Temperature/salinity fit | 0–100 | 0.15 |
| Biosecurity | 0–100 | 0.15 |

Composite = weighted mean of dimensions (weights justified per case, surfaced to the user). Every dimension score must cite at least one framework criterion or evidence source.

## Skill File Format Specification
Frontmatter: `name`, `description`. Required sections in `main.md`: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request; if inputs missing, run intake questions.
2. Select framework based on subject characteristics.
3. Gather evidence (prefer Systematic Review > Meta-analysis > RCT/empirical > expert opinion).
4. Score each dimension with cited justification.
5. Build prioritized roadmap.
6. Run devil's-advocate quality gate; revise; present artifact.
- Error handling: missing data → state assumptions + confidence; tool failure → degrade to knowledge base and signal limitation.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: *Aquaculture* (Elsevier), *Aquacultural Engineering*, WOAH (OIE) Aquatic Animal Health Code, FAO aquaculture technical papers.
- API providers: PubMed E-utilities, Crossref REST API, Semantic Scholar Graph API, arXiv API.
- Crawl queries: dissolved oxygen shrimp pond management, un-ionized ammonia toxicity fish, biofloc water quality optimization, RAS nitrification biosecurity, pond carrying capacity stocking density, nitrite toxicity aquaculture chloride, pH alkalinity stability aquaculture.
- Append format: dated entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance.
- Dedup: DOI/URL hash check before append.
- Run: `python tools/knowledge_updater.py --dry-run` to preview; `python tools/knowledge_updater.py` to append.

## Supporting Tools Spec — `knowledge_updater.py`
- Inputs: source list + query list (above), `--since` date, `--providers` list.
- Outputs: appended, de-duplicated entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- Schedule: weekly cron.

## Quality Gates (must be true before final output)
- [x] Framework selection justified
- [x] Every score cites a framework criterion or evidence source
- [x] Roadmap items have effort + impact + owner + expected effect
- [x] Assumptions and confidence stated; limitations disclosed
- [x] Devil's-advocate pass completed
- [x] Sources section lists every citation

## Test Scenarios (≥5)
1. **Shrimp pond low DO at dawn** — DO drops to 2.5 mg/L. Expect mortality-risk scoring and aeration/feeding-adjustment roadmap.
2. **Ammonia spike in RAS** — TAN high, pH 8.2, warm. Expect un-ionized ammonia calc and immediate mitigation steps.
3. **New tilapia farm setup** — User plans stocking density. Expect carrying-capacity reasoning and parameter targets.
4. **Disease outbreak biosecurity** — Sudden mortality. Expect WOAH-aligned biosecurity roadmap and diagnostic referral.
5. **Biofloc balance** — C:N ratio management. Expect floc-management guidance and monitoring schedule.

All scenarios are automated in `tests/test_scenarios.py` (`pytest tests/test_scenarios.py -v`; 7 tests, all passing).

## Key Design Decisions
1. Research-first; no memory-only claims when search is possible.
2. Named frameworks only — never ad hoc criteria.
3. Framework-selector adapts to subject; no one-size scoring.
4. Multi-dimensional score + prioritized roadmap are mandatory outputs.
5. Self-improving knowledge base via weekly API crawl.
6. Deterministic Python scoring/roadmap engines ensure reproducibility and enable automated regression tests.
