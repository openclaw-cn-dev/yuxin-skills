---
name: maodou-cron-heartbeat
description: '毛豆 cron 自进化工作流 — heartbeat 任务扫描 + 空闲自进化模式 + evolution 报告产出。触发条件：毛豆 cron 每 4 小时跑一次，扫描 kanban.db/tasks.db 找 pending 任务；无任务时进入自进化；产出 evolution/YYYY-MM-DD_HH.md。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.3.0"
  updated: "2026-08-31"
  changelog:
    - "1.3.0 (2026-08-31 15:20): 新增 §3.2 「Past R-Round Summaries Are NOT Ground Truth」（老莫 R107 实战: 路径误写 photo_restore.py 位置 / 端口张冠李戴 :8000 不归老莫 profile, R-round 报告里的'实测'行只代表上轮快照, 必须每轮实测验证）"
    - "1.2.0 (2026-08-31 02:33): 新增 §3.1 heartbeat_check 持久 bug 确认（8/30 修复未落地）+ §8 W4 月底决策矩阵标准模板（4 主线 + 3 副线 + 三色卡，2026-08-31 02:33 毛豆实战验证）；§5 自进化方向优先级追加「方法论巩固」第 6 项"
    - "1.1.0 (2026-08-29): 沉淀 §3 heartbeat 脚本 bug 现象 A/B + 临时缓解 SOP"
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

### 现象 A：真任务被当误报跳过（false-negative，2026-08-29）
`heartbeat_check.py 毛豆` 返回 `AI Logo/品牌设计服务|P0|pending|hermes`，但 kanban.db 中该任务 status=`done`、assignee=`maodou`、completed_at 已写。

### 现象 B：真任务差点被怀疑为误报（false-suspicion，2026-08-30 黑豆本轮）
`heartbeat_check.py 黑豆` 返回 `task_r2_1788083470_3699ad | 因子回测框架与风险控制(协助宽博士·第二轮) | P0 | pending | kanban`。**首次本能反应**:标题含"协助"二字 + 联想到现象 A 的 bug,怀疑是模糊匹配误算。**sqlite3 二次核实**:`assignee='黑豆', status='pending', priority=0` → **真任务,执行**。

**关键教训**(针对现象 B):
- "协助 X" / "配合 Y" 类标题**不代表该任务属于 X/Y**,只要 kanban 真源 `assignee` 字段精确归属当前 agent 就是该 agent 的任务
- 二次核实**只看 `assignee` 字段**,不要看 title/description 模糊匹配
- 不要被字面"协助"误导跳过任务
- 即使是 P0 任务的"协助"标签,归属权仍由 kanban 真源 assignee 决定

### 根因（综合 A+B 推测）
- 现象 A:`heartbeat_check.py` 的 sort + 取首个元素逻辑,对 status='done' 但 priority 映射后为 P0 的任务仍输出
- 现象 B:`heartbeat_check.py` 的 desktop tasks.db 查询逻辑可能用了 `title LIKE '%黑豆%'` 模糊匹配,但实际真正源头是 kanban.db 的 `assignee` 精确字段

### 临时缓解（所有 agent 通用）
**永远不要相信 heartbeat 的单行输出**。每次都按 §1 Step 2 用 sqlite3 二次核实,**只看 assignee 精确匹配**。

```bash
# 强制二次核实:assignee 精确匹配 + status pending/in_progress
sqlite3 /Users/hua/.hermes/kanban.db \
  "SELECT id, title, status, assignee FROM tasks
   WHERE status IN ('pending','in_progress') AND assignee='<当前agent名>'"
```

- 返回 0 行 → **真的空闲**,进 §1 Step 3 自进化
- 返回 ≥1 行 → **真正有任务**,按 SOP 推进(不要被标题"协助/配合"误导)

