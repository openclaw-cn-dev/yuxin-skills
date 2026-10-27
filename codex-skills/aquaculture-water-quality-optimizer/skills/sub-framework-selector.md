---
name: aquaculture-water-quality-optimizer-sub-framework-selector
description: Select the species-specific, citable water-quality envelope and system-management framework for the case at hand.
---

## Role
Sub-skill of `aquaculture-water-quality-optimizer`. You are the **framework selection stage**. Choose the named, citable evaluation framework that best matches the validated `IntakeProfile`. Explain the rationale to the user.

## Purpose
Select species-specific water-quality envelopes and the system-management model. The output drives scoring thresholds and roadmap actions.

## Inputs
- Validated `IntakeProfile` from `sub-profile-intake`.

## Framework Registry (from `tools/frameworks.py`)
| Framework | Species | System | Key Envelope Source |
|-----------|---------|--------|---------------------|
| Warm-water finfish pond | Tilapia, carp, catfish | Pond | Boyd & Tucker (1998); Boyd (2020) |
| Penaeid shrimp pond | *Litopenaeus vannamei*, *Penaeus monodon* | Pond | Boyd & Tucker (1998); FAO; Avnimelech (2012) |
| RAS — salmonid/high-value finfish | Salmon, trout, yellowtail | RAS | Timmons & Guerdat (2017); Malone & Pfeiffer (2006) |
| Biofloc Technology (BFT) | Shrimp, tilapia, catfish | Biofloc | Avnimelech (2012); Emerenciano et al. (2017) |
| Flow-through / cage freshwater finfish | Trout, salmon, carp, tilapia | Flow-through / cage | Boyd (2020); Wedemeyer (1996) |

## Selection Rules
Apply in strict order:
1. **System override**: `system_type == biofloc` → use **Biofloc Technology** framework.
2. **System override**: `system_type == ras` → use **RAS — salmonid/high-value finfish** framework.
3. **System override**: `system_type in (flow-through, cage)` → use **Flow-through / cage** framework.
4. **Species match in pond**: if species contains `shrimp`, `litopenaeus`, `penaeus`, `vannamei`, `monodon` → use **Penaeid shrimp pond**.
5. **Default**: use **Warm-water finfish pond**.

## Output Schema
Produce a JSON object matching `tools/schemas.py::Framework`:

```json
{
  "name": "string",
  "species": ["list of species this framework covers"],
  "system_types": ["pond | ras | biofloc | flow-through | cage"],
  "life_stages": ["larvae | juvenile | adult | broodstock | mixed"],
  "envelope": [
    {
      "parameter": "do_mg_l | tan_mg_l | unionized_nh3_mg_l | no2_mg_l | no3_mg_l | ph | alkalinity_mg_l_caCO3 | temp_c | salinity_ppt | c_n_ratio | tss_mg_l",
      "unit": "string",
      "min_optimal": "float | null",
      "max_optimal": "float | null",
      "min_stress": "float | null",
      "max_stress": "float | null",
      "lethal_below": "float | null",
      "lethal_above": "float | null",
      "source": "citation"
    }
  ],
  "carrying_capacity_model": "string | null",
  "biosecurity_standard": "string | null",
  "citations": ["list of canonical citations"],
  "rationale": "string explaining why this framework was selected"
}
```

## Procedure
1. Read the `IntakeProfile`.
2. Apply the selection rules above to pick a framework.
3. If the species is ambiguous (e.g. "freshwater prawn" vs shrimp), flag the assumption and use the closest framework with low confidence.
4. Surface the framework name, the envelope summary, and the rationale to the user.
5. If WebSearch/WebFetch is available, confirm the envelope bounds against a recent authoritative source and note any updates.

## Quality Gate (must be true before output)
- [ ] Framework name is from the registry.
- [ ] Selection rationale references the species and system type.
- [ ] Every envelope criterion has a named source.
- [ ] Carrying-capacity model and biosecurity standard are populated.
- [ ] User-facing justification is ≤ 2 sentences.

## Error Handling
- Unknown species/system → fall back to generic warm-water finfish pond, flag `low` confidence, and ask the user to confirm species.
- Conflicting evidence from WebSearch → prefer the canonical registry bound, but add a note to `assumptions` about the discrepancy.
