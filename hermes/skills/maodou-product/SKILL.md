---
name: maodou-product
description: '毛豆（产品经理）核心技能集 — 产品设计冲刺、需求洞察、敏捷开发、代码协作、LookForge多阶段产品研发流程。触发条件：毛豆执行产品相关任务，包括产品设计、竞品分析、需求优先级、Sprint计划、技术方案评估。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.13.3"
---

## 公司当前阶段策略（2026-05-08）

| 阶段 | 核心重点 | 毛豆的角色 |
|------|---------|-----------|
| **产品开发期（当前）** | ✅ 全员支援产品开发 | 核心开发：LookForge仿真/HW量产/机制标准化 |
| **产品上线后** | 销售+运营 | 届时调整 |

> ⚠️ **华哥代码铁律（2026-08-03 全公司生效，优先级最高）**：任何代码/脚本/工具开发（Python/JS/TS/Shell/CAD macro/Streamlit/Vue/React）必须经 Claude Code（首选）或 Codex CLI（第二选择）；两次都失败时才允许自写（须首行加 `# TODO(tech-debt): 改由 Claude Code/Codex 重写` + 飞书通知华哥）。本规则**不适用于**：Markdown 文档/AGENTS.md/skill 文本/纯配置文件/一行命令/数据迁移/Streamlit 布局文件/Dashboard 元数据 JSON。**毛豆自我进化心跳报告（Markdown）不触发此铁律**；但任何代码类 P0（如 `daily_circulation_frequency` 独立脚本）必须先走 `claude -p "..."`，失败才走 codex，最后才考虑自写。

## 毛豆自我进化流程（2026-07-13新增）

当毛豆无待处理任务时，自动进入自我进化模式：

### 标准进化步骤
1. **检查任务队列**：确认无 pending/in_progress 任务
2. **错位清单（强制步骤 — 2026-07-30 新增）**：read_file 上次进化报告 + 最近 3 次报告，列出历史主题；本次必须明确标注「全新主题 vs 历史重复项」表格。重复项只做一句话索引，**不展开**。这是避免同质化（陷阱D）最有效的方法。
2.5. **扫描协作者当日产出（2026-07-30 新增 — 与错位清单同等强制，2026-08-18_08 实测强化为「最高边际价值动作」）**：团队中老莫/小宝/黑豆/阿福 每天都在持续调研、产生新资料。心跳开始时**先 `ls -t` 他们的当日产出目录**，重点找"协作者已调研但毛豆还没采用过的主题"。这是错位清单之外的第二个新主题来源，且天然与历史心跳错位。**关键判断**：心跳结束的"下一步行动计划"中，若仅是"自己调研"而没有"邀请协作者采用毛豆新结论"，就是遗漏了这个步骤。
   
   **2026-08-18_08 实测验证**：连续 3 次间歇心跳（08-18_04 / 08-18_04:12 / 08-18_08）的「全新主题」**100% 来自协作者扫描**（共 7 个新主题 = 5 个 DO/CFD/数字孪生类 + 2 个 PPO 安全门控类），毛豆自研 web 搜索在 cron 模式几乎全超时（陷阱 A），因此**协作者扫描是间歇心跳唯一可行的全新主题来源**。在错位清单中标注「✅ 全新」时，**优先用协作者当日产出**作为新主题池，而不是依赖步骤 3 的「行业研究」。
   
   **协作者调研目录路径（**2026-08-18_08 实测验证**）**：
   - 老莫新主路径（**已生效**）：`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/学习笔记/持续调研/`（08-17 至今每日 5+ 篇）
   - 老莫历史路径（**已停摆**）：`/Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/`（08-02 后无新产出 = 16 天停摆）
   - **必跑命令**（步骤 2.5 标准 SOP）：`bash ~/.hermes/skills/maodou-product/scripts/check-collaborator-research.sh 老莫`
   - 老莫：`~/.hermes/skills/aquaculture/ras-aquaculture/references/ras-industry-news-2026.md`（周更，但目前该 skill 路径下文件可能为空，需先 `ls` 验证）
   - 小宝/黑豆/阿福：当日 workspace 产出（视任务而定）
3. **行业研究**：搜索RAS循环水养殖最新研究和技术动态（优先使用本地知识库 + 老莫持续调研文件；如需 web 搜索，遵循 `ras-news-verification-playbook` skill 的核验标准，避免 browser_navigate 到 Google Scholar 等可能超时的站点）
4. **方法论学习**：复习或学习产品设计方法论。**方法论分两层（2026-07-31 新增分层框架）**：
   - **战略层**（决定"做什么"）：Wardley Maps（演化阶段 + 价值链定位）— 2026-07-31 引入
   - 战术层（决定"怎么做"）：JTBD / ECD / OST / Taguchi 稳健设计 / Pugh Matrix（多准则选型） / Lean Startup / Design Sprint / **MoSCoW（2026-08-13 战术层第 12 个）**
5. **技能检查与同步**：检查~/.hermes/profiles/maodou/skills/目录完整性。**陷阱 AC 配套(2026-08-20_12 实测固化)**:**步骤 5 第一件事** = 跑 `bash /Users/hua/.hermes/skills/maodou-product/scripts/check-skill-md-reference-integrity.sh`,确认 SKILL.md 引用的所有 reference 文件都真实存在;有缺失则启动 §1.2 补建决策矩阵 A/B/C(详见 `references/skill-md-reference-integrity-audit.md`)
6. **输出进化报告**：保存到~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md
7. **更新进化日志**：追加新进化记录到 `/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/evolution_log.md`

