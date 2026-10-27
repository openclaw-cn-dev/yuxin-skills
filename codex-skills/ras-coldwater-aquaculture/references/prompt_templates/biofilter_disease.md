# Skill Template: biofilter_disease

## USER

Water-quality scorecard: {{scorecard_json}}
RAS config: {{ras_config_json}}
Biomass/feed: biomass_kg={{biomass_kg}} feed_kg_day={{feed_kg_day}} protein_pct={{feed_protein_pct}}
Disease references: {{disease_refs_json}}

Task: produce the biofilter & disease risk assessment per
`assets/schemas/biofilter_risk.schema.json`:
- TAN production from feed load (?35 g TAN/kg feed, protein-scaled).
- Biofilter capacity derated for measured T (cold-temperature penalty).
- Loading ratio = TAN produced / derated capacity ? status.
- Disease early-warning signals matched to observed stress conditions
  (low DO, high NH3/CO2, thermal shock, crowding). Mark WOAH-notifiable.
- Recommended treatments with magnitude + category + rationale.
- Advanced biofiltration options (MBBR, denitrification, ozone+UV, CO2 strip).

Apply gate G4: every out-of-envelope parameter maps to a concrete
water-treatment action with magnitude; biofilter actions distinct from
chemical/physical; cold-temperature derating applied.
