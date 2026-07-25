---
name: research
description: Research and information-gathering skills — arXiv papers, blog/RSS monitoring, Karpathy-style LLM wikis, prediction markets, and academic paper writing. Load when you need to gather, structure, or publish research.
version: 1.0.0
metadata:
  hermes:
    tags: [research, arxiv, rss, knowledge-base, prediction-market, papers]
---

# Research Skills

Class-level umbrella for research and information-gathering workflows.

## Children

- `arxiv/` — Search and fetch papers from arXiv (REST API, no key needed).
- `blogwatcher/` — Monitor blogs and RSS/Atom feeds via `blogwatcher-cli`.
- `llm-wiki/` — Build/query an interlinked markdown KB (Karpathy's LLM Wiki pattern).
- `polymarket/` — Query Polymarket: markets, prices, orderbooks, history.
- `research-paper-writing/` — Write ML papers for NeurIPS / ICML / ICLR.
- `research-collection/` — 渔芯资料收集 — high-efficiency industry / company / technical / competitor data gathering, organized into structured reports.

## How to choose

- **Find a paper** → `arxiv/`
- **Track a feed / industry blog** → `blogwatcher/`
- **Build an interlinked KB** → `llm-wiki/`
- **Check prediction market odds** → `polymarket/`
- **Write / submit a paper** → `research-paper-writing/`
- **Domain-specific competitor / market data** → `research-collection/`