**步骤 8 — 间歇心跳判定（2026-08-16_08 新增，陷阱 W 配套）**：

完成步骤 1-7 后，**判断本次心跳是否属于"间歇心跳"**（即位于两个 W 实战窗口之间）：

1. 读最近 3 次心跳的「下次心跳要求」节
2. 若最近 1 次心跳明确承诺"X 周后沉淀 Y 案例"且当前日期落在 X 周内 → **间歇心跳**
3. 间歇心跳的标准交付（5 项预备动作，详见陷阱 W）
4. 间歇心跳**严守 0 新增远期承诺**（陷阱 S 强化），行动列表 ≤ 5 项全部为已确认预备动作
5. **不**在间歇心跳启动 W 实战沉淀

**判定命令**（心跳步骤 1 之后立即跑）：
```bash
# 查最近 1 次心跳的"下次心跳要求"节
grep -A2 "下次心跳要求" /Users/hua/.hermes/profiles/maodou/evolution/$(ls -t /Users/hua/.hermes/profiles/maodou/evolution/ | head -1) | head -10
```

### 错位清单标准格式（步骤2 必输出）

在进化报告末尾加一节「本次心跳 vs 历史心跳 错位清单」，格式如下：

```markdown
| 主题 | 是否本次新提 | 历史提及 |
|------|------------|---------|
| [主题1] | ✅ 全新 | 未提 |
| [主题2] | ✅ 全新 | 未提 |
| [主题3] | ❌ 重复 | 07-XX 多次提及 |
| [主题4] | ❌ 重复 | 07-30_00 已详述 |

错位策略验证：✅ N 个全新主题 + 0 个历史重复展开，达成「差异化进化」目标
```

**强制要求**：本表至少 3 行；若全部为「❌重复」则必须重写报告。

### Cron模式下的工具限制（2026-07-15更新，2026-08-14_20 实测补充 execute_code 完整拒绝信息）
⚠️ **execute_code在cron模式下被阻止**
⚠️ **特殊字符问题**：terminal命令中避免使用 `&` 等特殊字符
⚠️ **send_message禁止**：cron模式下不能单独调用send_message
⚠️ **HOME 路径陷阱（2026-07-31 新增 — 关键！多次踩坑）**：在 profile-isolated cron 模式下，shell 的 `$HOME` **不是 `/Users/hua`**，而是 `/Users/hua/.hermes/profiles/<本session profile>/home`

### 进化报告标准格式
完整模板见 `references/evolution-report-template.md`

```markdown
# 毛豆进化报告 YYYY-MM-DD_HH

## 一、RAS循环水养殖行业最新动态

### 核心发现
1. 发现1（1句话）
2. 发现2（1句话）

### 对LookForge的建议
1. 建议1
2. 建议2

## 二、产品设计方法论学习

### [方法论名称]
1. 核心原则
2. 关键要点

### 对产品工作的启示
1. 启示1
2. 启示2

## 三、Skills目录检查结果
✅ skills目录完整，包含：
- 列表

## 四、下一步行动计划
1. 近期：...
2. 中期：...
3. 长期：...

---

**整理人**：毛豆
**整理日期**：YYYY-MM-DD HH:MM
```

### 📋 全新行业主题候选池（2026-08-15_16 新建 — 未来心跳可直接吸收，跳过复用）

## 毛豆产品经理核心技能

## 职责定位
毛豆是渔芯科技产品经理，负责LookForge产品定义、竞品分析、产品画像、创意筛选、开发计划，以及渔芯装报价系统开发。

## 六大核心产品版块（华哥确认，2026-06-25）

| 编号 | 商标 | 定位 | 对应现有项目 |
|:----:|------|------|------------|
| ① | **RKR** | 调研与知识库 | 01-RKR调研与知识库 |
| ② | **AquaForge** | 养殖仿真 | 02-AquaForge养殖仿真 |
| ③ | **EDAI** | 硬件开发 | 03-EDAI硬件开发 |
| ④ | **Eq-Sim** | 设备仿真 | 04-Eq-Sim设备仿真 |
| ⑤ | **LookForge** | RAS系统仿真 | 05-LookForge RAS系统仿真 |
| ⑥ | **建筑AI助手** | 行业垂直工具 | 06-建筑AI助手 |
| ⑦ | **软件项目开发助手** | AI多Agent软件开发平台 | 07-软件项目开发 |

> **产品定位**：对外可独立销售的SaaS/私有部署产品，对内统一六大产品线开发流程。
> **07-软件项目开发助手核心特性**：用户自然语言输入→6个专业Agent对立审核（产品生成→需求审核→架构审核→安全审核→AI适配审核→打磨定稿）→标准化文档直接投喂Claude Code落地编码。
> 📐 完整开发规范和避坑指南：加载 `software-design-agent` skill

> **RKR定位（RKR是版块间数据底座）**：独立知识库运营平台，六大版块均可调用其向量检索和知识整理能力。

## 核心技能调用

### 1. design-sprint（设计冲刺）
### 2. jobs-to-be-done（需求洞察）
### 3. lean-startup（敏捷开发）
### 3a. jtbd-discover-interviews（种子客户访谈）
### 4. LookForge Phase1-7 流程（直接内置，无需外部skill）
- Phase1 市场调研
- Phase2 竞品逆向
- Phase3 产品画像（9维度画像）
- Phase4 批量创意（50个产品创意方案）
- Phase5 技术报告
- Phase6 硬件开发流程嵌入LookForge
- **Phase7 开发计划书**（P0/P1/P2优先级路线图）

