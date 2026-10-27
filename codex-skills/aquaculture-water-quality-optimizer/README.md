# 🌊 Aquaculture Water Quality & Environment Optimizer

> A production-grade Claude skill that turns LLM reasoning into **an aquaculture systems specialist** — reading water-chemistry and stocking data the way a fisheries scientist and farm manager would.

[![Status](https://img.shields.io/badge/status-production--ready-success)](./PROJECT-DEVELOPMENT-PHASE-TRACKING.md)
[![Tests](https://img.shields.io/badge/tests-7%20passed-success)](./tests/test_scenarios.py)
[![Phase](https://img.shields.io/badge/phases-0--5%20done-success)](./PROJECT-DEVELOPMENT-PHASE-TRACKING.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## 🎯 Why This Exists

Fish and shrimp farmers lose crops every year because water-quality failures cascade fast:

- **Dawn DO crash** → mass mortality in hours
- **Ammonia spike** → acute toxicity amplified by high pH / warm temperature
- **Biofloc imbalance** → C:N drift, TSS overload, anoxic zones
- **Disease outbreak** → biosecurity gaps spread pathogens between ponds or RAS units
- **New farm setup** → carrying capacity, monitoring protocols, and emergency systems are under-designed

This skill provides a **research-first, reproducible, framework-grounded evaluation** rather than ad-hoc opinion. It scores the system across five dimensions, cites named world-renowned frameworks, and produces a prioritized improvement roadmap.

---

## 🧠 What It Does

```
User input (species, system, water params, biosecurity flags)
        ↓
[1] Intake → canonical IntakeProfile (tools/schemas.py)
        ↓
[2] Framework selection → named species/system envelope (tools/frameworks.py)
        ↓
[3] Evidence gathering → WebSearch/WebFetch or SECOND-KNOWLEDGE-BRAIN.md fallback
        ↓
[4] Scoring engine → 0-100 across 5 dimensions (tools/scoring_engine.py)
        ↓
[5] Roadmap engine → prioritized actions by mortality-risk urgency (tools/roadmap_engine.py)
        ↓
[6] Devil's advocate → challenge assumptions, revise, present final artifact
```

### The Five Dimensions

| Dimension | Default Weight | What It Measures |
|-----------|----------------|------------------|
| 🫁 **Oxygen status** | 25% | DO vs species-specific threshold; percent saturation when available |
| ☠️ **Nitrogen toxicity risk** | 25% | TAN, un-ionized NH₃ (Emerson equilibrium), NO₂ |
| 🧪 **pH/alkalinity stability** | 20% | pH and alkalinity within optimal/stress bands |
| 🌡️ **Temperature/salinity fit** | 15% | Temperature and salinity species envelope fit |
| 🛡️ **Biosecurity** | 15% | WOAH-aligned risk flags and positive controls |

---

## 📁 Repository Layout

```
.
├── skills/
│   ├── main.md                      # Main harness flow
│   ├── sub-profile-intake.md        # Intake sub-skill
│   ├── sub-framework-selector.md    # Framework selection sub-skill
│   ├── sub-scoring-engine.md        # Scoring sub-skill
│   └── sub-improvement-roadmap.md   # Roadmap sub-skill
├── tools/
│   ├── schemas.py                   # Pydantic data models
│   ├── frameworks.py                # Citable framework envelopes
│   ├── scoring_engine.py            # Deterministic scoring engine
│   ├── roadmap_engine.py            # Urgency-ranked roadmap generator
│   └── knowledge_updater.py         # Scholarly API crawler
├── tests/
│   ├── test-scenarios.md            # Manual scenario definitions
│   └── test_scenarios.py            # Automated pytest harness
├── SECOND-KNOWLEDGE-BRAIN.md        # Living knowledge base
├── PROJECT-detail.md                # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # Phase roadmap (100% done)
├── CLAUDE.md                        # Claude skill identity
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the automated scenario regression

```bash
pytest tests/test_scenarios.py -v
```

Expected output:

```text
============================== 7 passed in 0.08s ===============================
```

### 3. Preview a live knowledge update (dry-run, no writes)

```bash
python tools/knowledge_updater.py --dry-run --max-per-query 5
```

### 4. Use the Python scoring engine directly

```python
from schemas import IntakeProfile, StockingInfo, WaterParameters, BiosecurityFlags, SystemType
from frameworks import select_framework
from scoring_engine import compute_score
from roadmap_engine import build_roadmap

profile = IntakeProfile(
    stocking=StockingInfo(species="whiteleg shrimp", system_type=SystemType.POND),
    water=WaterParameters(
        do_mg_l=2.5,
        tan_mg_l=2.0,
        ph=8.2,
        temp_c=30.0,
        salinity_ppt=15.0,
    ),
    biosecurity=BiosecurityFlags(recent_mortality=True),
)

framework = select_framework(profile.stocking.species, profile.stocking.system_type)
score = compute_score(profile, framework)
roadmap = build_roadmap(profile, score, framework)

print(f"Framework: {framework.name}")
print(f"Composite score: {score.composite}")
for d in score.dimensions:
    print(f"  {d.dimension}: {d.value} — {d.justification[:60]}...")
for item in roadmap.items[:3]:
    print(f"#{item.rank}: {item.action} [{item.effort} effort | {item.impact} impact]")
```

---

## 📚 Frameworks We Ground On

Every score is tied to a named, citable framework:

| Framework | Source | Use Case |
|-----------|--------|----------|
| **Warm-water finfish pond** | Boyd & Tucker (1998); Boyd (2020) | Tilapia, carp, catfish in ponds |
| **Penaeid shrimp pond** | Boyd & Tucker (1998); FAO; Avnimelech (2012) | *Litopenaeus vannamei*, *Penaeus monodon* |
| **RAS high-value finfish** | Timmons & Guerdat (2017); Malone & Pfeiffer (2006) | Salmon, trout, yellowtail in RAS |
| **Biofloc Technology** | Avnimelech (2012); Emerenciano et al. (2017) | BFT shrimp/tilapia |
| **Flow-through / cage freshwater** | Boyd (2020); Wedemeyer (1996) | Open-water / flow-through finfish |

### Key scientific formulas

- **Un-ionized ammonia (NH₃)** — Emerson et al. (1975):
  ```
  pKa = 0.09018 + 2729.92 / T(K)
  fraction_NH3 = 1 / (10^(pKa - pH) + 1)
  NH3 = TAN × fraction_NH3
  ```
- **DO percent saturation** — Weiss (1970) seawater solubility polynomial.

---

## 🧪 Validated Scenarios

| # | Scenario | Key Expectation |
|---|----------|-----------------|
| 1 | Shrimp pond low DO at dawn | Aeration + feeding reduction top the roadmap |
| 2 | Ammonia spike in RAS | Un-ionized NH₃ calculated; biofilter / feed actions top the roadmap |
| 3 | New tilapia farm setup | Carrying-capacity reasoning and preventive monitoring schedule |
| 4 | Disease outbreak biosecurity | WOAH-aligned diagnostic + quarantine top the roadmap |
| 5 | Biofloc C:N imbalance | Carbon-source addition and floc-thinning actions |

All five scenarios are covered by automated tests in `tests/test_scenarios.py`.

---

## 🔄 Self-Improving Knowledge Base

`SECOND-KNOWLEDGE-BRAIN.md` is a living markdown knowledge base. It is refreshed weekly by `tools/knowledge_updater.py`, which queries:

- **PubMed E-utilities** — peer-reviewed biomedical/aquaculture literature
- **Crossref REST API** — publisher DOI metadata
- **Semantic Scholar Graph API** — open-access PDF links and abstracts
- **arXiv API** — relevant preprints (ML/modeling for aquaculture)

The crawler:
- deduplicates by DOI/URL hash
- scores entries by recency + domain relevance
- appends dated crawl sections
- degrades gracefully if any provider is unavailable

Run a dry-run to preview candidates without writing:

```bash
python tools/knowledge_updater.py --dry-run --providers pubmed crossref --since 2023-01-01
```

---

## 🛡️ Quality Gates

Before any final output, the harness enforces:

- [x] Framework selection justified to the user
- [x] Every dimension score cites a framework criterion or evidence source
- [x] Un-ionized NH₃ is computed when TAN + pH + temp are present
- [x] Roadmap items include effort, impact, rationale, owner, and expected effect
- [x] Monitoring schedule is included
- [x] Stopgap note appears when composite score < 50
- [x] Assumptions, confidence, and limitations are stated
- [x] Devil's-advocate review is completed
- [x] Sources section lists every citation

---

## 🌱 Design Philosophy

1. **Research-first** — no memory-only claims when search is possible.
2. **Named frameworks only** — never ad-hoc criteria.
3. **Adaptive framework selection** — species and system drive the envelope, not a one-size score.
4. **Multi-dimensional score + prioritized roadmap** — mandatory outputs.
5. **Self-improving knowledge base** — weekly scholarly API crawl.
6. **Deterministic, tested engines** — reproducible scoring and automated regression.

---

## 🧰 Tech Stack

- **Pydantic v2** — type-safe schemas and validation
- **Python 3.11+** — deterministic scoring/roadmap engines
- **pytest** — automated regression
- **aiohttp** — async scholarly API calls
- **crawl4ai** — optional web crawling (API-first design preferred)

---

## 📜 License

MIT — see [LICENSE](./LICENSE) for details.

---

## 🤝 Contributing

This skill is designed for the **Science, Engineering & Industry** cluster. Contributions that:

- add new species/system frameworks with cited envelopes
- improve scoring formulas
- expand test coverage
- add new scholarly API providers

are welcome. Please keep all criteria tied to named, citable sources.

---

## 🙏 Acknowledgments

This skill stands on the shoulders of decades of aquaculture science. Canonical references include:

- Boyd, C.E. & Tucker, C.S. (1998). *Pond Aquaculture Water Quality Management*.
- Boyd, C.E. (2020). *Water Quality: An Introduction*.
- Timmons, M.B. & Guerdat, T. (2017). *Recirculating Aquaculture*.
- Avnimelech, Y. (2012). *Biofloc Technology — A Practical Guide Book*.
- Emerson, K. et al. (1975). Aqueous ammonia equilibrium calculations. *J Fish Res Board Can* 32:2379-2383.
- WOAH (2024). *Aquatic Animal Health Code*.

---

<div align="center">

**[📖 Documentation](./PROJECT-detail.md) · [✅ Tracking](./PROJECT-DEVELOPMENT-PHASE-TRACKING.md) · [🧪 Tests](./tests/test_scenarios.py) · [🧠 Knowledge](./SECOND-KNOWLEDGE-BRAIN.md)**

</div>
