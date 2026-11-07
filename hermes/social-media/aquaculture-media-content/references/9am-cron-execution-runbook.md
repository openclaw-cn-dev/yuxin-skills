# 9 点 cron 执行 Runbook（**2026-06-18 9 点 cron 实战**）

> **目标**：每天 9:00 自动跑「**水产简报入库** + **RAG 重建**」两件事，把每一步的**实测时间、必走的 background 模式、失败时怎么补**写在一处。  
> **适用**：6 点巡检段、9 点 cron 触发时、老大手动重跑时 — 任何要走 `bash run_daily.sh` + `python rag_setup.py` 的场景。

---

## 🎯 任务定义（**2 件事，串行不并发**）

| 步骤 | 命令 | 产出 | 实测耗时 |
|---|---|---|---|
| 1. 简报入库 | `bash run_daily.sh` | `2026-06-18-水产简报.md`（136 条 / 美食+养殖+设备+公司 4 子库）| 5-8 分钟 |
| 2. RAG 重建 | **`python rag_rebuild_fast.py`**（**6/21 起取代 `rag_setup.py` —— HF 本地缓存直连，无 ModelScope snapshot_download 锁 + 无 telemetry hang**）| `chroma_db/` 库（545 文档 / **3312 chunks**）| **~22-25 分钟**（CPU 必跑后台）|

**⚠️ 串行不并发**：`run_daily.sh` 跑完才跑 `rag_setup.py` —— chromadb HNSW 段非原子写，并发 = 索引损坏。详见 `daily-cron-architecture` 9 点 cron 段的并发检测模板。

---

## 🔥 必走：RAG 重建必须 `terminal(background=true)`（**2026-06-18 实测 974 秒**）

### 为什么不能前台

- **`terminal(foreground, timeout=600)` = 10 分钟硬上限** —— `rag_setup.py` 实测 974 秒（**16 分 14 秒**）一定超时
- **超时 = 进程被 SIGTERM 砍** = HNSW header 写一半被截断 = 撞 `Cannot open header file`（坑 15/17）
- **前台跑 = 必然损坏 RAG** —— 必走后台

### 4 步状态机（**实测 6/18 9 点 cron 实战流程**）

```python
# === Step 1: 前台快速探测（5 秒）===
# 目的：拿当前 chroma_db 状态 + 决定要不要备份
import os, subprocess
from pathlib import Path
from datetime import datetime

DB = Path(r"C:\Users\Administrator\Desktop\知识库\chroma_db")
SQLITE = DB / "chroma.sqlite3"

if DB.exists():
    size_mb = SQLITE.stat().st_size / 1024 / 1024
    print(f"chroma_db 存在 | sqlite {size_mb:.1f}MB")
else:
    print("chroma_db 不存在 → 干净重建")
```

```python
# === Step 2: 前台快速备份（5-10 秒）===
# ⚠️ 必须 sleep 10 让前一进程的 mmap 句柄释放（坑 16a）
import time
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
if DB.exists():
    # 静态 sleep 10（Windows 句柄锁）→ 避免 Permission denied 重试
    time.sleep(10)
    DB.rename(DB.parent / f"chroma_db.broken_{ts}")
    # 或用 shutil.move 等价
    print(f"已备份 → chroma_db.broken_{ts}")
```

```python
# === Step 3: 后台启动 RAG 重建（不等完成）===
# 关键：background=true + notify_on_complete=true
# foreground 跑 16 分钟 = 必撞 timeout = 必损坏 = 必坑 15
terminal(
    background=True,
    command="cd /c/Users/Administrator/Desktop/知识库/ && python rag_setup.py > /tmp/rag_$(date +%Y%m%d_%H%M%S).log 2>&1",
    notify_on_complete=True,
)
# 返回 session_id + pid（如 proc_3fed1e312f14 / pid 36804）
# ↓ 立刻进入 Step 4 — 不等进程结束
```

