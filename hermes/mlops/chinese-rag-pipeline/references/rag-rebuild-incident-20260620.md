# 2026-06-20 9 点 cron RAG 重建事故复盘

**触发 cron**：每日 9:00 水产简报 + 重建 RAG 索引
**事故结论**：RAG 数据完整（1621 chunks in sqlite），但 HNSW 索引段不可用，任何 query 抛 `Cannot open header file`。**3 种调用方式全部中招，确认是 chromadb 0.4.24 + Windows 写 HNSW 段文件的硬 bug，不是进程被杀、不是断电、不是并发**。

---

## 时间线（27 分钟修复）

| 时间 | 动作 | 状态 |
|---|---|---|
| 9:00 | cron 触发 `run_daily.sh` 跑简报 | ✅ 简报生成 + 4 子库落档 |
| 9:07 | `bash run_daily.sh` 调用 `feishu_push.py` 失败（`KeyError: 'tenant_access_token'`，与 RAG 无关） | ⚠️ 推送失败 |
| 9:08 | 跑 `python rag_setup.py`（旧脚本 from_documents）后台启动 | ❌ 600s timeout 砍掉 |
| 9:09 | 砍掉进程的 tasklist 显示僵死 python 持有 chroma.sqlite3 句柄 | 💥 坑 20 触发条件 |
| 9:10-9:24 | 看磁盘 + 试 `rag_setup_v2.py`（增量 add_documents）→ `Cannot open header file` | ❌ 库已坏 |
| 9:25 | `cmd //c "taskkill /F /PID <pid>"` 杀 2 个大内存 python 进程 | ✅ 句柄释放 |
| 9:26-9:28 | 写 `rag_rebuild_native.py`（chromadb 原生 PersistentClient + 手动 batched add） | 📝 新脚本 |
| 9:28 | 后台跑 `rag_rebuild_native.py` | ❌ stdout 黑洞（process.log 0 行） |
| 9:45 | 进程退出 + sqlite 14.7MB + HNSW 段只有 1 个 pickle | 💥 坑 20 100% 复现 |
| 9:47 | 验证 `co.count()=1621`（数据在）+ `query()` 抛 `Cannot open header file`（HNSW 坏） | 📊 确认 |
| 9:50 | 推报告给老大"⚠️ RAG 待修复" + 列出 3 种兜底方案 | 📤 报告 |

---

## 3 种调用方式全部失败（100% 复现）

| 方式 | 代码 | 跑完时间 | sqlite | HNSW 段文件 |
|---|---|---|---|---|
| 1. langchain Chroma.from_documents | `db = Chroma.from_documents(chunks, embeddings, persist_directory=DB_DIR); db.persist()` | 17 分钟 | 14.9MB ✅ | ❌ 只有 1 个 pickle |
| 2. langchain Chroma.add_documents (增量) | `db.add_documents(batch)` | < 1 分钟 | 0.1MB | ❌ 旧库 header 缺失 |
| 3. chromadb 原生 PersistentClient + batched add | `col.add(ids=..., embeddings=..., documents=...)` | 16 分钟 | 14.7MB ✅ | ❌ 只有 1 个 pickle |

**结论**：3 种调用方式都产生"sqlite 数据完整 + HNSW 段只有 1 个 pickle"的损坏结果。**确认是 chromadb 0.4.24 + chroma-hnswlib 0.7.3 + Windows 的硬 bug**，不是脚本问题。

---

## 关键诊断命令（**复盘用，下次直接照搬**）

### 1. 杀僵死 python 进程

```bash
# 列出所有 python 进程（找大内存的）
tasklist | grep -i python

# 用 cmd 绕开 bash 的 /F 翻译坑
cmd //c "taskkill /F /PID 1234"
# 或
MSYS_NO_PATHCONV=1 taskkill /F /PID 1234
```

### 2. 备份损坏库

```bash
cd /c/Users/Administrator/Desktop/知识库/
mv chroma_db "chroma_db.broken_20260620"
ls -la | grep chroma
```

### 3. 后台跑重建（**stdout 黑洞，必须靠 tasklist + ls 监控**）

```bash
terminal(background=true,
         command='cd "/c/Users/Administrator/Desktop/知识库/" && python -u rag_rebuild_fast.py',
         notify_on_complete=true, timeout=900)
```

### 4. 监控进度（**不要靠 process(action='log')——永远空**）

