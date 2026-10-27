# SECOND-KNOWLEDGE-BRAIN.md — Aquaculture Water Quality & Environment Optimizer

> Living, self-improving knowledge base for `aquaculture-water-quality-optimizer`. Grown weekly by `tools/knowledge_updater.py`.

## 1. Core Concepts & Frameworks
This skill reasons with the following world-renowned frameworks:
- **Water-quality parameter envelopes (DO, TAN/NH3, NO2, NO3, pH, alkalinity, temp, salinity)** — Boyd & Tucker (1998); Boyd (2020).
- **Total Ammonia Nitrogen / un-ionized ammonia equilibrium** — Emerson et al. (1975).
- **Carrying-capacity & stocking-density models** — Boyd & Tucker (1998); Timmons & Guerdat (2017).
- **Biosecurity / WOAH (OIE) aquatic health standards** — WOAH Aquatic Animal Health Code.
- **RAS & biofloc management principles** — Timmons & Guerdat (2017); Avnimelech (2012); Emerenciano et al. (2017).
- **FCR / growth performance benchmarking** — FAO technical papers.

Scoring dimensions derived from these: **Oxygen status, Nitrogen toxicity risk, pH/alkalinity stability, Temperature/salinity fit, Biosecurity**.

## 2. Key Research Papers
| Title | Authors | Year | Venue | DOI/URL | Relevance |
|-------|---------|------|-------|---------|-----------|
| Pond Aquaculture Water Quality Management | Boyd, C.E. & Tucker, C.S. | 1998 | Springer | https://link.springer.com/book/10.1007/978-1-4615-5407-5 | Foundational envelope source for pond DO, ammonia, nitrite, pH, alkalinity |
| Water Quality: An Introduction | Boyd, C.E. | 2020 | Springer | 10.1007/978-3-030-23335-8 | Updated water-quality chemistry, criteria, and management principles |
| Recirculating Aquaculture | Timmons, M.B. & Guerdat, T. | 2017 | Ithaca Publishing | ISBN 978-0-9715026-5-8 | RAS design, biofilter sizing, ammonia/nitrite control, oxygenation |
| Biofloc Technology — A Practical Guide Book | Avnimelech, Y. | 2012 | World Aquaculture Society | ISBN 978-0-9848313-0-5 | BFT C:N ratio, TAN control, floc management, alkalinity |
| Aqueous ammonia equilibrium calculations: effect of pH and temperature | Emerson, K.; Russo, R.C.; Lund, R.E.; Thurston, R.V. | 1975 | J Fish Res Board Can 32:2379-2383 | https://doi.org/10.1139/f75-303 | Standard NH3–NH4⁺ equilibrium formula used in the scoring engine |
| Rating fixed film nitrifying biofilters used in recirculating aquaculture systems | Malone, R.F. & Pfeiffer, T.J. | 2006 | Aquacultural Engineering 34(3):389-402 | 10.1016/j.aquaeng.2005.06.003 | Biofilter performance and NO2⁻ dynamics in RAS |
| Carbon/nitrogen ratio as a control element in aquaculture systems | Avnimelech, Y. | 1999 | Aquaculture 176:227-235 | 10.1016/S0044-8486(99)00098-9 | Foundational C:N management in biofloc and heterotrophic systems |
| Biofloc Technology (BFT): A review of what we know and what we need to know | Emerenciano, G.C.; Martínez-Córdova, L.R.; Martínez-Porchas, M.; Miranda-Baeza, A. | 2017 | Aquacultural Engineering 77:100-117 | 10.1016/j.aquaeng.2017.06.002 | TSS targets, microbial community, system monitoring in BFT |
| Engineering analysis of the stoichiometry of photoautotrophic, autotrophic, and heterotrophic removal of ammonia-nitrogen in aquaculture systems | Ebeling, J.M.; Timmons, M.B.; Bisogni, J.J. | 2006 | Aquaculture 257:346-358 | 10.1016/j.aquaculture.2006.03.026 | Nitrification vs heterotrophic assimilation pathways |
| Fundamentals of Aquacultural Engineering | Lawson, T.B. | 1995 | Wiley | ISBN 978-0-471-10719-6 | Pond, raceway, and tank engineering principles |
| Carrying capacity models for aquaculture | Piedrahita, R.H. | 2003 | In: Aquaculture Engineering | — | Stocking-density and carrying-capacity reasoning |
| The basics of bio-flocs technology: The added value for aquaculture | Schryver, P.; Crab, R.; Defoirdt, T.; Boon, N.; Verstraete, W. | 2008 | Aquaculture 277(3-4):125-137 | 10.1016/j.aquaculture.2008.03.028 | BFT microbial ecology and water-quality benefits |
| Nitrogen removal techniques in aquaculture for a sustainable production | Crab, R.; Avnimelech, Y.; Defoirdt, T.; Bossier, P.; Verstraete, W. | 2007 | Aquaculture 270(1-4):1-14 | 10.1016/j.aquaculture.2007.05.006 | Survey of ammonia/nitrite management approaches |
| Aquatic Animal Health Code | WOAH | 2024 | WOAH | https://www.woah.org/en/what-we-do/standards/codes-and-manuals/aquatic-code-online-access/ | Biosecurity, disease reporting, and farm-level standards |
| Technical manual on pond culture of Penaeus vannamei | FAO | 2020 | FAO Fisheries and Aquaculture Technical Paper | http://www.fao.org/fishery | Species-specific shrimp pond water-quality guidance |
| Biofloc production systems for aquaculture | Hargreaves, J.A. | 2013 | SRAC Publication 4503 | https://srac.tamu.edu/ | Practical BFT management and monitoring |