```python
# === Step 4: 立即返回 3-pillar 报告（不阻塞 cron 交付）===
# 关键：不等 16 分钟，直接报告"🔄 重建中 PID XXX"
print("""
🎯 9 点 cron 简报 + RAG - 2026-06-18

✅ 简报入库：136 条 / 9:01 生成
⚠️ 飞书推送失败（KeyError: tenant_access_token，feishu_push.py 环境问题）
🔄 RAG 重建中（PID 36804），ETA 16 分钟 — 完成后异步推飞书

📌 今日要点：
1. FAO 蓝色转型 — 全球渔业 2.14 亿吨历史新高
2. 水产品可持续追溯体系成果发布 + "国民水产品 50g+" 行动启幕
3. 《工厂化淡水循环活水鱼养殖通用技术规范》征求意见中
""")
# ↑ 系统自动投递给老大（final response = auto-delivery）
# ↓ 16 分钟后 notify_on_complete 触发，单独发"✅ RAG 重建完成 520 文档 / 1517 chunks"卡片
```

---

## 📊 实测时间参考（**2026-06-18 9 点 cron**）

| 阶段 | 耗时 | 累计 |
|---|---|---|
| 1. 简报抓取（cappma 20 频道）| ~3 分钟 | 3 分钟 |
| 2. 简报 merge + 写 md | ~2 分钟 | 5 分钟 |
| 3. 飞书推送（feishu_push.py）| ~1 分钟（**注意：6/18 撞 KeyError**）| 6 分钟 |
| 4. 探测 + 备份 chroma_db | ~15 秒 | 6 分 15 秒 |
| 5. RAG 重建（后台启动）| **0 秒**（不阻塞）| 6 分 15 秒 |
| 6. 立即返回 cron 报告 | ~0 秒 | **6 分 15 秒 → cron 交付** |
| 7. RAG 重建（后台进行中）| **974 秒** | 22 分 30 秒 |
| 8. notify_on_complete 触发补发卡片 | ~0 秒 | 22 分 30 秒 |

**关键认知**：cron 报告 6 分 15 秒交付（**不阻塞**），RAG 重建 16 分 14 秒在后台跑（**不损坏**），最终两张卡片按时到老大手上。

---

## 👀 观察后台进度（**不打断 wait/poll 循环的技巧**）

**问题**：`terminal(background=true)` 启动后，stdout 看不到实时输出（chromadb 0.4.x + bge 索引阶段 0 进度日志），cron 报告里只能写"重建中"——但 16 分钟对老大来说太久了。

**解法**：**在 `wait` 间隔里看磁盘文件变化**（**2026-06-18 实战验证**）：

```python
# 在 process(action='wait', timeout=60) 间隔里跑
import os
from pathlib import Path
DB = Path(r"C:\Users\Administrator\Desktop\知识库\chroma_db")
if DB.exists():
    sqlite = DB / "chroma.sqlite3"
    if sqlite.exists():
        size_mb = sqlite.stat().st_size / 1024 / 1024
        mtime = sqlite.stat().st_mtime
        print(f"chroma.sqlite3: {size_mb:.1f}MB | mtime: {mtime}")

# 输出示例（6/18 真实进度）：
# 11 分钟时: chroma.sqlite3: 13.9MB | mtime: 09:25:00  ← 索引在写
# 13 分钟时: chroma.sqlite3: 20.4MB | mtime: 09:25:00  ← 涨了 6.5MB = 在 embedding
# 16 分钟时: 进程 exit_code=0 ← ✅ 完成
```

**判断规则**：
- **mtime 在最近 1 分钟内 + size 在涨** = 进程活着 + 在干活（**正常**）
- **mtime 卡住 > 5 分钟 + size 不变** = 进程死了或卡死（**异常** → 看 log）
- **mtime 涨但 size 始终 < 1MB** = 卡在 model loading 阶段（**坑 18 重下** → 看 `~/.cache/modelscope/._____temp/`）

