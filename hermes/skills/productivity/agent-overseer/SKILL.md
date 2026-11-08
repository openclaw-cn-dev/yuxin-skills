---
name: agent-overseer
description: 渔芯团队Agent监督者 — 检测空闲Agent并自动分配任务。当发现任何Agent超过30分钟无活跃，立即从任务池匹配分配，任务池空时主动创建对公司有益的任务。关键：workspace目录用拼音（workspace-heibdou），MEMORY路径必须精确。
triggers:
  - Agent空闲
  - 任务分配
  - 团队监督
  - idle detection
  - team monitoring
---

# 玉芬（Hermes）核心职责

1. **团队管理**：所有agent的记忆/技能更新/技能调用/自我进化机制
2. **任务调度**：分配任务并追踪进度
3. **技术方案**：组织相关agent对项目进行分析、评估、设计并给出最优技术方案
4. **知识库**：公司各部门专业知识库的建立与维护
5. **协作机制**：公司各agent团队协作机制的开发、维护与更新
6. **每日汇报**：作为专业公司管理人员，对公司整体发展负责。每天定时向华哥汇报各部门日常安排与进展。临时任务在大群追踪，按原方式进行。

---

## ⚠️ 重要发现（2026-06-11 → 2026-06-27 验证）：巡视procedure修订

**环境实际状态（2026-06-27 验证）**：
- `~/.hermes/kanban.db` 是真实任务库（**注意**：`团队协作/tasks.db` ≠ `~/.hermes/tasks.db` ≠ `kanban.db`，三者并存且各管一摊）
- 各 profile 下有独立 `kanban.db`（如 `~/.hermes/profiles/maodou/kanban.db`）— 谨慎确认查询的是哪一个
- `tasks` 表 schema 列名是 `assignee` / `status` / `started_at` / `created_at`（INTEGER 时间戳），**不是** `updated_at` / `description` / `agent`

**简化后的巡视步骤**（2026-06-27 强化版）：
```bash
# 1. 查任务池（主任务库）
sqlite3 ~/.hermes/kanban.db \
  "SELECT id, title, assignee, status, priority, started_at, worker_pid, consecutive_failures
   FROM tasks WHERE status IN ('pending','in_progress') ORDER BY priority DESC, started_at"

# 2. 查心跳cron实际执行结果（不要信 jobs.json 的 last_status！）
#    关键：读取每个 profile 最新 .md 文件的 FAILED 头标记
for p in maodou laomo afu heidou xiaobao; do
  latest=$(ls -t ~/.hermes/profiles/$p/cron/output/*/*.md 2>/dev/null | head -1)
  [ -n "$latest" ] && head -2 "$latest" | grep -oE "(FAILED|SUCCESS|COMPLETED)" | head -1 \
    | xargs -I {} echo "$p: {} $(basename $latest)"
done

# 3. 查 jobs.json 元数据（辅助参考，但**不能作为成功标志**）
python3 -c "
import json
d=json.load(open('$HOME/.hermes/cron/jobs.json'))
for j in d['jobs']:
  if '心跳' in j['name'] or '巡视' in j['name']:
    print(f\"{j['name']:30s} | last={str(j.get('last_run_at',''))[:19]} | st={j.get('last_status','')} | err={(j.get('last_error','') or '')[:60]}\")"
```

**报告生成规则**：
- 有任务进行中：列出每人任务数
- 无任务 + cron .md 全 SUCCESS/正常：标注"全员待机"
- **⚠️ cron .md 出现 FAILED 头** → 心跳异常（即使 `jobs.json` 写 `ok`）
- **⚠️ 连续多次 FAILED 且错误含 `402` / `insufficient_balance`** → LLM Provider 余额耗尽，**全团队级故障**，应立即汇报华哥

## ⚠️ 2026-06-27 关键发现：jobs.json last_status 不可信

**症状**：`jobs.json` 中 `last_status="ok"`，但 `cron/output/{jobid}/2026-06-27_12-00-24.md` 文件头明确写 `# Cron Job: ... (FAILED)`，且 `## Error` 段有 `RuntimeError: Error code: 402 - {'type': 'error', 'error': {'type': 'insufficient_balance_error'}}`。

**根因**：Hermes cron 调度器把"调度本身成功"（脚本被启动并退出）当作 `last_status=ok`，但 LLM 调用失败写在输出文件里。两者口径不同。

**正确做法（必须用）**：
1. 读 `cron/output/{jobid}/*.md` 的前 2 行 → 找 `FAILED` 字样
2. 读文件 `## Error` 段 → 找 `RuntimeError: Error code: 402` / `insufficient_balance`
3. **不要**只看 `jobs.json.last_status`

**402 余额耗尽时全团队表现**：
- 5个Agent心跳全部 FAILED
- 玉芬-主动巡视汇报自身也 FAILED
- 但所有 cron 仍按 schedule 触发（脚本启动没崩），只是 LLM 推理失败
- 解决：充值 / 切换 Provider / 等待额度恢复

**教训**：用 `jobs.json` 做健康检查 = 假阳性。每次巡视必须实际读 .md 文件头验证。

---

## 活跃判断逻辑（重要更正 2026-05-12）

**⚠️ 不要用MEMORY.md判断活跃**，各Agent更新频率不一致（小宝勤更新，黑豆/阿福不常更新）。**正确方式（按优先级）**：

### 方式1：查cron输出文件（最快，最可靠）
```python
import os, re
from datetime import datetime

cron_output_dir = os.path.expanduser("~/.hermes/cron/output")

def get_agent_last_activity(agent_name: str) -> str:
    """从cron输出文件获取Agent最后活跃时间"""
    marker_map = {
        "毛豆": "毛豆·每小时汇报",
        "老莫": "老莫·心跳",
        "黑豆": "黑豆·心跳",
        "小宝": "小宝·心跳",
        "阿福": "阿福·心跳",
    }
    marker = marker_map.get(agent_name, f"{agent_name}·心跳")
    for fname in sorted(os.listdir(cron_output_dir), reverse=True):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(cron_output_dir, fname)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        with open(fpath) as f:
            content = f.read()
        if marker in content:
            return mtime.strftime("%Y-%m-%d %H:%M")
    return "未知"
```

### 方式2：扫描workspace目录（有中文目录时才用）
```python
import os
from datetime import datetime, timedelta

def is_agent_idle(agent_name: str, idle_threshold_minutes=30) -> bool:
    """检查Agent是否空闲——以workspace文件修改时间为准，不看MEMORY.md"""
    workspace_map = {
        "毛豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace",
        "老莫": "/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维/workspace",
        "黑豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/黑豆-行政财务法务/workspace",
        "小宝": "/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营/workspace",
        "阿福": "/Users/hua/Desktop/渔芯科技/4-部门空间/阿福-客服/workspace",
    }
    path = workspace_map.get(agent_name)
    if not path or not os.path.exists(path):
        return True  # 目录不存在视为空闲

    latest = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(('.md', '.json', '.txt', '.py', '.yaml')):
                latest = max(latest, os.path.getmtime(os.path.join(root, f)))

    if latest == 0:
        return True  # 没有任何文件视为空闲

    diff_minutes = (datetime.now().timestamp() - latest) / 60
    return diff_minutes > idle_threshold_minutes
```

### ⚠️ 重要（2026-06-27 验证）：workspace 扫描方法的可靠性问题

**症状**：在 2026-06-27 巡视中发现，`/Users/hua/Desktop/渔芯科技/4-部门空间/{毛豆,老莫,小宝,黑豆,阿福}/` 目录下 `*.md` 24小时内全部为 0 个结果，但 kanban.db 显示毛豆有 `in_progress` 任务，sessions/ 24h 内有 6-13 个 dump。

**根因**：Agent 的实际"活跃"产出写入到 `~/.hermes/profiles/{agent}/sessions/` 和 `cron/output/`，**不会**回到中文 `4-部门空间/{Agent}/workspace/`。后者目录可能存在但内容长期空。

**修正后的活跃判断优先级（2026-06-27 强化）**：

1. **首选**：`~/.hermes/profiles/{agent}/sessions/` 内 `request_dump_*.json` 文件 24h 数量
   - `>0` → Agent 实际有 LLM 活动（包括心跳 cron 的 dump）
   - `=0` → Agent 24h 内零活动
2. **次选**：`~/.hermes/profiles/{agent}/cron/output/{jobid}/*.md` 最新文件时间和 FAILED 头
3. **再次**：`kanban.db` 中该 Agent 的 `in_progress` 任务数（有任务但 sessions=0 → 任务卡住，Agent 没在执行）
4. **最不可靠**：`4-部门空间/{Agent}/workspace/*.md`（**已多次验证为空或长期不更新**）

**正确命令**：
```bash
for p in maodou laomo afu heidou xiaobao; do
  n_sess=$(find ~/.hermes/profiles/$p/sessions -name "request_dump_*.json" -mtime -1 2>/dev/null | wc -l)
  latest_md=$(ls -t ~/.hermes/profiles/$p/cron/output/*/*.md 2>/dev/null | head -1)
  status=$(head -2 "$latest_md" 2>/dev/null | grep -oE "FAILED" | head -1)
  echo "$p: 24h_sessions=$n_sess cron_latest=${status:-OK} $latest_md"
done
```

**⚠️ 重要（2026-05-12）`~/Agents/` 和中文部门目录可能不存在。验证方法**：
```bash
ls ~/Agents 2>/dev/null || echo "不存在"
ls "/Users/hua/Desktop/渔芯科技/4-部门空间/" 2>/dev/null || echo "不存在"
```
如果都不存在，**只用方式1（cron输出）判断活跃**，不要依赖workspace扫描。

**各Agent真实活跃状态（2026-05-12验证）：**
| Agent | 最近活跃 | 距今 |
|-------|---------|------|
| 毛豆 | last_report_content.txt（毛豆·每小时汇报）| ~4小时（04:03）|
| 老莫 | 无最近报告 | ~2天 |
| 小宝 | 无最近报告 | ~1天 |
| 黑豆 | 无最近报告 | ~1天 |
| 阿福 | 无最近报告 | ~数小时 |

