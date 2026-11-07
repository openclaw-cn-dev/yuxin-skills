# ChromaDB 1.x HNSW 持久化 Bug（实战 2026-06-12）

## TL;DR

**别用 chromadb 1.x。锁死 `chromadb==0.4.24` + `chroma-hnswlib==0.7.3`。**

## 现象

- `co.count()` / `co.get()` / `co.query()` 全部抛：
  ```
  chromadb.errors.InternalError: Error executing plan: Error sending backfill request to compactor:
  Error constructing hnsw segment reader: Error creating hnsw segment reader: Error loading hnsw index
  ```
- `chroma.sqlite3` 看着有数据（1013 行 embeddings）
- hnsw 段目录 `chroma_db/<uuid>/` 只有 **1 个 `index_metadata.pickle`**
- pickle 里 `dimensionality: None, max_seq_id: None` —— 索引根本没初始化
- 用 `langchain_community.vectorstores.Chroma.from_documents(...)` + `.persist()` 100% 复现

## 诊断 3 步（5 秒判断是不是这个 bug）

```bash
# 1. 看版本
python -c "import chromadb; print(chromadb.__version__)"
# 输出 1.x = 命中

# 2. 看 hnsw 段目录有几个文件
ls "C:/Users/Administrator/Desktop/知识库/chroma_db/"*/
# 只有 1 个 index_metadata.pickle = 命中

# 3. 看 pickle 内容
python -c "
import pickle
with open('C:/Users/Administrator/Desktop/知识库/chroma_db/' + 
          __import__('os').listdir('C:/Users/Administrator/Desktop/知识库/chroma_db/')[0] + 
          '/index_metadata.pickle', 'rb') as f:
    m = pickle.load(f)
print('dim:', m.get('dimensionality'), 'max_seq_id:', m.get('max_seq_id'))
# 都 None = 命中
"
```

## 修复（实测 6/12 凌晨 100% 解决）

```bash
# 1. 降级
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" \
  -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "chromadb==0.4.24"

# 2. 删旧库（1.x 格式和 0.4 不兼容）
rm -rf "C:/Users/Administrator/Desktop/知识库/chroma_db"
# 备份到一边以防回滚
mv "C:/Users/Administrator/Desktop/知识库/chroma_db" \
   "C:/Users/Administrator/Desktop/知识库/chroma_db.broken_$(date +%Y%m%d_%H%M%S)"

# 3. 重建
cd "C:/Users/Administrator/Desktop/知识库"
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" rag_setup.py

# 4. 验证
python -c "
import chromadb
c = chromadb.PersistentClient(path='C:/Users/Administrator/Desktop/知识库/chroma_db')
co = c.get_collection('langchain')
print('count:', co.count())  # 应该输出实际数字，不抛错
"

# 5. 锁死版本（防别的 wrapper 静默升级）
pip freeze | grep -i chromadb
# 期望：chromadb==0.4.24 + chroma-hnswlib==0.7.3
```

## 原理

- chromadb 0.4.x：hnsw 段用 `chroma-hnswlib`（C++ hnswlib 绑定），写盘稳定
- chromadb 1.0+：hnsw 段用 **rust 内置实现**，indexing/persistence 在 langchain 包装的写入路径上有 bug
- 写入路径：langchain `Chroma.from_documents()` → `add()` → chromadb 客户端 → rust hnsw segment → flush
  - sqlite flush 成功（`chroma.sqlite3` 写完）
  - hnsw segment flush 失败（`index_metadata.pickle` 写出但 `hnswlib_index.bin` 这种没写）
  - 下次启动读 hnsw 段 → 找不到 data file → "Error loading hnsw index"

## 预防

- **`requirements.txt` 锁死 `chromadb==0.4.24`**
- CI / cron 重建前 `pip show chromadb` 确认版本
- 任何 `pip install` 升级 langchain / langchain-community / sentence-transformers **之后**都跑一次
  ```bash
  pip show chromadb | grep Version
  # 看到 1.x 就立刻降级
  ```
- 每天 21:00 cron 健康检查：
  ```python
  import chromadb
  from pathlib import Path
  c = chromadb.PersistentClient(path=str(Path(r'C:\Users\Administrator\Desktop\知识库\chroma_db')))
  co = c.get_collection('langchain')
  try:
      n = co.count()
      print(f'OK chunks={n}')
  except Exception as e:
      print(f'FAIL: {e}')  # 如果出现 "Error loading hnsw index" 立刻降级重建
  ```
- 升级任何依赖前先 `cp -r chroma_db chroma_db.bak.$(date +%Y%m%d)`

## 时间线（2026-06-12 实战）

| 时间 | 事件 | 状态 |
|---|---|---|
| 6:00 | cron 跑 rag_setup.py，chromadb 1.5.9 | ✅ sqlite 写完，❌ hnsw 没写 |
| 6:01 | 第一次"修复"：rm chroma_db/* + 重跑 | ❌ 9 分钟后同 bug（版本没变） |
| 6:15 | 降级到 chromadb 0.4.24 + rm chroma_db | ✅ 9 分钟后 hnsw 段有完整文件 |
| 6:25 | count() 验证 | ✅ 输出 1013 chunks |

## 经验总结

1. **症状相同 = 根因未必相同**。第一次以为是"交叉跑"导致损坏，重建同 bug 后才意识到是版本问题
2. **"删了重建"是 lazy fix**。版本不变，bug 一定回来
3. **诊断时一定要看 hnsw 段目录里到底有什么**，不要只看 sqlite
4. **锁版本是廉价的预防**。`pip install chromadb==0.4.24` 一行字，值 90 分钟排查时间
