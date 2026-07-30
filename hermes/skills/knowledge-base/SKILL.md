---
name: knowledge-base
description: "ChromaDB-backed knowledge-base workflows — sentence-transformers embeddings when built-in ONNX fails, LookForge KB health-score monitoring, blind-spot discovery, query-log analysis, emergency restores, and RAG quality tools. Load when working with a ChromaDB knowledge base (LookForge, RAG stack, project KB) and you need embeddings, health metrics, or restore/rebuild recipes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [knowledge-base, chromadb, rag, embeddings, lookforge, health-monitor]
---

# Knowledge Base (ChromaDB / RAG) Hub

ChromaDB-backed knowledge-base workflows — embeddings, health, restore, blind-spot discovery. Two main sub-areas: embedding setup (`chromadb-sentence-transformers`) and operational health (`lookforge-knowledge-health`).

## Quick Routing

| Task | Reference |
|------|-----------|
| Bulk image asset organization (rename, verify, pipeline stages) | → `references/image-asset-organization.md` |
| Replace failing ChromaDB built-in ONNX embeddings with sentence-transformers | → `references/chromadb-sentence-transformers.md` |
| KB health-score, blind-spot discovery, query-log analysis (LookForge-style) | → `references/lookforge-knowledge-health.md` |
| Probe the LookForge KB API | → `references/lookforge_api_probe.md` |
| Test-case template for KB queries | → `references/lookforge_test_case_template.md` |
| RAG quality tooling | → `references/rag_quality_tools.md` |
| seg_meta investigation (recorded bug) | → `references/bug001_segment_metadata_investigation.md` |
| **Personal RAG / digital-twin pattern (影身 v0.1, 2026-07-02)** | → `references/personal-rag-digital-twin.md` |

## Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `import_competitor_analysis.py` | Import competitor-analysis docs into LookForge KB |
| `chromadb_emergency_restore.sh` | Emergency restore of ChromaDB collections |
| `rebuild_collection_recipe.py` | Rebuild a collection (used after seq_id BLOB lockout — see `bugfix`) |
| `verify_chromadb.sh` | Verify ChromaDB integrity |

## Patterns

### When Built-In Embeddings Fail
ChromaDB's bundled ONNX embedding model can fail with SSL timeouts or corruption in restricted environments. Fallback: pre-compute embeddings with sentence-transformers and pass them in. See `references/chromadb-sentence-transformers.md`.

### KB Health Monitoring
`get_health_score()` + `query_log` + blind-spot discovery are the three levers for ongoing KB quality. LookForge Phase 1-4 deployment pattern is documented in `references/lookforge-knowledge-health.md`.

### Recovery From seq_id BLOB Lockout
When `query()` / `peek()` / `count()` all fail because of seq_id BLOB issues, the recipe combines:
- `bugfix/chromadb-seq-id-blob-fix` — root cause + fix
- `scripts/rebuild_collection_recipe.py` — runnable rebuild
- `scripts/chromadb_emergency_restore.sh` — last-resort restore

## Cross-references

- `bugfix/` — ChromaDB version compatibility fixes (NumPy 2.x, Pydantic v2)
- `lookforge-chromadb-debug` (in `product-debugging/`) — LookForge-specific debug playbook
