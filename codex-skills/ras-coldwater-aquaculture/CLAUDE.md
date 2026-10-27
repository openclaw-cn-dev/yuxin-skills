# CLAUDE.md — Skill 161: ras-coldwater-aquaculture

## Skill Identity
- **Skill Name:** `ras-coldwater-aquaculture`
- **Tagline:** Cold-Water Recirculating Aquaculture System (RAS) Design & Operation — Recirculating Aquaculture Systems & Cold-Water Fish Health Management analysis & decision-support harness.
- **Current Phase:** Phase 5 — Integration & Polish (PRODUCTION READY)
- **Folder:** `D:\972026\161-ras-coldwater-aquaculture\`

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Recirculating Aquaculture Systems & Cold-Water Fish Health Management**. It gathers authoritative real-time and reference data, applies
recognized domain methods, cross-references academic research, and delivers
actionable outputs that are fully evidenced, risk/limitation-disclosed, and
traceable to authoritative sources — continuously self-improving through an
automated knowledge crawl pipeline.

---

## Harness Flow Summary

```
/ras-coldwater-aquaculture invoked
│
├─ Step 1: sub-gather-requirements   → Clarify the cold-water species and life stage, RAS configuration (tank volume, make-up water, biofilter type/area/flow), current water-quality readings (T, DO, pH, TAN, NO2, NO3, alkalinity, CO2), feeding/biomass load, and language before any analysis.
├─ Step 2: sub-evidence-collector   → Fetch authoritative species-specific water-quality envelopes, biofilter nitrification parameters, and current disease-risk references for the species and life stage.
├─ Step 3: sub-water-quality-analysis   → Compute derived water-quality metrics from raw readings and quantify deviations from the species envelope: un-ionized ammonia NH3 (from T+pH), DO % saturation (vs T), nitrification status, alkalinity demand, CO2 accumulation.
├─ Step 4: sub-biofilter-disease-assessment   → Assess biofilter loading/performance and disease early-warning risk: biofilter surface-area adequacy, nitrification capacity vs feeding load, cold-water nitrification penalty, and match conditions against emerging-disease signals and advanced biofiltration/treatment remedies.
├─ Step 5: sub-knowledge-updater   → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative RAS, water-chemistry, biofiltration, and disease evidence; surface tiered citations and flag gaps for the crawl pipeline.
├─ Step 6: sub-ras-advisor   → Synthesize all prior analysis into a risk-disclosed verdict: system status, early-warning alerts, automated water-treatment procedure, and full evidence chain.
└─ Step 7: main (quality gate)       → verify evidence hierarchy, disclosure, output polish
```

---

## Programmatic Engine (v2.0)

Alongside the markdown prompt layer, the project ships a production-grade,
registry-based Python engine in `src/ras_aqua/` that executes the same 6-step
pipeline deterministically (real chemistry, biofilter, disease computations)
and degrades gracefully without an LLM. Key modules:

| Module | Purpose |
|--------|---------|
| `engine.py` | Orchestrator: run -> EngineReport |
| `registry.py` / `skills/` | Skill registry + 6 concrete skill executors |
| `router.py` | Chain-of-thought router (intent + plan + token budget) |
| `hooks.py` | Lifecycle hook bus (pre/post skill/engine/gate/error) |
| `tools.py` | Tool registry (validated JSON-schema handlers) |
| `chemistry.py` / `biofilter.py` / `diseases.py` | Real domain computation |
| `species.py` | Species envelope registry + name normalization |
| `gates.py` | U1-U6 + G1-G5 quality gates with auto-fix |
| `config/`, `references/`, `assets/`, `scripts/` | Modular dirs |

See `SKILL.md` for the full skill-registry contract. Run it:

```bash
python scripts/setup_env.py                          # setup + smoke test
python scripts/run_pipeline.py --input req.json --pretty
python scripts/ingest_water_log.py --log water.csv --out req.json
```

## Sub-Skills

| `skills/sub-gather-requirements.md` | Clarify the cold-water species and life stage, RAS configuration (tank volume, make-up water, biofilter type/area/flow), current water-quality readings (T, DO, pH, TAN, NO2, NO3, alkalinity, CO2), feeding/biomass load, and language before any analysis. |
| `skills/sub-evidence-collector.md` | Fetch authoritative species-specific water-quality envelopes, biofilter nitrification parameters, and current disease-risk references for the species and life stage. |
| `skills/sub-water-quality-analysis.md` | Compute derived water-quality metrics from raw readings and quantify deviations from the species envelope: un-ionized ammonia NH3 (from T+pH), DO % saturation (vs T), nitrification status, alkalinity demand, CO2 accumulation. |
| `skills/sub-biofilter-disease-assessment.md` | Assess biofilter loading/performance and disease early-warning risk: biofilter surface-area adequacy, nitrification capacity vs feeding load, cold-water nitrification penalty, and match conditions against emerging-disease signals and advanced biofiltration/treatment remedies. |
| `skills/sub-knowledge-updater.md` | Query SECOND-KNOWLEDGE-BRAIN.md for authoritative RAS, water-chemistry, biofiltration, and disease evidence; surface tiered citations and flag gaps for the crawl pipeline. |
| `skills/sub-ras-advisor.md` | Synthesize all prior analysis into a risk-disclosed verdict: system status, early-warning alerts, automated water-treatment procedure, and full evidence chain. |

---

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Recirculating Aquaculture Systems & Cold-Water Fish Health Management authoritative sources
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness

---

## Knowledge Sources

### Domain Authoritative Sources
- FAO Aquaculture Department — fao.org/fishery (RAS & water-quality guidelines, cultured species factsheets)
- DFO Canada (Fisheries & Oceans) — dfo-mpo.gc.ca (cold-water salmonid/char culture)
- The Freshwater Institute (RAS research, biofilter & water reuse) — freshwaterinstitute.org
- SRAC / US Regional Aquaculture Centers — extension factsheets (water-quality tables)
- World Organisation for Animal Health (WOAH) — woah.org (Aquatic Animal Health Code & notifiable diseases)
- USDA APHIS Aquaculture — aphis.usda.gov (disease surveillance)
- US EPA — Water Quality Criteria (ammonia criteria for aquatic life)
- YSI / Xylem — ysi.com (DO, pH, conductivity sensor specs)
- Hach — hach.com (colorimetric NH3/NO2/NO3/alkalinity methods & sensor specs)
- NOAA Fisheries Aquaculture — fisheries.noaa.gov (aquaculture regulations & health)
- NIWA (NZ) — cold-water aquaculture references

### Academic & Research Sources
- Aquacultural Engineering — Elsevier (RAS design, biofilters, water treatment)
- Aquaculture — Elsevier (species physiology, water quality)
- Journal of the World Aquaculture Society — Wiley
- Fish & Shellfish Immunology — Elsevier (disease & immunology)
- Diseases of Aquatic Organisms — Inter-Research
- Reviews in Aquaculture — Wiley (reviews & meta-analyses)
- Water Research — Elsevier (biofiltration & nitrification)
- Semantic Scholar — 'recirculating aquaculture system', 'un-ionized ammonia fish', 'RAS biofilter nitrification', 'cold-water salmonid water quality'

### Academic Crawl Targets
- Semantic Scholar / Google Scholar for "Recirculating Aquaculture Systems & Cold-Water Fish Health Management" keyword clusters
- Domain preprint servers where applicable
- Standards bodies and professional associations (see data sources)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | Crawl pipeline: fetches latest papers + news, SHA256 dedup, composite scoring, atomic append to SECOND-KNOWLEDGE-BRAIN.md. `--dry-run` / `--news-only` / `--json`. |
| `tools/test_knowledge_updater.py` | Hermetic unit tests for hash, scoring, formatting, config validation, dedup (no network). |
| `tools/run_test_scenarios.py` | Structural & content validator (8-File Contract deliverables, gates, scenarios). `--all` / `--json` / `--quiet`. |
| `tools/validate_project.py` | 8-File Contract validator per `D:\972026\SKILL-STANDARD.md`. `--json` / `--quiet`. CI-safe. |

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM) - all logs via stdout redirect
0 8 * * 1 python D:/972026/161-ras-coldwater-aquaculture/tools/knowledge_updater.py --no-log-file >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM) - RSS only
0 7 * * * python D:/972026/161-ras-coldwater-aquaculture/tools/knowledge_updater.py --news-only --no-log-file >> logs/knowledge_news.log 2>&1
```

Manual: `python tools/knowledge_updater.py --dry-run` | `--news-only` | `--keywords "..."` | `--json` | `--no-log-file`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (this file, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills (production-grade)
- [x] Phase 2: Main harness + quality gates + degradation
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation (all validators pass)
- [x] Phase 5: Integration & polish (PRODUCTION READY v1.0.0)
- [x] Phase 6: Skill-registry engine + modular dirs + hooks/tools + SKILL.md (PRODUCTION READY v2.0.0)

---

## References

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `D:\972026\SKILL-STANDARD.md` — library-wide standard
- Reference impl: `D:\vn-finance-analysis-hd-skill`
