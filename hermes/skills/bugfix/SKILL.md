---
name: bugfix
description: "Library/framework bug fixes and version-compatibility workarounds — ChromaDB 0.4.x issues (NumPy 2.x, seq_id BLOB, Pydantic v2), and other session-specific bug fixes that don't fit a normal 'use the library' workflow. Load when a known third-party library throws an error that doesn't match current docs — first check this hub for known fixes before reinventing."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bugfix, workaround, chromadb, compatibility, python, troubleshooting]
---

# Bugfix & Compatibility Workarounds

Session-specific bug fixes and version-compatibility workarounds for third-party libraries. Each entry is a named, reproducible problem + a verified workaround. When you hit a third-party library error that doesn't match current docs, **check this hub first**.

## Quick Routing

| Symptom / Library Version | Reference |
|---------------------------|-----------|
| ChromaDB 0.4.x + NumPy 2.x → `AttributeError: np.float_`/`np.int_` (Apple Silicon / Docker) | → `references/chromadb-numpy2-applesilicon-fix.md` |
| ChromaDB 0.4.x → `query()`/`peek()`/`count()` all fail with seq_id BLOB | → `references/chromadb-seq-id-blob-fix.md` |
| ChromaDB Settings + Pydantic v2 → "extra fields not permitted" | → `references/pydantic-v1-v2-chromadb-fix.md` |

## Scripts

- `scripts/chromadb-rebuild-from-sqlite.py` — Rebuild a ChromaDB collection from raw SQLite when seq_id BLOB lockout blocks `query()`/`peek()`/`count()`.

## Common Patterns

### Diagnose a ChromaDB Failure

Before reinventing a fix, check the three most likely categories:

1. **NumPy 2.x alias removal** — fixes the import error after `pip install -U numpy`. Affects ChromaDB ≤ 0.4.22 on Apple Silicon or Linux Docker with NumPy ≥ 2.0.
2. **seq_id BLOB** — query() returns empty even though embeddings are in SQLite. Fixed by `scripts/chromadb-rebuild-from-sqlite.py` extracting raw rows and rebuilding the collection with a fresh embedding function.
3. **Pydantic v2** — `extra fields not permitted` when ChromaDB's `Settings` inherits pydantic v1 in a pydantic-v2 project.

### Apply a Fix

Each reference file has: symptom → version table → exact diff/patch → verification step.

## How to Add a New Fix

When you hit a NEW reproducible third-party bug and have a verified workaround:

1. Create `references/<library>-<symptom>.md` with the recipe (problem, version table, fix, verify).
2. Add a row to the Quick Routing table above.
3. (Optional) Add scripts under `scripts/` for statically-runnable workarounds.

This keeps each fix one-click-findable without bloating a single mega-file.