## Agent监督者 — 渔芯团队任务分配机制

## 概述

Hermes作为团队监督者，持续监控5个Agent的活跃状态：\
- 毛豆（产品）、老莫（知识库）、小宝（销售）、黑豆（行政法务）、阿福（客服）

## 核心文件

- **脚本**：`/Users/hua/Desktop/渔芯科技/团队协作/agent_overseer.py`
- **Cron**：~~每15分钟自动执行（job_id: `2fb38f7262a9`）~~ ⚠️ 此cron已于2026-05-06移除（华哥决定各Agent心跳发总经理群，不再发私聊）
- **任务队列**：`~/.hermes/kanban.db`（**不是** `tasks.db`，后者是0字节空文件）
- **飞书汇报脚本**：`references/send_feishu_report.py`（读取config.yaml凭证，发送到总经理群）
- **汇报目标群**：`328306697`（总经理群/元宝派，从yuanbao skill确认）

## 关键教训

**workspace/MEMORY路径（统一在4-部门空间下）**：
- 所有Agent的workspace/memory/skills统一在 `/Users/hua/Desktop/渔芯科技/4-部门空间/{部门目录}/` 下
- 路径精确映射（已验证）：
  - 毛豆：`/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/`
  - 老莫：`/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维/`
  - 黑豆：`/Users/hua/Desktop/渔芯科技/4-部门空间/黑豆-行政财务法务/`
  - 小宝：`/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营/`
  - 阿福：`/Users/hua/Desktop/渔芯科技/4-部门空间/阿福-客服/`

## 空闲检测逻辑

1. 读取每个Agent的 `MEMORY.md` 最后修改时间
2. 超过30分钟无更新 → 判定为空闲
3. 匹配 `AGENT_DOMAINS` 关键词，从pending任务池分配
4. 任务池空 → 主动创建对公司有益的任务

## 团队任务分发放原则（2026-05-08 更新 — 动态策略）

### 华哥战略：资源灵活调配，随公司阶段切换

| 阶段 | 核心重点 | 人员策略 |
|------|---------|---------|
| **产品开发期（当前）** | ✅ 全员支援产品开发 | 毛豆核心开发 + 其余4人各自用专业能力支援毛豆 |
| **产品上线后** | 销售+运营 | 届时重新分配 |

### 当前策略（产品开发期）

| Agent | 定位 | 支援方向 |
|-------|------|---------|
| **毛豆** | 核心产品开发 | LookForge线上仿真、HW系列量产、硬件机制标准化 |
| **老莫** | 技术资料支援 | 整理产品技术文档、知识库沉淀、竞品技术分析 |
| **小宝** | 市场调研支援 | 设备商/养殖户需求调研、产品推广素材准备 |
| **黑豆** | 合规合同支援 | 起草产品合同模板、知识产权保护方案、行业合规 |
| **阿福** | 测试验收支援 | 产品测试用例、验收标准、用户手册编写 |

### 玉芬管理机制（资深管理人员）

**5条核心职责：**
1. **主动巡视**：每4小时定时cron（job_id: 3f109abd481b）检查全员状态并汇报华哥
2. **灵活调度**：根据公司阶段切换任务分配策略，不等指令
3. **掌握资源**：持续监控各Agent的workspace最新活跃文件（不是MEMORY.md）
4. **优化沟通**：各Agent心跳保持极简（~200字prompt），不占上下文
5. **动态调整**：发现Agent空闲/任务重复/汇报异常，立即处理

### ⚠️ 任务分配平衡性检查（2026-05-08 新增教训）

**问题现象**：手动发放任务时，容易把多个任务全部分配给同一Agent，或让某人承担与其本职不符的任务。

**典型错误**：毛豆拿3个任务，其余每人仅1个；小宝被安排纯测试任务而忽略本职（销售+自媒体）。

**分配后必做检查**：
```
1. 每人任务数是否均衡（毛豆硬件任务可偏多，其余每人2个左右）
2. 每人任务是否在各自本职基础上叠加软件测试职责
3. 小宝 = 1个测试任务 + 1个销售/运营任务（本职优先）
4. 黑豆 = 1个合规审查 + 1个行政法务任务（本职优先）
5. 老莫/阿福 = 各2个技术/功能测试任务
```

**正确分配示例（11个任务）**：
| Agent | 任务数 | 任务类型 |
|-------|--------|---------|
| 毛豆 | 3个 | 硬件（符合本职） |
| 老莫 | 2个 | 软件技术测试 |
| 小宝 | 2个 | 1测试 + 1销售运营 |
| 阿福 | 2个 | 软件功能测试 |
| 黑豆 | 2个 | 1合规审查 + 1行政法务 |

### ⚠️ 监控团队状态时必须同步检查Cron状态

**发现（2026-05-08）**：5个团队Agent的心跳cron（`ac9bae/260b7b/066886/9071b1/262419`）在上午10:46-11:45间全部被暂停，但tasks.db显示无任务进行中。

**根因**：未同步检查cron状态，只查了任务池。导致误判"团队在正常运转"。

**检查清单（每次汇报前必查）**：
```bash
# 必须同时检查两项：
1. cron list | grep -E "毛豆|老莫|小宝|黑豆|阿福"  # 确认 state=scheduled，非 paused
2. sqlite3 ~/.hermes/kanban.db "SELECT assignee, status, title FROM tasks WHERE status IN ('pending','in_progress')"  # 确认任务在进行中
```

### ⚠️ 主动创建任务时的职责对齐规则

**错误做法**：仅按关键词匹配，不看Agent本职，导致任务分配失衡。

**正确做法**：分配前先查当前任务数，确保均衡；毛豆硬件任务数量可>2，其余Agent尽量均衡在1-2个；小宝优先分配销售/运营类，黑豆优先分配行政法务类。

```python
AGENT_DOMAINS = {
    "毛豆": ["LookForge", "产品", "硬件", "Phase", "Orchestrator", "SkillDispatcher", "ChromaDB", "仿真", "设备开发", "RAS"],
    "老莫": ["知识库", "调研", "研究", "文档", "测试", "基础设施", "Docker", "Knowledge", "软件", "审查", "优化报告"],
    "小宝": ["销售", "自媒体", "内容", "运营", "推广", "素材", "客户", "软件", "审查", "优化报告"],
    "黑豆": ["行政", "财务", "法务", "合规", "合同", "制度", "流程", "软件", "审查", "优化报告"],
    "阿福": ["测试", "客服", "验收", "演示", "功能", "回归", "软件", "审查", "优化报告"],
    "宽博士": ["量化", "投资", "回测", "框架", "Backtrader", "Zipline", "vnpy", "RQAlpha", "RiceQuant"],
    "学习助手": ["知识库", "整理", "笔记", "学习", "资料"],
}
```

## ⚠️ Bug 6（2026-05-05）：create_useful_tasks() 逻辑缺陷——pending≥3时跳过创建，但pending任务可能全属其他Agent

**问题**：本次执行发现，小宝和阿福均空闲（>30分钟无MEMORY更新），但pending池有4个任务（全属毛豆的Blueprint/硬件任务）。`pending < 3` 判断为 False，跳过创建，导致两个空闲Agent无任务分配。

**根因**：`create_useful_tasks()` 的触发条件是 `pending_count < 3`，但这个条件只说明任务**数量少**，不说明有任务**匹配空闲Agent的领域**。当pending全是非空闲Agent的任务时，即使只有1个pending也会跳过创建。

**修复后的正确逻辑**：
```python
db_path = os.path.expanduser("~/.hermes/kanban.db")
# 修复：同时检查 pending 数量 AND 是否所有pending任务都已匹配给非空闲Agent
idle_agents = [a for a in AGENT_DOMAINS if is_idle(a)]
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT title, assignee FROM tasks WHERE status IN ('pending', 'in_progress')")
pending = [{"title": r[0], "assignee": r[1]} for r in cursor.fetchall()]
conn.close()

# 判断是否需要创建：pending太少 或 没有任何pending任务匹配当前空闲Agent的领域
def has_matching_pending(idle_agent, pending_list):
    domains = AGENT_DOMAINS[idle_agent]
    return any(any(d in f"{t.get('title','')} {t.get('body','')}" for d in domains)
               for t in pending_list)

needs_creation = len(pending) < 3 or not any(has_matching_pending(a, pending) for a in idle_agents)
```

**教训**：判断"是否需要创建任务"不能只看pending数量，必须同时验证pending任务中是否有**匹配当前空闲Agent领域**的任务。正确问法是："pending中有没有这个Agent能接的任务？"而不是"pending够不够3个？"

---

## ⚠️ Bug 5（2026-05-05）：Dashboard AGENTS列表不完整导致显示重复

**问题**：Dashboard（:9118）上毛豆/老莫等5个Agent出现**两个重复卡片**，而宽博士和学习助手完全不显示。

**根因**：`agent_dashboard_server.py` 的 `AGENTS` 列表只有5个成员：
```python
AGENTS = ['毛豆', '老莫', '小宝', '黑豆', '阿福']  # 漏掉了宽博士、学习助手
```
解析逻辑先用这5个名字从 `--report` 输出中提取状态，再把5个都放进 `assigned_names`。由于宽博士和学习助手不在这份列表中，它们**从未被解析**，直接被当作"未分配"补进了列表。而Dashboard的重复卡片是因为解析逻辑在处理多任务时可能有去重问题。

**修复**：每次添加新Agent到团队时，**必须同步更新两处AGENTS列表**：
1. `agent_overseer.py` 的 `AGENTS`
2. `agent_dashboard_server.py` 的 `AGENTS` ← 经常被遗漏

**教训**：新增Agent → 搜 `AGENTS = [` 全局搜索所有.py文件，同步更新。

## ⚠️ 已知Bug：Deduplication失效导致任务爆炸

### 团队技能定时更新与提升

