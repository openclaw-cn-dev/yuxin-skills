# Skill Template: evidence_collector

## USER

Species: {{species}} | Life stage: {{life_stage}}

Task: assemble the authoritative evidence bundle for this species+stage:
species-specific water-quality envelopes (T, DO, pH, TAN, NH3, NO2, NO3,
alkalinity, CO2), the species NH3-N chronic/acute thresholds, biofilter
nitrification parameters (specific surface area, reference capacity,
temperature derating), and current disease-risk references (WOAH notifiable +
stress-mediated). Prefer cached envelopes from the provided species registry;
fall back to knowledge-base entries and, if permitted, web sources. Tag every
source with a tier label (1?4).

If live sources are unreachable, set `status = "degraded"`, escalate
`degradation_level`, and emit an explicit limitation naming each substituted
source. Never fabricate envelopes.
