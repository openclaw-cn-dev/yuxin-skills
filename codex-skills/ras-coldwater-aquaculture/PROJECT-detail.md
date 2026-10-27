# PROJECT-detail.md — Skill 161: ras-coldwater-aquaculture

## Executive Summary

`ras-coldwater-aquaculture` is a professional-grade harness for Claude Code targeting the
**Recirculating Aquaculture Systems & Cold-Water Fish Health Management** domain. It transforms Claude into a domain-expert that delivers
structured, evidence-backed outputs by combining real-time data aggregation,
recognized domain methods, and academic research into a single orchestrated
workflow ending in a risk/limitation-disclosed recommendation.

---

## Problem Statement

Practitioners in this domain face three structural gaps:
1. **Data fragmentation**: authoritative data scattered across sources.
2. **Methodology gaps**: most advice lacks systematic, evidence-graded methods.
3. **No self-improvement**: static tools don't learn from new research.

This skill addresses all three via real-time aggregation, professional
frameworks, and a continuously-updated knowledge crawl pipeline.

---

## Target Users & Use Cases

| User | Trigger Example | Skill Response |
|------|----------------|----------------|
| Practitioner | "Analyze Recirculating Aquaculture Systems & Cold-Water Fish Health Management case X" | Full evidenced report |
| Researcher | "What methods apply to Y?" | Method-grounded guidance with citations |
| Decision-maker | "Assess risk/feasibility of Z" | Risk-disclosed assessment with scenarios |
| Learner | "Explain method M in this domain" | Educational framing with evidence |

---

## Harness Architecture

```
USER INPUT
    │
    ▼
[main.md — ras-coldwater-aquaculture]
    │
    ├─► sub-gather-requirements.md  → Clarify the cold-water species and life stage, RAS configuration (tank volume, make-up water, biofilter type/area/flow), current water-quality readings (T, DO, pH, TAN, NO2, NO3, alkalinity, CO2), feeding/biomass load, and language before any analysis.
    ├─► sub-evidence-collector.md  → Fetch authoritative species-specific water-quality envelopes, biofilter nitrification parameters, and current disease-risk references for the species and life stage.
    ├─► sub-water-quality-analysis.md  → Compute derived water-quality metrics from raw readings and quantify deviations from the species envelope: un-ionized ammonia NH3 (from T+pH), DO % saturation (vs T), nitrification status, alkalinity demand, CO2 accumulation.
    ├─► sub-biofilter-disease-assessment.md  → Assess biofilter loading/performance and disease early-warning risk: biofilter surface-area adequacy, nitrification capacity vs feeding load, cold-water nitrification penalty, and match conditions against emerging-disease signals and advanced biofiltration/treatment remedies.
    ├─► sub-knowledge-updater.md  → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative RAS, water-chemistry, biofiltration, and disease evidence; surface tiered citations and flag gaps for the crawl pipeline.
    ├─► sub-ras-advisor.md  → Synthesize all prior analysis into a risk-disclosed verdict: system status, early-warning alerts, automated water-treatment procedure, and full evidence chain.

    └─► [QUALITY GATE — main.md]
            ✓ Claims cited to sources
            ✓ Disclosure included
            ✓ Evidence hierarchy respected
            ✓ Output formatted per template
```

---

## v2.0 Architecture (Skill-Registry Engine)

The reference harness above is the **prompt layer**. v2.0 adds a modular,
registry-based Python engine (`src/ras_aqua/`) that executes the same 6-step
pipeline deterministically with real domain computation and graceful LLM-free
fallback. Flexible agent architecture:

- **Chain-of-thought router** (`router.py`): pre-flight language detection,
  intent classification, plan selection, token-budget enforcement.
- **Skill registry** (`registry.py` + `skills/`): declarative `SkillSpec`
  registration, DAG validation, ordered execution, retry + degradation.
- **Tool registry** (`tools.py`): rich tool definitions (JSON-schema input +
  validated handler) ? `compute_nh3`, `compute_do_saturation`,
  `compute_tan_production`, `compute_biofilter_capacity`,
  `match_disease_signals`, `query_knowledge_base`.
