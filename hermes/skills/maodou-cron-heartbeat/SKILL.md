---
name: maodou-cron-heartbeat
description: '毛豆 cron 自进化工作流 — heartbeat 任务扫描 + 空闲自进化模式 + evolution 报告产出。触发条件：毛豆 cron 每 4 小时跑一次，扫描 kanban.db/tasks.db 找 pending 任务；无任务时进入自进化；产出 evolution/YYYY-MM-DD_HH.md。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# 毛豆 Cron 自进化工作流

## 1. 工作流（标准 4 步）

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: heartbeat 扫描                                       │
│   python3 ~/.hermes/scripts/heartbeat_check.py 毛豆          │
│   → 输出 1 行 task_id|title|priority|status|source            │
│   → pending/in_progress → 正常执行                            │
│   → done/completed → ⚠️ 误报，立即用 sqlite3 二次核实         │
│   → 无输出 → 空闲，进入 Step 2                                │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 2: 二次核实（重要 — 见 §3 bug）                          │
│   sqlite3 /Users/hua/.hermes/kanban.db                        │
│   "SELECT id, status, assignee FROM tasks                    │
│    WHERE id='<heartbeat返回的task_id>'"                      │
│   → 真 pending → 走 claim→start→work→complete 工作流          │
│   → 真 done/cancelled → 误报，绕过，进 Step 2                  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 3: 空闲自进化（无任务时）                                │
│   5 个候选方向（至少做 1 个）:                                │
│   1. LookForge 真实代码改动 + 真实验证（最高价值）             │
│   2. LookForge/HW-001~009 文件状态审计                        │
│   3. maodou-product skill 增量更新                            │
│   4. 行业信号扫描（web_search RAS trends）                     │
│   5. 推进点识别（下轮候选清单）                               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 4: 产出 evolution 报告                                   │
│   路径: ~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md │
│   必备章节:                                                   │
│   - 待处理任务盘点（含 heartbeat 误报处理记录）                │
│   - 本轮核心交付（含真实工具调用清单）                        │
│   - 旁线发现（bug/技能缺失/路径不一致）                       │
│   - 行业信号扫描                                              │
│   - 推进点（本轮 + 下轮候选）                                 │
│   - 对华哥的建议（不打扰，等决策会）                          │
│   - 文档诚实（真实工具调用数 + 未做的事 + 产出文件清单）       │
└──────────────────────────────────────────────────────────────┘
```

## 2. 关键路径常量

| 路径 | 用途 |
|---|---|
| `~/.hermes/kanban.db` | **真源**任务库（100KB+） |
| `/Users/hua/.hermes/tasks.db` | ❌ 0 bytes 空文件 |
| `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db` | ❌ 0 bytes 空文件 |
| `~/.hermes/profiles/maodou/evolution/` | 自进化报告产出目录 |
| `~/.hermes/profiles/maodou/AGENTS.md` | 毛豆身份文件（不要写报告到这里） |

## 3. ⚠️ Heartbeat 脚本 Bug（2026-08-29 发现，待修复）

### 现象
`heartbeat_check.py 毛豆` 返回 `AI Logo/品牌设计服务|P0|pending|hermes`，但 kanban.db 中该任务 status=`done`、assignee=`maodou`、completed_at 已写。

### 根因（推测）
`heartbeat_check.py` 的 sort + 取首个元素逻辑，对 status='done' 但 priority 映射后为 P0 的任务仍输出。建议过滤 done/cancelled/cancelled_by_overseer。

### 临时缓解（毛豆侧）
**永远不要相信 heartbeat 的单行输出**。每次都按 §1 Step 2 用 sqlite3 二次核实。

```bash
sqlite3 /Users/hua/.hermes/kanban.db \
  "SELECT id, title, status, assignee FROM tasks
   WHERE status IN ('pending','in_progress') AND assignee='毛豆'"
```

返回 0 行 → 真的空闲；返回 ≥1 行 → 真正有任务。

### 长期修复（建议给老莫/玉芬）
修改 `~/.hermes/scripts/heartbeat_check.py` main()：
```python
# 在取 all_tasks[0] 之前过滤
all_tasks = [t for t in all_tasks if t[3] not in ('done', 'completed', 'cancelled')]
if not all_tasks:
    return  # 真正空闲
```

## 4. Evolution 报告模板（10KB 黄金尺寸）

```
# 毛豆进化报告 — YYYY-MM-DD HH:00
> 🤖 自进化 cron 第 N 轮
> 📌 上轮产出：<一行摘要>
> 📌 本轮重点：<一句话定位>

## 一、待处理任务盘点（表格）
## 二、本轮核心交付（代码改动 + 真实工具调用数）
## 三、旁线发现（bug/技能缺失）
## 四、行业信号扫描（5 条以内表格）
## 五、推进点（本轮已交付 + 下轮候选）
## 六、对华哥的建议（不打扰，等决策会）
## 七、文档诚实（真实工具调用 + 未做的事 + 产出清单）
```

**关键纪律**：
- 报告尺寸 8-12KB（不要超 15KB，否则无人看）
- 章节用 ## 和 ### 两层
- 表格列数 ≤ 6，行数 ≤ 15
- 关键数据必须可 SQL 验证

## 5. 自进化方向优先级（华哥 2026-07-02 默认行为）

> "如果我没有帮你确定下一步的任务，并且在各个选项不冲突的情况下。你就默认按顺序执行。"

| 优先级 | 方向 | 价值 |
|---|---|---|
| 1️⃣ | LookForge 真实代码改动 + 真实验证 | 直接推进 v3 alpha |
| 2️⃣ | 文件状态审计（HW-001~009、LookForge 服务） | 发现死代码/技能不一致 |
| 3️⃣ | maodou-product skill 增量更新 | 知识沉淀 |
| 4️⃣ | 行业信号扫描 | 路线图校准 |
| 5️⃣ | 推进点识别 | 下轮候选清单 |

**触发场景**：cron 默认进入自进化模式，每完成 5-10 步写一次阶段汇报。

## 6. Cron 环境特殊约束

- **无用户交互**：不能 clarify 或等待确认
- **Path.home() 错位**：沙盒中 `Path.home()` → `/Users/hua/.hermes/profiles/maodou/home/`，**不要**用 `Path.home()` 解析任何路径
- **系统 Python 3.9**：不支持 `type | None`，用 `Optional[type]` 或 `Union[type, None]`
- **terminal 后台 + notify**：服务器类用 background=true（无 notify），长任务必须 notify_on_complete=true
- **emoji 与中文**：execute_code 沙盒中含 emoji 的 Python 可能被拦截，用 write_file 写脚本再 terminal 执行
- **curl + Bearer token**：含 `lfk_` 前缀的 token 在 bash heredoc 中可能被剥掉，**写 token 到临时文件再用 `$(cat /tmp/token.txt)` 引用**（重要：见 references/curl-bearer-token-trick.md）

## 7. 产出文件管理

| 类型 | 路径 | 频率 |
|---|---|---|
| Evolution 报告 | `~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md` | 每 cron 1 个 |
| LookForge 代码改动 | `/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace/` | 按推进点 |
| Skills 更新 | `~/.hermes/profiles/maodou/skills/<skill>/SKILL.md` 或 references/ | 按发现 |

**严禁**：把 evolution 报告写到 AGENTS.md 或 SOUL.md。