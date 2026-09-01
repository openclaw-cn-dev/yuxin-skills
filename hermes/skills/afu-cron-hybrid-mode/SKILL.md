---
name: afu-cron-hybrid-mode
description: 阿福 cron「任务+进化」混合模式 playbook — 当华哥 P0/P1 直接派单时打破 4h 标准节奏，先执行任务再走 5 方向进化副产品。触发条件：heartbeat_check 返回 pending 任务且华哥/玉芬 inbox 派单文件存在；或 kanban.db 出现 assignee='阿福' 的 pending 任务。
version: 1.0.0
author: 渔芯科技 / 阿福
tags: [afu, cron, hybrid, p0-paiding, evolution, kanban]
changelog:
  - 1.0.0 (2026-08-30 18:10) — 首次创建；沉淀自 evolution/2026-08-30_18.md（第 33 档）「首次混合模式实测」；补全 ***SECRET*** v1.0.1 的 playbook 缺失部分
---

# 阿福 cron「任务+进化」混合模式 Playbook

> 🎯 适用：阿福 cron 档，**当 heartbeat 返回 pending P0/P1 任务时**
> 📌 来源：evolution/2026-08-30_18.md（第 33 档，首次实测）
> 🔗 关联：`***SECRET***` v1.0.1（标准 5 方向进化）+ `afu-workflow`（任务领取）

---

## 1. 何时进入混合模式

| 场景 | 模式 | 触发信号 |
|---|---|---|
| 无 pending 任务 | **纯进化模式** | heartbeat 返回 0 任务 → 走 5 方向 SOP |
| **有 P0/P1 pending 任务** | **混合模式（本 playbook）** | heartbeat + inbox 派单文件 + kanban.db 三重验证 |
| 只有 P2/P3 任务 | **进化模式 + 顺手 P2/P3** | 5 方向进化过程中完成 P2/P3 |

> **核心原则**：**华哥直接派单 = 最高优先级**（AGENTS.md 铁律第一条），即使会推迟 4h 标准节奏也要执行。

---

## 2. 5 阶段 SOP（约 90-120 分钟）

### Stage 1：心跳 + 任务分类（5 分钟）
```bash
# 绝对路径铁律（HOME 劫持）
python3 /Users/hua/.hermes/scripts/heartbeat_check.py 阿福

# 输出格式：task_id|title|priority|status|source
# 判定：有 P0/P1 → 混合模式；无 → 纯进化
```

### Stage 2：读取派单详情（5 分钟）
```bash
# 2.1 读 inbox 派单文件
ls /Users/hua/.hermes/orchestration/messages/afu/inbox/
cat /Users/hua/.hermes/orchestration/messages/afu/inbox/task_<date>_<topic>.md

# 2.2 验证 kanban.db 任务（真源）
sqlite3 /Users/hua/.hermes/kanban.db \
  "SELECT id, title, priority, status, body FROM tasks WHERE assignee='阿福' AND status='pending';"
```

### Stage 3：领域判定（2 分钟）
| 判定 | 行动 |
|---|---|
| **本职内**（客服/异议/RAS/心理学）| 直接执行 |
| **跨领域协助**（如量化行为金融）| 发挥 influence-psychology / hooked-ux / mom-test 优势 |
| **非阿福职责**（工程/UI/纯建模）| 转交玉芬/对应同事，**回复华哥已转交** |

### Stage 4：执行任务 + 产出副产品（60-90 分钟）

**本职内任务**：按方向 2「学 1 个新技巧」流程执行
**跨领域协助任务**：阿福心理+行为背景切入，3 件套产出：
1. 调研报告（evolution/_afu_<topic>_v1.md）
2. memory 沉淀（如有可提炼的技巧）
3. RKR 中转站入库（staging_save.py research source）

### Stage 5：收尾（10 分钟）
```bash
# 标 kanban.db 任务 done（必须！）
sqlite3 /Users/hua/.hermes/kanban.db \
  "UPDATE tasks SET status='done', completed_at=$(date +%s),
   result='<50字总结>' WHERE id='<task_id>';"

# 走剩余 5 方向进化（如时间允许）：
# - 复盘 3 次对话
# - 学 1 个新技巧（**与 P0 任务同源最佳**）
# - RAS 弹药盘点
# - skills 自检
# - 输出 evolution 报告
```

