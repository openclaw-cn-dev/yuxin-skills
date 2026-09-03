# -*- coding: utf-8 -*-
"""
rag_multi_group_query.py - 多群 RAG 查询 + 飞书推送模板

用法:
  # CLI 单次查询
  python rag_multi_group_query.py "你的问题"

  # 推送到 4 群
  python rag_multi_group_query.py --push "你的问题"

  # stdin 监听模式
  python rag_multi_group_query.py --watch

依赖:
  pip install langchain langchain-community langchain-core
  pip install chromadb sentence-transformers
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

# ====== 配置 ======
KB_DIR = Path(r"C:\Users\Administrator\Desktop\知识库")
CHROMA_DIR = str(KB_DIR / "chroma_db")
BGE_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5"
GROUPS_CONFIG = KB_DIR / "groups_config.json"

# ====== 加载 bge + Chroma（只一次）======
embeddings = HuggingFaceBgeEmbeddings(
    model_name=BGE_PATH,  # 关键：本地路径，跳过 modelscope snapshot_download
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

# ====== 工具函数 ======
def query_rag(query: str, top_k: int = 3):
    """查 RAG → (top1_content, [(source, score), ...])"""
    docs_with_score = db.similarity_search_with_score(query, k=top_k)
    if not docs_with_score:
        return "（未找到相关文档）", []
    citations = []
    for doc, score in docs_with_score:
        src = doc.metadata.get("source", "unknown").replace("\\", "/")
        citations.append((src, score))
    return docs_with_score[0][0].page_content, citations


def format_response(query: str, answer: str, citations):
    """拼飞书消息"""
    lines = [
        f"🔍 **RAG 查询**: {query}",
        "",
        f"💡 **答案**:",
        answer[:600] + ("..." if len(answer) > 600 else ""),
        "",
        "📌 **引用来源**:",
    ]
    for i, (src, score) in enumerate(citations, 1):
        lines.append(f"  {i}. `{src}` (相关度 {score:.2f})")
    lines.append("")
    lines.append(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    return "\n".join(lines)


def push_feishu(chat_id: str, message: str):
    """用 hermes send 推飞书"""
    cmd = ["hermes", "send", "feishu", chat_id, "--message", message]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            if "230002" in result.stderr:
                return False, f"❌ {chat_id} 机器人不在群（老大手动加）"
            elif "230020" in result.stderr:
                return False, f"❌ {chat_id} 权限不足（飞书后台加 im:message）"
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        pending = KB_DIR / "feishu_rag_pending.txt"
        with open(pending, "a", encoding="utf-8") as f:
            f.write(f"\n=== {datetime.now()} → {chat_id} ===\n{message}\n")
        return False, f"hermes CLI 不可用，已写到 {pending}"


def push_to_all_groups(query: str, response: str):
    """推送到所有 active 群"""
    if not GROUPS_CONFIG.exists():
        return [], "❌ groups_config.json 不存在"
    config = json.loads(GROUPS_CONFIG.read_text(encoding="utf-8"))
    results = []
    for group in config.get("groups", []):
        if group.get("status") != "active":
            continue
        if "FILL_IN" in group.get("chat_id", ""):
            continue
        ok, log = push_feishu(group["chat_id"], response)
        results.append((group["name"], ok, log))
    return results, None


# ====== 主程序 ======
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="查询问题")
    parser.add_argument("--push", action="store_true", help="推送到所有 active 群")
    parser.add_argument("--watch", action="store_true", help="stdin 监听模式")
    args = parser.parse_args()

    if args.watch:
        print("📝 stdin 监听模式 (粘贴消息回车, Ctrl+C 退出)")
        for line in sys.stdin:
            text = line.strip()
            if not text or "RAG:" not in text:
                continue
            query = text.split("RAG:", 1)[1].strip()
            answer, citations = query_rag(query)
            print(format_response(query, answer, citations))
            print("=" * 60)
        return

    if not args.query:
        parser.print_help()
        return

    answer, citations = query_rag(args.query)
    response = format_response(args.query, answer, citations)
    print(response)

    if args.push:
        results, err = push_to_all_groups(args.query, response)
        if err:
            print(f"\n{err}")
            return
        print("\n📤 推送结果:")
        for name, ok, log in results:
            icon = "✅" if ok else "❌"
            print(f"  {icon} {name}: {log}")


if __name__ == "__main__":
    main()
