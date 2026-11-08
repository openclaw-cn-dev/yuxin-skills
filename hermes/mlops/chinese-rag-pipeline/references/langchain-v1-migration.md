# langchain 0.1+ 拆包迁移指南

## 背景

langchain 0.1+ 把整个 monorepo 拆成多个独立包：
- `langchain` —— 核心抽象（缩减）
- `langchain-core` —— 基础接口（Document, BaseMessage）
- `langchain-community` —— 第三方集成（Chroma, HuggingFace, OpenAI）
- `langchain-text-splitters` —— 文本切分
- `langchain-openai` / `langchain-anthropic` —— LLM 集成（**独立**）
- `langchain-chroma` / `langchain-huggingface` —— 向量库 / Embedding（**新**）

## 错误信息速查

| 错误 | 旧导入 | 新导入 |
|---|---|---|
| `ImportError: cannot import name 'RecursiveCharacterTextSplitter' from 'langchain'` | `from langchain.text_splitter import RecursiveCharacterTextSplitter` | `from langchain_text_splitters import RecursiveCharacterTextSplitter` |
| `ImportError: cannot import name 'Document' from 'langchain'` | `from langchain.docstore.document import Document` | `from langchain_core.documents import Document` |
| `ImportError: cannot import name 'HuggingFaceBgeEmbeddings' from 'langchain'` | `from langchain.embeddings import HuggingFaceBgeEmbeddings` | `from langchain_community.embeddings import HuggingFaceBgeEmbeddings` |
| `ImportError: cannot import name 'Chroma' from 'langchain'` | `from langchain.vectorstores import Chroma` | `from langchain_community.vectorstores import Chroma` |
| `DeprecationWarning: class Chroma was deprecated` | `from langchain_community.vectorstores import Chroma` | `from langchain_chroma import Chroma` |

## 安装清单

```bash
uv pip install langchain langchain-core langchain-community langchain-text-splitters
# 可选
uv pip install langchain-chroma langchain-huggingface
```

## 完整新代码模板

```python
# 文本切分
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 文档类型
from langchain_core.documents import Document

# Embedding
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# 新版（推荐）
# from langchain_huggingface import HuggingFaceEmbeddings

# 向量库
from langchain_community.vectorstores import Chroma
# 新版（推荐）
# from langchain_chroma import Chroma

# LLM
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
```

## DeprecationWarning 不影响运行

`langchain_community.embeddings.HuggingFaceBgeEmbeddings` 还能用，**只是有 warning**：

```
LangChainDeprecationWarning: The class `HuggingFaceBgeEmbeddings` was deprecated in LangChain 0.2.2
```

**忽略 warning 不影响功能**——**新项目用 langchain-huggingface**——**老项目可以保持**。

## 中文 RAG 实战组合

```python
# 1. 加载 + 切分
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
)
chunks = splitter.split_documents(docs)

# 2. Embedding（中文 SOTA）
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
embeddings = HuggingFaceBgeEmbeddings(
    model_name=r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# 3. 索引
from langchain_community.vectorstores import Chroma
db = Chroma.from_documents(
    chunks, embeddings,
    persist_directory=r"C:\Users\Administrator\Desktop\知识库\chroma_db"
)
```

## 关键 takeaway

> **拆包不是破坏**——**是组织**——**新项目用独立包**——**老项目升级时逐个 import 改**
> **遇到 ImportError 第一反应** —— **去 pypi 搜 `langchain-*` 独立包**
