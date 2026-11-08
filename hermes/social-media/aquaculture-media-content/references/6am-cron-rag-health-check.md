# 6 点 cron RAG 健康检查（**避免触发 HNSW 损坏**）

> 适用：每天 6:00 的工作总结 cron（`4247b6d7d564`）跑 RAG 健康检查。
> 痛点：cron prompt 里硬编码的 `chromadb.get_collection()` 命令在 HNSW 损坏时直接抛 `RuntimeError: Cannot open header file`，整个检查脚本崩，老大拿到的报告只有 traceback，没有 chunks 数 / 索引状态等可观测数字。

## ⚠️ 核心问题（2026-06-19 6 点 cron 撞过）

prompt 里写的命令（**有问题**）：
```bash
"C:/.../python.exe" -c "
import chromadb
c = chromadb.PersistentClient(path='chroma_db')
co = c.get_collection('langchain')
n = co.count()
print(f'chunks:{n}')
" 2>&1 | tail -3
```

**实际表现**：HNSW 损坏时，`get_collection()` 抛异常 → Python 退出 → `tail -3` 只截最后 3 行 traceback → 老大看到的报告是：
```
RuntimeError: Cannot open header file
  File ".../local_persistent_hnsw.py", line 164, in _init_index
    index.load_index(
```
**没有任何数字**，RAG 状态是 🟢 还是 🔴 完全看不出来。

## ✅ 正确检查命令（**sqlite 直查，绕开 chromadb API**）

```bash
cd "C:/Users/Administrator/Desktop/知识库/"
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
import sqlite3
from pathlib import Path
SQLITE = Path(r'C:\Users\Administrator\Desktop\知识库\chroma_db\chroma.sqlite3')
conn = sqlite3.connect(str(SQLITE))
cur = conn.cursor()
cur.execute('SELECT count(*) FROM embeddings')
n = cur.fetchone()[0]
cur.execute('SELECT name FROM collections')
cols = [r[0] for r in cur.fetchall()]
conn.close()
# HNSW 索引目录大小（健康/损坏指纹）
uuid_dirs = [d for d in SQLITE.parent.iterdir() if d.is_dir()]
hnsw_kb = sum(sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) for d in uuid_dirs) / 1024
# HNSW 健康度（5-50MB 健康，< 1MB 损坏）
status = 'OK' if hnsw_kb > 1024 else 'BROKEN'
print(f'chunks:{n}')
print(f'collections:{cols}')
print(f'hnsw_dir_kb:{hnsw_kb:.1f}')
print(f'hnsw_status:{status}')
print(f'sqlite_mb:{SQLITE.stat().st_size/1024/1024:.1f}')
" 2>&1
```

**预期输出**（**健康**）：
```
chunks:1517
collections:['langchain']
hnsw_dir_kb:18432.5
hnsw_status:OK
sqlite_mb:13.6
```

**预期输出**（**HNSW 损坏**，2026-06-19 6 点实测）：
```
chunks:1517
collections:['langchain']
hnsw_dir_kb:54.7
hnsw_status:BROKEN
sqlite_mb:13.6
```

## 📋 6 点 cron 报告里的 RAG 段（**标准模板**）

拿到上面 5 个数字后，老大报告里这么写（**老大一眼能看**）：

```
## RAG 健康
- chunks: 1517
- HNSW: 🟡 54.7 KB（损坏） / 🟢 18 MB（健康）
- 9 点 cron: 将跑全量重建（修法 A：delete + recreate collection + Chroma.from_documents，~110s）

🟡 需要关注 —— RAG HNSW 索引损坏（sqlite 数据完整），等 9am cron 全量重建
```

## 🔁 9 点 cron 自动联动

如果 6 点检查发现 HNSW 损坏，**不要在 6 点 cron 修**（会阻塞报告交付 + 重建要 16 分钟）。

**正确做法**：
1. 6 点 cron 报告里标记 **🟡 需要关注**
2. 9 点 cron `31287df0e40a` 走 `9am-cron-execution-runbook.md` 的 4 步状态机（**后台重建 + notify_on_complete**）
3. 重建完成后 9 点 cron 自动补发一张"✅ RAG 已修"卡片给老大

## 🔗 关联文件

- `references/chroma-hnsw-corruption-recovery.md` — HNSW 损坏的**修法**（修法 A：delete collection + recreate + Chroma.from_documents）
- `references/9am-cron-execution-runbook.md` — 9 点 cron 必走的**后台模式 + 4 步状态机**（RAG 重建实测 974 秒必须后台）
- `C:\Users\Administrator\Desktop\知识库\chroma_db\chroma.sqlite3` — 元数据本体（即使 HNSW 损坏也在）
- `C:\Users\Administrator\Desktop\知识库\chroma_db\<uuid>\` — HNSW 索引（易坏）

## 🛑 关键铁律

- ❌ **6 点 cron 不要直接 `chromadb.get_collection()`**——HNSW 损坏时直接崩，没有可观测输出
- ❌ **6 点 cron 不要尝试修 RAG**——16 分钟重建会阻塞报告交付
- ✅ **6 点 cron 用 sqlite 直查**——稳，5 个数字 + 健康度判断，不依赖 chromadb API
- ✅ **HNSW 损坏 = 标记 🟡，等 9 点 cron 自动修**——职责清晰，不跨时段抢活