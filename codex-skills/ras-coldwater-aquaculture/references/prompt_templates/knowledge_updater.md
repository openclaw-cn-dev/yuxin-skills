# Skill Template: knowledge_updater

## USER

Topic keywords: {{keywords_json}}

Task: query the knowledge base for 3?5 authoritative RAS / water-chemistry /
biofiltration / disease citations matching the keywords. Return tiered
citations (Tier 1?4) and flag any knowledge gaps for the crawl pipeline in
`data.knowledge_gaps`. If no academic source is surfaced, set
`status = "degraded"` and emit a limitation. Provide an evidence-coverage
rating (high/medium/low).
