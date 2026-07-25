---
name: knowledge-base
description: ChromaDB integration patterns for project knowledge bases — embedding model fallback (sentence-transformers), and project-specific health monitoring. Load when wiring ChromaDB into a project or debugging RAG retrieval.
version: 1.0.0
metadata:
  hermes:
    tags: [knowledge-base, chromadb, sentence-transformers, rag, embeddings]
---

# Knowledge Base

Class-level umbrella for **project knowledge base patterns** — primarily ChromaDB integration. Recipe-style skills, not general-purpose.

## Children

- `chromadb-sentence-transformers/` — Use sentence-transformers with ChromaDB when the built-in ONNX embedding model fails (SSL timeout, corruption, network blocks).

## Related

- `bugfix/` — Generic ChromaDB 0.4.x runtime fixes (numpy 2.x, seq_id BLOB, Pydantic v1/v2).
- `product-debugging/references/lookforge-chromadb-debug.md` — LookForge-specific ChromaDB deployment issues.
- `product-debugging/references/lookforge-knowledge-health.md` — LookForge ChromaDB 知识库健康度监控.
