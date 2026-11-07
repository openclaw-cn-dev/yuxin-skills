"""
rag_ingest.py - RAG 增量入库脚本（langchain Chroma，2026-06-10 验证）

策略：
  1. 加载现有 Chroma（不重建全库）
  2. 把新 md 文件转 Document
  3. 切 chunk（500字 / 重叠 50）
  4. 调 add_documents 增量入库

⚠️ Pitfall（重要）：
  - langchain_chroma.Chroma 默认 collection 名 = `langchain`
  - **不要自定义 `collection_name="knowledge_base"`**（会新建空 collection）
  - bge 模型走 ModelScope 本地路径，**避免 HF-Mirror 1.3GB 卡死**

用法：
  # 增量入库（命令行）
  python rag_ingest.py file1.md file2.md

  # 在 Python 中调用
  from rag_ingest import ingest_files
  n = ingest_files([str(md_path)], category="搜索抓取")

  # 验证现有 chunks
  python rag_ingest.py --verify

  # 全量重建（极少用，5-10 分钟）
  python rag_ingest.py --reindex
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"

import time
import sys
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 默认路径（可通过环境变量覆盖）
KB_DIR = Path(os.environ.get("KB_DIR", r"C:\Users\Administrator\Desktop\知识库"))
DB_DIR = str(KB_DIR / "chroma_db")
MS_MODEL_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1___5"
COLLECTION_NAME = "langchain"  # ⚠️ 必须用 langchain_chroma 默认名


def get_vectordb():
    """加载现有 Chroma 向量库（增量入库用）"""
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=MS_MODEL_PATH,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vectordb = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    return vectordb


def ingest_files(md_files: list, category: str = "搜索抓取") -> int:
    """
    增量入库 md 文件到 RAG
    返回入库的 chunk 数
    """
    if not md_files:
        return 0

    # 1. 转 Document
    docs = []
    for f in md_files:
        try:
            content = Path(f).read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
            rel = Path(f).relative_to(KB_DIR) if Path(f).is_absolute() else Path(f)
            meta = {"source": str(rel), "category": category}
            docs.append(Document(page_content=content, metadata=meta))
        except Exception as e:
            print(f"   ⚠️ 跳过 {f}: {e}")

    if not docs:
        return 0

    # 2. 切 chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"   ✂️  切出 {len(chunks)} 个 chunk", flush=True)

    # 3. 加载现有向量库
    print(f"   📂 加载现有 Chroma...", flush=True)
    vectordb = get_vectordb()

    # 4. 增量入库
    print(f"   💾 增量入库...", flush=True)
    t0 = time.time()
    vectordb.add_documents(chunks)
    # 0.4.x 自动 persist，下面这一行是 deprecated 警告（无害）
    try:
        vectordb.persist()
    except Exception:
        pass
    print(f"   ✅ 入库完成 ({time.time()-t0:.1f}s)", flush=True)

    return len(chunks)


def reindex_full():
    """
    全量重建（保留兼容性，对应老 rag_setup.py）
    ⚠️ 慎用：5-10 分钟，期间 RAG 不可用
    """
    import shutil
    print("⚠️  即将全量重建 RAG 索引...")
    if Path(DB_DIR).exists():
        shutil.rmtree(DB_DIR)
        print("   删除旧 DB")

    from subprocess import run
    result = run(
        ["python", str(KB_DIR / "rag_setup.py")],
        capture_output=True, text=True, encoding="utf-8"
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 重建失败: {result.stderr}")
    return result.returncode == 0


def verify():
    """验证现有 RAG 状态"""
    vdb = get_vectordb()
    print(f"   collection: {vdb._collection.name}")
    print(f"   现有 chunk 数: {vdb._collection.count()}")
    print(f"   DB 位置: {DB_DIR}")
    return vdb._collection.count()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--verify":
        print("rag_ingest.py -- 验证现有 RAG...")
        verify()
    elif args[0] == "--reindex":
        reindex_full()
    else:
        # 入库指定文件
        files = [a for a in args if not a.startswith("--")]
        if not files:
            print("用法: python rag_ingest.py file1.md file2.md")
            print("      python rag_ingest.py --verify")
            print("      python rag_ingest.py --reindex")
            sys.exit(1)
        print(f"📥 增量入库 {len(files)} 个文件...")
        n = ingest_files(files)
        print(f"\n✅ 入库完成：{n} chunks")
        print(f"📊 现有总数：{verify()}")
