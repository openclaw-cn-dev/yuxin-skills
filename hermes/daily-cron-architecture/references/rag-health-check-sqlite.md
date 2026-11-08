# RAG 健康检查走 SQLite 元数据（**2026-06-14 重写**）

**问题**：原命令调 `co.count()` 走 HNSW 索引层 —— 0.4.24 + Windows 上 **任何** 访问 HNSW 的操作都可能撞 `Cannot open header file`，导致 6 点 cron 永远报 RAG 异常（即使数据完好）。

**根因**：
- chromadb 0.4.24 + Windows 写 HNSW header 不可靠（**3 天撞 2 次**：6/13、6/14）
- `co.count()` / `co.peek()` / `co.query()` 都触发 HNSW load → 撞 header file 损坏
- 但 `chroma.sqlite3` 元数据完好（document id + dimension + created_at 都在 `embeddings` 表）

**修复方案**：绕开 HNSW，直接查 SQLite 元数据

## 健康检查命令（**用这个**）

```bash
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
import sqlite3
from pathlib import Path
DB = Path(r'C:\Users\Administrator\Desktop\知识库\chroma_db\chroma.sqlite3')
if not DB.exists():
    print('❌ chroma.sqlite3 不存在')
else:
    size_mb = DB.stat().st_size / 1024 / 1024
    con = sqlite3.connect(str(DB))
    n = con.execute('SELECT COUNT(*) FROM embeddings').fetchone()[0]
    dim = con.execute('SELECT dimension FROM collections').fetchone()[0]
    last = con.execute(\"SELECT datetime(max(strftime('%s', created_at)), 'unixepoch') FROM embeddings\").fetchone()[0]
    con.close()
    print(f'chunks:{n} | dim:{dim} | size:{size_mb:.1f}MB | last:{last}')
"
```

## 判定 + 应对

| sqlite 状态 | HNSW 状态 | 判定 | 应对 |
|---|---|---|---|
| n > 0 | OK | ✅ 完全正常 | 无 |
| n > 0 | 报 Cannot open header file | 🟡 **HNSW 损坏，数据完好** | `python rag_setup.py` 重建（5-10 分钟） |
| n == 0 / 表不存在 | 任意 | 🔴 索引失败 | 查 9 点 cron log / `errors.log` / 全量重建 |
| 文件不存在 | — | ❌ 没建过库 | 跑 `python rag_setup.py` 首次建立 |

## HNSW 状态单独判断（**推荐配套跑**）

```bash
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
import sqlite3, chromadb
from pathlib import Path
DB_DIR = Path(r'C:\Users\Administrator\Desktop\知识库\chroma_db')
con = sqlite3.connect(str(DB_DIR / 'chroma.sqlite3'))
sqlite_n = con.execute('SELECT COUNT(*) FROM embeddings').fetchone()[0]
con.close()
try:
    c = chromadb.PersistentClient(path=str(DB_DIR))
    co = c.get_collection('langchain')
    hnsw_n = co.count()
    print(f'✅ HNSW 正常 | sqlite:{sqlite_n} | hnsw:{hnsw_n}')
except Exception as e:
    print(f'🟡 HNSW 损坏: {type(e).__name__}: {str(e)[:100]} | sqlite:{sqlite_n}')
"
```

## 关键教训

- **6 点 cron 必须先跑 SQLite 命令** —— 即使 sqlite 报"数据静止"（24h 无新增），不一定是异常 —— 也可能是 HNSW 损坏阻止 9 点 cron 写入
- **看到 `Cannot open header file` 不要立刻删 chroma_db** —— 数据通常完好，先验证 sqlite，再决定重建 HNSW 还是全量
- **升级路径**（待老大批准）：测 `chromadb>=0.5.x,<1.0` 或换原生 API 绕过 langchain wrapper

## 关联

- 主 SKILL.md → 「4. RAG / 知识库健康」段
- `chinese-rag-pipeline` 坑 15 + 坑 16a（HNSW 反复损坏实战）
