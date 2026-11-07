"""
RAG 知识库 - 中文文档查询脚本
模板：本地 bge + Chroma 检索
用法：
  python rag_query.py "你的问题"
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"

import sys
from pathlib import Path
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

# === 配置 ===
KB_DIR = Path(r"C:\Users\Administrator\Desktop\知识库")  # 改这里
CHROMA_DIR = str(KB_DIR / "chroma_db")
BGE_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5"
TOP_K = 3

# === 加载 bge（一次）===
print("🔢 加载 bge-large-zh-v1.5...", flush=True)
embeddings = HuggingFaceBgeEmbeddings(
    model_name=BGE_PATH,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
print("✅ 模型加载完成", flush=True)

# === 加载 Chroma（一次）===
db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
print("✅ Chroma 加载完成", flush=True)

def main():
    if len(sys.argv) < 2:
        print("用法: python rag_query.py <问题>")
        return
    query = " ".join(sys.argv[1:])

    print(f"\n🔍 查询: {query}\n" + "="*60)

    # 检索 Top K
    docs_with_score = db.similarity_search_with_score(query, k=TOP_K)

    print(f"📊 找到 {len(docs_with_score)} 条相关文档\n")
    for i, (doc, score) in enumerate(docs_with_score, 1):
        src = doc.metadata.get("source", "unknown").replace("\\", "/")
        print(f"--- Top {i} (相关度 {score:.4f}) ---")
        print(f"📁 来源: {src}")
        content = doc.page_content
        if len(content) > 300:
            content = content[:300] + "..."
        print(f"📝 内容: {content}")
        print()

    # 拼答案
    print("="*60)
    print("💡 建议答案（基于 Top1 整理）:\n")
    print(docs_with_score[0][0].page_content[:500])
    print(f"\n📌 引用来源: {docs_with_score[0][0].metadata.get('source','unknown')}")

if __name__ == "__main__":
    main()
