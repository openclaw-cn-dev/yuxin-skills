# SECOND-KNOWLEDGE-BRAIN.md — Skill 161: ras-coldwater-aquaculture

> **Living Knowledge Base** — updated by `tools/knowledge_updater.py` on a weekly
> schedule. All entries date-stamped; new entries appended at the bottom.
> Evidence hierarchy: Systematic Review > Meta-Analysis > Guideline/RCT > Cohort > Expert Consensus > News.

---

## 1. Core Concepts & Frameworks

### 1.1 Recirculating Aquaculture Systems & Cold-Water Fish Health Management — Foundational Methods

### 1.1 Water-quality physicochemistry
Un-ionized ammonia (Emerson et al. 1975): f = 1/(1+10^(pKa-pH)); pKa(T) = 0.09018 + 2727.92/T(K). NH3-N (mg/L) = TAN(mg/L) x f. NH3 is the toxic form; cold-water species are MORE sensitive (trout chronic threshold ~0.0125 mg/L NH3-N). DO saturation (Benson & Krause 1984 / APHA): DOsat(T) falls with T and salinity; report DO as mg/L AND % saturation. Nitrification: AOB (NH4+->NO2-) then NOB (NO2->NO3-); consumes ~7.14 mg CaCO3 alkalinity per mg TAN oxidized; optimal 25-30 C & pH 7.5-8.5; falls sharply <10-15 C (cold-water RAS biofilters must be oversized & seeded).

### 1.2 Cold-water species envelopes
Rainbow trout: T 10-16 C (lethal >~24 C), DO >6 mg/L (>80% sat), pH 6.5-8.5, NH3-N <0.0125 chronic, NO2-N <0.1. Atlantic salmon smolt: T 8-14 C, salinity transfer for smolts. Arctic char: T 6-12 C, very cold-tolerant. Sturgeon (Acipenser): T 14-18 C (juvenile), DO >6, ammonia-sensitive. All cold-water species are ammonia-sensitive compared to warm-water tilapia/catfish.

### 1.3 Biofilter engineering
TAN production ~30-40 g TAN per kg feed (protein-dependent). Biofilter capacity quoted as g TAN removed per m2 media surface per day. Derate for cold T (at 10 C, nitrification may be ~20-40% of 25 C rate). HRT, surface area, and DO (>4-5 mg/L in biofilter) must be sufficient. NO2 spike indicates NOB lag (new biofilter or cold shock).

### 1.4 Aquatic disease early-warning
WOAH notifiable aquatic diseases for cold-water salmonids: VHS, IPN, ISA, Gyrodactylosis, Saprolegniosis (fungal, stress-mediated), furunculosis (Aeromonas salmonicida). Stress (poor DO, high NH3/CO2, crowding) is the common trigger. Early-warning signals: reduced feeding, increased respiration, lethargy, lesions, gill damage.

### 1.5 Advanced water treatment
MBBR (moving-bed biofilm reactor), fixed-film, fluidized sand filters; denitrification for NO3; ozonation (toxic to fish - off-gas destruction & ORP control); UV for pathogens; CO2 strippers (packed columns, forced air); protein skimmers (marine); temp/flow adjustments; partial water exchange. Ammonia emergency: stop/reduce feeding, lower pH, increase aeration, water exchange.

### 1.6 Standards & reporting
FAO RAS guidelines; WOAH Aquatic Animal Health Code; APHA Standard Methods (water analysis); sensor metrology (YSI/Hach) with calibration; report T, DO mg/L + %sat, pH, TAN, NH3, NO2, NO3, alkalinity with units.

Knowledge categories covered:
- Water-quality physicochemistry (DO saturation vs T, un-ionized ammonia from T+pH, nitrite/nitrate, alkalinity, CO2, pH)
- Nitrification & biofilter engineering (TAN, NOB/AOB, surface area, HRT, C:N, nitrification kinetics & T-dependence)
- Cold-water species envelopes (salmonids/arctic char/sturgeon: T, DO, NH3, NO2, pH tolerances)
- Aquatic disease early-warning (WOAH notifiable diseases, biosecurity, outbreak signals)
- Advanced biofiltration & water treatment (MBBR, denitrification, ozonation, UV, CO2 stripping)
- Standards & reporting (FAO RAS guidelines, WOAH Aquatic Animal Health Code, APHA Standard Methods, sensor metrology)

### 1.2 Evidence Hierarchy (this domain)
- **Tier 1**: Systematic review / meta-analysis / official standard (ISO, IAWA, CITES, FSC, WHO, UNESCO…)
- **Tier 2**: Peer-reviewed academic paper / RCT
- **Tier 3**: Industry report / professional association guideline
- **Tier 4**: News / blog / vendor material

---

## 2. Key Research Papers & Standards

