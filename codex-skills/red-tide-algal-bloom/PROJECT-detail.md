# PROJECT-detail.md — Skill 308: red-tide-algal-bloom-monitoring

## Executive Summary

`red-tide-algal-bloom-monitoring` is a professional-grade harness for Claude Code targeting the
**Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety** domain. It transforms Claude into a domain-expert that delivers
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
| Practitioner | "Analyze Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety case X" | Full evidenced report |
| Researcher | "What methods apply to Y?" | Method-grounded guidance with citations |
| Decision-maker | "Assess risk/feasibility of Z" | Risk-disclosed assessment with scenarios |
| Learner | "Explain method M in this domain" | Educational framing with evidence |

---

## Harness Architecture

```
USER INPUT
    │
    ▼
[main.md — red-tide-algal-bloom-monitoring]
    │
    ├─► sub-gather-requirements.md  → Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
    ├─► sub-evidence-collector.md  → Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources.
    ├─► sub-core-analysis.md  → Monitor red tide (harmful algal blooms) and issue early warnings: satellite + in-situ detection, environmental triggers, toxin risk, and aquaculture alerts.
    ├─► sub-knowledge-updater.md  → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
    ├─► sub-advisor.md  → Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions.

    └─► [QUALITY GATE — main.md]
            ✓ Claims cited to sources
            ✓ Disclosure included
            ✓ Evidence hierarchy respected
            ✓ Output formatted per template
```

---

## Full Sub-Skill Catalog

### 1. `sub-gather-requirements.md`
- **Purpose:** Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
- **Role:** intake specialist for a Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety engagement
- **Inputs:** Raw user message + any provided materials/inputs.
- **Outputs:** Structured requirements: {object, scope, timeframe, available_inputs, target_audience, language, analysis_type}.
- **Tools:** - Conversation only (no external tools)
- **Quality Gate:** At least one object of analysis confirmed before proceeding.

### 2. `sub-evidence-collector.md`
- **Purpose:** Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources.
- **Role:** Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety data librarian
- **Inputs:** Requirements object from Step 1.
- **Outputs:** Evidence bundle: {current_data, authoritative_docs, recent_news, reference_benchmarks} with source + date per item.
- **Tools:** - WebSearch, WebFetch (domain + academic sources)
- Read (SECOND-KNOWLEDGE-BRAIN.md for cached benchmarks)
- **Quality Gate:** At least current data + 1 authoritative document retrieved, or a limitation flag if unavailable.

### 3. `sub-core-analysis.md`
- **Purpose:** Monitor red tide (harmful algal blooms) and issue early warnings: satellite + in-situ detection, environmental triggers, toxin risk, and aquaculture alerts.
- **Role:** HAB monitoring & aquaculture-safety analyst
- **Inputs:** Region, satellite, sensor data, aquaculture, language.
- **Outputs:** Detection + triggers + toxin + alerts + mitigation + scenarios.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md)
- WebFetch (IOC-UNESCO, NOAA, Copernicus)
- Reasoning / remote sensing
- **Quality Gate:** Bloom detected (satellite+in-situ); triggers analyzed; toxin risk; alert thresholds.

### 4. `sub-knowledge-updater.md`
- **Purpose:** Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
- **Role:** research librarian for Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety
- **Inputs:** Topic keywords from the current analysis.
- **Outputs:** 3-5 knowledge-base citations with Tier labels + flagged gaps.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md)
- WebSearch (gap-fill, max 2 queries)
- **Quality Gate:** At least 1 academic/authoritative source surfaced; coverage rating provided.

### 5. `sub-advisor.md`
- **Purpose:** Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions.
- **Role:** senior Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety advisor
- **Inputs:** Core analysis scorecard + evidence bundle + knowledge-base evidence.
- **Outputs:** Conclusion (one of N declared categories) + scenarios + key risks + evidence chain + remediation + mandatory disclosure.
- **Tools:** - Reasoning / synthesis
- Skill('sub-knowledge-updater') optional
- **Quality Gate:** Conclusion is exactly one of: Low Risk / Normal / Monitor (elevated) / Critical Bloom Alert / Inconclusive; disclosure appears before the conclusion.


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
1. User invokes /red-tide-algal-bloom-monitoring [query]
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
defined in `skills/main.md`: G1, G2, G3, G4

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

> Tạo Agent "Trợ lý Giám sát và Cảnh báo Hiện tượng Tảo nở hoa (Thủy triều đỏ) tại các vùng nuôi biển", tự động phân tích dữ liệu nhiệt độ nước và nồng độ chlorophyll qua ảnh vệ tinh, đưa ra các đề xuất ứng phó khẩn cấp dựa trên các phương pháp đánh giá uy tín trên thế giới và đưa ra các đề xuất, giải pháp cải tiến, không ngừng đi crawl data từ các nghiên cứu hải dương học sinh học hoặc document uy tín liên quan để cập nhật kiến thức cho Agent ngày càng tốt hơn, xu hướng hơn.