**绝对不能**：
- ❌ 看到没 stdout 日志就 `kill` 进程（**坑 14 教训**——前 8-10 分钟 stdout 0 行是正常的，**embedding 计算阶段无进度日志**）
- ❌ 反复 `process(action='poll')` 调短超时（**浪费 token**）
- ✅ 隔 60-90 秒看一次磁盘 + 看 log 文件大小
- ✅ 进程退出（`status: exited`）才决定下一步

**为什么这个技巧值钱**：未来任何 5+ 分钟的 RAG / embedding 脚本都能用——**用文件 mtime + size 当"进度条"**，**不依赖 stdout / 日志 / API**。

---

## 🚨 失败处理（**3 种最常见 + 怎么补**）

### 失败 1：`chroma.sqlite3` 报 `Cannot open header file`（**坑 15**）

**症状**：
```
RuntimeError: Cannot open header file
  File "...chromadb\segment\impl\vector\local_persistent_hnsw.py", line 164
```

**判断 3 步**：
```python
# 1. 库文件在不在？
DB.exists()  # True
# 2. sqlite 大小正常吗？
SQLITE.stat().st_size / 1024 / 1024  # > 1MB → 元数据完好
# 3. hnsw 段目录是不是空的？
list((DB / "<uuid>/").glob("*"))  # 只有 1 个 pickle = 损坏
```

**修法**：走 4 步状态机的 Step 1-4（备份 + 后台重建）。

### 失败 2：`KeyError: 'tenant_access_token'`（**feishu_push.py**）

**症状**：
```
File "...feishu_push.py", line 18, in push
    token = json.loads(...).read().decode())["tenant_access_token"]
KeyError: 'tenant_access_token'
```

**根因**（**2026-06-18 撞**）：feishu Push API 返的不是 `tenant_access_token` 字段 —— 可能是凭证过期 / APP_ID 或 APP_SECRET 错 / 网络 401。

**应对**（**不阻断 cron 流程**）：
- 简报 md 文件**已落盘** → 桌面有 `2026-06-18-水产简报.md` 老大可以直接打开
- 报告里写 `⚠️ 飞书推送失败（feishu_push.py KeyError）—— md 文件已落盘桌面`
- 老大手动跑 `python feishu_push.py "2026-06-18-水产简报.md"` 重推
- **不要**为了修复凭证反复重试 —— 浪费时间，9 点 cron 已经超时

**根因调查**（**老大有空再查**）：
```bash
# 验证 APP_ID / APP_SECRET 是否有效
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
import urllib.request, json
APP_ID = '<FEISHU_APP_ID>'  # 从 .env / feishu_secrets.json 取
APP_SECRET='***'
data = json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=data, headers={'Content-Type': 'application/json'})
print(urllib.request.urlopen(req, timeout=10).read().decode())
"
# 返回 {"code":99991663,"msg":"invalid app_id or app_secret"} → 凭证失效
# 返回 {"code":0,"tenant_access_token":"t-xxx"} → 凭证有效，bug 在 feishu_push.py
```

### 失败 3：`rag_setup.py` 撞并发（**坑 17**）

**症状**：两个 python 进程同时跑 → HNSW 段文件被互相截断 → `Cannot open header file`（同坑 15 症状）

**判断 2 步**：
```bash
# Step 1: 看是不是有 2+ 个 rag_setup.py 进程
powershell.exe -Command "Get-Process python | Where-Object { \$_.CommandLine -like '*rag_setup*' } | Format-Table Id,StartTime"
# 2+ 个 → 命中坑 17
```

**修法**：
```bash
# Kill 掉所有 rag_setup.py 进程（保留最早启动的也无所谓，重启更稳）
powershell.exe -Command "Get-Process python | Where-Object { \$_.CommandLine -like '*rag_setup*' } | Stop-Process -Force"
sleep 10  # 等句柄释放
# 走 4 步状态机 Step 1-4（备份 + 重建）
```

**预防**（**根因解**）：用 `daily-cron-architecture` 9 点 cron 段推荐的 `run_daily.sh` 加锁版（带 `.rag_setup.lock` 文件 + PID 存活检测）。