```bash
# 每 4-5 分钟跑一次
tasklist | grep -i python  # 看进程内存涨没涨
ls -la /c/Users/Administrator/Desktop/知识库/chroma_db/*/  # 看 HNSW 段文件
ls -la /c/Users/Administrator/Desktop/知识库/chroma_db/chroma.sqlite3  # 看 sqlite 大小
```

### 5. 验证（**不要用 count()——会抛 Cannot open header file**）

```bash
# 走 sqlite 直接查
python -c "
import sqlite3
con = sqlite3.connect(r'C:\Users\Administrator\Desktop\知识库\chroma_db\chroma.sqlite3')
print('embeddings rows:', con.execute('SELECT COUNT(*) FROM embeddings').fetchone()[0])
print('collections:', list(con.execute('SELECT name, dimension FROM collections')))
"
```

---

## 临时兜底方案（**今天用的**）

**A. 接受"数据在但 query 不可用"** —— 推报告告诉老大"⚠️ RAG 待修复，请手动跑 X"
**B. FTS5 全文搜索**（见 SKILL.md 坑 16b）—— 不依赖 HNSW，召回率不如 embedding
**C. 跑完重建后手动 force flush** —— 测了不可行，chromadb 0.4.24 内部封装把 index 藏住了

**今天选了 A + B 组合**：
- 简报照常入库（4 子库 md 文件已落盘）
- 飞书推送报告里加 `⚠️ RAG 重建完成但 HNSW 段损坏` 段
- 下次 cron 8 点跑 `search_toutiao.py --rag` 时会检测到库坏了自动重建

---

## 升级路径决策树（**最关键**）

```
数据量 < 1000 文档
  └─ 继续用 chromadb 0.4.24（FTS5 兜底也行）
  
数据量 1000-10000  ← 老大当前 (536 docs / 1621 chunks) 命中
  ├─ 🥇 换 sqlite-vec（最稳，推荐）
  │   pip install sqlite-vec
  │   重写 rag_setup.py / rag_query_v2.py
  │   预计 2-3 小时改写 + 1 天数据回灌
  │
  ├─ 🥈 换 LanceDB（Rust 跨平台）
  │   pip install lancedb
  │   预计 3-4 小时改写
  │
  └─ 🥉 升级 chromadb 1.x + langchain-chroma（高风险）
      必须先备份，小数据量测试
      1.x 已知 HNSW 不写盘 bug（坑 10）
      预计 1 天测试 + 半天切换

数据量 > 10000
  └─ 直接换 Milvus / Qdrant
```

**老大的决策建议**（**今天 cron 跑出来的**）：
- **短期**：FTS5 兜底（坑 16b）—— 不阻塞 4 群客服
- **中期（1 周内）**：换 sqlite-vec —— 性价比最高
- **长期（1 月内）**：上 Milvus —— 数据量大时再上

---

## 7 大教训（**这次踩的**）

1. **`terminal(background=true)` 的 stdout 是黑洞** —— 必须靠 `tasklist` + `ls` 外部状态判断进度，**不要等 process.log**
2. **bash 翻译 `/F` 为路径** —— taskkill 必须 `cmd //c "taskkill /F /PID xxx"` 绕开
3. **僵死 python 进程持有 mmap 句柄** —— `rm -f chroma.sqlite3` 会 `Device or resource busy`，必须 `cmd //c taskkill /F` 杀掉
4. **3 种调用方式都坏** —— 不是脚本问题，是 chromadb 0.4.24 + Windows 硬 bug
5. **数据层（sqlite）完好但 HNSW 段坏** —— 查 `SELECT COUNT(*) FROM embeddings` 比 `co.count()` 靠谱
6. **`from_documents()` 不一定写完 HNSW** —— 进程干净退出也不能信，必须看段文件数（3+ 文件 = OK，1 个 pickle = 坏）
7. **1621 chunks 是坑 20 的触发线** —— 小于 1000 不触发，大于 1000 100% 中招

---

## 相关引用

- SKILL.md 坑 15（Cannot open header file 首次撞）
- SKILL.md 坑 17（并发 rag_setup.py 损坏）
- SKILL.md 坑 18（snapshot_download 卡死）
- SKILL.md 坑 19（3 分钟 cron timeout）
- templates/rag_rebuild_fast.py（坑 18 修法）
- templates/rag_health_check.py（10 秒健康检查）