| Title | Authors | Year | Venue | DOI/URL | Tier |
|------|---------|------|-------|---------|------|
| Aqueous ammonia equilibrium calculations: effect of pH and temperature | Emerson, K. et al. | 1975 | J. Fish. Res. Board Can. 32:2379-2383 | 10.1139/f75-274 | 1 |
| The concentration of dissolved oxygen in fresh water | Benson, B.B. & Krause, D. | 1984 | Limnol. Oceanogr. 29:620-632 | 10.4319/lo.1984.29.3.0620 | 1 |
| APHA Standard Methods for the Examination of Water and Wastewater | APHA/AWWA/WEF | 2017 | 23rd ed. | standardmethods.org | 1 |
| Aquatic Animal Health Code | WOAH | current | WOAH | woah.org/en/what-we-do/standards/codes-and-manuals/aquatic-code-online-access | 1 |
| Recirculating Aquaculture | Timmons, M.B. & Ebeling, J.M. | 2013 | 3rd ed., Cayuga Aqua Ventures | ISBN 9780971264660 | 2 |
| Review of nitrification kinetics in biofilters for RAS | Eding, E.H. et al. | 2006 | Aquac. Eng. 34:364-376 | 10.1016/j.aquaeng.2005.09.003 | 2 |
| Effects of temperature on nitrification in biofilters | Zhu & Chen | 2002 | Aquaculture 213:121-130 | 10.1016/S0044-8486(02)00051-8 | 2 |

Authoritative sources registered:
- Aquacultural Engineering — Elsevier (RAS design, biofilters, water treatment)
- Aquaculture — Elsevier (species physiology, water quality)
- Journal of the World Aquaculture Society — Wiley
- Fish & Shellfish Immunology — Elsevier (disease & immunology)
- Diseases of Aquatic Organisms — Inter-Research
- Reviews in Aquaculture — Wiley (reviews & meta-analyses)
- Water Research — Elsevier (biofiltration & nitrification)
- Semantic Scholar — 'recirculating aquaculture system', 'un-ionized ammonia fish', 'RAS biofilter nitrification', 'cold-water salmonid water quality'

---

## 3. State-of-the-Art Methods & Tools

State-of-the-art RAS: (1) model-based control of TAN/DO/CO2 with sensor fusion; (2) cold-water RAS with oversized MBBR/fluidized-sand biofilters seeded for low-T nitrification; (3) denitrification reactors for zero-discharge NO3 control; (4) ozone + UV + CO2 stripping treatment train; (5) ML early-warning of disease/deviation from sensor time-series. Best-practice measurement per APHA Standard Methods and WOAH Aquatic Code. Crawl targets: Aquacultural Engineering, Aquaculture, Reviews in Aquaculture, Diseases of Aquatic Organisms.

---

## 4. Authoritative Data Sources

### 4.1 Domain authoritative sources
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

### 4.2 Academic & research sources
- Aquacultural Engineering — Elsevier (RAS design, biofilters, water treatment)
- Aquaculture — Elsevier (species physiology, water quality)
- Journal of the World Aquaculture Society — Wiley
- Fish & Shellfish Immunology — Elsevier (disease & immunology)
- Diseases of Aquatic Organisms — Inter-Research
- Reviews in Aquaculture — Wiley (reviews & meta-analyses)
- Water Research — Elsevier (biofiltration & nitrification)
- Semantic Scholar — 'recirculating aquaculture system', 'un-ionized ammonia fish', 'RAS biofilter nitrification', 'cold-water salmonid water quality'

---

## 5. Analytical Frameworks

Knowledge categories covered:
- Water-quality physicochemistry (DO saturation vs T, un-ionized ammonia from T+pH, nitrite/nitrate, alkalinity, CO2, pH)
- Nitrification & biofilter engineering (TAN, NOB/AOB, surface area, HRT, C:N, nitrification kinetics & T-dependence)
- Cold-water species envelopes (salmonids/arctic char/sturgeon: T, DO, NH3, NO2, pH tolerances)
- Aquatic disease early-warning (WOAH notifiable diseases, biosecurity, outbreak signals)
- Advanced biofiltration & water treatment (MBBR, denitrification, ozonation, UV, CO2 stripping)
- Standards & reporting (FAO RAS guidelines, WOAH Aquatic Animal Health Code, APHA Standard Methods, sensor metrology)

Cross-reference the sub-skill workflows in `skills/*.md` for the domain methods applied at each step. The fixed bookends (requirements → evidence → knowledge → synthesis → quality gate) are mandatory; the core analysis sub-skills implement the domain-specific methods.

---

## 6. Self-Update Protocol

- **Crawl pipeline:** `tools/knowledge_updater.py`
- **Schedule:** weekly academic (Mondays 08:00) + daily news (07:00); documented in `CLAUDE.md`
- **Dedup:** SHA256 of DOI/URL (case/whitespace-insensitive)
- **Scoring:** composite 0–10 = recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)
- **Crawl targets:** ArXiv categories []; Semantic Scholar keyword clusters; RSS feeds ['https://www.fao.org/newsroom/rss']
- **Gap-fill:** sub-knowledge-updater flags missing values as crawl queries
- **Append rule:** new entries appended under Section 7 with date stamp + relevance score

---

## 7. Knowledge Update Log

_(Appended automatically by the crawl pipeline. Baseline seeded with the references in Section 2.)_
