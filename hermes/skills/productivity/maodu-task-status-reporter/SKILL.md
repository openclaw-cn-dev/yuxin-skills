---
name: maodu-task-status-reporter
description: '毛豆任务状态汇报Cron — 每15分钟检查团队任务Dashboard，增量汇报到飞书群。关键：Hash必须用原始task_id计算，不能normalize。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# 毛豆任务状态汇报 Cron

## 用途
每15分钟检查渔芯团队任务Dashboard状态，增量汇报到飞书群。

## ⚠️ heartbeat 入口提示（毛豆 profile）
毛豆 hourly cron 的 prompt 第一步是 `python3 ~/.hermes/scripts/heartbeat_check.py 毛豆`，**该脚本不存在**（在 Maodou profile 下解析路径找不到文件）。**跳过它，直接进入下方"核心逻辑"或运行 `scanner.py 毛豆 --no-claim`**（见末尾"⚠️ 2026-06-26 验证"节）。

## 调度
```bash
*/15 * * * *
```
或通过 cronjob tool 创建。

## 核心逻辑

### 1. 读取当前状态
```python
import sqlite3
conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')

# 已完成（status=completed 或 done）
c.execute("""
    SELECT task_id, title, assignee, status, priority, done_at
    FROM tasks
    WHERE status IN ('completed', 'done')
    ORDER BY done_at DESC
""")
completed_rows = c.fetchall()

# 未完成（pending + in_progress 都要跟踪！）
c.execute("""
    SELECT task_id, title, assignee, status, priority, updated_at
    FROM tasks
    WHERE status IN ('pending', 'in_progress')
    ORDER BY updated_at DESC
""")
pending_rows = c.fetchall()
```

### 2. 读取上次 checkpoint
```python
import json
with open('/Users/hua/.hermes/cron/output/last_report.json') as f:
    last_data = json.load(f)

# checkpoint 字段说明：
# - completed: 所有已完成任务（status=completed 或 done）的 task_id 列表
# - pending: 所有未完成任务（status=pending 或 in_progress）的 task_id 列表
# - hash: 从 completed 列表计算的 MD5 hash（原始 task_id，不做 normalize）
```

### 3. Hash 计算方式（关键！）
Hash 必须从 **原始 task_id** 计算，不做任何 normalize/deduplicate！

```python
import hashlib
current_raw_ids = sorted(set(r[0] for r in completed_rows))
current_hash = hashlib.md5(','.join(current_raw_ids).encode()).hexdigest()
```

**之前犯过的错误**：对 task_id 做 normalize（把 `task_overseer_0501061511_老莫` 和 `task_overseer_0501061511_毛豆` 合并成 `task_overseer_老莫`），导致：
- Hash 与 checkpoint 中存储的 hash 不匹配（存储的是 raw ID hash）
- 把真正不同的任务误判为同一个
- 汇报逻辑出错

### 4. 对比变更（重要更新！）

**Bug 场景：** checkpoint 文件的 `hash` 字段可能与从其中 `completed` 列表重新计算的 hash 不一致（文件损坏、或历史写入失败）。此时直接比较 hash 会误判为"有变更"。

**正确流程：** 先比较两个 completed 列表（set 差集），而非直接比较 hash。

```python
import hashlib

# 从 checkpoint 读取
last_completed_set = set(last_data['completed'])
last_pending_set = set(last_data.get('pending', []))

# 从 DB 读取当前
current_completed_set = set(r[0] for r in completed_rows)
current_pending_set = set(r[0] for r in pending_rows)

# 重新计算 hash（不信任 checkpoint 中的旧值）
current_hash = hashlib.md5(
    ','.join(sorted(current_completed_set)).encode()
).hexdigest()

# Completed 变更
newly_completed = current_completed_set - last_completed_set
removed_from_completed = last_completed_set - current_completed_set

# Pending 变更（新进入 in_progress 的任务）
newly_pending = current_pending_set - last_pending_set
removed_from_pending = last_pending_set - current_pending_set

has_real_change = (
    len(newly_completed) > 0 or
    len(removed_from_completed) > 0 or
    len(newly_pending) > 0 or
    len(removed_from_pending) > 0
)

# 如果 hash 不一致但列表一致，说明 checkpoint 文件损坏，只需修复 hash
# 如果列表有差异，才是真正的工作进展，需要发送汇报
```

**为什么不能直接比较 hash：**
- checkpoint 的 hash 可能因文件写入不完整而损坏
- 列表一致 + hash 不一致 → 只需更新 checkpoint 的 hash，无需发送飞书
- 列表不一致 → 才是真正的工作进展，需要发送汇报

### 5. 生成汇报模板

**同时有完成和进行中变更时（最常见，Overseer批量分配场景）：**
```
📌 LookForge进度更新

✅ 新完成：[任务名]（负责人）
✅ 新完成：[任务名]（负责人）

🔄 新进行：[任务名]（负责人）
🔄 新进行：[任务名]（负责人）

📋 进行中：共N个任务（阿福×M / 黑豆×K / ...）
```

**只有新完成时：**
```
📌 LookForge进度更新
✅ 新完成：[任务名]（负责人）
📋 进行中：共N个任务
```

**只有新的进行中时：**
```
📌 LookForge进度更新
🔄 新进行：[任务名]（负责人）
📋 进行中：共N个任务
```

**Overseer任务去重：** 同一任务可能被创建多次（Overseer批量分配）。展示时按 (title, assignee) 去重：
```python
seen = {}
for tid, title, assignee in new_entries:
    key = (title, assignee)
    if key not in seen:
        seen[key] = (tid, title, assignee)
```

### 7. 更新 checkpoint

**注意：** Hash 必须从当前 DB 数据重新计算，不要信任旧值。

```python
new_report = {
    "completed": sorted(list(current_completed_set)),
    "pending": sorted(list(current_pending_set)),
    "hash": current_hash  # 始终用重新计算的值
}
with open('/Users/hua/.hermes/cron/output/last_report.json', 'w') as f:
    json.dump(new_report, f, ensure_ascii=False, indent=2)
```

## 发送目标
- 飞书大群 DM: `cli_a964873dd7b8dbda`（已确认无效，实际用 ***SECRET***）
- 备注：飞书大群名称是 `渔芯科技（大群）`，但 Hermes Bot 尚未加入

## 注意事项
- `cli_a964873dd7b8dbda` 是无效的 target，不要使用
- 任务状态枚举有两个：`completed` 和 `done`，查询时必须同时包含
- Hash 一致时发送方应静默跳过发送（但 cron 会自动跳过 origin delivery）

## ⚠️ 2026-06-26 验证：cron 提示词中的 `heartbeat_check.py` 路径不存在

毛豆 hourly cron（job_id `28f82651884b`）的 prompt 第一步是：
```
python3 ~/.hermes/scripts/heartbeat_check.py 毛豆
```
该路径在 Maodou profile 下解析为 `/Users/hua/.hermes/profiles/maodou/home/.hermes/scripts/heartbeat_check.py` — **文件不存在**。

**绕过方案**：直接用 `scanner.py --no-claim` 查毛豆的任务：
```bash
cd "/Users/hua/Desktop/渔芯科技/团队协作" && python3 scanner.py 毛豆 --no-claim
```
返回 JSON `{agent, workspace, claimed:[], in_progress:[], pending:[]}`，三组都为空时即可静默。

如果修 cron prompt，`jobs.json` 在 `~/.hermes/profiles/maodou/cron/jobs.json`，改 `prompt` 字段即可（属于 profile 文件，需用户授权后修改）。
