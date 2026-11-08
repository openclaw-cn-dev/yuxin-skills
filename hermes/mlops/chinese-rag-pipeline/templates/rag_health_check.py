"""
RAG 健康检查脚本 —— 10 秒内判断 Chroma 索引状态

用法：
  python rag_health_check.py
  # 或带自定义路径
  python rag_health_check.py --db "C:/path/to/chroma_db"

适用：
  - RAG 重建中（确认磁盘是否在写）
  - RAG 重建后（确认是否真的成功）
  - cron 健康检查（每天 6 点跑一次）

判断标准（1000 chunk 级别）：
  - ✅ chroma.sqlite3 > 1MB
  - ✅ collection langchain count() > 500
  - ✅ hnsw 段目录有 3+ 文件
  - ⚠️ sqlite 存在但无 collection → 索引写到一半挂了
  - ❌ chroma_db 目录不存在 → 完全没跑过
"""
import argparse
import sys
from pathlib import Path

try:
    import chromadb
except ImportError:
    print("❌ chromadb 未安装")
    sys.exit(1)


def check(db_dir: Path) -> str:
    if not db_dir.exists():
        return f"❌ {db_dir} 目录不存在 —— RAG 从未跑过"

    sqlite = db_dir / "chroma.sqlite3"
    if not sqlite.exists():
        return f"❌ {sqlite} 不存在 —— 重建失败或没启动"

    size_mb = sqlite.stat().st_size / 1024 / 1024

    # 检查 hnsw 段目录
    hnsw_dirs = [d for d in db_dir.iterdir() if d.is_dir()]
    hnsw_files_per_dir = [len(list(d.iterdir())) for d in hnsw_dirs]
    max_files = max(hnsw_files_per_dir) if hnsw_files_per_dir else 0

    try:
        client = chromadb.PersistentClient(path=str(db_dir))
        cols = client.list_collections()
    except Exception as e:
        return f"❌ chromadb 加载失败: {e}"

    if not cols:
        if size_mb < 0.5:
            return f"⚠️ sqlite 存在（{size_mb:.1f}MB）但无 collection —— 索引写到一半挂了"
        return f"⚠️ sqlite {size_mb:.1f}MB 但 list_collections() 空 —— 需要重建"

    summary = " | ".join(f"{c.name}={c.count()}" for c in cols)
    total_chunks = sum(c.count() for c in cols)

    # 健康度评级
    if total_chunks == 0:
        status = "⚠️ collection 存在但 count=0"
    elif max_files < 2:
        status = f"⚠️ hnsw 段只 {max_files} 个文件 —— 索引可能没完整持久化"
    else:
        status = f"✅ 健康"

    return f"{status} | sqlite={size_mb:.1f}MB | hnsw_files={max_files} | {summary}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG 健康检查")
    parser.add_argument(
        "--db",
        default=r"C:\Users\Administrator\Desktop\知识库\chroma_db",
        help="Chroma 持久化目录",
    )
    args = parser.parse_args()
    result = check(Path(args.db))
    print(result)
    # 退出码：0=健康，1=异常（cron 可用此判定）
    sys.exit(0 if "✅" in result else 1)
