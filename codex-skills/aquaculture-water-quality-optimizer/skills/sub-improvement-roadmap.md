---
name: aquaculture-water-quality-optimizer-sub-improvement-roadmap
description: Build a prioritized improvement roadmap ranked by mortality-risk reduction, with effort, impact, owner, expected effect, and framework source for each action.
---

## Role
Sub-skill of `aquaculture-water-quality-optimizer`. You are the **roadmap stage**. Convert low scores and flagged parameters into concrete, prioritized actions.

## Purpose
Recommend aeration, water-exchange, feeding, pH/alkalinity, C:N, and biosecurity actions ranked by mortality-risk reduction.

## Inputs
- `IntakeProfile`.
- `Framework`.
- `CompositeScore` from `sub-scoring-engine`.

## Prioritization Logic (mirror `tools/roadmap_engine.py`)
Each candidate action receives an urgency score:

```text
urgency = (100 - dimension_score) × urgency_coefficient / hours_to_effect
```

Urgency coefficients:
- Acute toxicants (NH3, NO2): 3.5
- Low DO: 3.0
- Biosecurity / disease events: 2.5
- Chronic nitrogen load: 2.0
- pH / alkalinity / temperature / salinity: 1.0

Actions are sorted by urgency descending, then by impact (high → low), then by effort (low → high).

## Action Catalog (from `tools/roadmap_engine.py`)
| Trigger parameter | Action | Effort | Impact |
|-------------------|--------|--------|--------|
| `do_mg_l` low | Increase mechanical aeration / emergency oxygenation | medium | high |
| `do_mg_l` low | Reduce feeding until DO stabilizes | low | medium |
| `do_mg_l` low | Increase water exchange / partial flush | medium | medium |
| `unionized_nh3_mg_l` high | Stop feeding / reduce protein input | low | high |
| `unionized_nh3_mg_l` high | Verify/adjust biofilter or floc activity | high | high |
| `unionized_nh3_mg_l` high | Lower pH cautiously if pH > 8.5 | medium | medium |
| `no2_mg_l` high | Add chloride source (NaCl) | low | high |
| `no2_mg_l` high | Accelerate biofilter maturation / water exchange | medium | medium |
| `tan_mg_l` chronic | Reduce stocking density or feed loading | high | high |
| `ph` out of range | Buffer with lime or bicarbonate | medium | high |
| `ph` high afternoon | Manage algal bloom / aeration | medium | medium |
| `alkalinity_mg_l_caCO3` low | Apply alkalinity amendment | medium | medium |
| `temp_c` out of range | Shade/insulate or regulate source water | high | medium |
| `salinity_ppt` out of range | Adjust salinity gradually | medium | medium |
| `c_n_ratio` off | Add carbon source (molasses/starch/glycerol) | medium | high |
| `tss_mg_l` high | Thin or harvest excess floc | high | medium |
| Biosecurity risk flags | Mortality diagnostic sampling + quarantine | high | high |
| Biosecurity risk flags | Document health checks / veterinary oversight | low | medium |
| Biosecurity risk flags | Disinfect equipment / control predator access | medium | medium |

## Output Schema
Produce a JSON object matching `tools/schemas.py::Roadmap`:

```json
{
  "items": [
    {
      "rank": 1,
      "action": "string",
      "target_parameter": "string | null",
      "target_dimension": "string | null",
      "effort": "low | medium | high",
      "impact": "low | medium | high",
      "rationale": "string",
      "owner": "string",
      "expected_effect": "string",
      "framework_source": "string",
      "urgency_hours": "float | null"
    }
  ],
  "monitoring_schedule": "string",
  "stopgap_note": "string | null"
}
```

## Procedure
1. Read the `CompositeScore` and identify every flagged parameter / low dimension.
2. Pull matching actions from the catalog.
3. Skip lower-impact actions when the dimension already scores ≥ 85.
4. Deduplicate by action text.
5. Assign ranks by the urgency formula.
6. Add a monitoring schedule and a stopgap note if the composite score is < 50.
7. Surface the top 3–5 actions to the user with rationale and expected effect.

## Quality Gate (must be true before output)
- [ ] At least one action exists for every dimension scoring < 70.
- [ ] Every item has `effort`, `impact`, `rationale`, `owner`, and `expected_effect`.
- [ ] `framework_source` cites the guideline for the action.
- [ ] `monitoring_schedule` is present.
- [ ] `stopgap_note` is present when `composite` < 50.

## Error Handling
- No flagged parameters and composite ≥ 70 → output a preventive maintenance schedule instead of acute actions.
- Missing framework source for a custom action → do not include the action until a source is found or flag it as opinion.
