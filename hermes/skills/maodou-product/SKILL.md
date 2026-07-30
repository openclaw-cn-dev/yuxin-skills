---
name: maodou-product
description: '毛豆（产品经理）核心技能集 — 产品设计冲刺、需求洞察、敏捷开发、代码协作、LookForge多阶段产品研发流程。触发条件：毛豆执行产品相关任务，包括产品设计、竞品分析、需求优先级、Sprint计划、技术方案评估。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# 毛豆产品经理核心技能

## 职责定位
毛豆是渔芯科技产品经理，负责LookForge产品定义、竞品分析、产品画像、创意筛选、开发计划，以及渔芯装报价系统开发。

## 公司两大品牌版块（产品决策必须对齐）

### 品牌一：AI赋能全链条
渔芯系列AI赋能整个水产养殖行业全链条，让整个水产养殖行业与AI深度适配、链接、绑定，随AI进化而进化。
→ 产品设计需思考：渔芯产品如何让客户绑定AI进化？

### 品牌二：看见未来
多环节数据线上仿真——养殖方案、设备、技术、设备开发均可在网上直接仿真测试验证。
→ **LookForge是"看见未来"的核心产品**，使命是让设备开发更新更便捷。

## 核心技能调用

### 1. design-sprint（设计冲刺）
当需要快速验证产品方向时加载。
流程：理解→聚焦→草图→决策→原型→测试，5天完成。

### 2. jobs-to-be-done（需求洞察）
当需要挖掘用户真实需求时加载。
核心：用户"雇用"产品完成什么"工作"？功能需求 vs 情感需求。

### 3. lean-startup（敏捷开发）
当需要定义MVP范围时加载。
Build-Measure-Learn循环：小步实验→验证→迭代或转型。

### 4. multi-phase-pipeline（多阶段产品开发）
LookForge专用流程：
- Phase1 市场调研 → 行业信息收集（research-collection）
- Phase2 竞品逆向 → 竞品功能/定价/策略分析
- Phase3 产品画像 → 9维度画像（目标用户/痛点/解决方案/价值主张等）
- Phase4 批量创意 → 50个产品创意方案
- Phase5 技术报告 → 精选方案技术可行性论证
- Phase6 硬件开发流程嵌入LookForge → 七环节标准化×仿真用例库×差异化配置（★RAS养殖专项仿真嵌入）
- Phase7 开发计划书 → P0/P1/P2优先级路线图

### 5. github-pr-workflow（代码协作）
当需要提交代码/创建PR/代码审查时加载。

## LookForge产品研发关键原则
1. 调研不够不输出——知识积累优先于快速输出
2. 竞品数据先行——没有竞品分析不拍板功能
3. 创意批量再精选——先50个再精选
4. 开发计划分优先级——P0核心/P1重要/P2可延期

## 常用输出模板

### 产品画像9维度
1. 目标用户
2. 用户痛点
3. 现有解决方案
4. 我们的解决方案
5. 独特价值主张
6. 客户收益
7.上市策略
8. 竞争壁垒
9. 成本结构

### 需求优先级矩阵
| 维度 | P0（立即） | P1（本Sprint） | P2（下个版本） |
|------|-----------|----------------|----------------|
**硬件开发任务子任务参考**（task_hw_05041523_*）：
- task_hw_05041523_1: 需求定义标准化（老莫）
- task_hw_05041523_2: 方案设计标准化（毛豆）
- task_hw_05041523_3: 仿真验证流程（毛豆）★ 已完成
  - 新增 `backend/app/services/simulation_service.py` — 仿真执行引擎（5个RAS仿真算法）
  - 新增 `backend/app/api/simulation.py` — 5个仿真API端点
  - 增强 `projects.py get_phase6_spec` — 自动注入仿真I/O schema
- task_hw_05041523_4: 工艺设计标准化（毛豆）
- task_hw_05041523_5: 生产测试标准化（毛豆）
- task_hw_05041523_6: LookForge嵌入（毛豆）★ 已完成
- task_hw_05041523_7: 差异化流程（毛豆）

## Phase 6 新增服务开发模式（仿真验证流程）

当需要为 Phase 6 新增子服务（如工艺设计、生产测试、差异化配置），遵循以下模式：

### 1. 新建 service 层
```python
# backend/app/services/xxx_service.py
class XxxService:
    def get_cases(self, hw_subtype): ...
    def run_xxx(self, case_id, inputs): ...
    def get_schema(self, case_id): ...
```
每个 case 的参数定义放在文件顶部 `SCHEMA` 常量中。