**技能扫描 Cron（技能系统自动维护）：**
- 全量扫描（每周三09:00）：`dfa9e16c0276`（`--full` 参数，扫描37个VoltAgent官方源 + awesome生态）
- 增量扫描（每天10:00）：`02b7b4944cc8`（每日10个priority repos）

**扫描脚本**：`~/.hermes/scripts/scan-agent-skills.py`

**当前已安装技能数**：95个（2026-05-04扫描后）

**玉芬对老莫报告的响应流程**：详见 `references/hermes-skill-lifecycle.md`

### 已知Bug（持续跟踪）

#### Bug 1（2026-05-01）：create_useful_tasks() 无标题去重

**问题**：`create_useful_tasks()` 被cron每15分钟调用时，每次都重复创建同名任务（官网检查被创建了54次）。

**根因**：`create_useful_tasks()` 没有检查任务是否已存在于数据库中，`pending < 3` 的判断只看任务数量，不看任务标题是否重复。

**修复**：在 `create_useful_tasks()` 中添加 `existing_titles` 去重集合：
```python
db_path = os.path.expanduser("~/.hermes/kanban.db")
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT title FROM tasks")
existing_titles = {row[0] for row in cursor.fetchall()}
conn.close()

# 创建任务前检查
if title not in existing_titles:
    conn.execute(insert_sql, ...)
```

**教训**：任务池子判断要用"标题去重"而非"数量判断"——`pending < 3` 永远只说明pending任务少，不说明同类任务已存在。

### Bug 2（2026-05-04）：claim_task() 重置状态导致重复分配

**问题**：运行 overseer 后，任务池出现大量重复任务（同一标题出现2-4条 in_progress 记录）。

**根因**：`task_queue.py` 的 `claim_task()` 方法（第80行）：
```python
conn.execute(
    "UPDATE tasks SET assignee=?, status='pending', updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
    (actor, task_id)
)
```
此方法将任务重置为 `pending`。而 `overseer_tick()` 的分配逻辑是：
1. 为空闲Agent从 pending 池匹配任务
2. `claim_task()` → 任务变 `pending`
3. `start_task()` → 任务变 `in_progress`

如果 overseer 在任务仍为 `in_progress` 时再次运行，它会从 pending 池找到该任务（被之前的 `claim_task` 重置过），再次 `claim + start`，生成一条**新的 task_id 的重复任务**。

**验证**：DB中同一标题出现多条 in_progress：`task_overseer_0504123032_xxx` 和 `task_overseer_0504124511_xxx` 和 `task_overseer_0504124755_xxx`。

**临时修复**：每次运行 overseer 前，先检查该任务是否已 in_progress（用 title + assignee 唯一性判断），或修改 `claim_task()` 不重置状态：

```python
# 用 title+assignee 唯一性判断
db_path = os.path.expanduser("~/.hermes/kanban.db")
conn = sqlite3.connect(db_path)
cur = conn.execute(
    "SELECT task_id FROM tasks WHERE title=? AND assignee=? AND status='in_progress'",
    (title, assignee)
)
existing = cur.fetchone()
conn.close()
if existing:
    return  # 已存在 in_progress，跳过
```

**核心教训**：`claim_task()` 语义是"领取任务"，不应该把 `in_progress` 任务重置回 `pending`。正确的领取逻辑应该保持原状态，只更新 assignee。

### Bug 8（2026-05-05）：overseer_tick() 创建后分配逻辑只给一个人——其他空闲Agent无任务

**问题**：执行 `overseer_tick()` 时，4个Agent（毛豆/老莫/黑豆/阿福）空闲，`create_useful_tasks()` 创建了4个任务，但只分配了1个（小宝←官网检查），其余3个空闲Agent无任务可做。

**根因**：分配逻辑用嵌套循环遍历**任务标题**匹配Agent领域，而不是遍历**空闲Agent**匹配任务：
```python
# 旧逻辑（错误）：按任务标题找Agent，5个任务全部匹配到第一个Agent
for ct_title in created:
    for a, domains in AGENT_DOMAINS.items():   # 遍历所有Agent
        if any(d in ct_title for d in domains):
            for task in q.get_pending_tasks():
                if task["title"] == ct_title:
                    q.claim_task(task["task_id"], a)   # 只分配给第一个匹配到的Agent
```

**修复后的正确逻辑（从空闲Agent出发找任务）**：
```python
db_path = os.path.expanduser("~/.hermes/kanban.db")
conn = sqlite3.connect(db_path)
cur = conn.execute(
    "SELECT task_id, title, body, assignee FROM tasks WHERE status IN ('pending','in_progress')"
)
all_tasks = [{"task_id": r[0], "title": r[1], "body": r[2] or "", "assignee": r[3]}
             for r in cur.fetchall()]
conn.close()

for agent, domains in AGENT_DOMAINS.items():
    # 该Agent已有任务在执行，跳过
    if any(t["assignee"] == agent for t in all_tasks if t["assignee"]):
        continue
    # 从pending中找该Agent领域匹配的任务
    for task in all_tasks:
        if task["assignee"] is not None:  # 已有归属
            continue
        combined = f"{task.get('title','')} {task.get('body','')}"
        if any(d in combined for d in domains):
            conn = sqlite3.connect(db_path)
            conn.execute("UPDATE tasks SET assignee=?, status='in_progress' WHERE task_id=?",
                         (agent, task["task_id"]))
            conn.commit()
            conn.close()
            assigned_count += 1
            break
```

**教训**：分配逻辑应该**从空闲Agent出发**找任务，而不是从任务出发找Agent。正确的分配模式是：`for each idle_agent: find matching pending task`（主动者模式），而不是 `for each task: find matching agent`（被动者模式）。

---

### Bug 9（2026-05-05，已废弃）：归档去重导致已废弃任务永远无法重建

⚠️ **此Bug描述已废弃**。实际情况见 Bug 7。归档去重**不是导致废弃任务无法重建的原因**，真正原因是 `create_useful_tasks()` 的去重逻辑**根本没有生效**。建议忽略本条描述，直接按 Bug 7 的修复方案处理。

---

### Bug 7（2026-05-05→06）：归档去重实际未生效——重复任务仍在创建

**问题（2026-05-06 验证）**：tasks.db 显示"鱼乐宝用户手册V1.0"任务已累计创建 **30+次**，横跨毛豆和阿福。overseer 每15分钟仍在重复创建同一标题的任务。

**根因**：`create_useful_tasks()` 的去重逻辑实际**未生效**。skill 文档描述的修复（"创建前去重：pending + in_progress + 30天archive"）在实际代码中并未实现，或实现有遗漏。

**当前实际状态**：同一任务被重复创建于：
- `task_overseer_0506050050_毛豆`（2026-05-06 05:00）
- `task_overseer_0506043108_毛豆`（2026-05-06 04:43）
- `task_overseer_0506033024_毛豆`（2026-05-06 03:40）
- ……（反复创建，累積30+次）

**紧急临时修复（各Agent侧）**：完成重复任务后，立即用 `execute_code` 直写归档 JSON，防止 overseer 下一轮继续分配：
```python
# execute_code 内执行，不走 subprocess（中文参数会触发安全扫描）
import sqlite3, hashlib, json, os
from datetime import datetime

task_id = "task_overseer_0506050050_毛豆"
hash_suffix = hashlib.md5(f"{task_id}鱼乐宝用户手册V1.0{datetime.now().isoformat()}".encode()).hexdigest()[:12]
archive_dir = "/Users/hua/Desktop/渔芯科技/团队协作/task_archive/"
os.makedirs(archive_dir, exist_ok=True)
with open(os.path.join(archive_dir, f"{task_id}_{hash_suffix}.json"), 'w', encoding='utf-8') as f:
    json.dump({"task_id": task_id, "title": "鱼乐宝用户手册V1.0",
               "result": "文件已存在，直接复用", "actor": "毛豆",
               "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False)
```

**真正修复（需修改 agent_overseer.py）**：`create_useful_tasks()` 必须在创建前真正执行：
```python
# 读取30天归档中的所有标题
archive_titles = set()
for fname in os.listdir(archive_dir):
    if fname.endswith('.json'):
        with open(os.path.join(archive_dir, fname)) as f:
            archive_titles.add(json.load(f)['title'])

# 创建前过滤
for t in task_templates:
    if t["title"] in archive_titles:
        continue  # 跳过已归档任务
    # 只有不在归档中才创建
```

**教训**：skill 文档写"已实施"不等于代码已实施。需对照代码验证，或在下次 session 发现重复任务时立即确认去重逻辑是否生效。

### Bug 3（2026-05-04）：create_task() 批量创建同名任务时只产生一条

**问题**：在 for 循环中连续调用 `q.create_task(title=..., assignee='毛豆')` 创建7个子任务，结果只创建出1条，其余被去重吞掉。

**根因**：`TaskQueue.create_task()` 内部用 `datetime.now().strftime('%y%m%d%H%M%S')` 生成 task_id（精确到秒）。同秒内多次调用产生相同 task_id，触发 UNIQUE 约束后只插入第一条。

**复现**：循环创建3个以上同名任务，每轮只产生1条，其余静默失败。

**正确做法**：直接用 SQL INSERT，手动生成唯一 task_id：
```python
import sqlite3
from datetime import datetime
db_path = os.path.expanduser("~/.hermes/kanban.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()
task_id = f"task_hw_{datetime.now().strftime('%m%d%H%M%S')}_{i}"  # 加序号保证唯一
c.execute("""INSERT INTO tasks
    (task_id, title, body, assignee, priority, status, created_at)
    VALUES (?, ?, ?, ?, ?, 'pending', ?)
""", (task_id, title, body, assignee, priority,
      int(datetime.now().timestamp())))
conn.commit()
conn.close()
```

**教训**：需要批量创建多个独立任务时，不依赖 `create_task()` 的内部 ID 生成逻辑，而是自己用 SQL + 唯一task_id（加时间戳+序号）写入。**表字段**：`created_at` 是 INTEGER（Unix时间戳），`started_at` 同。