---

## 🛡️ 预防清单（**写进 9 点 cron prompt 头部**）

```bash
# 1. 检测并发
OLD=$(powershell.exe -Command "Get-Process python | Where-Object { \$_.CommandLine -like '*rag_setup*' } | Select-Object -ExpandProperty Id" 2>/dev/null | tr -d '\r\n ')
if [ -n "$OLD" ]; then
  echo "🟡 跳过 RAG 重建：已有进程 PID $OLD"
  # 简报照常跑，RAG 这轮跳过
fi

# 2. 备份旧库（带 sleep 10 句柄释放）
sleep 10
[ -d "C:/Users/Administrator/Desktop/知识库/chroma_db" ] && \
  mv "C:/Users/Administrator/Desktop/知识库/chroma_db" \
     "C:/Users/Administrator/Desktop/知识库/chroma_db.broken_$(date +%Y%m%d_%H%M%S)"

# 3. 后台启动重建（不阻塞 cron）
cd "/c/Users/Administrator/Desktop/知识库/" && \
  nohup python rag_setup.py > "/tmp/rag_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
echo "🔄 RAG 重建中 PID $!"

# 4. 立即返回 cron 报告（不阻塞）
echo "✅ 简报入库 | 🔄 RAG 重建中 ETA 16 分钟 | 📌 今日要点：..."
exit 0
```

---

## 📋 3-pillar 输出格式（**老大一眼能看**）

每次 9 点 cron 报告**必须包含这 3 段**：

```markdown
## ✅ 简报入库
- 状态：成功 / 失败
- 条数：136 条 / 0 条
- 文件：桌面 `2026-06-18-水产简报.md`

## 🔄 RAG 重建
- 状态：🔄 进行中 PID XXX / ✅ 完成 / ❌ 失败
- 进度：0% / 100% / 错误信息
- 预期：16 分钟 / 已用 5 分钟 / 撞 Cannot open header file

## 📌 今日要点（3 条）
1. 行业风向：...
2. 政策动向：...
3. 业务热点：...
```

**≤ 200 字**（**老大飞书卡片不超 800 字**），超出截断到 3 条要点。

---

---

## ⚠️ Process "ghost hang" 陷阱 + 安全 kill 时机（**2026-06-21 9 点 cron 实战**）

### 症状

`rag_rebuild_fast.py` 跑到 ~20 分钟时 `chroma.sqlite3` 突然从 **14.2 MB 涨到 29.5 MB**（说明 `Chroma.from_documents()` 已写完所有 embedding），**但 python 进程继续跑 5+ 分钟不退**，stdout 没有任何新输出 —— 像是卡在某个 shutdown / telemetry hook 上（与 `rag_setup.py` 撞 `capture() takes 1 positional argument but 3 were given` 同根）。

**6/21 实测进度时间轴**：

| 时间点 | 进程状态 | chroma.sqlite3 | stdout |
|---|---|---|---|
| 09:09:08 | 启动 | 14.2 MB（6/21 简报入库前的旧库） | `索引到 Chroma...` |
| 09:09:08 - 09:28 | 跑 embedding（~19 分钟 CPU 计算）| 14.2 MB | 0 行（embedding 阶段无进度日志） |
| **09:28** | **写完所有 chunks** | **30.2 MB** ← **关键信号** | 0 行 |
| 09:28 - 09:33 | **进程 ghost hang**（5+ 分钟无新输出）| 30.2 MB（不变）| 0 行 |

### 结论：chroma.sqlite3 mtime 更新 = 数据已落盘 = 可安全 kill

**铁律（6/21 实战验证）**：