---

## 3. 验证清单（混合模式必跑）

- [ ] P0 任务在 kanban.db 已标 `done`（status + completed_at + result 三字段全填）
- [ ] 调研报告已写入 `evolution/_afu_<topic>_v1.md`（绝对路径）
- [ ] memory 沉淀已写入（如果有新技巧/方法）
- [ ] RKR 中转站已入库（staging_save.py 走 research source）
- [ ] **未误写到** `~/.hermes/profiles/afu/home/rkr_staging/...`（HOME 劫持铁律）
- [ ] evolution 报告包含本档完整的 5 方向产出 + 待办状态
- [ ] **诚实标注节奏打破**：晚于 4h 节奏时，evolution 报告 §0 启动校验必须显式记录 `延迟 X 小时`

---

## 4. 与纯进化模式的关键差异

| 维度 | 纯进化模式 | 混合模式 |
|---|---|---|
| 触发 | 无任务 | 有 P0/P1 |
| 节奏 | 严格 4h | **可能延后**（P0 优先）|
| 产出重点 | 5 方向各 1 件 | **任务本身**为主，5 方向为辅 |
| 心态 | 主动探索 | **目标导向** |
| 节奏打破记录 | 不需要 | **必须诚实标注** |

---

## 5. Pitfalls（本档实证 + 提前规避）

### Pitfall A — heartbeat 路径 HOME 劫持
- ❌ `python3 ~/.hermes/scripts/heartbeat_check.py 阿福` → `[Errno 2]`
- ✅ `python3 /Users/hua/.hermes/scripts/heartbeat_check.py 阿福`

### Pitfall B — kanban.db vs yaml 双轨制混淆 ⚠️ 重要
- **现状**：
  - `/Users/hua/.hermes/kanban.db`（SQLite 真源）—— 华哥派单
  - `/Users/hua/.hermes/state/tasks/active/*.yaml`（legacy 文件系统）—— 玉芬/老任务
- **工具适用性**：
  - `list_task.py --status active` → **只读 yaml**
  - `update_task.py --task-id <id>` → **只改 yaml**
  - `sqlite3 /Users/hua/.hermes/kanban.db "..."` → **只读改 kanban.db**
  - `heartbeat_check.py` → **两者都查**（只读）
- ❌ 用 `update_task.py` 标华哥 kanban.db 任务 → `未找到任务`
- ✅ 用 `sqlite3` 直接更新 kanban.db
- 必填：先看任务 ID 格式（`task_*` = kanban.db / `T-2026-*` = yaml）

### Pitfall C — staging_save --source 取值受限
- ❌ `--source quant` → `invalid choice`
- ✅ `--source research`（最接近量化调研的合法值）
- 合法值：`research / generated / report / raw / yuxin / findera / default`，无 `quant`

### Pitfall D — Evolution 报告文件名必须 24h 制 HH
- ❌ `2026-08-30_18:10.md`
- ✅ `2026-08-30_18.md`（与历史 evolution 文件名一致）

### Pitfall E — web_extract 后端受限
- ❌ `web_extract` 多数 URL 失败（ddgs 仅搜索不可抽取）
- ✅ `browser_navigate` + 必要时回退 `web_search` snippet 提取
- 必填：snippet 级证据 + 多源交叉验证，**不强行编造全文**

### Pitfall F — execute_code 在 cron 模式下被拒
- ❌ `execute_code` 跑 subprocess → `BLOCKED: ... bypass shell-string approval checks`
- ✅ 改用 `terminal()` 直接跑命令
- 必填：cron 档不要尝试 execute_code 调 subprocess

### Pitfall G — 节奏打破不诚实记录
- ❌ 把延后档位说成「按节奏」
- ✅ evolution 报告 §0 启动校验显式标注 `延迟 X 小时 + 破例原因`