### Bug 4（2026-05-04）：--report 输出格式变化导致解析逻辑失效

**问题**：`agent_overseer.py --report` 的输出格式已更新，新增"已分配任务"字段。旧解析逻辑只识别"有任务进行中：X→Y"，无法识别已分配但未开始的任务。

**当前输出格式（2026-05-04）**：
```
【团队监督】2026-05-04 21:46

空闲Agent（无任务）：黑豆（58分钟）

有任务进行中：无

当前待处理任务：0个
已分配任务：
  • 小宝 <- 【运营】渔芯科技官网现状检查与改进建议
  • 老莫 <- 【知识库】竞品分析报告：国内RAS循环水设备厂商对比
  • 毛豆 <- 【产品】鱼乐宝（SaaS）用户手册V1.0
  • 黑豆 <- 【行政】渔芯科技内部工作流SOP
```

**正确解析逻辑**：
1. `空闲Agent（无任务）：` → 空闲Agent列表（无任务且30分钟无活跃）
2. `有任务进行中：X→Y` → 真正在执行的任务
3. `已分配任务：` → 已分配但未开始的任务（assignee有任务title，但status不是in_progress）
4. `当前待处理任务：N个` → 未分配的pending任务数

**kanban.db查询（代替--report）**：
```bash
sqlite3 ~/.hermes/kanban.db \
  "SELECT assignee, status, title FROM tasks WHERE status IN ('pending','in_progress') ORDER BY assignee"
```

**教训**：解析 `--report` 输出时，必须同时处理"进行中"和"已分配"两种状态，否则会把已分配但未开始的任务误判为空闲。

## ⚠️ 关键教训（2026-05-06）：任务分配 ≠ 任务执行

**发现**：overseer 执行后，DB 显示5个任务全部 assigned，但 `get_in_progress_tasks()` 只返回4个（毛豆的 in_progress 为空）。

**根因**：overseer 通过 `claim_task()` + `start_task()` 把任务推入 `in_progress`，但这只是 DB 状态更新。如果毛豆的 cron 心跳没有在跑（或失败了），毛豆的 MEMORY 永远不会更新，任务永远不会真正被执行。

**两种"空闲"的区别**：
| 类型 | 判断标准 | 含义 |
|------|---------|------|
| DB空闲 | MEMORY.md 30分钟无更新 | Agent 的 cron 心跳未触发 |
| 任务空闲 | DB 中该 Agent 无 in_progress 任务 | Agent 没有在执行任何任务 |

**overseer 的职责边界**：
- ✅ 负责：检测 DB 空闲 → 分配任务到 DB（claim + start）
- ❌ 不负责：唤醒 Agent 的 cron 心跳（那是各 Agent 自己的职责）

**实际调度链**：
```
overseer cron（每30分钟）
  → 检测 MEMORY.md 空闲
  → claim_task() + start_task() 写入 DB
  → 下次该 Agent cron 心跳触发时
      → 检测到自己有 in_progress 任务
      → 开始执行
      → 更新 MEMORY.md（空闲状态解除）
```

**如果毛豆持续30小时空闲** → 说明毛豆的 cron 心跳本身就没有在跑，需要检查：
```bash
hermes cron list | grep 毛豆
# 或检查毛豆 gateway 是否还在运行
```

**教训**：overseer 报告"已分配"不代表任务在被执行，最终验证必须等 MEMORY.md 有更新。

## 主动创建任务的正确触发条件

**实际验证（2026-05-06）**：`pending < 3` 时确实触发了创建，创建了5个任务并成功分配给4个 Agent。

**但有个边界情况**：如果 pending = 0，条件 `pending < 3` 为 True，会立即创建所有任务。但如果某个任务创建后立即被其他 Agent claim走了（还没来得及分配给当前空闲的 Agent），这个空闲 Agent 还是会漏掉。

**当前逻辑已足够**，触发条件 `pending < 3` 是合理的（ pending = 0/1/2 时都应该补充任务）。

## 自我进化机制（岗位 idle 时的隐藏任务）

### 核心设计原则
**不要新建独立cron**，而是把进化逻辑**嵌入每个Agent现有的任务领取cron**里。

原因：每个Agent已有 `*/15 * * * *` 的任务领取cron（每15分钟）。如果再建独立的进化cron，两个机制会冲突——任务cron每15分钟抢任务，进化cron每4小时才跑，根本没有空闲机会。

### 触发逻辑（嵌入到每个任务领取cron的prompt里）

在任务领取cron的 prompt 中，第一步不是领任务，而是先查 pending 数量：

```python
import sqlite3
conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
pending_count = c.fetchone()[0]
conn.close()
print(f"pending任务数: {pending_count}")
```

- **pending > 0**：正常领任务执行
- **pending == 0（空闲）**：立即触发自我进化，不等待

### 各Agent进化研究方向

| Agent | 进化方向 |
|-------|---------|
| 毛豆 | 竞品研究（LookForge/RAS设备商）、用户洞察、产品设计方法、水产数字化趋势、管理成长 |
| 老莫 | AI技术（Agents/Docker/DB）、知识库建设、新工具新skill、自动化运维、团队协作 |
| 黑豆 | 财税政策、农业优惠、合规风控、合同法务、行政管理、行业法规 |
| 小宝 | B2B销售策略、自媒体运营（抖音/小红书）、竞品分析、水产行业知识 |
| 阿福 | 客服话术、投诉处理、谈判说服心理学、异议处理、客户心理 |
| 宽博士 | 量化框架对比、因子研究、实盘通道、因子库、Portfolio优化 |
| 学习助手 | 知识管理方法论、个人效率工具、信息加工策略 |

### 进化输出格式

每次选1个方向深入研究，输出到该Agent的 `workspace/evolution_log.md`：

```markdown
## 进化记录 YYYY-MM-DD HH:MM

### 研究主题：[主题名称]

**核心发现：**
- 发现1
- 发现2

**具体行动计划：**
- 行动1
- 行动2
```

完成后在飞书渔芯大群（cli_a964873dd7b8dbda）发一条：【X豆进化】+ 简要结论（50字内）

### 进化成果 → 飞书知识库同步

- 脚本：`/Users/hua/Desktop/渔芯科技/团队协作/sync_evolution_to_wiki.py`
- 各Agent的 `WIKI_NODES` 字典需配置对应的飞书Wiki节点token
- UAT过期时无法写入Wiki，需先刷新凭证

### 关键教训：创建新cron前的 checklist

在新建任何 cron 之前，必须先执行 `cronjob list` 检查是否已有同类机制：
1. 该功能是否已有 cron 在跑？（例：已有任务领取cron，不要再建独立进化cron）
2. 新cron和现有cron会不会冲突或重复执行？
3. 更好的设计是把新逻辑**嵌入现有cron**，而不是另起炉灶

## ⚠️ 关键教训（2026-05-07）：心跳两层架构——极简心跳+按需加载技能

**背景**：之前每个心跳cron预加载2个完整skill，每次触发消耗大量token（每20分钟×5个Agent = 每小时15次×~650 tokens）。

**问题**：
```
旧设计：每20分钟 × 5个Agent × 每次加载完整skill
= 每小时15次心跳 × skill token成本（通常5-15K tokens）
```
大部分skill内容是静态的（角色定义、流程框架），只有任务数据是动态的。

**解决方案（2026-05-07实施）**：拆成两层：

| 层 | 内容 | 加载频率 |
|---|------|---------|
| **基础层** | 角色定义+职责 | 每个cron tick只加载一次（心跳prompt自带，不走skill） |
| **执行层** | 具体任务指令 | **只在有实际工作时才加载skill** |

**具体做法**：
1. **心跳prompt极度精简**（~200字）：只含角色定位、检查任务队列的逻辑
2. **发现任务后才加载完整skill**：去掉预加载 `skills=[]`，改为心跳内部按需 `skill_view` 调用
3. **无任务时静默退出**：回复「[X豆] 心跳 OK（无待处理任务）」，不发长报告

**当前心跳cron配置（2026-05-07）**：

| Agent | Job ID | Skills配置 |
|-------|--------|-----------|
| 毛豆 | `ac9bae2949bd` | `skills=[]`（按需加载maodou-workflow） |
| 老莫 | `260b7b982ab7` | `skills=[]`（按需加载laomo-workflow） |
| 小宝 | `066886014d67` | `skills=[]`（按需加载xiaobao-workflow） |
| 黑豆 | `9071b1bae756` | `skills=[]`（按需加载heidou-workflow） |
| 阿福 | `262419748f9b` | `skills=[]`（按需加载afu-workflow） |

**心跳prompt标准模板**：
```
你是[名字]（渔芯科技[职责]）。

## 每次心跳任务
检查任务队列：`sqlite3 .../tasks.db "SELECT ... WHERE assignee='[名字]' ..."`

**有任务** → 立即加载 `[name]-workflow` skill（skill_view），按完整工作流执行

**无任务** → 回复：「[名字] 心跳 OK（无待处理任务）」，静默退出
```

**Token节省估算**：
- 旧：5 Agent × 3次/小时 × ~650 tokens = ~9,750 tokens/小时
- 新：5 Agent × 3次/小时 × ~200 tokens = ~3,000 tokens/小时（节省~70%）
- 有任务时才额外加载完整skill，总量更低

**Overseer cron 已移除**：华哥决定不再需要玉芬的监督者cron（各Agent心跳发总经理群，私聊只保留玉芬和华哥的对话）。

---

## ⚠️ 关键教训（2026-05-05）：每个Agent必须有专属workflow skill，不能共用

**问题**：今天检查发现，5个Agent（毛豆/老莫/小宝/黑豆/阿福）全部共用 `xiaobao-workflow`，没有任何一个有自己的专属workflow skill。

**根因**：skill创建/复制时，只复制了xiaobao的workflow，其他Agent从未创建自己的。

