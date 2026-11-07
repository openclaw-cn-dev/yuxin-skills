"""
RAG 知识库 - 中文文档索引脚本
模板：Chroma + bge-large-zh-v1.5 + langchain
用法：
  1. 改 KB_DIR 为你的知识库目录
  2. python rag_setup.py
  3. 输出: chroma_db/ 目录 + chunk 统计
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"

import time
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# === 配置 ===
KB_DIR = Path(r"C:\Users\Administrator\Desktop\知识库")  # 改这里
DB_DIR = str(KB_DIR / "chroma_db")
BGE_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# === 1. 加载文档 ===
print("📂 加载文档...", flush=True)
t0 = time.time()

# 找所有 .md（可改 .txt / .pdf）
md_files = list(KB_DIR.rglob("*.md"))
docs = []
for f in md_files:
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            continue
        rel = f.relative_to(KB_DIR)
        meta = {
            "source": str(rel),
            "category": rel.parts[0] if len(rel.parts) > 1 else "根目录"
        }
        docs.append(Document(page_content=content, metadata=meta))
    except Exception as e:
        print(f"   ⚠️ 跳过 {f.name}: {e}", flush=True)

print(f"✅ 加载 {len(docs)} 个文档 ({time.time()-t0:.1f}s)", flush=True)

# === 2. 切分 ===
print(f"\n✂️  切分 chunk ({CHUNK_SIZE}字 / 重叠{CHUNK_OVERLAP})...", flush=True)
t0 = time.time()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
)
chunks = splitter.split_documents(docs)
print(f"✅ 切出 {len(chunks)} 个 chunk ({time.time()-t0:.1f}s)", flush=True)

# === 3. 加载 bge（用本地 modelscope 路径，不要 snapshot_download）===
print(f"\n🔢 加载 bge-large-zh-v1.5...", flush=True)
t0 = time.time()

embeddings = HuggingFaceBgeEmbeddings(
    model_name=BGE_PATH,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
print(f"✅ 模型加载完成 ({time.time()-t0:.1f}s)", flush=True)

# === 4. 索引到 Chroma ===
print(f"\n📦 索引到 Chroma ({DB_DIR})...", flush=True)
t0 = time.time()

db = Chroma.from_documents(
    chunks, embeddings,
    persist_directory=DB_DIR,
    # collection_name 默认是 "langchain"
)
db.persist()

print(f"✅ 索引完成 ({time.time()-t0:.1f}s)", flush=True)
print(f"\n🎉 完成！向量库在 {DB_DIR}")
print(f"   文档数: {len(docs)}")
print(f"   Chunk 数: {len(chunks)}")
