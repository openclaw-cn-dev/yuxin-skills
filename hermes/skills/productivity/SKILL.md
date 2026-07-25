---
name: productivity
description: Skills for document creation, presentations, spreadsheets, and other productivity workflows. Most skills here are also available at the top-level (`document`, `spreadsheet`, `presentation`, etc.) — this directory is a flat workspace snapshot. Prefer top-level skills for discoverability.
version: 1.0.0
metadata:
  hermes:
    tags: [productivity, documents, spreadsheets, presentations, workflows]
---

# Productivity Skills

This directory is a **flat workspace snapshot** — many of its children are also available as top-level skills (e.g. `docx/`, `pdf/`, `pptx/`, `xlsx/`, `ux-heuristics/`). Prefer the top-level versions for better discoverability via the umbrella.

## Children

- Document creation / edit: `docx/`, `pdf/`, `pptx/`, `xlsx/`, `nano-pdf/`, `powerpoint/`, `notion/`, `ocr-and-documents/`
- Project management / tasks: `linear/`, `airtable/`, `notion/`
- Workflows: `afu-workflow/`, `heidou-workflow/`, `maodu-workflow/`, `xiaobao-workflow/`, `laomo-workflow/`
- Knowledge / research: `laomo-knowledge/`, `maodou-product/`, `laomo-research-local-fallback/`
- Communication: `google-workspace/`, `feishu/` (top-level umbrella — 飞书 skills moved there)
- Specialized: `agent-overseer/`, `yuxin-daily-briefing/`, `maodu-task-status-reporter/` (multi-phase-pipeline / projectforge-optimization moved to `product/` umbrella; lookforge-mcp-hermes recipe demoted to `mcp/references/lookforge-chromadb-integration.md`)

## Recommendation

The flat snapshot is here for legacy reasons. Prefer the **top-level equivalents** for new work — they're easier to discover via the umbrella skill descriptions.
