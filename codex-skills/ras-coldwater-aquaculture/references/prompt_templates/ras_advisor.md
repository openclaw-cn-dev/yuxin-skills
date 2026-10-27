# Skill Template: ras_advisor

## USER

Water-quality scorecard: {{scorecard_json}}
Biofilter/disease assessment: {{biofilter_risk_json}}
Evidence bundle: {{evidence_bundle_json}}
Knowledge-base evidence: {{kb_evidence_json}}

Task: synthesize the final verdict per `assets/schemas/verdict.schema.json`:
- A mandatory disclosure block BEFORE the recommendation (gate U2).
- Verdict = exactly one of: Optimal | Adjust Required | Critical Alert | Inconclusive.
- Early-warning alerts (deduplicated, severity-ordered).
- Automated water-treatment procedure as ordered steps with magnitude + safety limits.
- Best / base / worst scenarios for borderline cases.
- Key risks, evidence chain (every claim ? ?1 tiered source), remediation.
- `degradation_level` inherited from upstream.

Gate G2/G3/G4 must be satisfied by the upstream scorecards; if not, the
quality-gate layer will auto-fix or flag a limitation.
