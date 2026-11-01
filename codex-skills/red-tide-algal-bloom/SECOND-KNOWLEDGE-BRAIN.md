# SECOND-KNOWLEDGE-BRAIN.md — Skill 308: red-tide-algal-bloom-monitoring

> **Living Knowledge Base** — updated by `tools/knowledge_updater.py` on a weekly
> schedule. All entries date-stamped; new entries appended at the bottom.
> Evidence hierarchy: Systematic Review > Meta-Analysis > Guideline/RCT > Cohort > Expert Consensus > News.

---

## 1. Core Concepts & Frameworks

### 1.1 Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety — Foundational Methods

### 1.1 Species/toxins
Karenia/Dinophysis/Alexandrium; toxins (paralytic/diarrhetic shellfish poisoning); bioaccumulation in shellfish.
### 1.2 Detection
Sentinel-3 OLCI chlorophyll-a, SST, turbidity; in-situ fluorometer, microscopy, qPCR; thresholds.
### 1.3 Triggers
Temperature, nutrients (N/P/Si), upwelling, stratification, salinity; bloom initiation models.
### 1.4 Alerts/mitigation
Aquaculture & public health alert thresholds, harvest closure, toxin monitoring, mitigation (clay flocculation, water exchange).

Knowledge categories covered:
- HAB species & toxins (paralytic, diarrhetic)
- Satellite chl-a & SST detection
- In-situ sensors (fluorometer, nutrients)
- Environmental triggers (T, nutrients, upwelling)
- Aquaculture & health alert thresholds
- Response & mitigation

### 1.2 Evidence Hierarchy (this domain)
- **Tier 1**: Systematic review / meta-analysis / official standard (ISO, IAWA, CITES, FSC, WHO, UNESCO…)
- **Tier 2**: Peer-reviewed academic paper / RCT
- **Tier 3**: Industry report / professional association guideline
- **Tier 4**: News / blog / vendor material

---

## 2. Key Research Papers & Standards

| Title | Authors | Year | Venue | DOI/URL | Tier |
|------|---------|------|-------|---------|------|
| HAB remote sensing review | Blondeau-Patissier et al. | 2014 | Remote Sens. Environ. | 10.1016/j.rse.2013.10.027? | 1 |
| Does gamification work? | Hamari et al. | 2014 | Comput. Hum. Behav. | 10.1016/j.chb.2014.03.006 | 2 |
| HAB monitoring & forecasting | Stumpf et al. | 2003 | Oceanography | 10.5670/oceanog.2003.30 | 1 |
| IOC HAB references | IOC-UNESCO | current | IOC | ioc-unesco.org/hab | 1 |

Authoritative sources registered:
- Harmful Algae — Elsevier
- Remote Sensing of Environment — Elsevier
- Aquaculture — Elsevier
- Toxicon — Elsevier
- Remote Sensing (MDPI)
- Estuarine, Coastal and Shelf Science — Elsevier

---

## 3. State-of-the-Art Methods & Tools

State of the art: satellite chl-a + ML bloom prediction, autonomous gliders/fluorometers, qPCR toxin assays, multi-sensor fusion, aquaculture alert dashboards. Crawl targets: Harmful Algae, Remote Sens. Environ., Aquac., Toxicon, Remote Sens., Estuar. Coast. Shelf Sci.

---

## 4. Authoritative Data Sources

### 4.1 Domain authoritative sources
- IOC-UNESCO HAB references
- NOAA HAB-OFS references
- Copernicus satellite (Sentinel-3 OLCI) references
- Phytoplankton/toxin references (WOAH)
- Aquaculture safety references
- Sensor (chl-a fluorometer) references

### 4.2 Academic & research sources
- Harmful Algae — Elsevier
- Remote Sensing of Environment — Elsevier
- Aquaculture — Elsevier
- Toxicon — Elsevier
- Remote Sensing (MDPI)
- Estuarine, Coastal and Shelf Science — Elsevier

---

## 5. Analytical Frameworks

Knowledge categories covered:
- HAB species & toxins (paralytic, diarrhetic)
- Satellite chl-a & SST detection
- In-situ sensors (fluorometer, nutrients)
- Environmental triggers (T, nutrients, upwelling)
- Aquaculture & health alert thresholds
- Response & mitigation

Cross-reference the sub-skill workflows in `skills/*.md` for the domain methods applied at each step. The fixed bookends (requirements â†’ evidence â†’ knowledge â†’ synthesis â†’ quality gate) are mandatory; the core analysis sub-skills implement the domain-specific methods.

---

## 6. Self-Update Protocol

- **Crawl pipeline:** `tools/knowledge_updater.py`
- **Schedule:** weekly academic (Mondays 08:00) + daily news (07:00); documented in `CLAUDE.md`
- **Dedup:** SHA256 of DOI/URL (case/whitespace-insensitive)
- **Scoring:** composite 0â€“10 = recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)
- **Crawl targets:** ArXiv categories []; Semantic Scholar keyword clusters; RSS feeds []
- **Gap-fill:** sub-knowledge-updater flags missing values as crawl queries
- **Append rule:** new entries appended under Section 7 with date stamp + relevance score

---

## 7. Knowledge Update Log

_(Appended automatically by the crawl pipeline. Baseline seeded with the references in Section 2.)_