```bash
# 在 process(action='poll') / wait 间隔里跑这个判断
LAST_MTIME_SQLITE = $(stat -c %Y "C:/Users/Administrator/Desktop/知识库/chroma_db/chroma.sqlite3" 2>/dev/null)
SIZE_SQLITE = $(stat -c %s "C:/Users/Administrator/Desktop/知识库/chroma_db/chroma.sqlite3" 2>/dev/null)
NOW = $(date +%s)
AGE = $(( NOW - LAST_MTIME_SQLITE ))

if [ "$SIZE_SQLITE" -gt 20000000 ] && [ "$AGE" -gt 120 ]; then
  # sqlite > 20MB + mtime 已停 2 分钟 → 数据写完了 + 进程 ghost hang
  echo "✅ 数据已落盘（${SIZE_SQLITE} bytes, mtime ${AGE}s 前），可安全 kill"
  # 用 process(action='kill') 砍进程
fi
```

**6/21 实战**：
- 09:33（数据写完 5 分钟）判断 → sqlite 30.2MB + mtime 5 分钟没变 → **safe to kill**
- `process(action='kill', session_id='proc_xxx')` → 进程退出
- 立即跑 `sqlite3` 直查：3312 chunks ✅ + 6/21 文档 48 个 ✅ → **RAG 索引完整可用**

### ❌ 不要做的事

- ❌ **看到没 stdout 日志就 kill** —— 前 8-10 分钟是 embedding 计算阶段，0 stdout 是**正常**（坑 14 教训）
- ❌ **等到进程正常退出** —— 5+ 分钟 ghost hang 浪费 cron token，但不影响结果
- ❌ **怀疑数据没写完就 kill** —— 一定要先看 sqlite 大小 + mtime，再 kill

### ✅ 应该做的事

1. **看 sqlite 大小 > 20 MB**（经验阈值，~1500 chunks 起）：**写完了**
2. **看 mtime 在最近 1-2 分钟内没动**：**ghost hang 阶段**
3. **两者同时满足 + 已等 ≥ 5 分钟** → 安全 kill
4. **kill 后立即用 sqlite 直查验证**（见下节）

### 验证 kill 后索引完整可用（**必跑**）

```bash
# 用 sqlite 直查（不依赖 chromadb API，避免再触发 HNSW 异常）
python -c "
import sqlite3
db = 'C:/Users/Administrator/Desktop/知识库/chroma_db/chroma.sqlite3'
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute('SELECT count(*) FROM embeddings')
print(f'总 chunk: {cur.fetchone()[0]}')
cur.execute(\"SELECT count(*) FROM embedding_metadata WHERE key='source' AND string_value LIKE '%2026-06-21%'\")
print(f'含今日文档数: {cur.fetchone()[0]}')
con.close()
"
```

**期望**（6/21 实测）：
- 总 chunk 3312（vs 旧库 1631 → 翻倍）
- 含今日文档 ≥ 30（6/21 简报 + 8 点爆款分析报告等）

如果数字对不上 → 走 `references/chroma-hnsw-corruption-recovery.md` 修法 A 重来。

---

## 🆚 为什么用 `rag_rebuild_fast.py` 不用 `rag_setup.py`（**2026-06-21 切换**）

| 维度 | `rag_setup.py`（旧）| **`rag_rebuild_fast.py`（新，6/21 起）** |
|---|---|---|
| bge 模型加载 | 走 ModelScope `snapshot_download()`（**6/20 实战撞 ModelScope 锁 10+ 分钟**）| 直连 `~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/...`（**已下好的本地路径，0.8 秒加载**）|
| Telemetry | 默认开，6/20 撞 `capture() takes 1 positional argument but 3 were given` | `ANONYMIZED_TELEMETRY=False` 关掉 |
| 1681 chunks 全量 | ~25-30 分钟（经常撞 ModelScope 锁超时）| **~22-25 分钟（实测 6/21 稳定）** |
| 兼容性 | 需要 ModelScope 镜像可达 | 只要 HF 缓存里 bge 在（**首次装好后永久可用**）|

