# CLAUDE.md — Skill 308: red-tide-algal-bloom-monitoring

## Skill Identity
- **Skill Name:** `red-tide-algal-bloom-monitoring`
- **Tagline:** Red Tide (Harmful Algal Bloom) Monitoring & Early Warning — Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety analysis & decision-support harness.
- **Current Phase:** Phase 5 — Integration & Polish (v2.0.0 Production Ready)
- **Folder:** `D:\972026\308-red-tide-algal-bloom-monitoring\`
- **Version:** 2.0.0

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety**. It gathers authoritative real-time and reference data, applies
recognized domain methods, cross-references academic research, and delivers
actionable outputs that are fully evidenced, risk/limitation-disclosed, and
traceable to authoritative sources — continuously self-improving through an
automated knowledge crawl pipeline.

---

## Harness Flow Summary

```
/red-tide-algal-bloom-monitoring invoked
│
├─ Step 1: sub-gather-requirements   → Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
├─ Step 2: sub-evidence-collector   → Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources.
├─ Step 3: sub-core-analysis   → Monitor red tide (harmful algal blooms) and issue early warnings: satellite + in-situ detection, environmental triggers, toxin risk, and aquaculture alerts.
├─ Step 4: sub-knowledge-updater   → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
├─ Step 5: sub-advisor   → Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions.
└─ Step 6: main (quality gate)       → verify evidence hierarchy, disclosure, output polish
```

---

## Sub-Skills

| `skills/sub-gather-requirements.md` | Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching. |
| `skills/sub-evidence-collector.md` | Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources. |
| `skills/sub-core-analysis.md` | Monitor red tide (harmful algal blooms) and issue early warnings: satellite + in-situ detection, environmental triggers, toxin risk, and aquaculture alerts. |
| `skills/sub-knowledge-updater.md` | Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline. |
| `skills/sub-advisor.md` | Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions. |

---

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety authoritative sources
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness

---

## Knowledge Sources

### Domain Authoritative Sources
- IOC-UNESCO HAB references
- NOAA HAB-OFS references
- Copernicus satellite (Sentinel-3 OLCI) references
- Phytoplankton/toxin references (WOAH)
- Aquaculture safety references
- Sensor (chl-a fluorometer) references

### Academic & Research Sources
- Harmful Algae — Elsevier
- Remote Sensing of Environment — Elsevier
- Aquaculture — Elsevier
- Toxicon — Elsevier
- Remote Sensing (MDPI)
- Estuarine, Coastal and Shelf Science — Elsevier

### Academic Crawl Targets
- Semantic Scholar / Google Scholar for "Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety" keyword clusters
- Domain preprint servers where applicable
- Standards bodies and professional associations (see data sources)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | Crawl pipeline: fetches latest papers + news → appends to SECOND-KNOWLEDGE-BRAIN.md |

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM)
0 8 * * 1 python D:/972026/308-red-tide-algal-bloom-monitoring/tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM)
0 7 * * * python D:/972026/308-red-tide-algal-bloom-monitoring/tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
```

Manual: `python tools/knowledge_updater.py --dry-run` | `--keywords "..."` | `--news-only`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (this file, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills (production-grade)
- [x] Phase 2: Main harness + quality gates + degradation
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation (all validators pass)
- [x] Phase 5: Integration & polish (PRODUCTION READY v1.0.0)

---

## References

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `D:\972026\SKILL-STANDARD.md` — library-wide standard
- Reference impl: `D:\vn-finance-analysis-hd-skill`