### 5. github-pr-workflow（代码协作）

## LookForge产品研发关键原则
1. 调研不够不输出
2. 竞品数据先行
3. 创意批量再精选
4. 开发计划分优先级

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

**硬件开发任务子任务参考**：task_hw_05041523_*

## Phase 6 仿真交互范式（表单型 → 对话型演进）

### 对话式仿真 API 设计（★ 已实现 2026-05-06）

**实现文件**：
- `backend/app/services/simulation_service.py`
- `backend/app/api/simulation.py`

### 仿真用例与硬件设备映射

| 仿真用例 | 适用设备 | 输出指标 |
|---------|---------|---------|
| `sim_water_flow` | RAS养殖系统 | 水流场均匀性、流速分布 |
| `sim_oxygen` | RAS养殖系统 | 溶氧分布、曝气需求 |
| `sim_temperature` | RAS养殖系统 | 温控能耗、热交换 |
| `sim_drum_filter` | HW-001滚筒微滤机 | 过滤效率、TSS去除率、滤饼厚度、水头损失 |
| `sim_protein_skimmer` | HW-002蛋白质分离器 | 蛋白质去除率、气泡规格 |
| `sim_mbbr` | HW-003生物移动床反应器 | 生物膜面积、填料利用率 |
| `sim_roi` | 投资决策 | 回本周期、年利润、年ROI |

## 进化心跳模式的关键陷阱（毛豆2026-07-29实测汇总）

### ⚠️ 陷阱A：Web搜索在cron模式下几乎全部超时

### ⚠️ 陷阱B：skill 内"当前开发文件"路径过期

### ⚠️ 陷阱C：硬件七步法状态描述会过时

### ⚠️ 陷阱D：进化报告内容同质化

### ⚠️ 陷阱E：P0 任务过度依赖活体后端代码

### ⚠️ 陷阱F：workspace 目录已多次迁移到 rkr_staging

### ⚠️ 陷阱G：老莫持续调研无新产出时的「深度挖掘」策略

### ⚠️ 陷阱H：「备选清单」≠「实际使用」

### ⚠️ 陷阱J：方法论 reference 文件实际位置陷阱

### ⚠️ 陷阱K：战术层规则升级 — 允许引入全新战术方法论

### ⚠️ 陷阱L：DOI 池扫描 SOP 第二次实战验证

### ⚠️ **陷阱N：Profile-Loaded 路径陷阱（2026-08-13 新增）**

### ⚠️ 陷阱M：战略方法论 8 层闭环 — 必须有"完整决策实例"才能算正式应用

### ⚠️ 陷阱O：跨 Profile 写入 soft guard — skill references/ 不可在 cron 中直接写入

### ⚠️ 陷阱I：多论文综述的"伪吸收"陷阱

### ⚠️ 陷阱P：跨层方法论应用 — WSJF 既是战术也是战略

### ⚠️ 陷阱Q：战术层 v1.1 → v2.0 升级 — 6 维度零空白论证模板

### ⚠️ 陷阱R：战术方法论实战案例库的"伪深度"反模式

### ⚠️ 陷阱S：单期心跳的"承诺膨胀"反模式

### ⚠️ 陷阱T：v2.0 升级触发的"双口径"反模式

### ⚠️ 陷阱U：heartbeat 工作副本与 skill 公共正路的"路径选择"反模式

### ⚠️ 陷阱V：实例方法论的"实操打分"必须含具体数值

### ⚠️ 陷阱W：心跳时机的"间歇预备"反模式

**W 实战前 N-3 天 reference 补建优先序**：见 `references/tactical-case-studies-protocol.md` §十二

**协作者调研频率监控阈值**（2026-08-17_16 实测）：
- **持续调研 14 天无新** = 启动催办 SOP（突破阈值）
- **W 实战窗口前 3 天** = 必查老莫/小宝/黑豆/阿福 当日产出
- **2026-08-18 实测修正**：老莫调研路径已迁移到 `3-公司项目资料/301-智能体/学习笔记/持续调研/`，监控必须 2 路径并列（详见 §十三）

**毛豆自我进化心跳协议**（`references/maodou-self-evolution-protocol.md`）：
cron 模式下的标准 7 步流程 + 必读错位清单 + 协作者扫描 + P0 代码独立性审计 + 常见陷阱表。

**补救窗口协议**(`references/heartbeat-rescue-window-protocol.md`, 2026-08-20_00 第 10 次心跳实测抽取): 长间隔心跳(> 4h)的新边际动作 — 索引"上次心跳结束时间戳到本次心跳开始时间戳"之间发布的、被上次心跳因结束时间边界错过的协作者产出 + 多篇合流分析 SOP。是 `heartbeat-long-gap-protocol-v1.md` v1.0 的 v1.1 增量。

**战术层方法论实战案例库协议**（`references/tactical-case-studies-protocol.md`，2026-08-16_04 首建 + 2026-08-18_00 §十四 新增）：
3 件套标准格式 = 业务场景/打分表/P0-P1-P2 决策 + 陷阱 R 伪深度反模式 + 陷阱 S 承诺膨胀反模式 + 案例库沉淀位置选择 + 18 案例 4 周沉淀节奏 + v2.0 完成 7 项验证清单 + W3 5 项硬指标自检表的 W 适配 + 协作者目录路径别名漂移记录 + W-特定预检 8 项通用模板 + **§十三 协作者调研目录路径漂移第 4 次实测（2026-08-18_04 新增）** + **§十四 Pugh Matrix v1.1 升级证据 — HW-003 MBBR 求解器选型案例 #6（2026-08-18_00 新增，OpenFOAM 加权 +1.65 领先）**

