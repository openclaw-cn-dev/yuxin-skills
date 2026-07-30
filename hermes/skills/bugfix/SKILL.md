---
name: bugfix
description: "Bugfix recipes — known-issue remediation patches for specific library/framework version conflicts. Each child documents one concrete bug, root cause, and tested fix."
version: 1.0.0
author: Hermes Agent (consolidation)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bugfix, chromadb, numpy, pydantic, known-issues, patches]
---

# Bugfix Recipes

Known-issue remediation patches. Each entry documents a specific bug, its root
cause, and a tested fix. Use these when you encounter the exact error signature
described.

## ChromaDB 0.4.x Fixes

ChromaDB 0.4.x has known compatibility issues with NumPy 2.x and Pydantic v2
in modern Python environments. Three separate bugs are documented below.

### 1. NumPy 2.x Compatibility (Apple Silicon / Mac Docker)

**Error signature:**
```
AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```
Variants: onnxruntime `_ARRAY_API not found`, HTTP 502 for localhost:8001 (unrelated proxy issue).

**Root cause:** ChromaDB 0.4.22 uses `np.float_/np.int_/np.uint` (NumPy 1.x aliases removed in NumPy 2.x). The Docker entrypoint re-installs chroma-hnswlib on every boot, pulling in NumPy 2.x regardless of pinning.

**Fix (Docker-based):** Patch `docker_entrypoint.sh` to pin numpy AFTER the hnswlib reinstall:
```bash
# Inside the container or Dockerfile patching:
sed -i '/pip install.*chroma-hnswlib/a\
pip install "numpy<2" --force-reinstall --no-cache-dir' docker_entrypoint.sh
```

**Fix (non-Docker):** Pin in requirements or environment:
```bash
pip install "numpy<2" chromadb==0.4.22
```

### 2. seq_id BLOB Error

**Error signature:**
```
chromadb.errors.InternalError: Error reading from metadata segment reader:
mismatched types; Rust type `u64` (INTEGER) is not compatible with SQL type `BLOB`
```
All of count(), peek(), query() fail.

**Root cause:** ChromaDB 0.4.x `_decode_seq_id()` expects INTEGER but SQLite column is BLOB. Data is intact in SQLite.

**Fix — rebuild from SQLite:**
```python
import sqlite3, chromadb
from chromadb.utils import embedding_functions

DATA_DIR = '/path/to/data/chroma'
OLD_NAME = 'lookforge_knowledge'

# Extract all records via SQLite
conn = sqlite3.connect(f'{DATA_DIR}/chroma.sqlite3')
rows = conn.execute('''
    SELECT e.id, e.embedding_id, e.string_value, d.dimension
    FROM embedding_metadata e
    JOIN embeddings d ON e.embedding_id = d.embedding_id
''').fetchall()
conn.close()

# Rebuild collection with embedding function
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path=DATA_DIR)
collection = client.create_collection(name=f'{OLD_NAME}_rebuilt', embedding_function=ef)
documents = [r[2] for r in rows if r[2]]
ids = [r[0] for r in rows if r[2]]
if ids:
    collection.add(documents=documents, ids=ids)
```

### 3. Pydantic v1/v2 Settings Conflict

**Error signature:**
```
pydantic.v1.error_wrappers.ValidationError: extra fields not permitted
```
Triggered when passing `Settings(...)` to `chromadb.PersistentClient()`.

**Root cause:** ChromaDB 0.4.x `Settings` inherits from pydantic v1, but a modern env has both pydantic v1 and v2. Pydantic v2 validation rejects v1 fields.

**Fix — omit settings parameter:**
```python
# DON'T pass settings:
_client = chromadb.PersistentClient(path=persist_dir, settings=Settings(...))  # ❌

# DO:
_client = chromadb.PersistentClient(path=persist_dir)  # ✅
```
Let ChromaDB use its internal defaults. If you need `anonymized_telemetry=False`, the correct field name is `anonymized_telemetry` (NOT `anonymized_telemetry_reporting`), but still avoid passing it — the pydantic conflict persists regardless.
