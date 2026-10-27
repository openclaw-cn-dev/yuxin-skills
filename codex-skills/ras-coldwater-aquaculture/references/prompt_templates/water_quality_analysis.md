# Skill Template: water_quality_analysis

## USER

Water-quality readings: {{wq_json}}
Species envelope: {{envelope_json}}

Task: compute the water-quality scorecard per
`assets/schemas/water_quality_scorecard.schema.json`:
1. NH3-N from T+pH via Emerson (1975) ? state f, pKa, units mg/L NH3-N.
2. DO % saturation vs T via Benson-Krause/APHA ? report mg/L AND % sat.
3. Nitrification status from TAN/NO2/NO3 pattern.
4. Alkalinity demand (~7.14 mg CaCO3 per mg TAN oxidized) and CO2 status.
5. Per-parameter deviation table with severity (ok/watch/alert/critical).
6. Data-quality flags for any missing/stale readings.

Compare every value to the species envelope. State every formula and unit.
