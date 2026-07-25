---
name: bugfix
description: Library of reproduction recipes for real bug-fix sessions — primarily ChromaDB 0.4.x runtime issues and other MLOps dependencies. Each entry under references/ is a self-contained "what broke, why, exact fix, verification" record. Load this skill when debugging ChromaDB startup / API / persistence errors or when working with Pydantic v1/v2 interop in Python RAG stacks.
version: 1.0.0
metadata:
  hermes:
    tags: [bugfix, chromadb, rag, troubleshooting, runtime-fixes]
---

# Bugfix Library

Class-level umbrella for **real bug-fix sessions** — not theory, not docs links, but exact reproductions we hit in production.

## When to use this skill

- ChromaDB container fails to start (NumPy 2.x alias removed)
- ChromaDB 0.4.x `query()`/`peek()`/`count()` returns InternalError / BLOB type mismatch
- Pydantic v1 vs v2 conflict with ChromaDB Settings
- Any future runtime bug in the MLOps stack (HuggingFace, llama-cpp, vLLM, etc.)

**NOT for**: theoretical docs, library API references, generic "how to use ChromaDB" content. This is a *bug recipe library* — load only when you have a specific failure signature matching one of the entries.

## Reference index

Each `references/*.md` file is a complete fix recipe. Load the one matching your error signature:

### ChromaDB family (most common)

- `references/chromadb-numpy2-applesilicon-fix.md` — Container dies with `np.float_ was removed in the NumPy 2.0 release`. Build a patched image.
- `references/chromadb-seq-id-blob-fix.md` — `query()/peek()/count()` all fail with Rust/SQLite type mismatch on `seq_id`. Rebuild collection by extracting from SQLite directly.
- `references/pydantic-v1-v2-chromadb-fix.md` — `pydantic.v1.error_wrappers.ValidationError: extra fields not permitted` on `chromadb.PersistentClient`. Drop the `settings` parameter.

## Recipe format

Every reference file follows the same skeleton so you can scan it fast under pressure:

1. **Symptom** — the exact error string or observable behavior
2. **Root cause** — why it happens
3. **Fix** — copy-paste-ready commands or code
4. **Verification** — how to confirm it worked
5. **Failed approaches** — what NOT to try (saves time)

## Adding new entries

When you hit a bug that takes more than 30 minutes to resolve and the fix is non-obvious, write a new `references/<bug-name>.md` following the recipe format above. Do not create a new top-level skill — add to this umbrella.