**正确做法**：每个Agent在 `~/.hermes/profiles/{agent}/skills/` 下必须有：
- `{agent}-workflow/SKILL.md` —— 专属工作流，含idle自我提升逻辑
- `{agent}-技能名/SKILL.md` —— 专属核心技能

**已创建（2026-05-05）**：
| Agent | Workflow Skill | 核心技能 Skill |
|-------|---------------|---------------|
| 毛豆 | maodou-workflow | maodou-product |
| 老莫 | laomo-workflow | laomo-knowledge |
| 小宝 | xiaobao-workflow | xiaobao-sales |
| 黑豆 | heidou-workflow | heidou-admin |
| 阿福 | afu-workflow | afu-customer-service |
| 宽博士 | quant-workflow | quantitative-research |
| 整理师 | zhenglishi-workflow | research |

**教训**：创建新Agent时，workflow skill是必须配置的，不能用其他人的workflow代替。每个Agent是独立个体，有自己的职责域和工作节奏。

## ⚠️ 核心管理原则（2026-05-05 + 2026-06-26 更新）

华哥明确授权：**公司正常运营问题，技术/团队管理问题，发现后立即处理，不用等华哥来指令。**

这意味着：
1. **发现问题 → 直接修复**。不要先问"要不要修"，不要汇报问题等指示
2. **技术问题自己研究解决**。华哥说"技术上的问题就是你每天的工作任务"
3. **团队管理主动作为**。overseer发现空跑Agent → 立即建心跳cron；发现缺workflow → 立即补
4. **优化迭代随时进行**。 MEMORY/skills/workflow有问题，随时改，改完立即生效

**不需要请示的情况**：
- 技术问题（工具/框架/skill/架构）
- 团队管理优化（cron/skill/workflow分配）
- 知识库建设（自我提升、资料收集）
- 流程优化（任务分配/汇报机制）

**需要华哥决定的情况**：
- 战略方向（公司定位、业务优先级）
- 重大资源投入（预算、人员、项目立项）
- 对外合作（商务谈判、客户重大需求）

### 报告风格（2026-06-26 强化 — 华哥明确偏好）

**华哥原话**："大概告诉我一下原因就行了，把问题修复好就行了。"

执行含义：
1. **A/B 对比找根因 → 动手修 → 简短结论**，不要长篇分析占用户时间
2. **默认自主决策 + 拍板**：涉及 operational 问题不需要"3 个选项请你拍板"。直接选最稳的方案动手，**做完后简短汇报**（什么 + 结果 + 用户可能要 follow-up 的事）。
3. **请示必须"带上方案"**：真需要用户决策时（如资源切换、provider 选择），给 2-3 个**明确推荐**而不是平铺选项。

### 基于事实下结论（2026-06-26 强化 — 华哥纠正过）

**华哥质疑**："你终于来了" + "你以前判断错了"

执行含义：
1. **"感觉跑得顺" ≠ "配置对"**。每个结论必须带证据：pid、日志时间戳、字段值、命令输出
2. **"配置 OK" ≠ "能正常工作"**。`hermes status` 显示 Model+Provider 不代表能跑通，必须看 `gateway.log` 的 `response ready:` 行
3. **CLI/AIAgent 直调 ≠ gateway 路径**。用 CLI 测 provider 永远 404（base_url 走 `/anthropic` 端点 MiniMax 未开放），要测就发飞书消息端到端验证
4. **数字、字段、pid 出现在结论里** — 不要说"大约"、"可能"、"看起来"，给具体值

这条原则是所有团队管理决策的底层逻辑：**operational问题自主解决，strategic问题才请示**。

**教训**：创建新Agent时，workflow skill是必须配置的，不能用其他人的workflow代替。每个Agent是独立个体，有自己的职责域和工作节奏。

---

## ⚠️ 关键教训（2026-05-13）：按需唤醒模式替代心跳轮询

**问题**：5个Agent每小时心跳cron，绝大多数时间空跑（无任务），却每次都加载上下文+执行逻辑。计算：5 Agent × 每小时 × ~200 tokens = 每天~24,000 tokens 空烧，且严重占上下文。

**用户原话**：「以前好像就是用的这种方式沟通的，这种方式不是很浪费token跟上下文的吗？」

**结论**：心跳轮询是错误范式，应该用**按需唤醒**替代。

**新旧模式对比**：

| | ❌ 心跳轮询（旧） | ✅ 按需唤醒（新） |
|--|--|--|
| Agent行为 | 每小时自动触发，检查任务队列 | 不跑cron，完全被动等待 |
| Token消耗 | 5 Agent × 720次/天 × ~200 tokens | ≈0（纯Python watchdog） |
| 响应速度 | 即时 | 有任务时玉芬即时派发 |
| 实现复杂度 | 高（5个cron+skill加载） | 低（1个watchdog） |

**新架构（现行）**：

```
华哥/玉芬 写任务文件
    ↓
飞书云盘 任务派发/{Agent名}/
    ↓
watchdog（no_agent cron，每30分钟，纯API轮询 ≈0 token）
    ↓
检测到新文件 → 推送通知到汇报群
    ↓
玉芬收到通知，主动派发给对应Agent
    ↓
Agent执行 → 回传云盘 → 玉芬汇报华哥
```

**watchdog实现**：
- 脚本：`~/.hermes/scripts/task_watchdog.py`
- 创建：`cronjob create --no-agent --script task_watchdog.py --schedule "*/30 * * * *"`
- 检测方式：扫描 `Vb83fsimklzqKDdd0dHcc3g2nhd/任务派发/{Agent}/` 目录，对比 `task_watchdog.db` 中已跟踪文件，发现新文件则推送飞书群通知
- **无Agent介入**：cron 的 `no_agent=true`，纯执行Python脚本，不加载任何LLM上下文
- Token消耗：几乎为0（只有检测到新任务时才发送一条飞书文字消息）

**已暂停的cron（2026-05-13）**：
- 5个Agent心跳：`ac9bae`（毛豆）、`260b7b`（老莫）、`066886`（小宝）、`9071b1`（黑豆）、`262419`（阿福）
- 玉芬巡视：`3f109abd481b`
- 团队每小时汇报：`9a1cee1a301b`

**保留的cron**：
- watchdog：`1afa96340e1b`（每30分钟，no_agent）
- 每日早间简报：`51a621334eea`（8:00）
- 玉芬每日汇报：`92ab47de8cf4`（18:00）

**何时用按需唤醒**：团队成员相对稳定，不需要实时响应，任务以批次/天为单位。

---

## 团队Agent架构（2026-05-05 更新）

### 当前7个Agent团队

| Profile | 人设 | 职责 | 是否纳入玉芬监督cron |
|---------|------|------|---------|
| `maodou` | 产品经理 | LookForge/产品设计 | ✅ 纳入 |
| `laomo` | 知识库 | 资料收集/测试/Docker | ✅ 纳入 |
| `xiaobao` | 销售 | B2B销售/自媒体 | ✅ 纳入 |
| `heidou` | 行政法务 | 行政/财务/法务/合规 | ✅ 纳入 |
| `afu` | 客服 | 客服/测试 | ✅ 纳入 |
| `quant` | 宽博士 | 量化研究 | ❌ **不纳入**，只接华哥直接派的任务 |
| `zhenglishi` | 学习助手 | 个人知识库整理 | ❌ **不纳入**，只接华哥直接派的任务 |

**⚠️ 重要**：团队监督cron（`2fb38f7262a9`）**只调度毛豆/老莫/小宝/黑豆/阿福**，不调度宽博士和学习助手。这两个是华哥直接管理的Agent。

**启动命令**：
```bash
# Mac mini上的5个Agent
maodou gateway start
laomo gateway start
heidou gateway start
xiaobao gateway start
afu gateway start

# 宽博士和学习助手（各自独立Profile）
quant gateway start
zhenglishi gateway start
```

### ⚠️ 教训：Browser窗口是谁开的？排查方法

**问题现象**：Mac mini上出现了浏览器窗口（x-cursor/xhb等），用户以为是openclaw残留。

**排查步骤**：
```bash
# 1. 确认没有openclaw进程在跑
ps aux | grep -i "openclaw" | grep -v "grep\|\.bak\|\.openclaw_backups"
# 输出应为空

# 2. 搜索各Agent的session文件，找browser_navigate调用
grep -h "browser_navigate\|xhs\|xiaohongshu\|小红书" \
  /Users/hua/.hermes/profiles/*/sessions/*.json 2>/dev/null

# 3. 查各Agent最近session的修改时间
ls -lt /Users/hua/.hermes/profiles/*/sessions/*.json | head -10
```

**结论**：所有自动开浏览器都是Hermes Agent的正常行为（browser工具），不是openclaw。openclaw已完全清除，无残留进程。

**如需禁止某Agent开浏览器**：修改其 `config.yaml` 中的tools配置，移除browser工具。

### Hermes Profiles vs OpenClaw

**当前架构**：所有Agent已迁移到 Hermes Profiles，完全隔离。每个profile有独立的 `config.yaml`、`.env`、`SOUL.md`、`memories/MEMORY.md`——完全隔离。

**OpenClaw已于2026-05-04完全清除**：
- 无launchd残留
- 无cron任务残留
- npm包已移除（仅保留.bak备份目录）
- 飞书插件配置已迁移到各Hermes Profile

每个profile有独立的 `config.yaml`、`.env`、`SOUL.md`、`memories/MEMORY.md`——完全隔离。

**飞书限制**：所有profile共用同一个Feishu Bot（`cli_a964873dd7b8dbda`），同一Bot同时只能在一个会话中活动。调度必须通过**飞书云盘**中转。

**启动命令**：
```bash
maodou gateway start   # 毛豆
laomo gateway start    # 老莫
xiaobao gateway start  # 小宝
heidou gateway start   # 黑豆
afu gateway start      # 阿福
```

详细操作见 `hermes-agent` skill 的 `references/multi-agent-team-setup.md`。

**任务派发新机制（2026-05-13）**：详见 `references/task-dispatch-workflow.md`。