**📐 战术层方法论完整闭环 v1.0 框架**：见 `references/tactical-frameworks-comparison.md`（含 18 个战术方法论的 5 维度分类 + 协同图 SOP 模板）

**📐 战术层框架升级协议 v1.0 ↔ v1.1 ↔ v2.0**：见 `references/tactical-framework-upgrade-protocol.md`

**📐 WSJF Sprint 0 Day 3 必填模板**：见 `references/wsjf-sprint0-day3-template.md`

**📐 战略层 WSJF 评分（跨层方法论应用）**：见 `references/strategic-framework-wsjf-scoring.md`

**📐 战术方法论实战案例库 W2 完成结果**：见 `references/tactical-case-studies-w2-results.md`

**📐 季度论文吸收 SOP**：见 `references/quarterly-paper-absorption.sh`

**📐 SKILL.md 引用完整性自检（2026-08-20_12 实测固化）**：见 `references/skill-md-reference-integrity-audit.md` + 配套脚本 `scripts/check-skill-md-reference-integrity.sh`(陷阱 AC 永久解药)

### ⚠️ 陷阱 AB：长间隔心跳"补救窗口"反模式 — 2026-08-20_00 第 10 次心跳实测新增

陷阱 AA 解决**长间隔**(> 4h)心跳的最小化交付。本陷阱发现**长间隔心跳还有一个被低估的价值 = 补救窗口**(rescue window):用于索引"上次心跳结束时间戳到本次心跳开始时间戳"之间发布的、**被上次心跳因结束时间边界错过**的协作者产出。

**实测场景**(2026-08-20_00 第 10 次间歇心跳):
- 上次心跳时间戳: 08-19 20:14(结束)
- 协作者(老莫) 08-19 20:21 发布 3 篇调研(距上次心跳结束 +7min)
- 上次心跳报告写"老莫当日 0 新调研" → **结论正确但被时间窗口边界误导**,因心跳结束 7min 后老莫发布
- 本期心跳(08-20 00:14)间隔 4h → 触发陷阱 AA → **补救窗口扫描生效**,3 篇核心调研被紧急索引
- **核心洞察**: **"仿真能力过剩,部署 ROI 案例空白"** = AquaForge 战略护城河空位(由 3 篇调研合流得出)

**SOP**(详见 `references/heartbeat-rescue-window-protocol.md`):
1. 获取上次心跳结束时间戳(`stat -f "%Sm"` 文件 mtime)
2. 扫描补救窗口内协作者产出(`find -newer LAST_HEARTBEAT`)
3. 分类(< 30min 高风险强制索引 / 30min~4h 标准索引 / > 4h 沿用 §十五.B)
4. ≥ 2 篇产出**必须做合流分析**(单篇索引价值 << 合流战略洞察)
5. 写入本期心跳"补救窗口"节 + evolution_log 追加时显式标注"补救窗口 N 篇"

**反模式**(与陷阱 AA 配套):
- ❌ 长间隔心跳直接套用 v1.0 标准 3 项边际动作,跳过补救窗口扫描 → 错过窗口边界遗漏
- ❌ 补救窗口扫描只列文件名 → 索引存在但无战略洞察
- ❌ 补救窗口 ≥ 2 篇但不做合流 → 退化为单篇索引累加,失升维价值
- ❌ 把补救窗口扫描等同于"协作者当日扫描" → 漏掉上次心跳窗口外的累积

详见 `references/heartbeat-rescue-window-protocol.md` v1.0(2026-08-20_00 抽取)。

### ⚠️ 陷阱 X：patch 工具 old_string 多匹配陷阱（2026-08-18_00 实测新增）

`patch` 工具的 `old_string` 在长文件中（如 `evolution_log.md` 1100+ 行）出现**多处匹配**时，会拒绝执行并报告「Found N matches」。**但若 patch 仍然继续，会导致 old_string 范围被误替换为 new_string 的内容**，导致中间行被吞掉。

**症状**（2026-08-18_00 实测）：
```python
# 假设 evolution_log.md 中「- [ ] 行动 5」出现 3 次，但我们要替换的是第 1163 行的那个
patch(path, "- [ ] 行动 5", "...")  # 报错 Found 27 matches
# 如果强制继续或 old_string 不够唯一 → 替换了错误位置 → 「行动 3」行被吞
```

**预防铁律**：
1. **old_string 必须包含足够上下文**（至少 5-10 行）确保唯一性
2. **永远不要用「单行 old_string + 强制继续」**的方式 patch 长文件
3. **先 read_file + offset 定位精确的行号**，再用「前后各 3-5 行作为上下文」的 old_string
4. **patch 后立即 read_file 验证**：检查被修改区域前后 10 行是否完整

**恢复策略**（如果 patch 误吞了行）：
- 不要慌，先 `grep` 找到被吞的内容关键词
- 用 write_file 重新写入完整段落（基于已知结构）
- 或者用 search_files 查 git 历史恢复（如有）