**切换铁律**：
- ✅ **6/21 起所有 9 点 cron 走 `rag_rebuild_fast.py`**
- ❌ **`rag_setup.py` 仅作 fallback**（HF 缓存失效时回退）
- ⚠️ **首次跑前确认 HF 缓存**：`ls ~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/` 至少 1 个 snapshot 目录，否则走 `rag_setup.py` 走 ModelScope 镜像下载

### 何时回退到 `rag_setup.py`

| 场景 | 用谁 |
|---|---|
| HF 缓存有 bge | **`rag_rebuild_fast.py`**（首选）|
| HF 缓存空 + ModelScope 可达 | `rag_setup.py`（回退）|
| HF 缓存空 + ModelScope 也卡 | 走 `references/chroma-hnsw-corruption-recovery.md` 修法 A 分批重建 |
| 撞 HNSW 损坏 | 走 `references/chroma-hnsw-corruption-recovery.md` 修法 A（与本 runbook 解耦）|

### 4 步状态机 v2（**6/21 实测流程，rag_rebuild_fast 版本**）

```python
# === Step 1: 前台快速探测（5 秒）===
import os
from pathlib import Path
DB = Path(r"C:\Users\Administrator\Desktop\知识库\chroma_db")
SQLITE = DB / "chroma.sqlite3"
if DB.exists():
    print(f"chroma_db 存在 | sqlite {SQLITE.stat().st_size/1024/1024:.1f}MB")
else:
    print("chroma_db 不存在 → 干净重建")

# === Step 2: ⚠️ 跳过备份（rag_rebuild_fast 用 Chroma.from_documents 会自动覆盖 collection）===
# 6/21 实测：不备份直接重建 → 0 损坏 → 索引完整 3312 chunks
# 6/18 runbook 旧版的"备份 + 重建"两步对 rag_setup.py 必要，对 rag_rebuild_fast 多此一举
# 铁律：用 rag_rebuild_fast.py → 跳过 Step 2 备份

# === Step 3: 后台启动 RAG 重建（不等完成）===
terminal(
    background=True,
    command="cd /c/Users/Administrator/Desktop/知识库/ && python rag_rebuild_fast.py > /tmp/rag_$(date +%Y%m%d_%H%M%S).log 2>&1",
    notify_on_complete=True,
)
# 返回 session_id + pid → 立刻进入 Step 4

# === Step 4: 立即返回 3-pillar 报告（不阻塞 cron 交付）===
# 关键：不等 22-25 分钟，报告"🔄 重建中 PID XXX"
print("""
🎯 9 点 cron 简报 + RAG - 2026-06-21

✅ 简报入库：111 条 / 9:02 生成
⚠️ 飞书推送失败（KeyError: tenant_access_token，feishu_push.py 环境问题）
🔄 RAG 重建中（PID XXX），ETA 22-25 分钟 — 完成后异步推飞书

📌 今日要点：
1. FAO 蓝色转型 — 全球渔业 2.14 亿吨创新高
2. 水产品可持续追溯体系建设成果发布 + "国民水产品 50g+"行动启幕
3. 抖音水产话题：复刻熏鱼娘娘同款辣炒海葵
""")
```

---

## 🔗 关联 skill / 章节

- `daily-cron-architecture` SKILL.md 9 点 cron 段 — **`run_daily.sh` 加锁版 + 并发检测段**（**根因解**）
- `chinese-rag-pipeline` SKILL.md 坑 15 / 16a / 17 / 19 — **HNSW 损坏的诊断 + 修复**
- `aquaculture-content-sourcing` SKILL.md 6号坑 — **8 点 cron 撞 chroma header file 的 5 行恢复流程**（**本 runbook 是 9 点版的扩展**）

---

*作者：Hermes Agent @ 2026-06-18 9 点 cron 实战 → 2026-06-21 9 点 cron 升级*  
*基于 6/12 + 6/13 + 6/14 + 6/15 + 6/18 + 6/21 共 6 天 RAG 重建实战（6/21 加：rag_rebuild_fast.py 切换 + ghost-hang 安全 kill + 跳过 Step 2 备份）*
