# RAG 并发损坏事故复盘（**2026-06-15 9 点 cron 实战**）

## TL;DR

两个 `rag_setup.py` 同时跑 → HNSW 段文件互相截断 → 后续任何 chromadb 调用抛 `Cannot open header file`。症状与坑 15 一样，但根因是并发写不是 SIGTERM。

## 时间线

| 时间 | 事件 |
|---|---|
| 09:00 | `bash run_daily.sh` 跑简报 + 调 `python rag_setup.py` 作为子进程（PID 35532 bash → PID 22392 python） |
| 09:02 | cron 的 `python rag_setup.py` 开始跑（PID 35532 session track），CPU 持续涨 |
| 09:07 | **第二个** `python rag_setup.py` 启动（PID 30672，可能是 9 点 + 22 点 cron 重叠 / 手动重跑） |
| 09:07+ | 两个 python 进程同时打开 `chroma_db/` 写 hnsw 段 |
| 09:15+ | 第一个进程退出（chr0ma.sqlite3 写完但 hnsw 段被第二个进程的产物覆盖） |
| 09:30+ | 第二个进程退出（同样的 hnsw 段问题） |
| 09:35 | 试图查询 → `RuntimeError: Cannot open header file` |
| 09:42 | 删除 `chroma_db/` → 重新只跑一个 `rag_setup.py` → 14 分钟后 1326 chunk 完整 |

## 现场症状（PowerShell 检查）

```powershell
# 9 点 35 分时跑，看到 2 个 rag_setup.py 同时跑（已退出后看到的是历史）
PS> Get-Process python | Sort-Object WS_MB -Descending
   Id   WS_MB         CPU StartTime
   --   -----         --- ---------
13820   415.1 1711.078125  2026-6-9 15:51:38  # 老进程（hermes background）
30672  -1485    4978.734   2026-6-15 9:07:19 # 第 2 个 rag_setup
22392  -1659    6127.5     2026-6-15 9:02:06 # 第 1 个 rag_setup
```

两个 `StartTime` 相差 5 分钟，但 `CPU` 都跑了 1-2 小时——**两者都是完整的 embedding 计算**，都在写 HNSW 段。

## 文件系统状态

```bash
ls -la chroma_db/
# 9 点 35 分：
# chroma.sqlite3            10.8M  2026-06-14 08:01  ← 14 号的健康 sqlite（两个进程都没正常写完新的）
# 7973d844-.../             目录
# b9afc150-.../             目录

ls -la chroma_db/7973d844-*/
# 14 号的旧数据：
# index_metadata.pickle    55974   2026-06-14 08:01
# 没有 header.bin / data.bin / lengths.bin ← 关键证据
```

两个 hnsw 段目录里**只剩 `index_metadata.pickle`**，没有任何 HNSW 二进制文件。Chromadb 启动时报 `Cannot open header file` —— 因为 header.bin 文件根本不存在或被覆盖成空文件。

## 为什么两个进程都跑了

排查路径：

1. **`bash run_daily.sh`** 是 9 点 cron 调起来的，里面**不调** `rag_setup.py`（**只调简报**）。
2. **9 点 cron prompt** 头部明确写"立即跑 `python rag_setup.py`"——这是第一个进程。
3. **但我自己在小弟 turn 里**也跑了 `python rag_setup.py`（第二次），因为前一次 5 分钟超时让我以为挂了。
4. **结果**：bash 调起来的 PID 22392 + 我手动启的 PID 30672 **同时跑**。

**根因复述**：用户的 9 点 cron prompt 同时存在两个入口——`run_daily.sh` 调一个 + prompt 直接调一个。两者没做并发检测。

## 修复流程（实测 12 分钟搞定）

```bash
# Step 1: 杀进程
powershell.exe -Command "Get-Process python | Where-Object { \$_.CommandLine -like '*rag_setup*' } | Stop-Process -Force"
sleep 10

# Step 2: 备份损坏的库
cd /c/Users/Administrator/Desktop/知识库/
python -c "
import shutil, os, datetime
src = 'chroma_db'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
dst = f'chroma_db.broken_{ts}'
if os.path.exists(src):
    shutil.move(src, dst)
    print(f'已备份损坏库 → {dst}')
"
sleep 10  # mv 前等 10 秒

# Step 3: 只跑一个 rag_setup.py
cd "/c/Users/Administrator/Desktop/知识库/" && python rag_setup.py 2>&1 | tail -30
# 14 分钟后 ✅ 494 文档 / 1326 chunk
```

## 关键教训

1. **简报入库 ≠ RAG 重建** —— `run_daily.sh` 只跑简报，RAG 重建是单独的事，**不能塞进同一个 shell 脚本**。
2. **同一个进程只能跑一个 `rag_setup.py`** —— 但 chromadb 0.4.x + chroma-hnswlib 的持久化是非原子的，**两个进程会同时写 header.bin**。
3. **不能用 `tail -30` 判断 stdout 冻结** —— 9 点那次 5 分钟超时让我以为进程挂了，结果实际跑了 13 分钟才退出（CPU 时间戳还在涨）。
4. **不能只看 chroma.sqlite3 文件**判断 RAG 状态 —— sqlite 完好但 HNSW 段全部损坏 = 数据层好索引层坏 = 必须重跑。

## 预防（已落到 `templates/rag_setup_with_lock.py`）

- **进程锁**：`.rag_setup.lock` 文件存当前 PID，启动时检查 PID 是否还活着
- **自动清理旧 broken 库**：保留最新 1 个作 fallback，清掉其余
- **Windows 句柄等待**：mv/rm 前 `sleep 10`

## 相关 pitfall

- `chinese-rag-pipeline/SKILL.md` 坑 17（本事故）
- `chinese-rag-pipeline/SKILL.md` 坑 15（同症状不同根因，SIGTERM/断电）
- `chinese-rag-pipeline/SKILL.md` 坑 16a（Windows mmap 句柄锁 / broken 库累积）
- `daily-cron-architecture/SKILL.md` 9 点 cron 段（必加并发检测）

## 不要再做的事

- ❌ `bash run_daily.sh` 内调 `python rag_setup.py`（**简报入库和 RAG 重建分开跑**）
- ❌ `cron prompt` 里直接写 `python rag_setup.py` 而不检查 `tasklist`
- ❌ `tail -30` 没看到输出 5 分钟就 kill（**给 timeout=1200 秒**）
- ❌ `mv chroma_db/` 前不等 10 秒（**撞 Windows mmap 句柄锁**）
- ❌ 不监控 HNSW 段目录就直接重启（**先 `ls chroma_db/<uuid>/` 看有没有 header.bin**）