# Domain Guidelines ? RAS Cold-Water Aquaculture

> Authoritative grounding rules used by the engine and skills. These mirror the
> evidence in `SECOND-KNOWLEDGE-BRAIN.md` (Tier 1?2) and MUST be respected by
> every computed output and LLM-generated text.

## 1. Evidence hierarchy (mandatory tier labels)
- **Tier 1** ? Systematic review / meta-analysis / official standard (FAO, WOAH, APHA Standard Methods, ISO).
- **Tier 2** ? Peer-reviewed academic paper / RCT.
- **Tier 3** ? Industry report / professional association guideline (SRAC, Freshwater Institute).
- **Tier 4** ? News / blog / vendor material.

Every claim in a final report MUST carry at least one tier-labelled source, or
be explicitly flagged `[analyst judgment ? no cited source]`.

## 2. Physicochemistry rules (no approximations)
- **Un-ionized ammonia (NH3-N):** use the Emerson et al. (1975) equilibrium.
  `f = 1 / (1 + 10^(pKa - pH))` with `pKa(T) = 0.09018 + 2727.92 / T(K)`.
  `NH3-N (mg/L) = TAN (mg/L) ? f`. Always state f, pKa, and units (mg/L NH3-N).
- **DO saturation:** use the Benson & Krause (1984) / APHA freshwater formula
  (salinity-corrected when salinity is provided). Report DO as **both** mg/L and
  % saturation vs the measured temperature.
- **Nitrification alkalinity demand:** ~7.14 mg CaCO3 consumed per mg TAN
  oxidized. Report as mg/L CaCO3 per day when feed/TAN load is known.
- **Cold-water species are MORE ammonia-sensitive** than warm-water species;
  never apply tilapia/catfish envelopes to salmonids.

## 3. Biofilter engineering rules
- TAN production ? 30?40 g TAN per kg feed (protein-dependent; default 35 g/kg
  at ~40% protein; scale linearly with protein fraction).
- Nitrification is temperature-dependent. Derate capacity below 15 ?C using the
  Arrhenius-style factor in `biofilter.py`; at 10 ?C expect ~25?40% of the 25 ?C
  rate. Cold-water RAS biofilters MUST be oversized and pre-seeded.
- Biofilter capacity is quoted as g TAN / (m? media surface ? day). Always
  report the derated capacity, the loading ratio, and the penalty percent.
- A NO2 spike with low NO3 indicates NOB lag (new biofilter or cold shock).
  TAN + NO2 both high with stable NO3 indicates nitrification failure.

## 4. Disease early-warning rules
- WOAH-notifiable cold-water salmonid diseases: VHS, IPN, ISA, Gyrodactylosis,
  furunculosis (Aeromonas salmonicida), Saprolegniosis (fungal, stress-mediated).
- Stress (low DO, high NH3/CO2, crowding, thermal shock) is the common trigger.
- Match observed conditions to disease signals via the rule table in
  `diseases.py`; never diagnose a disease ? only raise an **early-warning**
  signal with the matched conditions and recommend veterinary follow-up.

## 5. Disclosure & safety
- A mandatory disclosure block MUST precede any recommendation.
- Never fabricate a missing reading: emit `DATA UNAVAILABLE` and degrade.
- Treatments are operational guidance, not veterinary prescriptions; flag
  chemical/ozone interventions with safety limits and off-gas/ORP controls.
- Ozone is toxic to fish: require off-gas destruction and ORP control.

## 6. Reporting standards
- State every formula and unit explicitly in the scorecard.
- Provide best / base / worst scenarios for borderline cases.
- Verdict MUST be exactly one of: `Optimal`, `Adjust Required`,
  `Critical Alert`, `Inconclusive`.