### 2. 新建 API 路由
```python
# backend/app/api/xxx.py
from fastapi import APIRouter
router = APIRouter(tags=["xxx"])  # ← 不要加 prefix！

# 注意：Router 不要加 prefix！
# 主 app 用 app.include_router(xxx.router, prefix="/api/projects") 挂载
# 如果在 router 里再加 prefix="/projects"，路径会变成 /api/projects/projects/...
```

### 3. 注册到 main.py
```python
from app.api import simulation, xxx  # 新API
app.include_router(xxx.router, prefix="/api/projects", tags=["xxx"])
```

### 4. 在 phase6 spec 中注入数据
在 `projects.py` 的 `get_phase6_spec` 中，给对应字段补充 schema：
```python
from app.services.xxx_service import SCHEMA
cases = hw_spec.get("xxx_cases", [])
for case in cases:
    case["schema"] = SCHEMA.get(case["id"], {})
```

### 5. 路由前缀防踩坑
**错误**：
```python
# simulation.py
router = APIRouter(prefix="/projects", ...)  # ❌ 错误

# main.py
app.include_router(simulation.router, prefix="/api/projects")  # → /api/projects/projects/...
```
**正确**：
```python
# simulation.py
router = APIRouter(tags=["simulation"])  # ✅ 无 prefix

# main.py
app.include_router(simulation.router, prefix="/api/projects")  # → /api/projects/{project_id}/simulation/...
```

## 当前开发文件
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/orchestrators/phase_orchestrator.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/dispatchers/skill_dispatcher.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/api/knowledge.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/api/projects.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/api/orchestrator.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/models/domain.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/services/simulation_service.py` ★ 新增
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/api/simulation.py`          ★ 新增

**仿真算法参考**（`references/simulation-algorithms.md`）：
5个RAS仿真用例的物理模型、关键公式、判断标准和参数说明，供后续开发参考。

**SaaS免费转付费转化路径**（`references/saas-conversion-path.md`）：
eFishery信任建立模式、3档触发点设计、LTV/CAC指标、LookForge订阅管理嵌入方式。

**硬件开发任务子任务参考**（task_hw_05041523_*）：
- task_hw_05041523_1: 需求定义标准化（老莫）
- task_hw_05041523_2: 方案设计标准化（毛豆）
- task_hw_05041523_3: 仿真验证流程（毛豆）
- task_hw_05041523_6: LookForge嵌入（毛豆）★ 已完成

## 任务队列工作流（重要 — 曾导致分配错误）

渔芯团队使用共享任务库 `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db`。

**TaskQueue 三步工作流：**
```python
q = TaskQueue()
# 第1步：创建（status=pending）
q.create_task(task_id="task_xxx", title="...", assignee="毛豆", ...)
# 第2步：认领（assignee变更，status仍是pending）
q.claim_task("task_xxx", "毛豆")
# 第3步：开始（status改为in_progress）⭐ 必须单独调用！
q.start_task("task_xxx", "毛豆")
```

**关键教训（已导致分配错误）：**
- `claim_task` 只改 assignee，status 仍是 'pending'，不调用 `start_task` 任务就不会进入"进行中"
- 如果先 `claim_task` 再 `start_task` 顺序反了，assignee 会正确但状态干净
- 分配任务给错误的人之后，可以用 `claim_task(task_id, correct_person)` 修正

**批量创建（防止 task_id 冲突）：**
```python
from datetime import datetime
import random, time

tasks = [("标题", "描述", "项目", "负责人", "P1"), ...]
for title, desc, project, assignee, priority in tasks:
    tid = f"task_{datetime.now().strftime('%m%d%H%M%S')}{random.randint(10,99)}"
    q.create_task(task_id=tid, title=title, description=desc,
                  project=project, assignee=assignee, priority=priority)
    q.claim_task(tid, assignee)   # 立即分配
    q.start_task(tid, "Hermes")  # 立即开始
    time.sleep(0.2)  # 间隔保证ID唯一
```

**验证命令：**
```bash
sqlite3 /Users/hua/Desktop/渔芯科技/团队协作/tasks.db "SELECT task_id, title, assignee, status, priority FROM tasks WHERE status='in_progress'"
```

### 常见死代码陷阱

**陷阱1：`generate_development_details()` 仅被 `run_phase2` 调用但生成通用选项**
- `run_phase2` 在第197行调用了它，但 `generate_development_details()` 只生成通用硬件选项（外观设计/控制系统/结构设计/材料工艺/安全合规/功能规格），不结合具体硬件子类型
- 正确做法：Phase6 `run_phase6` 已用 `_build_simulation_cases(hw_subtype, project)` 等方法补充了RAS专项仿真用例，Phase2的通用选项 + Phase6的专项仿真结合使用