- **Lifecycle hooks** (`hooks.py`): `pre/post skill/engine/gate/error/
  degradation` events for state sync, metrics, audit.
- **Type-safe config** (`config/`): env-driven `Settings`/`FeatureFlags` +
  `species_envelopes.json` + `feature_flags.json`.
- **Modular dirs**: `references/` (prompt templates + guidelines),
  `assets/` (JSON schemas + diagram), `scripts/` (setup/pipeline/ingest/seed).
- **Quality gates** (`gates.py`): U1-U6 + G1-G5 with auto-fix + 2-retry.
- **Structured logging** (`logging_config.py`): JSON events to stderr; clean
  JSON report on stdout.

Input/output JSON schemas live in `assets/schemas/` (`requirements`,
`water_quality_scorecard`, `biofilter_risk`, `verdict`). See `SKILL.md` for the
canonical skill-registry documentation.

---

## Full Sub-Skill Catalog

### 1. `sub-gather-requirements.md`
- **Purpose:** Clarify the cold-water species and life stage, RAS configuration (tank volume, make-up water, biofilter type/area/flow), current water-quality readings (T, DO, pH, TAN, NO2, NO3, alkalinity, CO2), feeding/biomass load, and language before any analysis.
- **Role:** intake specialist for a cold-water RAS facility
- **Inputs:** Raw user message + any attached water-quality logs/CSV, system schematic, stocking/biomass data.
- **Outputs:** Structured requirements: {species, life_stage, ras_config {tank_volume, makeup_pct, biofilter_type, biofilter_area, flow_lpm}, wq {T_C, DO_mgL, pH, TAN_mgL, NO2_mgL, NO3_mgL, alkalinity_mgL, CO2_mgL}, biomass_kg, feed_kg_day, target_objective, language}.
- **Tools:** - Conversation only (no external tools)
- **Quality Gate:** Cold-water species confirmed and at least T + DO + pH + TAN readings present before proceeding.

### 2. `sub-evidence-collector.md`
- **Purpose:** Fetch authoritative species-specific water-quality envelopes, biofilter nitrification parameters, and current disease-risk references for the species and life stage.
- **Role:** cold-water aquaculture data librarian
- **Inputs:** Requirements object from Step 1 (species, life stage).
- **Outputs:** Evidence bundle: {wq_envelopes by stage, nh3_safe_threshold, do_floor, biofilter_params, disease_references, recent_research}.
- **Tools:** - WebSearch, WebFetch (FAO, DFO, Freshwater Institute, SRAC, WOAH, USDA APHIS)
- Read (SECOND-KNOWLEDGE-BRAIN.md for cached envelopes)
- **Quality Gate:** Optimal T/DO/pH/TAN envelopes and species NH3 safe threshold retrieved, or a limitation flag.

### 3. `sub-water-quality-analysis.md`
- **Purpose:** Compute derived water-quality metrics from raw readings and quantify deviations from the species envelope: un-ionized ammonia NH3 (from T+pH), DO % saturation (vs T), nitrification status, alkalinity demand, CO2 accumulation.
- **Role:** RAS water-quality physiologist
- **Inputs:** Water-quality readings (Step 1) + species envelopes (Step 2).
- **Outputs:** Water-quality scorecard: {nh3_mgL, nh3_status, do_sat_pct, do_status, nitrification_status, alkalinity_status, co2_status, deviations[], trend, data_quality_flags}.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md physicochemistry formulas)
- Arithmetic / chemical-equilibrium calculation
- **Quality Gate:** NH3 computed from T+pH with the stated formula and units (mg/L NH3-N); DO reported as % saturation vs temperature; both compared to the species envelope.

### 4. `sub-biofilter-disease-assessment.md`
- **Purpose:** Assess biofilter loading/performance and disease early-warning risk: biofilter surface-area adequacy, nitrification capacity vs feeding load, cold-water nitrification penalty, and match conditions against emerging-disease signals and advanced biofiltration/treatment remedies.
- **Role:** RAS biofilter & fish-health risk analyst
- **Inputs:** Water-quality scorecard (Step 3) + RAS config + biomass/feed (Step 1) + disease references (Step 2).
- **Outputs:** Risk assessment: {biofilter_capacity_status, loading_ratio, nitrification_penalty, disease_early_warning[], recommended_treatments, advanced_biofiltration_options}.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md biofilter & disease sections)
- Reasoning over the evidence bundle
- **Quality Gate:** Biofilter capacity estimated with cold-temperature derating; disease signals matched to specific conditions; treatments recommended with rationale.

