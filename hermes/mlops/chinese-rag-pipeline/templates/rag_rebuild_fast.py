# -*- coding: utf-8 -*-
"""
rag_rebuild_fast.py —— RAG 重建（跳过 ModelScope snapshot_download，直接用 HF 缓存）

何时用：
- rag_setup.py 调 snapshot_download 卡死（坑 18，2026-06-18 6 点巡检撞）
- HF 缓存里 bge-large-zh-v1.5 已完整（~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/<hash>/）
- ModelScope 缓存残缺 / 网络抽风

与 rag_setup.py 的关键差异：
- ❌ 不调 snapshot_download
- ✅ 直接 HuggingFaceBgeEmbeddings(model_name=BGE_PATH) 喂 HF snapshot 路径
- ✅ 关掉 ANONYMIZED_TELEMETRY（chromadb 0.4.x telemetry 噪声）

使用方法：
1. 把 BGE_PATH 改成你机器上 HF snapshot 的实际路径（ls ~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/）
2. terminal(background=true, notify_on_complete=true) 跑 —— 10-15 分钟
3. 等 notify 回来发"✅ RAG 重建完成"卡片
"""
import os, time, sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

KB_DIR = Path(r"C:\Users\Administrator\Desktop\知识库")
DB_DIR = str(KB_DIR / "chroma_db")
# ⚠️ 改成你机器上的实际 snapshot hash 目录名
BGE_PATH = r"C:\Users\Administrator\.cache\huggingface\hub\models--BAAI--bge-large-zh-v1.5\snapshots\79e7739b6ab944e86d6171e44d24c997fc1e0116"

# === Step 1: 加载文档 ===
print(f"[{time.strftime('%H:%M:%S')}] 1/3 加载文档...", flush=True)
md_files = list(KB_DIR.rglob("*.md"))
docs = []
for f in md_files:
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            continue
        rel = f.relative_to(KB_DIR)
        meta = {"source": str(rel), "category": rel.parts[0] if len(rel.parts) > 1 else "根目录"}
        docs.append(Document(page_content=content, metadata=meta))
    except Exception as e:
        print(f"   跳过 {f.name}: {e}", flush=True)
print(f"[{time.strftime('%H:%M:%S')}]   文档 {len(docs)}", flush=True)

# === Step 2: 切 chunk ===
print(f"[{time.strftime('%H:%M:%S')}] 2/3 切 chunk (500字/重叠50)...", flush=True)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
)
chunks = splitter.split_documents(docs)
print(f"[{time.strftime('%H:%M:%S')}]   chunk {len(chunks)}", flush=True)

# === Step 3: 加载 bge（直接 HF 路径，0 网络）===
print(f"[{time.strftime('%H:%M:%S')}] 3/3 加载 bge (HF 缓存 {BGE_PATH[-12:]})...", flush=True)
t0 = time.time()
embeddings = HuggingFaceBgeEmbeddings(
    model_name=BGE_PATH,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
print(f"[{time.strftime('%H:%M:%S')}]   bge 加载 {time.time()-t0:.1f}s", flush=True)

# === Step 4: 索引到 Chroma ===
print(f"[{time.strftime('%H:%M:%S')}] 4/4 索引 (预计 9-15 分钟)...", flush=True)
t0 = time.time()
vectordb = Chroma.from_documents(
    chunks, embeddings,
    collection_name="langchain",
    persist_directory=DB_DIR,
)
print(f"[{time.strftime('%H:%M:%S')}]   索引 {time.time()-t0:.1f}s", flush=True)

# === Step 5: persist + verify ===
vectordb.persist()
cnt = vectordb._collection.count()
print(f"[{time.strftime('%H:%M:%S')}] ✅ 完成！chunks={cnt}", flush=True)
print(f"[{time.strftime('%H:%M:%S')}] 路径: {DB_DIR}", flush=True)

# === Step 6: 健康检查 ===
import chromadb
client = chromadb.PersistentClient(path=DB_DIR)
cols = client.list_collections()
for c in cols:
    print(f"[{time.strftime('%H:%M:%S')}]   collection={c.name} count={c.count()}", flush=True)