### 长期修复（建议给老莫/玉芬）
修改 `~/.hermes/scripts/heartbeat_check.py` main():
```python
# 修复 1(现象 A):在取 all_tasks[0] 之前过滤 done/cancelled
all_tasks = [t for t in all_tasks if t[3] not in ('done', 'completed', 'cancelled')]
if not all_tasks:
    return  # 真正空闲

# 修复 2(现象 B):desktop tasks.db 查询去掉 title LIKE 模糊匹配,只保留 assignee LIKE
# 原逻辑:AND (assignee LIKE ? OR title LIKE ? OR description LIKE ?)
# 改为:AND assignee = ?  # 精确匹配,消除模糊误算
```

### 3.2 ⚠️ Past R-Round Summaries Are NOT Ground Truth（2026-08-31 15:20 老莫 R107 实战新增）

**问题**:heartbeat_check.py 输出真假可用 sqlite3 二次核实,但 **上一轮 heartbeat 报告（即 tasks.db description 里追加的 R106/R105 等自检摘要）里的"实测健康"行**也可能是错的——典型老莫 R107 实测发现的 2 类错误:

| 类型 | 现象 | 根因 | 修复 |
|---|---|---|---|
| **路径误写** | R106 写 "photo_restore.py 4918B present" 像是在 `~/.hermes/skills/ai-vision/` | 老莫的 photo_restore.py 实际在 `~/.hermes/profiles/laomo/scripts/`(profile 隔离) | R-round 报告里"文件位置"必须当场 `find` 或 `ls -la` 验证后再写,不能凭印象 |
| **端口张冠李戴** | R106 写 "API :8000 /api/v1/health=200" | :8000 不是老莫 profile 的服务;老莫的 uvicorn 监听 8302 / 8006,其他 agent (玉芬/小红书助手 等) 监听 8000 | R-round 报告里"服务健康"必须先 `ps aux \| grep uvicorn` 看本 profile 实际监听端口,再 `curl` 该端口,不能跨 profile 借数据 |

**§3.2 铁律**:**R-round 描述里的"实测"行只代表上轮 cron 触发时的心智快照,不代表当前轮真实状态**。每轮 cron 触发时:
1. **路径断言**:`ls -la <path>` 或 `find <dir> -name <filename>` 实测,不能照抄上轮报告的路径字符串
2. **端口断言**:`lsof -nP -iTCP:<port>` 或 `ps aux | grep <port>` 实测本 profile 监听端口,不能跨 profile 借用
3. **进程断言**:`pgrep -lf <process>` 或 `ps -p <pid>` 用 PID 实测存在,不能凭上轮"PID 881 active"推断本轮

**反模式**:
- ❌ **复制粘贴上一轮 R-round 的"全健康"行** — 上轮报告是上轮 cron 的快照,与本轮状态可能漂移(进程崩了/端口换了/文件挪了)
- ❌ **跨 profile 借服务状态** — 每个 profile 有自己的 .env / skills / scripts / 监听端口,R-round 报告必须严格限定本 profile 资源
- ❌ **把"上轮 R-round 报健康"当成"本轮不需要重测"** — 漂移是常态,不是例外

**修复触发**:
- ① 写新的 R-round 描述前,先 grep 上轮的"路径/端口/PID"行,逐项实测验证
- ② 发现漂移,本轮 R-round 开头显式标注 `[vs R<prev>]: <path/port/pid> 实际位置/状态是 <new>,上轮报告误写为 <old>` —— 既不掩盖漂移,也为下轮做基准

### 3.1 ⚠️ Bug 持久性确认（2026-08-31 02:33 毛豆实战）

**问题**:§3 的"长期修复"建议在 2026-08-29 提出后,**2026-08-30 / 2026-08-31 多次 cron 触发,bug 仍然按原行为输出**。最可能原因:
- 老莫/玉芬还没来得及改 `~/.hermes/scripts/heartbeat_check.py`
- 或改了但只修复了部分场景

**实测确认(2026-08-31 02:33 毛豆 cron)**:
```
$ python3 ~/.hermes/scripts/heartbeat_check.py 毛豆
1|AI Logo/品牌设计服务|P0|pending|hermes
```