**陷阱2：检查方法** — 确认每个 `run_phaseN` 都实际调用了它声明要做的所有工作，不要只看方法存在。搜索 `generate_development_details` 的所有调用点，确认调用上下文是否符合预期。

**陷阱3：`_build_simulation_cases` 的 `project` 参数未充分利用**
- 该方法接收 `project` 对象但仅用 `hw_subtype` 做分支判断，`project` 可用于从 `project.hardware_blocks` 提取具体仿真需求，未来应扩展利用

### 任务队列纠错模式（重要）

**场景A：批量创建导致重复任务**
监督者创建任务时，同一任务可能被创建两次（不同时间戳）。旧任务需取消。

```python
# 识别：同一标题有两个 task_id（旧task_id含较早时间戳）
# 解决：取消旧任务，保留新任务
c.execute("""
    UPDATE tasks SET status='cancelled', result='重复任务，已被替代' 
    WHERE task_id = ?
""", ('task_overseer_旧时间戳_负责人',))
```

**场景B：任务分配给错误的人**
跨Agent任务（如"客服FAQ"分配给"毛豆"）。用 claim_task 修正。

**场景B2：监督者创建的成对任务分配错误**
监督者有时会创建成对任务（如同一天创建的 `task_overseer_0504161523_毛豆` 和 `task_overseer_0504161523_阿福`），如果毛豆领取了阿福的任务，立即修正。
判断方法：查看任务description中的角色关键词（"客服FAQ"→阿福，"产品手册"→毛豆）。
```python
# 典型错误分配
('task_overseer_0504161523_阿福', '【客服】鱼乐宝SaaS产品客服FAQ扩充', '毛豆', 'in_progress')
# 修正
c.execute("UPDATE tasks SET assignee='阿福' WHERE task_id='task_overseer_0504161523_阿福'")
```

```python
c.execute("UPDATE tasks SET assignee='正确负责人' WHERE task_id = ?")
```

**场景C：同一任务被多个子任务重复认领**
主任务 task_0504152217（硬件开发流程标准化）拆分出7个子任务（task_hw_05041523_1~7）。
执行前必须先查询 tasks.db 确认：
- 该任务是否已被其他Agent领取？
- 该任务的 task_id 与其他子任务是否重复？

```python
# 执行前检查
c.execute("SELECT task_id, title, assignee, status FROM tasks WHERE title LIKE '%需求定义%'")
results = c.fetchall()
# 如发现已有关闭/完成状态的重复任务，标记自己的为完成即可
```

**⚠️ execute_code 沙盒环境限制：**
`from task_queue import TaskQueue` 在 `execute_code` 沙盒中不可用（ModuleNotFoundError）。
**解决方案**：在 execute_code 中使用原生 sqlite3：

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
c = conn.cursor()

# 完成任务
c.execute("""
    UPDATE tasks 
    SET status = 'completed', 
        result = ?,
        done_at = ?
    WHERE task_id = 'task_overseer_xxx'
""", (result_text, datetime.now().isoformat()))