### Pitfall H — 任务完成不更新 kanban.db
- ❌ 写完产物就算任务完成 → 任务永远 pending
- ✅ 必填 `UPDATE tasks SET status='done', completed_at=..., result='...'`

---

## 6. 节奏打破的诚实记录模板

```yaml
rhythm_break_record:
  scheduled_slot: 2026-08-30_16
  actual_slot: 2026-08-30_18
  delay_hours: 2
  reason: 华哥 P0 派单（行为金融调研，双任务）
  resolution: 已写入 evolution-protocol v1.0.1「华哥 P0 派单 SOP」+ 本 playbook 完整 SOP
  risk: 连续 P0 派单持续推迟节奏 → 建议玉芬/华哥评估任务专属 cron 分流
  honesty: 本档严格遵循「简化版进化指令」(5 方向 + 报告输出到固定路径)
```

---

## 7. 本档实证（2026-08-30 18:10 第 33 档）

### 7.1 派单详情
- **来源**：华哥 → 玉芬 → 阿福 inbox
- **任务**：P0-1（散户情绪因子）+ P0-2（情绪指数+微观结构）
- **task_id**：`task_1788067928_f21a71` + `task_r2_1788083470_b17db3`

### 7.2 产出（10 件）
| 类型 | 路径 | 大小 |
|---|---|---|
| P0-1 行为金融散户情绪因子（8 因子）| `evolution/***SECRET***.md` | 14.6 KB |
| P0-2 投资者情绪+微观结构（7 因子）| `evolution/***SECRET***.md` | 13.4 KB |
| 衍生技巧 #52 锚定重构（与 P0 同源）| `evolution/_afu_tactic_anchor_reframe_v1.md` | 11.7 KB |
| RAS 弹药 T/U/V | `evolution/_afu_ras_ammunition_20260830.md` | 8.1 KB |
| 进化报告（本档）| `evolution/2026-08-30_18.md` | 24.9 KB |
| memory 沉淀 | `memory/***SECRET***.md` | 11.7 KB |
| RKR 入库（4 件）| `/Users/hua/rkr_staging/文档中转站/01-调研资料/` | 4 份 md + 4 meta.json |
| skills 升版 | ***SECRET*** v1.0.0 → v1.0.1 | changelog+章节 |

### 7.3 关键判断
- **本职内？**：❌ 跨领域（量化行为金融）
- **阿福优势切入**：✅ psychology + hooked-ux + mom-test 完美契合 Kahneman 前景理论 + 散户行为
- **节奏打破**：2h（16:00 → 18:10）

---

## 8. 升级建议（待玉芬/华哥决定）

### 8.1 短期
- 在 AGENTS.md 写明「华哥直接派单 P0/P1 走混合模式」
- 在 evolution-protocol SKILL.md 顶部引用本 playbook

### 8.2 中期
- 统一任务 DB（kanban.db ↔ yaml），消除双轨制
- 评估「任务专属 cron」分流（避免混合模式持续破节奏）

### 8.3 长期
- 混合模式成熟化 → 形成阿福差异化竞争力
- 推广到其他同事（玉芬/毛豆/老莫/黑豆/小宝）

---

## 9. 引用 & 关联

- **主 skill（已升版）**：`***SECRET***` v1.0.1（patch 增加了「华哥 P0 派单 SOP」+ 自主沉淀清单扩到 #52）
- **AGENTS.md**：「华哥直接指令 = 最高优先级（铁律第一条）」
- **本档实证**：evolution/2026-08-30_18.md（第 33 档）
- **memory 沉淀**：`memory/***SECRET***.md`（衍生 #52）
- **RKR 入库**：4 份产物在 `/Users/hua/rkr_staging/文档中转站/01-调研资料/`
- **相关 skill**：afu-workflow（任务领取）/ afu-customer-service（话术剧本）/ aquaculture（RAS 行业知识）

---

> 🤖 阿福 cron 进化档 · 2026-08-30 18:10 v1.0
> 📌 首次「任务+进化」混合模式实测通过
> 📌 8 个 Pitfall + 5 阶段 SOP + kanban/yaml 双轨制认知
> 📌 class-level umbrella 沉淀，跨 session 可复用