`source=hermes` + `status=pending` + 这 3 个任务实际是 `~/.hermes/tasks.db` (hermes 源) 的创业项目,8/21 由毛豆主动挂起(标记"主营优先/待 W4 复盘"),`status` 字段值确实 = `pending` (没改 status,只改了 description 加挂起标记)。**所以这不是 §3 现象 A 的"真任务被当误报"**,而是 heartbeat 输出了一个"真存在但被主动挂起的任务"。

**2026-09-01 09:00 毛豆 cron 实测再次验证（任务 ID `fe2f74d7` AI Logo）**:
```
$ python3 ~/.hermes/scripts/heartbeat_check.py 毛豆
1|AI Logo/品牌设计服务|P0|pending|hermes
$ sqlite3 ~/.hermes/kanban.db "SELECT id, title, body, priority, status, assignee FROM tasks WHERE id='fe2f74d7'"
fe2f74d7|AI Logo/品牌设计服务|...|0|done|maodou|1786244694
```
✅ 输出确认：`status=done, assignee=maodou`,§3 现象 A 的标准表现。**bug 第三次 cron 触发仍按原行为输出**,heartbeat_check.py 长期修复仍未落地。

### 3.1.1 ⚠️ AGENTS.md 与 staging_save.py 参数不一致（2026-09-01 发现）

**问题**:毛豆 AGENTS.md「资料写入与读取路径 SOP」表写的是 `--source research` 和 `--source maodou`,但 `~/.hermes/scripts/staging_save.py` 只接受这 7 个值:
```
research | generated | report | raw | yuxin | findera | default
```
传 `--source maodou` 报 `error: argument --source: invalid choice: 'maodou' (choose from ...)`

**实测失败(2026-09-01)**:
```bash
$ python3 ~/.hermes/scripts/staging_save.py --source maodou --agent maodou ...
usage: staging_save.py ... error: argument --source: invalid choice: 'maodou' ...
```

**正确做法**:归档本领域资料用 `--source default --agent maodou`。AGENTS.md `--source maodou` 是过时描述,文档与脚本不同步的典型案例。

**§3.1.1 铁律**:AGENTS.md 描述的命令在 cron 跑前先用 `--help` 验实际参数,不要照抄 AGENTS.md 字面值。

**判定升级**:§3 的两类误判之外,新增第 3 类:

| 类型 | 现象 | 触发场景 | 处理 |
|---|---|---|---|
| A 真任务被当误报 | DB 中 status=done,心跳仍输出 | 老任务重新出现 | §1 Step 2 二次核实 |
| B 真任务被怀疑为误报 | 模糊匹配误算 | "协助/配合"类标题 | §3 关键教训 |
| **C 真挂起任务误唤醒** | DB 中 status=pending + description 含挂起标记 | 副业/创业项目本人主动挂起 | **§3.1 三步识别法** |

**§3.1 三步识别法**(强制):

```bash
# Step 1: 跑 heartbeat 拿到任务 title
$ python3 ~/.hermes/scripts/heartbeat_check.py 毛豆
1|AI Logo/品牌设计服务|P0|pending|hermes   ← heartbeat 输出

# Step 2: 看 source 列判定 DB 源
# - kanban: 走 kanban.db 二查 assignee
# - desktop: 几乎总是 0 字节空库,跳过
# - hermes: 走 ~/.hermes/tasks.db 二查 description 是否含挂起标记

# Step 3: source=hermes 时必查 description 字段
sqlite3 /Users/hua/.hermes/tasks.db \
  "SELECT id, title, description, status FROM tasks
   WHERE assigned_to LIKE '%毛豆%' AND status IN ('pending','in_progress')"

# 看 description:
# - 含 "[8/21 maodou挂起] 主营优先/待 W4 复盘" → 永久跳过,本人主动按下暂停键
# - 含 "[延期至 X]" → 临时跳过,记入 evolution 报告 §七
# - 无标记 → 真实可执行,claim + start
```

