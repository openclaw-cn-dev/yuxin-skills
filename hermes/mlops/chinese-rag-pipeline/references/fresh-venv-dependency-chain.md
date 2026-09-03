# Fresh Venv RAG Dependency Install Chain

**验证日期**：2026-07-07
**环境**：Hermes venv (Python 3.11), Windows 10, 清华源

## 安装顺序（**顺序重要！**）

```bash
# Step 1: langchain 全家桶 + chromadb 0.4.24（一起装，避免 NumPy 冲突）
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  langchain langchain-text-splitters langchain-community langchain-core \
  "chromadb==0.4.24"

# Step 2: sentence-transformers（会拉 NumPy 2.x + torch）
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  sentence-transformers

# Step 3: 降级 NumPy（chromadb 0.4.24 不兼容 NumPy 2.x）
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "numpy<2.0"
```

## 为什么这个顺序

| 顺序 | 如果搞反了 | 后果 |
|---|---|---|
| sentence-transformers 先装 | NumPy 2.x 先进来 → chromadb import 崩 | `np.float_` removed (坑13) |
| chromadb 后装 | 已经有的 NumPy 2.x 不兼容 | 同上 |
| numpy 不降级 | chromadb 0.4.24 + NumPy 2.x = 必崩 | `AttributeError: np.float_` |

## 验证

```bash
python -c "
import chromadb; print('chromadb', chromadb.__version__)
import numpy; print('numpy', numpy.__version__)
import langchain_text_splitters; print('text_splitters ok')
import langchain_community.embeddings; print('embeddings ok')
from langchain_community.vectorstores import Chroma; print('Chroma ok')
"
# 预期输出：
# chromadb 0.4.24
# numpy 1.26.4
# text_splitters ok
# embeddings ok
# Chroma ok
```

## 坑

- ❌ `uv pip install` 可能报 `Could not acquire lock`（uv cache 锁），换 `python -m pip`
- ❌ 清华源偶尔卡 `chroma-hnswlib` 下载 → 等 30 秒重试
- ✅ 装完 sentence-transformers 后 NumPy 必是 2.x → **必须降级**