**🚨 架构变更（华哥 2026-07-31 14:55+ 明确）**：本 skill 历史描述的"任务流转机制 = 飞书云盘 任务派发/{Agent名}/"是**反模式**。正确做法：

- **Agent 之间协作、玉芬对同事管理** = 全部在**本地协作框架** `~/.hermes/orchestration/` 中完成
- **飞书** = 仅做华哥↔玉芬的汇报与沟通渠道
- **任务池** = `~/.hermes/kanban.db`（**不新建**）
- **Agent 收件箱** = `~/.hermes/orchestration/messages/<agent>/inbox/`
- **Agent 发件箱** = `~/.hermes/orchestration/messages/<agent>/outbox/`
- **Agent 工作区** = `~/.hermes/orchestration/workspace/<agent>/`
- **共享状态** = `~/.hermes/orchestration/shared_state/`
- **事件流** = `~/.hermes/orchestration/events/events.jsonl`

完整本地框架设计：见 `multi-agent-team-architecture` skill 的 `references/local-orchestration-framework.md`。

## 重要：Workspace/Memory命名

**⚠️ 先验证再使用（2026-05-12）**：中文部门目录 `~/Desktop/渔芯科技/4-部门空间/` 可能不存在。**正确路径**统一在 `~/.hermes/profiles/{profile}/` 下：
- Config：`~/.hermes/profiles/{profile}/config.yaml`
- SOUL：`~/.hermes/profiles/{profile}/SOUL.md`
- Memory：`~/.hermes/profiles/{profile}/memories/MEMORY.md`
- Skills：`~/.hermes/profiles/{profile}/skills/`
- Cron输出：`~/.hermes/cron/output/`（读取 `last_report_content.txt` 获取Agent最后状态）

**验证脚本**：
```bash
ls ~/Desktop/渔芯科技/4-部门空间/ 2>/dev/null && echo "存在" || echo "不存在，用hermes profiles路径"
ls ~/.hermes/profiles/ 2>/dev/null
ls ~/.hermes/cron/output/last_report_content.txt 2>/dev/null && echo "有cron输出"
```

**可靠活跃判断**：读取 `~/.hermes/cron/output/last_report_content.txt`（cron输出），匹配Agent名字段（如"毛豆·每小时汇报"）。这是最可靠的活跃状态来源，不依赖文件系统路径。

**OpenClaw配置关键教训（历史记录，已迁移到Hermes）**：
- 2026-05-04 所有Agent已从OpenClaw迁移到Hermes Profiles
- Hermes Profile机制更优：`hermes profile create --clone` 自动创建完整隔离环境
- 各Agent workspace统一路径格式：`/Users/hua/Desktop/渔芯科技/4-部门空间/{部门名}/workspace`
- 新Agent加入：用 `hermes profile create <name> --clone` 代替手动配置openclaw.json

## 新Agent加入标准化流程（适用于任何电脑、任意数量Agent）

### 核心原则
飞书平台限制：bot之间不能私聊通信，群聊中只有主bot（Hermes/玉芬）能收到消息。
因此**所有跨Agent调度必须通过共享存储中转**，不依赖bot间私聊。

### Agent注册表（按电脑分组，持续更新）

**Mac mini（玉芬所在主机）— 本机直接调度，无需飞书中转**
| Agent名 | Workspace目录 | 职责域 |
|---------|---------------|--------|
| 玉芬 | — | 总指挥/任务分解/汇报 |
| 毛豆 | 毛豆-产品交付/workspace/ | 产品/项目/LookForge开发 |
| 老莫 | 老莫-技术运维/workspace/ | 知识库/测试/资料收集 |
| 黑豆 | 黑豆-行政财务法务/workspace/ | 行政/财务/法务/合规 |
| 宽博士 | `/Users/hua/.hermes/profiles/quant/` | 量化研究 |
| 学习助手 | `/Users/hua/.hermes/profiles/zhenglishi/` | 个人知识库整理 |

**Windows B（远程）— 必须通过飞书云盘中转**
| Agent名 | Workspace目录 | 职责域 | 飞书App ID |
|---------|---------------|--------|-----------|
| 小网红 | 待确认 | 自媒体帐号矩阵研究 | `cli_a97208b201f81bc0` |
| 小宝 | 小宝-商务运营/workspace/ | 销售/自媒体 | — |
| 阿福 | 阿福-客服/workspace/ | 销售/客服/测试 | — |

**第三台/ N 电脑（远程）— 必须通过飞书云盘中转**
（加入时在此补充）

**飞书云盘地址**：`Vb83fsimklzqKDdd0dHcc3g2nhd`
**云盘任务目录结构**：`任务派发/{Agent名}/` 下放置待领取的任务文件

### 新Agent加入步骤（Hermes Profile模式）

**第一步：创建Profile**
```bash
hermes profile create <name> --clone
```
自动创建完整隔离环境（config.yaml/.env/SOUL.md/memories/）。

**第二步：配置人设和记忆**
- 写入 `~/.hermes/profiles/<name>/SOUL.md`（人格定义）
- 写入 `~/.hermes/profiles/<name>/memories/MEMORY.md`（业务记忆）
- 写入 `~/.hermes/profiles/<name>/memories/USER.md`（用户画像）
- 复制飞书凭证到 `~/.hermes/profiles/<name>/.env`

**第二步：注册（必须同步更新多处列表）**
- 在 `AGENT_DOMAINS` 添加职责关键词
- ⚠️ **搜索所有 `.py` 文件中的 `AGENTS = [`**，同步更新每个文件中的列表（经常遗漏 `agent_dashboard_server.py`）
- 在本skill上方Agent注册表中添加新行
- 宽博士和学习助手**不需要加入团队监督**，它们只接华哥直接派的任务

**第四步：建立任务入口**
- 在飞书云盘 `任务派发/` 下创建新Agent文件夹
- 玉芬将任务文件放入该文件夹
- 验证调度链路

### 任务流转机制（所有Agent通用）

```
1. 玉芬接收华哥指令
         ↓
2. 玉芬将任务文件放入 飞书云盘/任务派发/{Agent名}/
         ↓
3. Agent的cron扫描到任务文件（每N分钟检查一次）
         ↓
4. Agent读取任务、执行
         ↓
5. Agent将产出上传到 飞书云盘/{Agent名}/ 完成/
         ↓
6. Agent扫描"完成"文件夹，通知玉芬（或玉芬定时检查）
         ↓
7. 玉芬汇总结果，在飞书群向华哥汇报
```

### 给新Agent的配置文件模板

新Agent的OpenClaw配置需包含以下任务扫描cron：

```yaml
# 每5分钟扫描一次任务入口
cron:
  - name: scan-tasks
    schedule: "*/5 * * * *"
    prompt: |
      检查飞书云盘 任务派发/{Agent名}/ 目录
      如果有新的任务文件，读取并执行
      完成后将结果上传到 飞书云盘/{Agent名}/完成/
      结果文件命名规范：{原任务名}_完成_{时间戳}
      
      飞书云盘ID: Vb83fsimklzqKDdd0dHcc3g2nhd
      使用feishu_drive工具操作云盘
      
      如果没有新任务，静默退出，不要重复汇报
```

### 可扩展性说明

此架构天然支持任意数量电脑、任意数量Agent：
- 新电脑 → 新Agent → 在本skill注册 → 分配云盘文件夹 → 立即纳入调度
- 无需修改玉芬的核心逻辑，只需在注册表中添加新行
---

## 内存监控与网关关闭流程

### 内存检查命令

```bash
top -l 1 | grep PhysMem
# 输出：PhysMem: 15G used (1893M wired, 7416M compressor), 488M unused
# 关注：compressor 大小 + unused 剩余空间
```

### 关闭阿福/黑豆/老莫网关（内存紧张时）

当 Mac 内存紧张（compressor > 8G，unused < 500M）时，正确关闭流程：

```bash
# 1. unload + disable + kill（完整关闭，避免 KeepAlive 重启）
launchctl unload /Library/LaunchAgents/ai.hermes.gateway-afu.plist
launchctl unload /Library/LaunchAgents/ai.hermes.gateway-heidou.plist
launchctl unload /Library/LaunchAgents/ai.hermes.gateway-laomo.plist
launchctl disable system/ai.hermes.gateway-afu
launchctl disable system/ai.hermes.gateway-heidou
launchctl disable system/ai.hermes.gateway-laomo
kill -9 $(ps aux | grep "hermes_cli.*(afu|heidou|laomo)" | grep -v grep | awk '{print $2}') 2>/dev/null

# 2. 验证
ps aux | grep "hermes_cli.*gateway" | grep -v grep  # 应只剩必要网关
top -l 1 | grep PhysMem  # 内存应释放
```

### 恢复已关闭的网关

```bash
launchctl enable system/ai.hermes.gateway-afu
launchctl enable system/ai.hermes.gateway-heidou
launchctl enable system/ai.hermes.gateway-laomo
launchctl load /Library/LaunchAgents/ai.hermes.gateway-afu.plist
launchctl load /Library/LaunchAgents/ai.hermes.gateway-heidou.plist
launchctl load /Library/LaunchAgents/ai.hermes.gateway-laomo.plist
sleep 3 && ps aux | grep "hermes_cli.*gateway" | grep -v grep  # 验证
```

**关键教训**：简单 `kill` 对 launchd 管理的服务无效，必须 `unload + disable + kill` 三步走才能完全停止。详见 `openclaw-launchd-macos` skill 的 `references/***SECRET***.md`。

### 网关进程状态速查

```bash
ps aux | grep "hermes_cli.*gateway" | grep -v grep
launchctl list | grep -E "(afu|heidou|laomo|maodou|xiaobao|quant)"
```

---

## 手动执行

```bash
cd ~/Desktop/渔芯科技/团队协作 && python3 agent_overseer.py
```

## Agent监控面板

**HTTP面板**（端口9118）：`/Users/hua/.hermes/scripts/agent_dashboard_server.py`
**Skill支持文件**：`scripts/agent_dashboard_server.py`（监控面板主脚本）

