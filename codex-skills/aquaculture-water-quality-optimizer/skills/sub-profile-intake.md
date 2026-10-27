---
name: aquaculture-water-quality-optimizer-sub-profile-intake
description: Capture species, system type, stocking density, water-chemistry parameters, and biosecurity flags; validate required fields and emit a canonical IntakeProfile.
---

## Role
Sub-skill of `aquaculture-water-quality-optimizer`. You are the **intake stage**. Do not score or recommend yet — your job is to collect, normalize, and validate inputs into the canonical `IntakeProfile` schema.

## Purpose
Capture species, system type (pond / RAS / biofloc / flow-through / cage), stocking density, measured water-chemistry parameters, and biosecurity flags. Request missing critical fields. Surface assumptions and confidence.

## Inputs
- The user request and any artifacts supplied.
- Structured output from the previous harness stage (if any).

## Required Fields
| Field | Why it matters |
|-------|----------------|
| `stocking.species` | Determines species-specific water-quality envelope. |
| `stocking.system_type` | Selects pond vs RAS vs biofloc framework. |
| `water.temp_c` | Required for NH3 equilibrium and temperature fit. |
| `water.ph` | Required for NH3 equilibrium and pH stability. |
| `water.do_mg_l` | Required for oxygen-status scoring (mandatory for RAS/biofloc; strongly recommended for ponds). |

## Optional but High-Value Fields
`water.tan_mg_l`, `water.no2_mg_l`, `water.no3_mg_l`, `water.alkalinity_mg_l_caCO3`, `water.salinity_ppt`, `water.turbidity_ntu`, `water.tss_mg_l`, `water.c_n_ratio`, `water.secchi_cm`, `stocking.stocking_density_kg_m3`, `stocking.stocking_count_m2`, `stocking.water_volume_m3`, `stocking.culture_days`, `biosecurity.*` flags.

## Procedure
1. Parse the user request and any attached data.
2. Map free-form species to a normalized name (e.g. "white shrimp" → `Litopenaeus vannamei`).
3. Map system type to one of: `pond`, `ras`, `biofloc`, `flow-through`, `cage`.
4. If a critical field is missing, ask a **single targeted question** per missing field rather than dumping a long form.
5. Compute derived fields using the Python reference implementation:
   - `water.unionized_nh3_mg_l` via Emerson et al. (1975) equilibrium (`tools/schemas.py`).
   - `water.percent_saturation` via Weiss (1970) if DO, temp, and salinity are present.
6. Populate `missing_fields` and `critical_missing`.
7. Assign confidence:
   - `high` — all critical fields present.
   - `medium` — one critical field missing or some derived values estimated.
   - `low` — two or more critical fields missing.
8. Record assumptions in `assumptions` (e.g. "salinity assumed 15 ppt because brackish-water shrimp farm").

## Output Schema
Produce a JSON object matching `tools/schemas.py::IntakeProfile`:

```json
{
  "farm_id": "string | null",
  "location": "string | null",
  "intake_date": "YYYY-MM-DD | null",
  "stocking": {
    "species": "string",
    "scientific_name": "string | null",
    "system_type": "pond | ras | biofloc | flow-through | cage",
    "life_stage": "larvae | juvenile | adult | broodstock | mixed",
    "stocking_density_kg_m3": "float | null",
    "stocking_count_m2": "float | null",
    "water_volume_m3": "float | null",
    "production_target_kg": "float | null",
    "feed_rate_kg_day": "float | null",
    "culture_days": "int | null"
  },
  "water": {
    "do_mg_l": "float | null",
    "tan_mg_l": "float | null",
    "no2_mg_l": "float | null",
    "no3_mg_l": "float | null",
    "ph": "float | null",
    "alkalinity_mg_l_caCO3": "float | null",
    "temp_c": "float | null",
    "salinity_ppt": "float | null",
    "turbidity_ntu": "float | null",
    "c_n_ratio": "float | null",
    "tss_mg_l": "float | null",
    "secchi_cm": "float | null"
  },
  "biosecurity": {
    "recent_mortality": false,
    "recent_stocking_without_quarantine": false,
    "shared_equipment_between_ponds": false,
    "predators_or_birds_observed": false,
    "untreated_water_source": false,
    "recent_weather_extreme": false,
    "disease_history": false,
    "health_checks_documented": false,
    "veterinary_oversight": false
  },
  "notes": "string | null",
  "missing_fields": ["list of missing field paths"],
  "assumptions": ["list of assumptions made"],
  "confidence": "low | medium | high"
}
```

## Quality Gate (must be true before output)
- [ ] `stocking.species` and `stocking.system_type` are present and normalized.
- [ ] At least `water.temp_c` and `water.ph` are present, or the user has been asked.
- [ ] Derived `unionized_nh3_mg_l` is computed when TAN + pH + temp are available.
- [ ] `critical_missing` is empty or the user has been explicitly prompted.
- [ ] `assumptions` and `confidence` are populated.

## Error Handling
- Missing data → ask targeted question, set confidence to `low`/`medium`.
- Conflicting units → convert to schema units and note the conversion in assumptions.
- Unknown species → use the generic warm-water finfish pond framework and flag low confidence.
