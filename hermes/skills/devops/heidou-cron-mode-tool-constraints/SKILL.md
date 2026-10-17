---
name: cron-mode-tool-constraints
description: heidou self-evolution cron 触发下 execute_code 等工具的 BLOCKED 约束实战记录 + 替代方案 + §37 周末傍晚档决策树分支沉淀。触发场景:任何黑豆 cron 自进化会话。
---

# cron_mode 工具约束实战记录(2026-09-13 18 时档首登 · 坑 #CR)

> 适用范围:所有黑豆(heidou profile)self-evolution cron 触发场景
> 沿用:本 skill 是 ***SECRET*** 的 cron_mode 工具约束子型,实战沉淀

## §0 核心结论(必读)

cron_mode 下,`execute_code` 工具被永久 BLOCKED(无用户在旁审批)。所有需要批量处理 / 多工具编排 / subprocess 调用的场景,**必须改用普通工具链**(terminal / read_file / write_file / patch / search_files)。

## §1 BLOCKED 工具完整清单

| 工具 | 拦截原因 | 替代方案 |
|---|---|---|
| `execute_code` | 执行任意本地 Python(含 subprocess 绕过 shell-string 审批) | `terminal` 跑 heredoc / `write_file` 直接覆盖 |
| `process` | 后台进程管理在 cron 上下文禁用 | `terminal` foreground only |
| `delegate_task` | cron 默认 max_spawn_depth=1,不派生子代理 | 主 agent 自己处理 |
| `text_to_speech` | 用户交互工具,cron 无对象 | 不需要 |
| `vision_analyze` | 用户交互工具,cron 无对象 | 不需要 |

## §2 execute_code 拦截原文(2026-09-13 18:32 实测)

```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls
that bypass shell-string approval checks). Cron jobs run without a user present
to approve it. Use normal tools instead, or set approvals.cron_mode: approve
only if this cron profile is intentionally trusted.
```

## §3 实战替代案例 · evolution_log.md 补登

**原计划(被 BLOCKED)**:
```python
# 想用 execute_code 拼 evolution_log.md 补登条目
import os
from datetime import datetime
log_path = "/Users/hua/.hermes/profiles/heidou/evolution/evolution_log.md"
entry = """..."""
with open(log_path, "a", encoding="utf-8") as f:
    f.write(entry)
```

**实际替代(用 terminal heredoc)**:
```bash
cat >> /Users/hua/.hermes/profiles/heidou/evolution/evolution_log.md << 'EOF'

## 2026-09-13 18:32(本条 · 周末傍晚档收口子型)
- ...(entry 内容)...

EOF
```

## §4 反模式(必须避免)

- ❌ 用 `python3 -c` 走 terminal 绕过 — 仍受 cron_mode 审计(terminal 内 subprocess 也会拦截)
- ❌ 用 `python3 << EOF` 走 heredoc 间接执行 — 同上
- ❌ 反复 retry `execute_code` 期待放开 — 不会自动放开,需要华哥显式授权 `approvals.cron_mode: approve`
- ❌ 改用 `delegate_task` 派生 subagent 绕开 — cron_mode 默认 max_spawn_depth=1,且 subagent 同样受 cron_mode 约束

## §5 解禁条件

仅当 cron profile 被显式授权 `approvals.cron_mode: approve` 才可解禁 `execute_code`。授权窗口由华哥拍板,日常 cron 触发**默认按 BLOCKED 假设写脚本**。

## §6 允许工具完整清单(cron 模式下)

✅ `terminal`(foreground only, ≤ 600s)✅ `read_file` / `write_file` / `patch` ✅ `search_files` ✅ `web_search` / `web_extract` ✅ `skill_view` / `skill_manage`(skill 管理)✅ `memory`(持久记忆,若未禁用)✅ `todo`(任务列表)

## §7 沿用坑列表(本档累计登记)

- 坑 #H:heartbeat_check.py 简化版永远空 stdout(沿用既有)
- 坑 #BW:heartbeat_check.py 简化版列名错配(累计第 3 次登记,本档 18 时档)
- 坑 #AS:staging_save.py 第 36 行 Path.home()(累计第 14 次登记,本档 18 时档)
- 坑 #AW:9-7_cron_startup 第 33 行错误 kanban.db 路径(累计第 19 次登记,本档 18 时档)
- 坑 #X:skill_view 加载失败累计 ≥ 13 次(本档 18 时档,触发独立索引卡阈值)
- 🆕 **坑 #CR**:cron_mode 下 execute_code BLOCKED(本档首登,2026-09-13 18 时档)

## §8 §37 周末傍晚档决策树分支(2026-09-13 实战沉淀)

> **触发条件**(同时满足):
> 1. 周末(周六/周日)18 时档 — 比 16 时档更临近全日收口
> 2. 阶段 0 五确认全过 + 4 主题全饱和(compliance ≥ 30 / contracts ≥ 31 / sop ≥ 100 / skills 审计 v1.0 已就位)
> 3. N=5(4 方向 + 1 输出)

> **行为模式**:严守纪律不执行 1-4 方向,只做"输出 evolution 报告 + 议题沿承登记"。**严禁"全拒绝 0 产出"**。

### 与 §37 周末午后档延伸型的差异

| 维度 | 16 时档(午后) | 18 时档(傍晚) |
|---|---|---|
| 位置 | 全日 round 9(中段) | 全日 round 10(末段前) |
| 字数上界 | 6~13 KB | 6~13 KB |
| 议题沿承 | 4 项 | 4 项(沿用 16 时档) |
| skills 扫描 | 仅议题登记 | **增量加 1 项 skills 状态扫描**(7 个 heidou 专属 skill 健康检查) |
| 下档预告 | 18 时档(傍晚) | **20 时档(夜晚)→ 22 时档(全日收口子型判定)** |

### 9 条不越界声明(周末傍晚档专用)

① 不学新政 ② 不重写 v1.x ③ 不抢下档活(20 时档)④ 不出新 memory ⑤ 不动既有 skills(除非授权)⑥ 不绕过 cron_mode ⑦ 不擅改 staging_save.py ⑧ 不抢 9-15 申报活 ⑨ **不抢 22 时档全日收口判定活**(本档末尾仅做预告)

## §9 决策树 elif 单条件命中规则 · v1.16 升级(2026-09-13 实战)

> 原规则仅描述"4 方向饱和就不执行",实战发现需细化 **N=5 时第 5 方向必须执行**(避免"全拒绝 0 产出")。

### 命中优先级

1. **方向 1-4 全饱和** → 严守纪律不执行 → ✅ 输出 evolution(方向 5)
2. **方向 1-4 部分饱和** → 按饱和度决定执行/不执行 → ✅ 输出 evolution
3. **方向 1-4 全开放** → 全执行 → ✅ 输出 evolution

### 反模式(必须避免)

- ❌ "全拒绝 0 产出":4 方向都饱和就拒绝写 evolution → 浪费 cron 触发,决策树失去意义
- ❌ "全执行不饱和":4 方向都已饱和还硬出新 memory/skills → 重复造轮子,违反 §三 沿用既有
- ❌ "跨档抢活":把下档的活(如周末简报预备 / 全日收口判定)提前做 → 破坏节奏

---

> 📌 **实战来源**:2026-09-13 18 时档(本档)第 10 次自进化 cron 触发
> 📌 **报告路径**:`/Users/hua/.hermes/profiles/heidou/evolution/2026-09-13_18.md`
> 📌 **配套 skill**:***SECRET***(本 skill 是其 cron_mode 子型,沿用既有决策树 v1.16)