## 3. State-of-the-Art Methods & Tools
- **Dissolved oxygen management**: dawn monitoring, emergency aeration, feeding reduction, water exchange (Boyd & Tucker 1998; Boyd 2020).
- **Ammonia toxicity assessment**: compute un-ionized NH3 with Emerson et al. (1975) equilibrium; acute toxicity dominated by pH and temperature (Timmons & Guerdat 2017).
- **Nitrite mitigation**: maintain chloride:nitrite ratio > 10:1; mature biofilters; water exchange (Boyd & Tucker 1998; Malone & Pfeiffer 2006).
- **pH/alkalinity buffering**: lime (CaCO3), hydrated lime, or sodium bicarbonate to keep alkalinity > 80 mg/L CaCO3 in shrimp ponds and > 50 mg/L in RAS (Boyd 2020; Avnimelech 2012).
- **Biofloc C:N control**: add carbohydrate (molasses, starch, glycerol) to maintain C:N 10–15 and TSS 300–500 mg/L (Avnimelech 2012; Emerenciano et al. 2017).
- **Biosecurity**: WOAH-aligned quarantine, health documentation, equipment disinfection, predator control, diagnostic referral (WOAH 2024).
- Evidence hierarchy enforced: Systematic Review > Meta-Analysis > RCT/empirical > Cohort > Expert Opinion > Blog.

## 4. Authoritative Data Sources
- *Aquaculture* (Elsevier)
- *Aquacultural Engineering* (Elsevier)
- WOAH Aquatic Animal Health Code
- FAO aquaculture technical papers
- NCBI PubMed / E-utilities
- Crossref / Semantic Scholar / arXiv (for open-access preprints)

## 5. Analytical Frameworks (used for evaluation)
- **Water-quality parameter envelopes** — Boyd & Tucker (1998); Boyd (2020).
- **Total Ammonia Nitrogen / un-ionized ammonia equilibrium** — Emerson et al. (1975).
- **Carrying-capacity & stocking-density models** — Boyd & Tucker (1998); Timmons & Guerdat (2017); Piedrahita (2003).
- **Biosecurity / WOAH standards** — WOAH Aquatic Animal Health Code.
- **RAS & biofloc management principles** — Timmons & Guerdat (2017); Avnimelech (2012); Emerenciano et al. (2017).
- **FCR / growth performance benchmarking** — FAO; Lawson (1995).

## 6. Self-Update Protocol (crawl4ai / API config)
- **Sources:** *Aquaculture* (Elsevier), *Aquacultural Engineering*, WOAH Aquatic Animal Health Code, FAO aquaculture technical papers.
- **API providers:** PubMed E-utilities, Crossref REST API, Semantic Scholar Graph API, arXiv API.
- **Search queries:** dissolved oxygen shrimp pond management, un-ionized ammonia toxicity fish, biofloc water quality optimization, RAS nitrification biosecurity, pond carrying capacity stocking density, nitrite toxicity aquaculture chloride, pH alkalinity stability aquaculture.
- **Frequency:** weekly (cron / scheduled job).
- **Append format:** dated entry → Title | Authors | Year | Venue | DOI/URL | key finding | relevance.
- **Dedup:** DOI/URL hash check before append (`<!--hash:...-->`).
- **Run:** `python tools/knowledge_updater.py --dry-run` to preview; `python tools/knowledge_updater.py` to append.

## 7. Knowledge Update Log
- 2026-06-18 — Knowledge base seeded at initial build (idea 118). Frameworks and sources registered; awaiting first live API crawl.
- 2026-06-22 — Seeded with 16 canonical, citable papers and books covering pond water quality, RAS, biofloc, ammonia equilibrium, nitrite, and biosecurity. Updater refactored to use real scholarly APIs (PubMed, Crossref, Semantic Scholar, arXiv) with deduplication and rate limiting.