### 5. `sub-knowledge-updater.md`
- **Purpose:** Query SECOND-KNOWLEDGE-BRAIN.md for authoritative RAS, water-chemistry, biofiltration, and disease evidence; surface tiered citations and flag gaps for the crawl pipeline.
- **Role:** research librarian for RAS engineering & aquatic health
- **Inputs:** Topic keywords from the current analysis (e.g. 'un-ionized ammonia trout', 'RAS biofilter cold nitrification', 'VHS salmonid').
- **Outputs:** 3-5 knowledge-base citations with Tier labels + flagged knowledge gaps.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md)
- WebSearch (gap-fill, max 2 queries)
- **Quality Gate:** At least 1 academic/authoritative source surfaced; evidence coverage rating provided.

### 6. `sub-ras-advisor.md`
- **Purpose:** Synthesize all prior analysis into a risk-disclosed verdict: system status, early-warning alerts, automated water-treatment procedure, and full evidence chain.
- **Role:** senior cold-water RAS operations advisor
- **Inputs:** Water-quality scorecard, biofilter/disease risk assessment, evidence bundle, knowledge-base evidence.
- **Outputs:** Verdict (one of 4 categories) + early-warning alerts + water-treatment procedure + key risks + evidence chain + remediation + mandatory disclosure.
- **Tools:** - Reasoning / synthesis
- Skill('sub-knowledge-updater') optional
- **Quality Gate:** Verdict is exactly one of the 4 declared categories; disclosure appears before the verdict.


---

## Skill File Format Specification

```markdown
---
name: {skill-name}
description: {one-line summary}
---
## Role & Persona
## Workflow (Harness Flow)
## Sub-skills Available   (main.md only)
## Tools
## Output Format
## Quality Gates
```

---

## E2E Execution Flow

```
1. User invokes /ras-coldwater-aquaculture [query]
2. main.md → sub-gather-requirements → structured requirements
3. sub-evidence-collector → data bundle
4. core analysis sub-skills → scorecard / signal set
5. sub-knowledge-updater → academic evidence entries
6. sub-advisor/synthesizer → final draft
7. main.md Quality Gate → verify, auto-fix, deliver
```

**Error handling:** primary sources fail → fallback chain → knowledge base →
explicit limitation flag; never silently proceed with stale data.

---

## SECOND-KNOWLEDGE-BRAIN Integration

- **Sources crawled:** academic databases + domain RSS + standards docs
- **Crawl config:** `KNOWLEDGE_CONFIG` in `tools/knowledge_updater.py`
- **Dedup:** SHA256 of DOI/URL
- **Scoring:** recency + keyword relevance + citation count

---

## Quality Gates Definition

Universal gates U1–U6 (see library SKILL-STANDARD.md) plus the domain gates
defined in `skills/main.md`: G1, G2, G3, G4, G5

---

## Test Scenarios

See `tests/test-scenarios.md` for 5+ concrete scenario tests.

---

## Key Design Decisions

1. Domain sub-skills kept separate (distinct methods/data).
2. Authoritative domain sources as primary; global fallback secondary.
3. Disclosure enforced at the quality-gate level, not optional.
4. SECOND-KNOWLEDGE-BRAIN as living memory updated by crawl pipeline.
5. Graceful degradation to knowledge base with explicit limitation flags.

---

## Idea (Vietnamese)

> Tạo skill thiết kế và vận hành hệ thống nuôi trồng thủy sản tuần hoàn (RAS) cho các loài thủy sản nước lạnh, liên tục crawl dữ liệu về các chỉ số hóa lý của nước, dịch bệnh thủy sản mới và các giải pháp lọc sinh học tiên tiến để đưa ra cảnh báo sớm và quy trình xử lí nước tự động.
