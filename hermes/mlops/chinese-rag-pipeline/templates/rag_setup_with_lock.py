"""
RAG 知识库 - 中文文档索引脚本（**带进程锁版**，防坑 17）

与 templates/rag_setup.py 的区别：
- 启动时检查 `.rag_setup.lock` 文件里的 PID 是否还活着
- 还活着 → 直接退出（避免两个 rag_setup.py 并发跑导致 HNSW 损坏）
- 启动时清理 chroma_db.broken_* 旧库（保留最新 1 个，详见坑 16a）
- 退出时自动释放锁

用法：
  python rag_setup_with_lock.py

依赖：Windows（用了 tasklist 检查 PID）
Unix 改 is_pid_alive() 用 `kill -0` 即可
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"

import sys
import time
import atexit
import shutil
import subprocess
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# === 配置 ===
KB_DIR = Path(r"C:\Users\Administrator\Desktop\知识库")
DB_DIR = str(KB_DIR / "chroma_db")
BGE_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
LOCK_FILE = KB_DIR / ".rag_setup.lock"


# === 进程锁（防坑 17）===
def is_pid_alive(pid: int) -> bool:
    """Windows 检查 PID 是否还活着"""
    if pid <= 0:
        return False
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True, timeout=5
        )
        return str(pid) in r.stdout
    except Exception:
        return False


def acquire_lock() -> bool:
    """尝试获取锁。返回 True=拿到锁，False=已有别的进程在跑"""
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            if is_pid_alive(old_pid):
                print(f"❌ 已有 rag_setup.py 在跑（PID {old_pid}）— 拒绝启动避免并发损坏 chromadb",
                      file=sys.stderr)
                print(f"   如果确认没有别的进程在跑，删 {LOCK_FILE} 后重试",
                      file=sys.stderr)
                return False
            else:
                print(f"🧹 清 stale lock（PID {old_pid} 已退出）", flush=True)
        except (ValueError, FileNotFoundError):
            # 锁文件损坏，当作没锁
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    """释放锁（atexit 调用）"""
    try:
        if LOCK_FILE.exists():
            # 只删属于自己的锁（防止误删别人的）
            try:
                stored = int(LOCK_FILE.read_text().strip())
                if stored == os.getpid():
                    LOCK_FILE.unlink()
            except (ValueError, FileNotFoundError):
                pass
    except Exception:
        pass


# === 启动清理（防坑 16a 旧 broken 库累积）===
def cleanup_old_broken_dbs():
    """保留最近 1 个 chroma_db.broken_*，清掉其余"""
    broken = sorted(KB_DIR.glob("chroma_db.broken_*"),
                    key=lambda p: p.stat().st_mtime, reverse=True)
    for old in broken[1:]:  # 跳过最新 1 个
        try:
            size_mb = old.stat().st_size / 1024 / 1024 if old.is_file() else 0
            if old.is_dir():
                size_mb = sum(f.stat().st_size for f in old.rglob('*') if f.is_file()) / 1024 / 1024
            print(f"🧹 清旧 broken 库: {old.name} ({size_mb:.1f}M)", flush=True)
            shutil.rmtree(old, ignore_errors=True)
        except Exception as e:
            print(f"   ⚠️ 跳过 {old.name}: {e}", flush=True)


def main():
    # 1. 进程锁
    if not acquire_lock():
        sys.exit(1)
    atexit.register(release_lock)

    # 2. 清理旧 broken 库
    cleanup_old_broken_dbs()

    # 3. 加载文档
    print("📂 加载文档...", flush=True)
    t0 = time.time()
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

    # 4. 切分
    print(f"\n✂️  切分 chunk ({CHUNK_SIZE}字 / 重叠{CHUNK_OVERLAP})...", flush=True)
    t0 = time.time()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ 切出 {len(chunks)} 个 chunk ({time.time()-t0:.1f}s)", flush=True)

    # 5. 加载 bge
    print(f"\n🔢 加载 bge-large-zh-v1.5...", flush=True)
    t0 = time.time()
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=BGE_PATH,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    print(f"✅ 模型加载完成 ({time.time()-t0:.1f}s)", flush=True)

    # 6. 索引
    print(f"\n📦 索引到 Chroma ({DB_DIR})...", flush=True)
    t0 = time.time()
    db = Chroma.from_documents(
        chunks, embeddings,
        persist_directory=DB_DIR,
    )
    db.persist()
    print(f"✅ 索引完成 ({time.time()-t0:.1f}s)", flush=True)

    print(f"\n🎉 完成！向量库在 {DB_DIR}")
    print(f"   文档数: {len(docs)}")
    print(f"   Chunk 数: {len(chunks)}")


if __name__ == "__main__":
    main()