conn.commit()
conn.close()
```

**tasks表结构**：`task_id, title, description, project, assignee, priority, status, result, created_at, updated_at, done_at`

## 团队Agent监督模式

Hermes（我）担任团队监督者。监督脚本位于：
`/Users/hua/Desktop/渔芯科技/团队协作/agent_overseer.py`

Cron：`*/15 * * * *`，每次检查所有Agent最后活跃时间，超过30分钟判定为空闲。

**监督策略（自动分配逻辑）：**
1. 读取各Agent的MEMORY.md修改时间（路径：`/Users/hua/Desktop/渔芯科技/4-部门空间/{部门目录}/memory/MEMORY.md`）
2. 空闲Agent → 从 tasks.db 匹配技能领域任务 → claim + start
3. 任务池空 → 主动创建对公司有益的任务并分配
4. 有情况时汇报飞书群

**已分配的典型任务（供参考）：**
- 毛豆：LookForge后端开发（ChromaDB接入/PhaseOrchestrator/PostgreSQL）
- 老莫：知识库建设、竞品调研
- 小宝：销售素材、自媒体内容
- 黑豆：法务合规、合同模板
- 阿福：测试验收、演示系统准备

## 任务状态报告Cron（毛豆进度汇报）

**调度**：每15分钟 cron `*/15 * * * *`

**核心逻辑**（增量汇报，去重压缩）：
1. 读取 tasks.db，查询 `status IN ('completed', 'done')` 作为已完成，`status IN ('pending', 'in_progress')` 作为进行中
2. 对比上次 checkpoint（`/Users/hua/.hermes/cron/output/last_report.json`）的 hash
3. hash 无变化 → 静默结束（不发送任何消息）
4. 有变化 → 生成压缩增量汇报，发送 final response（通过 cron origin auto-delivery 送达）

**重要经验教训：**
- 任务状态枚举有两个：`completed` 和 `done`（都算完成），查询时必须同时包含两者
- ⛔ **Cron 模式禁止单独调用 send_message**：Cron 的 final response 通过 origin auto-delivery 自动送达。尝试手动 `send_message` 到同一目标会触发 `duplicate_target` 或 `Could not resolve` 错误，导致发送失败。本session教训：即使想补充通知，也不要对同一 target 二次发送，统一走 final response 即可。
- 飞书大群实际名称：`渔芯科技（大群）`，但 Hermes Bot 尚未加入；当前可用的 DM：`oc_2db3b5373825567c3681d1ca580e0143`
- `cli_a964873dd7b8dbda` 是无效的 target name

**Checkpoint 文件格式**：
```json
{
  "completed": ["task_id_1", "task_id_2"],
  "pending": ["task_id_3"],
  "hash": "md5_hash_of_completed_ids"
}
```

**增量汇报模板**：
- ✅ 新完成：[任务名]（负责人）
- 🔄 新进行：[任务名]（负责人）

---

## maodu-Workflow — TaskQueue Automation Workflow

For the full maodu-workflow skill, see `references/maodu-workflow.md`. Summary:

### TaskQueue 三步工作流
```python
q = TaskQueue()
# 第1步：创建（status=pending）
q.create_task(task_id="task_xxx", title="...", assignee="毛豆", ...)
# 第2步：认领（assignee变更，status仍是pending）
q.claim_task("task_xxx", "毛豆")
# 第3步：开始（status改为in_progress）⭐ 必须单独调用！
q.start_task("task_xxx", "毛豆")
```

### execute_code 沙盒限制
`from task_queue import TaskQueue` 在 `execute_code` 沙盒中不可用（ModuleNotFoundError）。使用原生 sqlite3：
```python
import sqlite3
from datetime import datetime
conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
```

---

## maodu-Task-Queue-Debug — TaskQueue 调试经验

For the full debug skill, see `references/maodu-task-queue-debug.md`. Summary:

### 核心教训

**教训1：task_id后缀 ≠ 实际负责人**
任务归属只看 `assignee` 字段，不看 task_id 后缀。
```python
c.execute("SELECT task_id, title, assignee, status FROM tasks WHERE assignee='毛豆' AND status='in_progress'")
```

**教训2：重复任务清理**
清理前先确认产出物是否存在：
```python
import os
if os.path.exists(file_path):
    # 确认文件存在 → 标记重复任务为completed
```

**教训3：MEMORY.md并发写入损坏**
症状：残缺内容、多段拼接、文件异常变长。修复：覆盖全部内容，不用patch。

---

## maodu-Workflow-Cron — Cron 环境注意事项

For the full cron workflow skill, see `references/maodu-workflow-cron.md`. Summary:

### 已知问题：scanner.py 在 cron 环境下返回空

直接使用 TaskQueue API：
```python
import sys
sys.path.insert(0, '/Users/hua/Desktop/渔芯科技/团队协作')
from task_queue import TaskQueue
q = TaskQueue()
my_tasks = q.get_my_tasks('毛豆')
```

### 毛豆核心开发文件
- `phase_orchestrator.py` (793行)
- `skill_dispatcher.py` (155行)
- `knowledge.py` (334行)

---

## maodu-Task-Status-Reporter — 增量汇报 Cron

For the full task status reporter skill, see `references/maodu-task-status-reporter.md`. Summary:

### Hash 计算方式（关键！）
Hash 必须从原始 task_id 计算，不做 normalize/deduplicate：
```python
current_raw_ids = sorted(set(r[0] for r in completed_rows))
current_hash = hashlib.md5(','.join(current_raw_ids).encode()).hexdigest()
```

**易犯错误**：对 task_id 做 normalize 会导致 Hash 与 checkpoint 不匹配。

### 正确对比流程
先比较两个 completed 列表（set 差集），而非直接比较 hash。
- 📋 进行中：共N个任务