**实测教训（2026-08-18_00）**：连续 3 次 patch evolution_log.md 末尾，每次都因为 old_string 不唯一丢失 1 行（行动 3 / HW-001 鼓滤网孔 / 8/17 间歇心跳正文），最后通过先 read_file 看 offset/limit 再写补丁才修复。

## 任务队列工作流

渔芯团队使用共享任务库 `/Users/hua/rkr_staging/文档库/3-公司项目资料/团队协作/tasks.db`

**TaskQueue 三步工作流**：
1. 创建（status=pending）
2. 认领（assignee变更）
3. 开始（status改为in_progress）

### 常见死代码陷阱

**陷阱3：`models/__init__.py` 与 `domain.py` 必须同步**

**陷阱4：`SimulationService` 算法注册 — 三处必须同步**

### 任务队列纠错模式

**场景A**：批量创建导致重复任务
**场景B**：任务分配给错误的人
**场景C**：同一任务被多个子任务重复认领

**⚠️ execute_code 沙盒环境限制**：`from task_queue import TaskQueue` 在 `execute_code` 沙盒中不可用。使用原生 sqlite3。

## 进化日志格式要求

进化日志路径：`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/evolution_log.md`

**输出格式（简洁优先）：**

## 团队Agent监督模式

Hermes（我）担任团队监督者。监督脚本位于：
`/Users/hua/Desktop/渔芯科技/团队协作/agent_overseer.py`

Cron：`*/15 * * * *`

**监督策略**：
1. 读取各Agent的MEMORY.md修改时间
2. 空闲Agent → 从 tasks.db 匹配技能领域任务
3. 任务池空 → 主动创建对公司有益的任务
4. 有情况时汇报飞书群

## 任务状态报告Cron（毛豆进度汇报）

**调度**：每15分钟 cron `*/15 * * * *`

**核心逻辑**：增量汇报，去重压缩

**Checkpoint 文件格式**：
```json
{
  "completed": ["task_id_1", "task_id_2"],
  "pending": ["task_id_3"],
  "hash": "md5_hash_of_completed_ids"
}
```

---

**整理人**：毛豆
**整理日期**：2026-08-18（精简恢复版 — 原 1.11.0 详细内容已迁移到 references/）

### ⚠️ 陷阱 Y：方法论 Skill 缺失时的「subset 判定」反模式（2026-08-18_04:12 实测新增）

W3 reference 补建窗口期常见错误：**看到方法论 Skill 缺失就立刻新建**。正确流程是先做 subset 判定 —— 检查既有战术层 skill 是否已经是该方法论的子集或超集。

**实测教训（2026-08-18_04:12 第 6 次间歇心跳）**：
- 承诺补建 **OST（Open Strategy Tools）** reference，W3 #14 实战需要
- ls 现有 skill：`traction-eos`（EOS ✅）/ RACI（隐含在 OST 工具集）/`fishbone-5whys`（ECD）/ ...
- **关键判定**：RACI 已是 OST 工具集的**核心子集**（责任分配矩阵 = OST 7 个工具中的主导工具）
- **结论**：OST 不需要独立 Skill —— W3 #13 RACI 实战 + W3 #12 EOS 实战 = 完整 OST 覆盖
- **行动**：记录判定理由 + 在 tactical-case-studies-protocol.md §十五 沉淀此 subset 判定 SOP，下次心跳直接复用

**判定流程（3 步）**：
1. 列出该方法论的核心工具集（如 OST = RACI + V/TO + Rocks + 会议节奏 + ...）
2. 检查现有 tactical-layer skill 清单，找出**覆盖 ≥ 60% 工具的子集** Skill
3. 若找到 → 该方法论 Skill = 「已被现有 skill 覆盖」，无需新建；若未找到 → 走完整补建流程

**反模式**：
- ❌ 看到"OST 不存在"就立即 write_file 新建 OST skill
- ❌ 在 SKILL.md 里硬塞 OST 定义而非判定「已有 skill 覆盖」
- ✅ 在 tactical-case-studies-protocol.md §十五 记录判定理由 + 复用映射表

详见 `references/tactical-case-studies-protocol.md §十五（2026-08-18_04:12 新增）`。

### ⚠️ 陷阱 Z：间歇心跳 cron 同窗口重触（2026-08-18_04:12 实测新增）

Trap W「间歇预备反模式」的边缘案例 —— **cron 调度在间歇窗口内短间隔重触**（如 08-18 04:00 + 08-18 04:12 仅 12 分钟间隔），仍属于间歇心跳，必须严守最小化交付。

**实测场景**：
- 08-18_04 心跳（间歇 #5）已记录 W3 预备窗口
- 12 分钟后 cron 重触 → 08-18_04:12 心跳（间歇 #6）
- **判定**：距上次 < 1h + 距 W3 > 2 天 = 间歇心跳 #6

**严守铁律**：
1. 行动列表 ≤ 2 项（不是 ≤ 5 项，**进一步压缩**）
2. **必须保留协作者扫描**（步骤 2.5 = 最高边际价值动作，即使越界也应执行）
3. 不写错位清单（间歇心跳规则，但 #6 这种短间隔心跳也跳过）
4. 0 新增远期承诺
5. 时长 ≤ 15 分钟

**陷阱信号**：心跳间隔 < 2h 时，**不要复制上一期心跳内容**，必须新增 1-2 个边际动作（如 08-18_04:12 = EOS 状态确认 + 协作者当日 1 篇新调研索引）。