**启动方式**：
```bash
python3 /Users/hua/.hermes/scripts/agent_dashboard_server.py &
# 访问 http://localhost:9118
# 局域网访问：http://<本机IP>:9118
```

**API端点**：
- `GET /` → HTML监控面板（自动刷新30秒）
- `GET /api/status` → JSON格式Agent状态

### ⚠️ 关键教训：--report 输出格式解析

`agent_overseer.py --report` 的输出格式**会随版本变化**，解析逻辑必须同步更新：

**当前输出格式（2026-05-04起）**：
```
【团队监督】2026-05-04 21:51

空闲Agent（无任务）：无

有任务进行中：毛豆→【任务A】, 老莫→【任务B】, 小宝→【任务C】, 黑豆→【任务D】

当前待处理任务：0个
```

**正确解析方式**：
1. `空闲Agent（无任务）：` → 空闲Agent列表（无任务且30分钟无活跃）
2. `有任务进行中：名字→任务, 名字→任务` → 真正在执行的任务（多组以`, `分隔，**不要**用简单split）
3. `当前待处理任务：N个` → 未分配的pending任务数

**正确正则（处理多任务同行）**：
```python
pattern = r'([\w\u4e00-\u9fff]{2,4})→(.+?)(?=, [\w\u4e00-\u9fff]{2,4}→|$)'
matches = re.findall(pattern, raw_line, re.DOTALL)
```
❌ **错误方式**：先split逗号再split箭头，或用 `line.split('→')` 只取前两组

**去重逻辑**：
```python
assigned_names = {a['name'] for a in result['agents']}  # 用set去重
for agent in AGENTS:
    if agent not in assigned_names:
        result['agents'].append(...)
```
❌ **错误方式**：`if agent not in result['agents']` ——列表比较永远不等，导致重复添加

**解析失败表现**：面板显示重复的agent卡片（如毛豆出现两次），或任务名错位（如"国内RAS循环水, 小宝"变成一个任务）

## 飞书汇报机制

**汇报发送到**：总经理群（`328306697`，元宝派）

**凭证读取（已验证正确）**：从 `~/.hermes/config.yaml` 顶层键 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 读取，**不要**从 `sync_to_group.py` 源码复制（那是截断显示，会报 10014）。

**发送脚本**：`productivity/laomo-feishu-sync/references/send_feishu_report.py`（已验证 code=0 成功）

**问题**：`send_message` 到华哥 open_id（`***SECRET***`）返回 HTTP 400。

**根因**：飞书IM API 通过 `receive_id_type=open_id` 发送私信时，`receive_id` 必须是用户的 **union_id** 或 **user_id**，而不是 **open_id**。这两个ID体系不同，Bot用open_id找不到用户。

**临时解法**：发送汇报到**渔芯大群**（总经理群）：
```python
CORRECT_GROUP_ID = "***SECRET***"
# 使用 receive_id_type=chat_id 而非 open_id
"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
```

**代码**：
```python
import json, urllib.request
from pathlib import Path

HERMES_CONFIG = Path.home() / '.hermes' / 'config.yaml'
import yaml
with open(HERMES_CONFIG) as f:
    _cfg = yaml.safe_load(f)
APP_ID = _cfg['FEISHU_APP_ID']
APP_SECRET = _cfg['FEISHU_APP_SECRET']

def get_token():
    tok_req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(tok_req) as resp:
        return json.loads(resp.read())['tenant_access_token']

token = get_token()
CORRECT_GROUP_ID = "***SECRET***"

req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
    data=json.dumps({
        'receive_id': CORRECT_GROUP_ID,
        'msg_type': 'text',
        'content': json.dumps({'text': msg_content})
    }).encode(),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    method='POST'
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())  # {'code': 0, 'msg': 'success'}
```

**教训**：飞书报工单/汇报统一发送到**总经理群**（群ID固定），不要用个人DM。个人DM需要先通过 `https://open.feishu.cn/open-apis/contact/v3/users/{open_id}?user_id_type=open_id` 接口把 open_id 转换成 union_id 才能用于 IM API。

## 团队沟通架构（2026-05-04 确立）

### 群组结构

| 群名 | 用途 | 飞书群ID |
|------|------|----------|
| 总经理群 | 华哥与我，管理/战略/私事 | `***SECRET***` |
| 产品交付群 | LookForge 开发任务（毛豆） | 待确认 |
| 商务运营群 | 销售/自媒体（小宝）+ 客服（阿福） | 待确认 |
| 技术运维群 | 技术/运维/老莫 | 待确认 |
| 行政财务法务群 | 黑豆 | 待确认 |

### 通信规则

**本地Agent（Mac mini）→ 直接沟通**
- 毛豆、老莫、黑豆：直接对话，不走cron

**远程Agent（Windows）→ cron + 云盘**
- 小宝、阿福：任务文件写入飞书云盘 `任务派发/{Agent名}/` → cron扫描 → 完成回传云盘 `完成/`

**汇报流程（2026-05-04 新确立）：**
1. 各Agent在**自己部门群**领取任务、汇报完成
2. 玉芬在**总经理群**做整体进度汇总（不多头汇报）
3. 若无法直接与远程Agent沟通 → 走cron+云盘传统模式

### 阿福归属
- 客服（阿福）**在商务运营群**，不独立建群

### 飞书凭证UAT过期应对（已知问题）
- 症状：`Current user_access_token is invalid or expired`
- 影响：无法通过 API 查询群列表/群ID
- 解法：用户手动提供群ID，或重新授权（`hermes gateway setup`）

## Deliverable Audit Workflow（Agent 产出审查流程）

当华哥要求审查某个 Agent 的交付物（代码项目、工具、文档）时，按以下流程执行：

### 审查步骤

**Step 1：盘点文件清单**
```bash
# 列出所有源文件（排除 node_modules/dist/__pycache__）
find <project_dir> -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.css" -o -name "*.js" -o -name "*.yaml" -o -name "*.yml" -o -name "*.html" \) ! -path "*/node_modules/*" ! -path "*/dist/*" ! -path "*/__pycache__/*"
```

**Step 2：读全部核心源码**
- 入口文件（main.tsx / index.ts / app.py 等）
- 所有组件/模块文件
- 配置文件（package.json / tsconfig / vite.config / requirements.txt 等）
- 样式文件

**Step 3：验证能构建**
```bash
# 前端项目
cd <project_dir> && npm run build 2>&1
# Python 项目
cd <project_dir> && python -c "import <main_module>" 2>&1
```

**Step 4：按 P0/P1/P2 分级问题**

| 级别 | 定义 | 示例 |
|------|------|------|
| **P0** | 致命缺陷，系统不可用 | 全 Mock 无后端、构建失败、核心功能缺失 |
| **P1** | 严重影响质量 | 状态管理缺失、日期混乱、与研究成果脱节 |
| **P2** | 小问题 | 未使用的配置、代码分割、样式冗余 |

