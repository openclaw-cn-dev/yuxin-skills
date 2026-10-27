# tests/test-scenarios.md — Aquaculture Water Quality & Environment Optimizer

These scenarios validate the `aquaculture-water-quality-optimizer` harness end-to-end.

Two ways to run them:
1. **Automated** — `pytest tests/test_scenarios.py -v` (or `python tests/test_scenarios.py` if pytest is unavailable).
2. **Manual / LLM harness** — invoke the skill with the input below and verify the expected behavior.

---

### Scenario 1: Shrimp pond low DO at dawn
- **Input:** `species=whiteleg shrimp`, `system=pond`, `DO=2.5 mg/L`, `TAN=1.2 mg/L`, `pH=8.0`, `temp=29 °C`, `salinity=15 ppt`.
- **Expected harness behavior:**
  - Framework: Penaeid shrimp pond (Boyd & Tucker, 1998; FAO; Avnimelech, 2012).
  - Oxygen status dimension scores < 50 and flags `do_mg_l`.
  - Top roadmap action is aeration / emergency oxygenation.
  - Roadmap includes feeding reduction until DO stabilizes.
- **Pass criteria:** framework justified; all 5 dimensions scored; every score cited; assumptions + limitations stated; devil's-advocate pass evident.

### Scenario 2: Ammonia spike in RAS
- **Input:** `species=atlantic salmon`, `system=ras`, `DO=6.5 mg/L`, `TAN=2.5 mg/L`, `pH=8.2`, `temp=18 °C`, `salinity=0 ppt`.
- **Expected harness behavior:**
  - Framework: Recirculating Aquaculture Systems (Timmons & Guerdat, 2017).
  - Un-ionized NH3 is calculated with Emerson et al. (1975) equilibrium.
  - Nitrogen toxicity risk scores very low (< 40) and flags `unionized_nh3_mg_l`.
  - Top roadmap actions: verify biofilter function + stop/reduce feeding.
- **Pass criteria:** framework justified; NH3 calculation shown; all 5 dimensions scored; every score cited; assumptions + limitations stated.

### Scenario 3: New tilapia farm setup
- **Input:** `species=tilapia`, `system=pond`, `stocking_count_m2=5`, `water_volume_m3=1000`, `DO=5.5 mg/L`, `pH=7.5`, `temp=28 °C`, `alkalinity=80 mg/L`, `salinity=0 ppt`.
- **Expected harness behavior:**
  - Framework: Warm-water finfish pond (Boyd & Tucker, 1998; Boyd, 2020).
  - Carrying-capacity reasoning surfaced based on density, volume, and feed loading.
  - Composite starts ≥ 60 because chemical parameters are reasonable.
  - Roadmap emphasizes preventive monitoring and density/feed planning.
- **Pass criteria:** framework justified; carrying-capacity model cited; all 5 dimensions scored; every score cited.

### Scenario 4: Disease outbreak biosecurity
- **Input:** `species=whiteleg shrimp`, `system=pond`, `DO=4.2 mg/L`, `TAN=0.8 mg/L`, `pH=8.0`, `temp=29 °C`, biosecurity flags: recent_mortality=true, shared_equipment=true, untreated_water_source=true.
- **Expected harness behavior:**
  - Framework: Penaeid shrimp pond.
  - Biosecurity dimension scores < 60 and flags the raised risk factors.
  - Top roadmap action is mortality diagnostic sampling + quarantine.
  - WOAH Aquatic Animal Health Code cited for biosecurity actions.
- **Pass criteria:** framework justified; biosecurity score reflects flags; diagnostic/quarantine in top actions; every score cited.

### Scenario 5: Biofloc balance
- **Input:** `species=whiteleg shrimp`, `system=biofloc`, `DO=4.0 mg/L`, `TAN=1.8 mg/L`, `pH=8.0`, `temp=29 °C`, `salinity=20 ppt`, `C:N=6.0`, `TSS=650 mg/L`.
- **Expected harness behavior:**
  - Framework: Biofloc Technology (Avnimelech, 2012; Emerenciano et al., 2017).
  - C:N ratio and TSS are evaluated against BFT-specific envelope.
  - Roadmap includes carbon-source addition and floc thinning.
- **Pass criteria:** framework justified; BFT-specific parameters scored; carbon-source action in roadmap; every score cited.

---

## Regression Checklist (run after any edit)
- [ ] Framework selection always justified to the user.
- [ ] Scorecard includes all 5 dimensions with cited justifications.
- [ ] Un-ionized NH3 is calculated when TAN + pH + temp are present.
- [ ] Roadmap items carry effort + impact + rationale + owner + expected effect.
- [ ] Roadmap includes monitoring schedule.
- [ ] Stopgap note present when composite < 50.
- [ ] Graceful degradation when WebSearch/WebFetch unavailable (fallback to SECOND-KNOWLEDGE-BRAIN.md).
- [ ] Sources section lists every citation.
- [ ] `pytest tests/test_scenarios.py -v` passes (or `python tests/test_scenarios.py` if pytest missing).