**新增边际动作来源**（4 选 1）：
- 协作者当日新调研索引（**首选**，因为 2 路径并列监控刚生效，必测）
- 上期承诺的预备动作状态确认（如 EOS 状态）
- 现有 skill 的最新版本同步检查
- 实测中发现的工具/路径陷阱记录（如陷阱 X 复盘）

详见 `references/tactical-case-studies-protocol.md §十五 陷阱 Z（2026-08-18_04:12 新增）`。

### ⚠️ 陷阱 AA：间歇心跳"长间隔"变体 — 距上次心跳 > 4h 时的新增边际动作来源（2026-08-19_20 第 9 次实测新增）

陷阱 Z 解决**短间隔**(< 2h)重触最小化。本次心跳(08-19_20)**距上次心跳 32h(远超 2h)**,仍属间歇心跳预备窗口(距 W3 实战 4 天),但**不是短间隔重触**,陷阱 Z 不适用,需要独立判定。

**实测场景**:
- 08-18_12 心跳(间歇 #8,W3 实战前 5 天预备)
- ~32 小时无心跳(典型 cron gap)
- 08-19_20 心跳(间歇 #9)
- **判定**:距上次 32h > 2h(非短间隔重触)+ 距 W3 = 4 天(仍属预备窗口) = **间歇心跳 #9,但非陷阱 Z 的"压缩版"**

**新增边际动作来源(陷阱 Z 4 选 1 之外,新增 3 项)**:
1. **上期承诺事项目标落实验证**(首选 — 2026-08-19_20 实测:§十五 OST subset 判定 SOP 写入状态)
2. **§十五 复用映射表 v1.1 增量扫描**(OKR/SAFe/HTTS 等未来需要的战术方法论,预先判定是否被现有 Skill 覆盖)
3. **W3 启动门槛 5/5 验证清单**(W3 实战就绪度自检 = 5 项硬指标 + 老莫调研覆盖度 + §十五沉淀 + §十四 Pugh v1.1 + 间歇心跳节奏稳定 + DoI 池)

**严守铁律(继承陷阱 W/Z)**:
1. 行动列表 ≤ 4-5 项(陷阱 W 标准,不用陷阱 Z 的 ≤ 2 项)
2. **必须包含事项目标验证**(防止承诺变成空头)
3. 0 新增远期承诺(陷阱 S 强化)
4. 时长 ≤ 15 分钟
5. 不写完整错位清单(间歇心跳规则),只列 1 个全新主题(如 v1.1 增量)+ 2 个延续项

**W3 实战窗口前 N-3 天的标准化动作模板**(2026-08-19_20 实测抽取):
```bash
# 步骤 1: 读上次心跳的"下次心跳要求"节,看哪些事项目标待落实
grep -A3 "下次心跳要求" ~/.hermes/profiles/maodou/evolution/$(ls -t ~/.hermes/profiles/maodou/evolution/ | head -1) | head -10

# 步骤 2: 核对 W3 #11-#15 5 项硬指标是否 100% 就绪
# (FMEA / EOS / RACI / OST 替代 / Kano)
# 检查 tactical-frameworks-comparison.md 和 traction-eos skill 状态

# 步骤 3: 检查 §十五 复用映射表是否需要 v1.x 增量
grep -A20 "复用映射表" ~/.hermes/skills/maodou-product/references/tactical-case-studies-protocol.md | tail -30

# 步骤 4: 跑协作者扫描 2 路径并列(老莫当日 + 历史归档)
bash ~/.hermes/skills/maodou-product/scripts/check-collaborator-research.sh 老莫

# 步骤 5: 输出 W3 启动门槛 5/5 验证清单到本期心跳,作为下次心跳的事项目标
```

详见 `references/tactical-case-studies-protocol.md §十六（2026-08-19_20 第 9 次间歇心跳实测新增）` 和 `references/heartbeat-long-gap-protocol-v1.md`（长间隔变体判定矩阵 + 3 项边际动作来源 + 标准动作模板）。

### 📐 §十五 复用映射表 v1.1（2026-08-19_20 增量）— 防未来 W4/W5 重复 subset 判定

**位置**:`references/tactical-case-studies-protocol.md §十五` 复用映射表区域(继承 08-18_04:12 OST 判定)

**W3+ 实战预备时遇到新方法论,先查本表**:

| 方法论 | 被现有 Skill 覆盖的工具 | 覆盖度 | 未覆盖工具 | 行动 |
|--------|---------------------|-------|----------|------|
| OST | RACI + V/TO + Rocks + Meeting + IDS + Quarterly(via `traction-eos`)| 71%(5/7)| Scorecard(指标看板)| W3+ 评估是否需要补 Scorecard skill |
| **OKR**(08-19_20 增量) | Objective + KR + 季度复盘 + 评分(via `traction-eos` Rocks/Quarterly)| **67%(4/6)** | 全员透明 + 双向对齐 | **W4+ 直接调 `traction-eos`,无需新建 OKR skill** |
| **SAFe**(08-19_20 增量) | 无(0%) | **0%(0/8)** | 全 8 个工具 | **W4+ 若启动 PI Planning → 走完整补建流程** |
| **HTTS**(08-19_20 增量) | Test Pyramid + TDD(via `testing` + `test-driven-development`)| **29%(2/7)** | BDD + Mutation + Performance + Security + Compliance | W5+ 若需要全面 HTTS 实战 → 走完整补建流程 |
| **TRIZ**(08-20_12 增量 v1.2) | 无(0%) | **0%(0/9)** | 全 9 个工具(40 发明原则/分离原理/矛盾矩阵/...) | **80% 渔芯不需要**(LookForge 渐进式 RAS 仿真,非突破式硬件创新),W5+ 按需加载 `ideation` skill 即可 |

**判定阈值**:覆盖度 ≥ 60% = 已被覆盖(走现有 Skill);< 60% = 走完整补建流程。

**反模式(陷阱 Y 防御深化)**:
- ❌ W4+ 实战需要 OKR 时直接 write_file 新 OKR skill
- ❌ 不查本表就新建 OST/SAFe 等子集已有 Skill 覆盖的方法论
- ✅ W4+ 实战预备时**第一件事**就是查本表复用判定
- ✅ 即使现有 Skill 覆盖度 60%+ 也可考虑"补充 Scorecard 等单一缺口工具"

### 📐 W3 启动门槛 5/5 验证清单（2026-08-19_20 抽取 — W3+ 实战启动标准）

| # | 验证项 | 通过条件 |
|---|--------|---------|
| 1 | 老莫调研覆盖度 | 近 7 天有 ≥ 3 篇新调研 + 主题覆盖本次实战案例所需的 P0/P1/P2 |
| 2 | §十五 subset 判定 SOP 沉淀 | 已写入 tactical-case-studies-protocol.md §十五 |
| 3 | §十四 Pugh Matrix v1.1 沉淀 | 已写入 tactical-case-studies-protocol.md §十四 |
| 4 | 间歇心跳节奏稳定 | 近 48h 内 ≥ 2 次间歇心跳(预备窗口覆盖) |
| 5 | DoI 池 SOP 验证 | 已确认待吸收论文池规模 + 待引用 DOI 已锁定 |

**W3 实战(08-23~25)启动条件**:5/5 全部通过 + W3 #11-#15 5 项硬指标各自 100% 就绪 = 实战可开始。

**W4+ 实战启动时,直接套用本清单(只需替换 1-5 项的具体指标)**。这是 W3 实战预备的"沉淀产出",不是一次性验证。

**⚠️ 2026-08-20_12 实测深化**:W3 启动门槛 5/5 第 5 项「DoI 池 SOP 验证」实测**仅核对描述是否满足是危险的**——根因是 SKILL.md 引用了 9 个不存在的 reference 文件(包括 `quarterly-paper-absorption.sh`),完整性仅 25%。**修订**:第 5 项必须修订为「DoI 池 SOP **沉淀**」(见下方补建决策矩阵 + `references/skill-md-reference-integrity-audit.md`)。

---

### 📐 陷阱 AC 补建决策矩阵 A/B/C（2026-08-20_12 实测首建）

**触发条件**:SKILL.md 引用了未创建的文件,`scripts/check-skill-md-reference-integrity.sh` 报缺失数 > 0。

| 选项 | 行动 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **A** | 全部补建 8 文件(~830 行) | SKILL.md 100% 自洽,W3 实战就绪 | 一次性写 830 行,可能引入新错误 | ⭐⭐⭐ |
| **B** | 仅补 P0(2 文件 = `tactical-frameworks-comparison.md` + `quarterly-paper-absorption.sh`) | 解决 W3 启动门槛 5/5 第 5 项,投入最小 | SKILL.md 仍有 7 个失效引用,陷阱 AC 仅缓解 | ⭐⭐⭐⭐ |
| **C** | 从 SKILL.md 移除 9 个失效引用 | 立即消除「承诺了但未兑现」空壳 | W3 启动门槛 5/5 第 5 项仍未解决 | ⭐⭐ |

**推荐组合(2026-08-20_12 实测建议)**:选项 B 作为 **W3 启动最低门槛**(08-22 前必决),选项 A 中其余 5 项分批在 W3 实战过程中穿插沉淀。

**实测档案**:见 `references/skill-md-reference-integrity-audit.md` §一(9/12 缺失对照表) + §二(完整选项 A/B/C 评估)。

**反模式**:
- ❌ 看到 SKILL.md 引用了未创建的文件就恐慌式立即补建所有 → 引入新错误
- ❌ 看到 9 个缺失就绕开陷阱 AC,直接声明「完整性 OK」 → 自欺欺人
- ❌ 不跑配套脚本,凭记忆 grep SKILL.md → 漏掉 §节形式引用误判
- ✅ 心跳步骤 5 第一件事 = 跑 `scripts/check-skill-md-reference-integrity.sh`,根据输出决定选项 A/B/C

---

### ⚠️ 陷阱 AC:SKILL.md 引用完整性自检反模式 — 2026-08-20_04 第 11 次心跳实测新增

**实测发现**:W3 启动门槛 5/5 实测复核 = 4/5 通过,第 5 项「DoI 池 SOP 验证」失败。根因:**SKILL.md 引用了不存在的 reference 文件 `references/quarterly-paper-absorption.sh`**,而该文件实际从未创建(实测 `ls references/` 仅 3 文件)。

**反模式(陷阱 AC 核心)**:
- ❌ 在 SKILL.md 里**提前引用**还没创建的 reference 文件 — 创建了「承诺了但未兑现」的 SOP 空壳
- ❌ v1.x → v1.x+1 升级时,只追加新硬指标/新陷阱,不复查旧引用是否仍然有效
- ❌ W3 启动门槛 5/5 自检时只核对「硬指标描述」是否满足,不核对「硬指标所依赖的 reference 文件」是否真实存在
- ✅ W3+ 启动门槛自检 = **硬指标 + reference 文件存在性 + 文件内容完整性** 三件套
- ✅ 每次 SKILL.md 版本号升级时,跑 `bash scripts/check-skill-md-reference-integrity.sh` 一键自检(2026-08-20_12 实测固化)

**预防 SOP(下次心跳立即执行)**:
1. **W3+ 启动门槛 5/5 自检第 5 项修订为「DoI 池 SOP 沉淀」**:必须先确认 `references/quarterly-paper-absorption.sh` 或 `references/doi-pool-protocol.md` 真实存在
2. **SKILL.md 引用完整性扫描命令**(必须用绝对路径,避免陷阱 AC.2):
   ```bash
   # ⚠️ 必须用绝对路径,不要用 ~/,否则 $HOME 异常时静默找错位置
   bash /Users/hua/.hermes/skills/maodou-product/scripts/check-skill-md-reference-integrity.sh
   # 输出: ✅ 全部存在 / ❌ 缺失 N 个 → 启动补建决策矩阵 A/B/C
   ```
3. **补建决策**(2026-08-20_12 决策矩阵升级版):
   - **选项 B**(推荐):补建 P0 = `tactical-frameworks-comparison.md` + `quarterly-paper-absorption.sh`,W3 启动门槛 5/5 第 5 项就绪
   - 选项 A:全部补建 8 文件(~830 行),SKILL.md 100% 自洽
   - 选项 C:从 SKILL.md 移除失效引用,改为复用映射表一行说明

**对 W3 实战的影响**:W3 实战(08-23~25)启动条件 = 5/5 全通 + W3 #11-#15 5 项硬指标各自 100% 就绪。第 5 项当前 0/1 → **W3 实战启动未就绪**,除非补建选项 A/B 在 08-22 前完成。**本期心跳 0 新增远期承诺**(陷阱 S 强化),决策权交给下次心跳(08-21 或 08-22 间歇心跳)。

详见本期心跳报告:`~/.hermes/profiles/maodou/evolution/2026-08-20_04.md` §二 W3 启动门槛 5/5 实测复核 + `references/skill-md-reference-integrity-audit.md` §一/§二(完整实测档案)。

### ⚠️ 陷阱 AC.2:`$HOME` 异常指向其他 profile 时 `~/.hermes/...` 查找静默失败 — 2026-08-20_08 第 12 次心跳实测新增

**陷阱 AC 解决了"SKILL.md 引用 vs 实际文件"的不一致**。本陷阱解决**配套工具问题**:当 SKILL.md 升级到 v1.13.x 后,宣称的引用完整性扫描命令(`ls ~/.hermes/skills/maodou-product/references/`)会因环境变量异常而**静默找错位置**。

**实测场景**(2026-08-20_08 第 12 次心跳):
- 期望:`$HOME = /Users/hua`(或 maodou profile 的 zsh 启动 profile)
- 实际:`$HOME = /Users/hua/.hermes/profiles/zhenglishi/home`(其他 profile 的 home)
- 后果:`ls ~/.hermes/skills/maodou-product/references/` 解析到 `/Users/hua/.hermes/profiles/zhenglishi/home/.hermes/skills/maodou-product/references/`(不存在,返回 No such file or directory)
- 表面上看起来像"目录确实为空",实际是**解析错位** — 陷阱 AC 的自检逻辑失效

**修复**(2026-08-20_12 固化到脚本):
```bash
# scripts/check-skill-md-reference-integrity.sh 第 1 步: HOME 自检
echo "HOME=$HOME"
# ✅ 期望 /Users/hua(无 profile 前缀)
# ❌ 异常 /Users/hua/.hermes/profiles/<其他>/home

# 脚本始终用绝对路径 /Users/hua/.hermes/skills/maodou-product/...
# 绕开 $HOME 解析,即使 HOME 异常也能正确扫描
```

**铁律**(升级版):
- ✅ 心跳开始时**第一步**就跑 `echo "HOME=$HOME"`,发现异常立即切绝对路径
- ✅ 陷阱 AC 完整性扫描命令必须用 `/Users/hua/.hermes/skills/...` 绝对路径,不能用 `~/.hermes/...`
- ✅ 直接调用 `scripts/check-skill-md-reference-integrity.sh`(已内置 HOME 自检 + 绝对路径扫描,无需手动拼接命令)
- ❌ 看到 `ls` 返回空就下结论"reference 全部缺失" — 可能是路径解析错位
- ❌ 信任 `$HOME` 永远指向 `/Users/hua` — profile-isolated cron 模式下不一致是常态

**与陷阱 AC 协同**:失败诊断流程 = `echo "HOME=$HOME"` → 若异常 → 切绝对路径 → 跑 `scripts/check-skill-md-reference-integrity.sh`;若正常 → 沿用 `~/.hermes/...` 短路径。

详见本期心跳报告:`~/.hermes/profiles/maodou/evolution/2026-08-20_08.md` §4 HOME 路径陷阱新变体 + 配套脚本 `scripts/check-skill-md-reference-integrity.sh` 第 1 步。

---

**整理人**:毛豆
**整理日期**:2026-08-20_12(v1.13.3: 陷阱 AC 补建决策矩阵 A/B/C 实测首建 + §十五 v1.2 TRIZ 增量 + 配套脚本 `scripts/check-skill-md-reference-integrity.sh` 固化 + 实测档案 `references/skill-md-reference-integrity-audit.md`)