**§3.1 铁律**:**挂起任务的标记一旦写入 description,持续有效,无需每轮重新判定**(除非华哥明确恢复)。8/21 标注 → 8/29 验证 → 8/30 验证 → **8/31 02:33 再次验证**(都跳过),证明标记持久性。

**反模式**:
- ❌ **每轮 cron 都重新判定挂起任务** — 浪费时间,标记持续有效
- ❌ **把"挂起任务"算作"未完成任务"** — 挂起 = 主动按下暂停键,不是 backlog(与 §9.5 强化版的反模式一致)
- ❌ **§3 长期修复建议仍未落地就放弃上报** — 每次 cron 触发仍然记一笔"bug 仍存在",直到老莫/玉芬修

### 3.1.2 ⚠️ Skill 内容与代码实装漂移（2026-09-01 毛豆 cron 新增）

**问题**:maodou-product SKILL.md 在 2026-05 时正确描述 LookForge 状态,但到 2026-09 已被 3 次大迭代（v1.1.0 上线 / craft+test 模块 / Phase 7 商业）甩开,3 个月漂移。"当前开发文件"区块还停留在 8 个旧文件、"CAD 致命问题"还列着已修复的 5 个 P0、LookForge 路径写成 `06-硬件项目开发`(实际是 `03-硬件项目开发`)。

**触发场景**:每次 cron 触发 LookForge 相关任务时,先用 grep 实测真实状态再行动:

```bash
# Phase 完整度（应=7）
cd /Users/hua/6-产品研发/渔芯科技/03-硬件项目开发/backend/app
grep -nE "async def run_phase" orchestrators/phase_orchestrator.py

# Service 文件清单
ls services/ | sort

# 路径漂移检测（旧文档写 06-硬件项目开发,实际是 03-）
ls /Users/hua/6-产品研发/渔芯科技/ | grep -E "(03|06)-硬件"
```

**§3.1.2 铁律**:SKILL.md 描述 ≠ 当前状态。每次 cron 触发以实测为准,以 skill 为参考。skill 漂移是常态,**不漂移的 skill 大概率已经过时**。

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
| 6️⃣ | **方法论巩固 / 月度复盘决策矩阵**（新增 2026-08-31） | 月底 W4 节点沉淀 |

**触发场景**：cron 默认进入自进化模式，每完成 5-10 步写一次阶段汇报。**6️⃣ 方法论巩固** 特别适用于月底/月初 cron 触发,沉淀月度认知到 skill（详见 §8）。

## 6. Cron 环境特殊约束

