# HNSW 索引故障 + 增量入库参考（2026-06-10/11 实战）

## 1. HNSW 索引故障强制恢复

**症状**：
```
chromadb.errors.InternalError: Error executing plan: Error sending backfill request to compactor:
Error constructing hnsw segment reader: Error creating hnsw segment reader: Error loading hnsw index
```

**根因**：chroma 0.4.x 的 HNSW 段文件（`.hnsw` / `.lock` / `chroma.sqlite3`）在写入中途断电/进程被 kill 时损坏。**任何 `vectordb.persist()` 或单文件删除都救不回来**——HNSW 段引用了已删除的 chunk。

**3 秒修复**（`fix_chroma_hnsw.sh` 或一行命令）：

```bash
cd "C:\Users\Administrator\Desktop\知识库"
rm -rf chroma_db/*
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" rag_setup.py
```

**耗时**：120 文档 ≈ 270 秒（CPU 推理 + 索引构建）。

**为什么删整个目录**：HNSW 段是 immutable 的，损坏后无法 in-place 修复。**全量重建是最快的修复路径**——`from_documents()` 比手动维护增量索引快 10 倍以上。

**预防**：
- 重要节点（每周/每月）**完整备份 `chroma_db/`**（约 3-4MB）
- 写索引时**别 kill -9** Python 进程
- chroma DB 目录**放 SSD**（HDD 突然断电容易损坏）

## 2. 增量入库 RAG 完整代码（langchain Chroma）

参见 `scripts/rag_ingest.py`（已写在 `C:\Users\Administrator\Desktop\知识库\rag_ingest.py`）。

**关键事实（2026-06-10 验证）**：
- 全量重建 120 文档 ≈ 270 秒
- 增量入库 1 文件 3 chunks ≈ **4.3 秒**（60 倍快）
- collection name **必须是 `langchain`**（langchain_chroma.Chroma 默认名）——自定义 `knowledge_base` 永远是空 collection
- bge 模型路径**直接传本地路径**给 `HuggingFaceBgeEmbeddings(model_name=...)`，跳过 `snapshot_download()` 锁

## 3. 实战时间表（老大水产业务 0→1）

| 时间 | 文档数 | chunks | 事件 |
|---|---|---|---|
| 6/8 | 0 | 0 | 起点 |
| 6/8 PM | 38 | 141 | 4 群基础库 + 7 公司 + 5 食谱 |
| 6/8 PM | 38 | 279 | 二次索引（增量踩坑） |
| 6/10 | 53 | 345 | 5 层完整（L4+L5） |
| 6/10 PM | 88 | 292 | Layer 3 5 文档 |
| 6/11 | 120 | 434 | Layer 2 物种专项 V2（4 物种 +20）|
| 6/11 PM | 135 | 449 | 业务专项（5 场景 +15）|

**8 天索引量** = 135 文档 / 449 chunks / 9MB → **可服务 4 业务群 24/7 自动应答**