**Step 5：结构化报告**
```markdown
## 项目名 审查报告

**状态**：能/不能构建通过

### P0 严重问题
1. **问题**：描述 + 影响

### P1 中等问题
...

### P2 小问题
...

### 结论
整体评价 + 还缺什么 + 下一步建议
**Skill支持文件**：`scripts/agent_dashboard_server.py`（监控面板主脚本）
**Cron健康监控**：`references/cron-health-monitor.md`（cron状态/活跃判断/汇报模板）
**巡视验证脚本**：`references/***SECRET***.md`（2026-06-27 验证：jobs.json 不可信，必须读 .md FAILED 头 + 24h sessions 计数）

### 审查后的分工

- **玉芬**：审查 → 写报告 → 向华哥汇报
- **Claude Code**（delegate_task）：接玉芬派的修复任务，改代码
- **被审查的 Agent**：接收 Claude Code 的修复 PR，继续迭代

**核心原则**：玉芬不做代码实现。审查发现问题 → 分派给 Claude Code 修复。华哥 7 条原则第 5 条"Claude Code 技能更新与合理使用"——玉芬负责维护 Claude Code skill 的时效性，让 Claude Code 去执行编码任务。

### 已审查项目记录

| 日期 | 项目 | Agent | 结论 |
|------|------|-------|------|
| 2026-05-08 | 渔芯量化 v1.0 | 宽博士 | UI壳完成，零后端/全Mock/无策略引擎，P0致命 |
| 2026-05-08 | 渔芯量化 v2.0 | 玉芬(接手重做) | 全栈重构：FastAPI+akshare+因子/回测/模拟引擎 + React+Zustand+4Tab UI，构建通过 |

详见 `references/deliverable-audit-template.md`

---

## 更新日志
**真正修复（需修改 agent_overseer.py）**：`create_useful_tasks()` 必须在创建前真正执行：
```python
db_path = os.path.expanduser("~/.hermes/kanban.db")
archive_dir = os.path.expanduser("~/Desktop/渔芯科技/团队协作/task_archive/")

# 读取30天归档中的所有标题
archive_titles = set()
for fname in os.listdir(archive_dir):
    if fname.endswith('.json'):
        with open(os.path.join(archive_dir, fname)) as f:
            archive_titles.add(json.load(f)['title'])

# 从DB读取所有已存在标题（pending + in_progress）
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT title FROM tasks")
existing_titles = {row[0] for row in cursor.fetchall()}
conn.close()
all_seen = archive_titles | existing_titles

# 创建前过滤
for t in task_templates:
    if t["title"] in all_seen:
        continue  # 跳过已存在任务
```

**教训**：skill 文档写"已实施"不等于代码已实施。需对照代码验证，或在下次 session 发现重复任务时立即确认去重逻辑是否生效。

---

### Bug 10（2026-05-07）：`.pyc` 缓存导致代码修改不生效——去重逻辑永远失效

**问题**：`create_useful_tasks()` 的去重逻辑已在文件中修改，但 tasks.db 仍持续出现重复任务（同一标题创建30+次）。

**根因**：Python 解释器在运行 `import` 时将 `.py` 编译为 `.pyc` 字节码缓存到 `__pycache__/` 目录。此后即使 `.py` 文件被修改，如果缓存文件的时间戳比源文件更新，Python 会直接加载缓存中的旧代码，**完全忽略源文件的修改**。

**症状**：
- 代码 `grep` 确认已改，但函数行为仍是旧版
- `importlib.reload()` 或 `rm __pycache__/*.pyc` 后行为才正确
- 调试时发现内存中的变量值与文件中的代码不一致

**正确验证步骤**（修改 `agent_overseer.py` 等被其他模块 import 的脚本后）：
```bash
# 方案1：删除所有 .pyc 缓存（推荐）
rm -rf /Users/hua/Desktop/渔芯科技/团队协作/__pycache__/

# 方案2：用 importlib 强制重新加载
python3 -c "
import sys, importlib
import agent_overseer
importlib.reload(agent_overseer)
result = agent_overseer.create_useful_tasks()
print('创建的新任务:', result)
"

# 方案3：用 -B 标志避免生成 .pyc
python3 -B /Users/hua/Desktop/渔芯科技/团队协作/agent_overseer.py
```

**教训**：修改被 `import` 引入的 `.py` 文件后，必须清除 `__pycache__/` 或显式 `reload()`，否则代码修改不会生效。skill 文档写"已修复"不等于代码真的在跑那个版本。

- 2026-05-12：
  - **重大修正**：`~/.hermes/tasks.db` 是0字节空文件，真实kanban DB是 `~/.hermes/kanban.db`
  - 活跃判断改为首选 **cron输出文件**（`~/.hermes/cron/output/last_report_content.txt`），次选workspace扫描
  - 所有SQL引用统一改为 `kanban.db` 路径 + 正确schema（`assignee`/`started_at`/`body`，无`agent`/`updated_at`/`description`列）
  - 修复Bug 1/2/3/4/6/7/8中的所有 `tasks.db` 路径和错误schema字段引用
- 2026-06-27：
  - **重大发现**：`jobs.json.last_status` 不可信（402 错误时仍记 `ok`）— 必须读 `cron/output/{jobid}/*.md` 的 FAILED 头
  - 多个 `tasks.db` 并存：① `~/.hermes/kanban.db`（主任务池）② `~/.hermes/profiles/*/kanban.db`（profile级）③ `~/Desktop/渔芯科技/团队协作/tasks.db`（scanner.py 私有）④ `~/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/tasks.db`（0 字节）⑤ `~/.hermes/tasks.db`（hermes 内置,创业项目等 — ⚠️ heartbeat_check.py 未扫描此源,2026-08-09 已修复）— 巡视**只用** ①,但心跳脚本现已经覆盖 ①+③+⑤
  - 🆕 2026-08-09：发现 heartbeat_check.py 三数据库盲区 — 创业 P0 任务全在 ⑤ 但 Agent 看不到。已修复：迁移到 kanban.db + 脚本新增第三源。详见 `multi-agent-team-architecture` skill 的 `references/***SECRET***.md`
  - 活跃判断改为**首选 sessions/*.json 24h 数量**（最准确，反映真实 LLM 调用），次选 cron .md FAILED 头
  - 4-部门空间 workspace 扫描方法**已弃用**（目录长期为空，假阳性高）
  - 报告新规则：cron .md 出现 FAILED + 含 `402 / insufficient_balance` → 立即标"全团队 Provider 余额故障"

## ⚠️ 2026-06-26 验证：毛豆心跳cron提示词中的 `heartbeat_check.py` 路径不存在

**症状**：毛豆 hourly cron 提示词第一步让跑 `python3 ~/.hermes/scripts/heartbeat_check.py 毛豆`。该路径在当前 Maodou profile 下解析为 `/Users/hua/.hermes/profiles/maodou/home/.hermes/scripts/heartbeat_check.py` — **文件不存在**。执行报 `[Errno 2] No such file or directory`。

**真实的任务查询工具**：`/Users/hua/Desktop/渔芯科技/团队协作/scanner.py`（同 cron 提示词第一步说的 `scanner.py 毛豆 --no-claim` 一样）：
```bash
cd "/Users/hua/Desktop/渔芯科技/团队协作" && python3 scanner.py 毛豆 --no-claim
# 返回 JSON：{agent, workspace, claimed:[], in_progress:[], pending:[]}
```

**直接查 kanban.db 的等价 SQL**（不依赖 scanner.py）：
```sql
SELECT id, title, status, priority FROM tasks
WHERE status IN ('pending','in_progress') AND assignee='毛豆'
ORDER BY priority, created_at
```

**教训**：
1. cron 提示词是历史遗留，**第一步的命令路径已失效**，但第二步到 scanner.py 的命令仍然有效。
2. 修复方式：在 cron 提示词中删除 `heartbeat_check.py` 步骤，直接走 scanner.py。`jobs.json` 在 `~/.hermes/profiles/maodou/cron/jobs.json`，修改属于 profile 文件，需用户明确授权。
3. 当前 cron（job_id `28f82651884b`，2026-05-17 创建）已运行 449 次，最后一次状态 `ok` 但有 delivery 错误 `[99992402] field validation failed`（飞书消息字段校验失败，可能是 msg 中带 emoji 或 text 超长）。

**为什么 scanner.py 仍可用**：scanner.py 读 `tasks.db`（其自己的 `~/Desktop/渔芯科技/团队协作/tasks.db`，不是 0 字节的 `~/.hermes/tasks.db`），该 DB 在 2026-06-18 还有写入（20KB），是 scanner 自己的独立数据库。Maodou 主流程的 kanban 才是 `~/.hermes/kanban.db`。两套数据源并存，scanner.py 负责 cron 心跳，kanban.db 负责主任务池。

---

## ⚠️ 2026-07-13 验证：所有 Agent 心跳 cron 都可能遇到 profile 路径解析问题

**扩展问题**：不仅是毛豆，小宝/老莫/黑豆/阿福的心跳 cron 都可能遇到同类路径问题。当 cron 在某个 profile 上下文（如 zhenglishi profile）中运行时：

```
~/.hermes/scripts/heartbeat_check.py
→ 实际解析为：/Users/hua/.hermes/profiles/zhenglishi/home/.hermes/scripts/heartbeat_check.py
```

**2026-07-13 小宝心跳实际报错**：
```
[Errno 2] No such file or directory: '/Users/hua/.hermes/profiles/zhenglishi/home/.hermes/scripts/heartbeat_check.py'
```

**已修复**：已在全局路径创建脚本和空数据库：
- 脚本：`/Users/hua/.hermes/scripts/heartbeat_check.py`
- 数据库：`/Users/hua/.hermes/tasks.db`（空表结构已初始化）

**推荐修复所有心跳 cron**：将命令从相对路径改为绝对路径：
```bash
# 修改前（有问题）
python3 ~/.hermes/scripts/heartbeat_check.py 小宝

# 修改后（推荐）
python3 /Users/hua/.hermes/scripts/heartbeat_check.py 小宝
```

**各 Agent 心跳 cron job_id 速查**：
| Agent | job_id | 当前状态 |
|-------|--------|---------|
| 小宝 | `066886014d67` | 2026-05-13 已暂停（按需唤醒模式） |
| 毛豆 | `ac9bae2949bd` | 2026-05-13 已暂停 |
| 老莫 | `260b7b982ab7` | 2026-05-13 已暂停 |
| 黑豆 | `9071b1bae756` | 2026-05-13 已暂停 |
| 阿福 | `262419748f9b` | 2026-05-13 已暂停 |

**注意**：由于 2026-05-13 已切换到"按需唤醒"模式，所有心跳 cron 已暂停，此路径问题当前无实际影响。但如果未来恢复心跳 cron，必须先统一改为绝对路径调用。

---

## ⚠️ 2026-07-16 验证：heartbeat_check.py 与实际 Schema 列名不匹配（assigned_to vs agent）

**问题**：`heartbeat_check.py` 脚本内部的 CREATE TABLE 语句用的是 `assigned_to` 列：
```python
# heartbeat_check.py 第23-25行
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assigned_to TEXT NOT NULL,  # ← 脚本创建用的列名
    ...
)
```

但实际生产环境的 Global Tasks 和所有 profile 下的 tasks.db 用的都是 `agent` 列：
```sql
-- 实际 Schema
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    agent TEXT NOT NULL,  # ← 实际用的列名
    ...
)
```

当 `heartbeat_check.py` 在一个不存在数据库的环境中首次运行时，它会创建一个**错误 schema** 的空表，导致后续所有查询都报：
```
sqlite3.OperationalError: no such column: assigned_to
```

**影响范围**：所有 Agent（小宝/毛豆/老莫/黑豆/阿福）的心跳脚本，以及任何调用 `heartbeat_check.py` 的 cron。

**解决方案（三选一，按优先级）**：

**方案1（推荐）：直接查 kanban.db 跳过 heartbeat_check.py**
Kanban 系统是稳定真源，Schema 正确无歧义：
```bash
sqlite3 /Users/hua/.hermes/kanban.db "SELECT id, title, priority, status FROM tasks WHERE assignee='小宝' AND status='pending' ORDER BY priority ASC, created_at ASC LIMIT 1"
```

**方案2：修复 heartbeat_check.py 脚本的列名**
把脚本中所有 `assigned_to` 改成 `agent`（但注意：脚本可能会被回滚，需在所有 profile 下同步修改）。

**方案3：ALTER TABLE 修复已有数据库**
```bash
sqlite3 /Users/hua/.hermes/tasks.db "ALTER TABLE tasks RENAME COLUMN assigned_to TO agent"
# 对每个有问题的 tasks.db 重复
```

**关键教训**：`heartbeat_check.py` 不是可靠的任务入口——它自带 bug 会破坏数据库结构。**优先直查 kanban.db**，其次是直查 Global Tasks（用 `agent` 列），最后才考虑心跳脚本。