- **无用户交互**：不能 clarify 或等待确认
- **Path.home() 错位**：沙盒中 `Path.home()` → `/Users/hua/.hermes/profiles/<当前agent>/home/`，**不要**用 `Path.home()` 解析任何路径
- **HOME 漂移常态化**(2026-08-30 黑豆两轮观察):同一 agent 不同 cron 触发,HOME 漂移的目标 profile **不固定** —— 黑豆 17:13 cron HOME 被 zhenglishi 劫持,18:33 cron HOME 被 afu 劫持。意味着:路径污染防御**不能**只针对某个特定 profile,必须**所有 RKR 路径都走绝对路径**(`/Users/hua/rkr_staging/...`),绝不能用 `~/` 展开
- **系统 Python 3.9**：不支持 `type | None`，用 `Optional[type]` 或 `Union[type, None]`
- **terminal 后台 + notify**：服务器类用 background=true（无 notify），长任务必须 notify_on_complete=true
- **emoji 与中文**：execute_code 沙盒中含 emoji 的 Python 可能被拦截，用 write_file 写脚本再 terminal 执行
- **Python heredoc 中文编码(2026-08-31 毛豆实战新增)**：cron 环境下 `python3 -c "中文"` 或 `python3 << 'PYEOF' ...中文... EOF` 触发 `SyntaxError: Non-UTF-8 code starting with '\xe8'`，**解决：write_file 写 `.py` + 文件头部加 `# -*- coding: utf-8 -*-` + 用 `/usr/bin/python3 /tmp/script.py` 跑**。即使是纯 ASCII 脚本也建议加 coding 声明(参见 references/***SECRET***.md §6)
- **curl + Bearer token**：含 `lfk_` 前缀的 token 在 bash heredoc 中可能被剥掉，**写 token 到临时文件再用 `$(cat /tmp/token.txt)` 引用**（重要：见 references/curl-bearer-token-trick.md）
- **Kanban P0 任务交付标准 SOP**：见 references/kanban-task-delivery-sop.md（7 步流程 + 关键路径 + Pitfall + Evolution 报告 8 章节模板），适用于任何 agent 领取的 P0/P1 任务交付
- **R 轮产品化收口 deliverable 模板**：见 references/***SECRET***.md（12 章节结构 + SKU 收敛原则 + 双轨 3 层归档 + Kanban 闭环 SOP），适用于任何 agent 在多 agent 子任务中担任"末棒产品化"角色

## 7. 产出文件管理

| 类型 | 路径 | 频率 |
|---|---|---|
| Evolution 报告 | `~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md` | 每 cron 1 个 |
| LookForge 代码改动 | `/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace/` | 按推进点 |
| Skills 更新 | `~/.hermes/profiles/maodou/skills/<skill>/SKILL.md` 或 references/ | 按发现 |

**严禁**：把 evolution 报告写到 AGENTS.md 或 SOUL.md。

## 8. W4 月底决策矩阵标准模板（2026-08-31 02:33 毛豆实战新增）

### 8.1 何时用

当 cron 触发日期落入**月度最后一周**（约每月 25 日到月末，俗称 W4 节点），且本周期无真实可执行任务时，**强制进入"W4 月底决策矩阵模式"**，不做代码改动也不做调研，只做**信息收敛 + 决策铺垫**——把本月所有悬而未决的主线 + 副线收口成"等华哥下月 W1 决策"清单。

**触发条件**：
- cron 触发日期 ≥ 当月 25 日
- kanban + tasks.db 双源均无真任务
- 主营业务处于"等待外部输入"状态（如等华哥决策 / 玉芬协调 / Claude Code 协助）

### 8.2 决策矩阵结构（4 主线 + 3 副线 + 三色卡）

```
§1 待处理任务盘点（继承 §1 Step 1/2 结果）
§2 决策矩阵核心：4 主线 + 3 副线 + 三色卡
  ├─ 主营 4 主线（🔴 必保 / 🟡 重要 / 🟢 锦上添花）
  └─ 副业 3 副线（A 立即启动 / B 暂缓 / C 砍掉）
§3 决策矩阵推荐（不抢跑，仅供华哥参考）
§4 9 月 W1 行动建议（触发清单）
§5 文档诚实 + 数据验证（SQL 验证命令）
§6 产出文件清单（仅 evolution 报告，无其他产物）
§7 本轮结论（一句话）
```

### 8.3 三色卡判定标准（强制使用）

| 颜色 | 含义 | 决策需求 | 行动 |
|---|---|---|---|
| 🔴 P0 | 阻塞主营 / 护城河窗口期 | **立即决策** | 9 月 W1 必须启动 |
| 🟡 P1 | 重要但非阻塞 | 本月排期 | 9 月内分批推进 |
| 🟢 P2 | 锦上添花 | 下季度规划 | 视资源决定 |

**副业三色卡**(A/B/C)：
- 🟢 **A 立即启动** — 启动成本 ≤ 1 心跳闭环 + 与主营协同度高 + 客户验证度中等
- 🟡 **B 暂缓** — 需主营业务先落地 + 启动成本 5-10 人天 + 协同度高
- 🔴 **C 砍掉** — 独立低协同 + 高风险 + 与主营完全无交集

### 8.4 实测案例（2026-08-31 02:33 毛豆 W4 决策矩阵）

**主营 4 主线**：
| # | 主线 | 状态 | 决策 | 色 |
|---|---|---|---|---|
| M1 | LookForge v3 alpha OpenFOAM 集成 | demo 已规划（08-30 22:00） | 是否启动 9 月容器化攻坚？ | 🔴 P0 |
| M2 | HW-001~009 目录标准化 | 7 环节文档框架就绪 | 是否启动批量 Phase 3 仿真用例库？ | 🟡 P1 |
| M3 | 量化策略订阅产品（宽博士 R3） | 8/30 收口完成 | 是否进入冷启动？ | 🟡 P1 |
| M4 | UI 设计铁律 v1.4（8/29 批准） | 6 项验收清单已写入 skill | 是否作为 9 月前端强制卡门？ | 🟢 P2 |

**副业 3 副线**：
| # | 副线 | 投入 | 启动条件 | 月收入 | 协同度 | 决策推荐 |
|---|---|---|---|---|---|---|
| S1 | AI Logo/品牌设计服务 | 0.5 心跳 | LookForge 主线稳定 ≥ 1 周 | ¥5K | ⭐⭐⭐ | 🟢 A 立即启动 |
| S2 | AI 数据仪表板 SaaS | 5-10 人天 | 因子库稳定 ≥ 1 个 | ¥10K | ⭐⭐⭐⭐⭐ | 🟡 B 暂缓 |
| S3 | AI 装修/室内设计预览 | 3-5 人天 | ComfyUI stable | ¥3K | ⭐ | 🔴 C 砍掉 |

### 8.5 关键纪律

1. **不抢跑**：决策矩阵只是"信息收敛 + 决策铺垫"，**不替代华哥决策**。所有标 🟢A 的副线，需等华哥在 9 月 W1 明确批准后才启动
2. **不重复造轮子**：W4 决策矩阵不重复产出现有 evolution 报告已写的内容,只做"跨周汇总 + 决策建议"
3. **不超 12KB**：W4 决策矩阵报告尺寸 ≤ 12KB,比日常 evolution 报告略大,但不超过 15KB 上限
4. **9 月 W1 行动建议必须含触发条件 + 责任人 + 关键路径**：决策铺垫的目的是让华哥下月 W1 看完后能直接拍板

### 8.6 反模式

- ❌ **W4 决策矩阵当成启动副业的依据** — 决策矩阵≠ 行动授权,等华哥拍板
- ❌ **副线一刀切全砍或全留** — 3 副线综合 6 维度（启动成本/月收入/协同度/验证度/风险度/主营稳定度）后差异化推荐
- ❌ **决策矩阵不含三色卡色标** — 色标是决策可读性的关键,缺少就退化成普通表格
- ❌ **W4 决策矩阵产出于非月末 cron 触发** — 仅月末触发,避免占用日常 cron 节奏

## 9. 与 ***SECRET*** 的边界

- **本 skill (maodou-cron-heartbeat)**:承载 cron 工作流 + heartbeat 处理 + evolution 报告模板
- *****SECRET*****:承载 5 步骤 SOP + P0 闭环 + 双阶段 verify + 任务池 schema 漂移修正
- **两 skill 共同覆盖毛豆 cron 自进化全流程,各自独立维护**

**重叠点**（已知,不强制去重）：
- heartbeat 三源（kanban/desktop/hermes）判定 SOP 在两 skill 都有（§3 vs §15-16），由 cron 触发时任一加载即可
- 挂起任务识别在两 skill 都有（§3.1 vs §9），本 skill §3.1 简化版（看 description 含挂起标记即跳过）,self-evolution §9 是详版（三步识别法）

**下次更新触发**：
- ① 当 §3 长期修复最终落地（老莫/玉芬改 `heartbeat_check.py`）→ §3 末尾标注"已修复"+ 移除 §3.1
- ② 当 W4 决策矩阵跑满 3 个月（9 月/10 月/11 月）→ §8 追加"季度汇总"模式,提炼跨月趋势
- ③ 当副业决策出现反复（如 S1 标 🟢A 但实际延迟到 Q4）→ §8.5 追加"启动延迟预警"纪律
- ④ 当三色卡判定标准被华哥挑战或扩展 → §8.3 升级为 4 色或加入新维度