# Quality Standards Reference — red-tide-algal-bloom-monitoring

## Evidence Hierarchy

### Tier 1 — Systematic Reviews / Meta-Analyses / Official Standards
- Systematic reviews with meta-analysis
- Official standards (ISO, IOC-UNESCO, WHO, WOAH, CODEX)
- Government-issued regulatory frameworks
- Landmark papers with >500 citations in domain
- Example: IOC-UNESCO HAB Programme guidelines

### Tier 2 — Peer-Reviewed Domain Research
- Peer-reviewed articles in recognized journals
- Randomized controlled trials (RCTs)
- Large cohort studies (n > 100)
- Conference proceedings from major domain events
- Example: Articles in Harmful Algae, Remote Sensing of Environment

### Tier 3 — Professional / Industry Reports
- Industry association guidelines
- Gray literature from recognized bodies
- Technical reports from government agencies
- Example: State-level monitoring program annual reports

### Tier 4 — News / Blog / Unverified Sources
- News articles
- Blog posts (even expert-written)
- Vendor marketing materials
- Personal communications
- Example: Local news coverage of bloom events

## Analytical Standards

### Satellite Data Quality
- **Coverage:** ≥70% valid pixels in region of interest
- **Timeliness:** Data within 48 hours of analysis date
- **Algorithm:** Published, peer-reviewed with documented uncertainties
- **Validation:** Compared against in-situ measurements (R² > 0.7)
- **Resolution:** Appropriate for coastal/estuarine applications (≤1km)

### In-Situ Data Quality
- **Calibration:** Sensors calibrated per manufacturer schedule
- **QA/QC:** ≥10% duplicates, blanks, CRM per batch
- **Detection Limit:** Method detection limit ≤10% of regulatory threshold
- **Precision:** RSD ≤20% at regulatory threshold
- **Traceability:** Measurements traceable to SI units via CRMs

### Bloom Detection Confidence
- **High:** Confirmed by ≥2 independent methods (satellite + in-situ)
- **Medium:** Single method with corroborating environmental data
- **Low:** Single method only, limited data
- **Very Low:** Indirect indicators only (e.g., satellite chl-a alone)

### Toxin Risk Confidence
- **High:** Direct toxin measurement + species identification
- **Medium:** Species identification + cell counts above threshold
- **Low:** Environmental conditions favorable + satellite indication
- **Very Low:** Model-based prediction only

## Quality Gate Specifications

### Universal Gates (U1-U6)

| Gate | Criterion | Pass Threshold | Max Retries | Auto-Fix Action |
|------|-----------|---------------|-------------|-----------------|
| U1 | Source citations | ≥3 total, ≥1 Tier 1-2 | 2 | Search + add missing sources |
| U2 | Disclosure section | Present before conclusion | 2 | Prepend standard disclosure |
| U3 | Evidence hierarchy | Every source labeled Tier 1-4 | 1 | Annotate unlabeled sources |
| U4 | Language match | Output matches LANG | 1 | Translate to target language |
| U5 | Template compliance | All mandatory sections | 2 | Restructure to template |
| U6 | Claim traceability | Every claim → source or [judgment] | 2 | Add attribution flags |

### Domain Gates (G1-G4)

| Gate | Criterion | Pass Threshold | Max Retries | Auto-Fix Action |
|------|-----------|---------------|-------------|-----------------|
| G1 | Multi-method detection | ≥2 methods (satellite + in-situ) | 1 | Add fallback detection method |
| G2 | Regulatory limits | Explicitly cited per toxin | 1 | Add regulatory limit reference |
| G3 | Species-specific impact | Aquaculture species named | 1 | Add species vulnerability detail |
| G4 | Alert category mapping | Matches defined 5 categories | 1 | Map to standard category |

## Conclusion Categories

### Category Definitions

| Category | Conditions | Implied Action |
|----------|-----------|----------------|
| Low Risk | No bloom detected, favorable conditions | Routine monitoring |
| Normal | Background levels, no risk indicators | Standard monitoring |
| Monitor (elevated) | Bloom indicators present, below threshold | Enhanced monitoring, pre-emptive actions |
| Critical Bloom Alert | Bloom confirmed, thresholds exceeded | Immediate action, harvest closure |
| Inconclusive | Insufficient data for classification | Data collection required |

### Classification Rules
1. **Critical Bloom Alert** if: cell count > threshold AND toxin detected OR satellite + in-situ both positive
2. **Monitor (elevated)** if: any positive indicator OR environmental conditions favorable
3. **Normal** if: all indicators within background range
4. **Low Risk** if: all indicators below background AND unfavorable conditions for bloom
5. **Inconclusive** if: conflicting indicators OR data insufficient for any category

## Mandatory Output Sections

1. **Executive Summary** — 2-3 sentences
2. **Inputs & Scope** — object, timeframe, constraints, audience
3. **Evidence Collected** — data + authoritative docs with source + date + tier
4. **Analysis / Scorecard** — detection, triggers, toxin, aquaculture impact
5. **Control / Action Plan** — concrete actions with priorities
6. **Academic Evidence** — KB citations with tiers
7. **Disclosure / Limitations** — mandatory before conclusion
8. **Conclusion** — verdict category, scenarios, risks, evidence chain, recommendations
9. **Post-Execution Gate Checklist** — all gates with status

## Professional Standards

### Tone & Language
- Professional, evidence-based, no hyperbole
- Units stated for all measurements
- Confidence levels explicit (Very Low, Low, Medium, High, Very High)
- No single-point predictions without stated uncertainty
- Conditional language only when evidence supports it

### Citation Format
```
Author(s) (Year). Title. Venue. DOI/URL. [Tier X]
```
For standards/guidelines:
```
Organization (Year). Document Title. Document ID. URL. [Tier 1]
```

### Disclaimer Language
```
This analysis is based on available data as of [timestamp] and
should not be the sole basis for operational decisions. Consult
local regulatory authorities for official guidance. All
recommendations are advisory unless regulatory status is cited.
```

## Cross-Reference

See `PROJECT-detail.md` for full quality gate specification. See `SKILL.md` for hook-based gate enforcement. See `tests/test-scenarios.md` for gate coverage matrix.
