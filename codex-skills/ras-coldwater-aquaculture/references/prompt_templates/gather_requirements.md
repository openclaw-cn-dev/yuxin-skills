# Skill Template: gather_requirements

## USER

Raw user message:
{{user_message}}

Attached water-quality log (optional, CSV/JSON):
{{attached_log}}

Task: produce the structured `Requirements` object per
`assets/schemas/requirements.schema.json`. Clarify the cold-water species and
life stage, RAS configuration (tank volume, make-up water %, biofilter
type/media volume/area, flow lpm), current water-quality readings
(T, DO, pH, TAN, NO2, NO3, alkalinity, CO2), biomass, feed load + protein %,
target objective, and language.

If a critical field is missing (species, life_stage, or any of T/DO/pH/TAN),
emit a clarifying question list in `data.clarifying_questions` and set
`status = "degraded"` with `degradation_level = 3`. Do NOT proceed to analysis.

Quality gate G0: species confirmed + T, DO, pH, TAN present (or clarifying
questions returned).
