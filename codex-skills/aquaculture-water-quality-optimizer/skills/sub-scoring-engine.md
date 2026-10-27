---
name: aquaculture-water-quality-optimizer-sub-scoring-engine
description: Score each parameter against the selected framework envelope and compute a 0–100 composite index across five dimensions with cited justifications.
---

## Role
Sub-skill of `aquaculture-water-quality-optimizer`. You are the **scoring stage**. Compute a reproducible 0–100 score for each of the five dimensions, cite the framework criterion or source for every score, and produce a composite index.

## Purpose
Score each parameter vs the safe envelope and compute an overall water-health + biosecurity index.

## Inputs
- Validated `IntakeProfile`.
- Selected `Framework` from `sub-framework-selector`.

## Scoring Dimensions and Weights
| Dimension | Default weight | What it measures |
|-----------|----------------|------------------|
| Oxygen status | 0.25 | Dissolved oxygen vs species-specific threshold; percent saturation when available. |
| Nitrogen toxicity risk | 0.25 | TAN, un-ionized NH3 (Emerson equilibrium), and NO2 vs framework bounds. |
| pH/alkalinity stability | 0.20 | pH and alkalinity within optimal/stress bands. |
| Temperature/salinity fit | 0.15 | Temperature and salinity within species envelope. |
| Biosecurity | 0.15 | WOAH-aligned checklist of risk flags and positive controls. |

Weights can be adjusted per case, but the adjustment and justification must be surfaced.

## Scoring Algorithm (mirror `tools/scoring_engine.py`)
For each envelope criterion:
1. **Lethal zone** → score = 0.
2. **Stress zone** (between stress and optimal boundaries) → linear 25–75.
3. **Optimal zone** → score = 100.
4. **Missing value** → neutral score = 50; confidence reduced.

Special handling:
- **Un-ionized NH3** is computed with the Emerson et al. (1975) equilibrium and receives a 1.5× weight within the nitrogen dimension because it is the acute toxicant.
- **Biosecurity** is scored from the `BiosecurityFlags` checklist: each risk flag deducts points; positive controls (documented health checks, veterinary oversight) add points back. Capped at 0–100.

## Output Schema
Produce a JSON object matching `tools/schemas.py::CompositeScore`:

```json
{
  "dimensions": [
    {
      "dimension": "Oxygen status | Nitrogen toxicity risk | pH/alkalinity stability | Temperature/salinity fit | Biosecurity",
      "value": 0.0,
      "weight": 0.0,
      "justification": "One sentence with measured value, bound, and source.",
      "sources": ["citation"],
      "flagged_params": ["do_mg_l", ...],
      "confidence": "low | medium | high"
    }
  ],
  "composite": 0.0,
  "confidence": "low | medium | high",
  "missing_data_note": "string | null"
}
```

Composite is the weighted mean of dimension scores.

## Procedure
1. Read `IntakeProfile` and `Framework`.
2. For each dimension, apply the scoring algorithm above.
3. Cite the specific envelope source for every value (e.g. "DO 2.5 mg/L below Boyd & Tucker (1998) optimal 4 mg/L").
4. Compute `unionized_nh3_mg_l` from `water.tan_mg_l`, `water.ph`, and `water.temp_c` if available.
5. Adjust weights only if a dimension is disproportionately critical (e.g. acute NH3 toxicity in RAS); state the rationale.
6. Determine overall confidence from the per-dimension confidence flags and missing critical fields.
7. Record `missing_data_note` if critical fields are absent.

## Quality Gate (must be true before output)
- [ ] All five dimensions are present.
- [ ] Every dimension score has a cited justification.
- [ ] Un-ionized NH3 is calculated when TAN + pH + temp are available.
- [ ] Weights sum to 1.0 (or the explicit remainder is explained).
- [ ] `composite`, `confidence`, and `missing_data_note` are populated.

## Error Handling
- Missing parameter → assign neutral 50, lower confidence, and list in `missing_data_note`.
- Framework missing a parameter → use the nearest framework's bound or flag low confidence.
- Out-of-range units → convert and note the conversion in assumptions.
