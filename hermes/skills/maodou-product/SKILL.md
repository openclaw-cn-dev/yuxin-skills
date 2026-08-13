---
name: maodou-product
description: '毛豆（产品经理）核心技能集 — 产品设计冲刺、需求洞察、敏捷开发、代码协作、LookForge多阶段产品研发流程。触发条件：毛豆执行产品相关任务，包括产品设计、竞品分析、需求优先级、Sprint计划、技术方案评估。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.8.0"
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
2.5. **扫描协作者当日产出（2026-07-30 新增 — 与错位清单同等强制）**：团队中老莫/小宝/黑豆/阿福 每天都在持续调研、产生新资料。心跳开始时**先 `ls -t` 他们的当日产出目录**，重点找"协作者已调研但毛豆还没采用过的主题"。这是错位清单之外的第二个新主题来源，且天然与历史心跳错位。**关键判断**：心跳结束的"下一步行动计划"中，若仅是"自己调研"而没有"邀请协作者采用毛豆新结论"，就是遗漏了这个步骤。
   - 老莫：`/Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/`（每日多份，**2026-08-10 实测路径**——注意路径段名又变了：从 2026-07-30 的 `1-通用知识` 升级为 `1-公共知识`；如该路径也失效，用 `find /Users/hua/rkr_staging -name "持续调研" -type d` 定位）
   - 老莫：`~/.hermes/skills/aquaculture/ras-aquaculture/references/ras-industry-news-2026.md`（周更）
   - 小宝/黑豆/阿福：当日 workspace 产出（视任务而定）
3. **行业研究**：搜索RAS循环水养殖最新研究和技术动态（优先使用本地知识库 + 老莫持续调研文件；如需 web 搜索，遵循 `ras-news-verification-playbook` skill 的核验标准，避免 browser_navigate 到 Google Scholar 等可能超时的站点）
4. **方法论学习**：复习或学习产品设计方法论。**方法论分两层（2026-07-31 新增分层框架）**：
   - **战略层**（决定"做什么"）：Wardley Maps（演化阶段 + 价值链定位）— 2026-07-31 引入
   - **战术层**（决定"怎么做"）：JTBD / ECD / OST / Taguchi 稳健设计 / Pugh Matrix（多准则选型） / Lean Startup / Design Sprint
   - 选方法论前先想清楚"今天要回答的是战略问题还是战术问题"，避免战略问题用战术方法或反之
   - **历史使用清单**（按日期）：
     - 07-30_00：JTBD Discover Interview（战术）
     - 07-30_12：Evidence-Centered Design（战术）
     - 07-30_16：Opportunity Solution Tree（战术）
     - 07-30_20：Taguchi 稳健设计（战术）
     - 07-31_00：**Wardley Maps（战略）— 首次战略层方法论**
     - 07-31_08：**Pugh Matrix（战术）— 多技术横向选型（固液分离三技术对比）**
     - 07-31_12：**Crossing the Chasm（战略）— Geoffrey Moore 跨越鸿沟 + Whole Product 5 层**
     - 07-31_16：**FMEA（战术）— 故障模式与影响分析 + RPN 评分 + RAS 可靠性建模**
     - 08-01_00：**BCG Matrix（战略）— 12 仿真用例象限分布 + 资源 60%/收割/选择性投资分配 + 3 项反模式警示**
     - 08-01_08：**EOS  Entrepreneurial Operating System（战术）— 季度 Rocks + 周 Scorecard + IDS 会议**
     - 08-03_20：**Value Chain Analysis 波特价值链分析（战略）— 9 环节价值创造结构 + 价值洼地识别（服务/出料后勤）+ Q3 资源从 50%生产运营降至 35%，新增 15% 投服务+出料后勤**
     - 08-09_00：**Design of Experiments 实验设计（战术）— 因子设计+响应面方法+功效分析三件套 + 与 Taguchi 形成「优化-验证」闭环 + CCD 中心复合设计 20 组标定模板**
     - 08-09_H2：**Blue Ocean Strategy 蓝海战略（战略）— ERRC 四行动框架 + Strategy Canvas 战略布局图 + 三层非客户 + 六路径框架 + LookForge 在央企入局时代的蓝海定位**
     - 08-09_16：**Design Sprint 设计冲刺（战术）— 5 天 Map-Sketch-Decide-Prototype-Test + LookForge 4 个未验证假设 Sprint 排期（H1分享/H2 ROI理解/H3碱度警报/H4央企竞标）+ 反模式警示（范围蔓延/完美原型/跳过测试/假客户）**
     - 08-10_04：**Porter's Five Forces 波特五力（战略）— 5 力结构（供应商/购买者/进入者/替代品/现有竞争）+ LookForge 行业 3 绿 2 黄评分 + 与 BCG/VCA/Blue Ocean 形成战略方法论完整闭环 + 反模式警示（列表练习/只看现状/与SWOT混用/忽略互补品）**
   - 08-10_08：**Lean Startup 精益创业（战术）— Build-Measure-Learn + Innovation Accounting + Pivot or Persevere + 指标仪表盘 MVE `/metrics` 端点设计（7 字段）+ 4 项 Sprint 假设重审 + 战略+战术方法论 6 层完整闭环（Porter+BCG+VCA+Blue Ocean+Design Sprint+Lean Startup）**
   - 08-10_16：**Ansoff Matrix 安索夫矩阵（战略）— 4 象限框架（市场渗透/产品开发/市场开发/多元化）+ LookForge 资源分配（①40%/③30%/②20%/④10%）+ 与 6 个战略方法论协同定位（Porter/BCG/VCA/Blue Ocean/Chasm/Wardley）+ 4 项反模式警示 + 全球 RAS 5 个细分市场数据（CAGR 7.9-12.6%）首次作为兜底来源**
   - 08-10_20：**Kano Model 狩野模型（战术层第 11 个）— 5 类别 M/O/A/I/R + Phase 7 P0/P1/P2 标准化映射（P0=M+基础 A 70% / P1=O+进阶 A 25% / P2=I 5% / R 禁止）+ 5 类别与 JTBD/Lean Startup/Design Sprint/Pugh Matrix/OST/FMEA/Taguchi/EOS/DOE 9 个方法论的协同定位 + LookForge 用户 Kano 问卷 5 问模板 + 4 项反模式警示 + 战术层规则升级（见陷阱 K）**
   - **08-13_12：GE McKinsey 9 盒矩阵（战略层第 8 个）— 3 维度行业吸引力（规模 40%/增速 30%/盈利 30%）× 3 维度竞争地位（份额 30%/差异化 40%/获取难度 30%）= 9 象限 + 3 战略（投资增长/选择性投资/收获退出）+ 12 仿真用例 9 盒分布（4 个核心 + 1 个极品蓝海 + 4 个收获退出）+ 资源分配 60/15/5/20 三档聚焦（BCG 12 象限均匀 → GE McKinsey 60%集中度提升 50%）+ 季度复盘 SOP（10/1 首次实施）+ 4 项反模式警示 + 与 BCG/VCA/Blue Ocean/Porter/Ansoff 5 个战略方法论协同定位 + 8 层战略方法论完整闭环首次构建**
   - **下次心跳要求**：战略层和战术层交替使用时，优先选**未使用过的层级**，避免方法论同质化（陷阱D 变体）。当前状态：08-13_12 战略层（GE McKinsey 9 盒矩阵）后，**下次强制回到战术层**。战略层至此覆盖 8 个（Wardley/Chasm/BCG/VCA/Blue Ocean/Porter/Ansoff/GE McKinsey），战术层覆盖 11 个（JTBD/ECD/OST/Taguchi/Pugh/FMEA/EOS/DOE/Design Sprint/Lean Startup/Kano）。**战术层规则已升级（陷阱 K）**：当战术层所有已用方法论都做过"季度复盘/SOP 化"后，**允许引入新的战术方法论**（Storybrand Messaging / Influence Psychology / TRIZ / OKR / Eisenhower Matrix / MoSCoW / RACI 等），不再局限于已用清单。**战略层规则升级（2026-08-13 新增）**：战略层 8 个方法论已覆盖完整（地图+客户+价值链+行业+组合），下次战略方法论可优先选择**战略集团分析（Strategic Group Mapping）** — 识别渔芯 + 中科海 + 绿脉 + 崇睿 + 海大等设备商集团定位，与现有 8 个战略方法论互补。
   - ⚠️ **战略/战术分层轮换的反模式（陷阱 H 衍生 — 2026-08-10 新增）**：备选清单中出现 N 次 ≠ 实际使用过。Porter 五力在备选清单中出现 6 次（07-31_12 / 08-01_00 / 08-03_20 / 08-09_00 / 08-09_H2 / 08-09_16），但直到 2026-08-10_04 才被首次实际应用——这意味着前 6 次心跳都被"分层原则正确"误判，实际"战略层"从未真正覆盖。**修正**：轮换原则应基于「上次实际使用过的层级」而非「上次应该去的层级」。未来分层规则改为：检查 evolution_log.md 最近 3 次心跳中**实际应用的**方法论层级，而非备选清单。
   - 📐 **Wardley Maps 完整方法论**：见 `references/wardley-maps-methodology.md`（含 LookForge 当前快照 + 季度复盘 SOP）
   - 📐 **Pugh Matrix 完整方法论**：见 `references/pugh-matrix-methodology.md`（含固液分离选型实操案例 + LookForge API 设计 + 在设备选型/品种选型的复用方案）
   - 📐 **Crossing the Chasm 完整方法论**：见 `references/crossing-the-chasm-methodology.md`（含 LookForge 鸿沟诊断 10 分制 + Whole Product 5 层缺口清单 + Bowling Pin 滩头选择 6 准则）
   - 📐 **BCG Matrix 完整方法论**：见 `references/bcg-matrix-methodology.md`（含 12 仿真用例象限分布实操 + 季度评审 SOP + 3 项反模式警示 + 4 象限资源分配公式）
   - 📐 **Value Chain Analysis 完整方法论**：见 `references/value-chain-analysis-methodology.md`（含 LookForge 9 环节价值创造结构 + 价值洼地识别 + Q3 资源从 50%生产运营降至 35% + 与 BCG 协同用法 + 6 个复用场景 + 3 项反模式警示）
   - 📐 **Design of Experiments 完整方法论**：见 `references/doe-methodology.md`（含因子设计+响应面方法+功效分析三件套 + Taguchi-DOE 闭环 + CCD 20 组标定模板 + 3 项反模式警示 + LookForge 仿真参数标定实操案例）
   - 📐 **Blue Ocean Strategy 完整方法论**：见 `references/blue-ocean-strategy-methodology.md`（含 ERRC 四行动框架 + Strategy Canvas 模板 + 三层非客户 + 六路径框架 + LookForge 实操 + 季度评审 SOP + 3 项反模式警示）
   - 📐 **Design Sprint 完整方法论**：见 `references/design-sprint-lookforge-application.md`（含 5 天 Map-Sketch-Decide-Prototype-Test 框架 + LookForge H1-H4 四假设 Sprint 排期 + 4 项反模式警示 + 与精益创业组合用法）
   - 📐 **Porter's Five Forces 完整方法论**：见 `references/porter-five-forces-methodology.md`（含 5 力评分表 + LookForge 3 绿 2 黄实操 + 战略方法论完整闭环图（BCG+VCA+Blue Ocean+Porter 四支柱）+ 4 项反模式警示 + 季度五力复盘 SOP）
   - 📐 **Lean Startup 完整方法论**：见 `references/lean-startup-methodology.md`（含 Build-Measure-Learn / Innovation Accounting 三阶段 / Pivot-or-Persevere 决策框架 / 指标仪表盘 `/metrics` 端点设计（7 字段）/ 4 项反模式警示 / 当前 4 个 Sprint 假设重审 / 战略+战术方法论 6 层完整闭环）
   - 📐 **Ansoff Matrix 完整方法论**：见 `references/ansoff-matrix-methodology.md`（含 4 象限框架 + LookForge 资源分配 ①40%/③30%/②20%/④10% + 与 6 个战略方法论协同定位 + 4 项反模式警示 + 全球 RAS 5 个细分市场 CAGR 数据 + Q4 Ansoff 季度评审 SOP）
   - 📐 **Kano Model 完整方法论**：见 `references/kano-model-methodology.md`（含 M/O/A/I/R 5 类别详解 + Phase 7 P0/P1/P2 映射 + 9 个方法论协同表 + LookForge Kano 问卷 5 问模板 + 4 项反模式警示 + Kano × Lean Startup MVP 范围决策）
   - 📐 **GE McKinsey 9 盒矩阵完整方法论（2026-08-13 新增）**：见 `references/ge-mckinsey-9box-methodology.md`（含 3 维度行业吸引力 × 3 维度竞争地位 = 9 象限 + 12 仿真用例 9 盒分布 + 60/15/5/20 资源三档聚焦 + 季度复盘 SOP + 4 项反模式警示 + 与 BCG/VCA/Blue Ocean/Porter/Ansoff 5 个战略方法论协同定位）
   - 📐 **战略方法论完整闭环 8 层框架（2026-08-13 新增）**：见 `references/strategic-frameworks-comparison.md`（含 Wardley/Chasm/BCG/VCA/Blue Ocean/Porter/Ansoff/GE McKinsey 8 个战略方法论的协同图 + 4 维度分类 + LookForge 12 仿真用例完整决策实例 + 季度评审 SOP + 4 项反模式警示 + 未来战略方法论候选清单（战略集团分析/PESTEL/CAGE/ADL/麦肯锡 7S））
5. **技能检查与同步**：检查~/.hermes/profiles/maodou/skills/目录完整性，若为空或不完整：
   - 先用`skills_list`查看当前所有可用技能
   - 通过`skill_view`加载需要的技能
   - 从~/.hermes/skills/同步可用技能（注意：该目录本身内容可能稀疏，主要技能通过技能系统直接管理）
6. **输出进化报告**：保存到~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md
7. **更新进化日志**：追加新进化记录到 `/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/evolution_log.md`（**2026-08-03 实测路径**——见陷阱F第二次迁移；旧 `/Users/hua/Desktop/渔芯科技/4-部门空间/...` 和 `/Users/hua/rkr_staging/文档库/渔芯项目/4-部门空间/...` 均已不存在）

### P0 工作的"代码独立性"原则（2026-07-30 新增 — 与陷阱B 互补）

陷阱B 记录了"活体代码路径找不到"导致 P0 阻塞的多次教训。本原则给出**绕过路径依赖的设计策略**：

- **首选确定性规则 / Excel / 独立脚本可验证的 P0**：例如 `sim_tank_geometry` v0.1 用经验公式（不要 OpenFOAM）；U_crit 校验接入 `_sim_roi` 是 5 行 patch（不需要新文件）；CFD SOP 是文档（不需要代码）。
- **理由**：活体代码路径确认可能耗时数小时到数天；P0 工作如果只在"等路径"期间才能开工，就会被永远推迟。
- **判定标准**：P0 任务描述中如果出现"必须找到活体后端"等前置条件，**立即重写为不依赖活体后端的等价任务**。
- **示例**（2026-07-30_20 心跳）：3 个 P0（`sim_tank_geometry` v0.1 / U_crit 校验 / CFD SOP）合计 2-3 人天，**比"等路径确认"快 1-2 周**。

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

### Cron模式下的工具限制（2026-07-15更新，2026-07-31 增补 HOME 路径陷阱）
⚠️ **execute_code在cron模式下被阻止**：不能使用execute_code来写文件或执行Python脚本。**三件套替代方案**：
  - **新建文件** → `write_file` 工具
  - **追加/前置插入文本到已有文件** → `patch` 工具（提供 `old_string` + `new_string` 即可，无需 read 全文）
  - **执行 shell 命令** → `terminal` 工具
  - **教训（2026-07-31_08 实测）**：往 `evolution_log.md` 前置插入新记录时，`patch` 工具只需提供"前 N 行 + 新文本 + 后 N 行"作为 `new_string` 即可，比 `write_file` 全文覆盖更安全（避免覆盖其他心跳记录）

⚠️ **特殊字符问题**：terminal命令中避免使用 `&` 等特殊字符，会导致语法错误。

⚠️ **send_message禁止**：cron模式下不能单独调用send_message，所有通知必须通过final response自动送达，禁止对同一target二次发送。

⚠️ **HOME 路径陷阱（2026-07-31 新增 — 关键！多次踩坑）**：在 profile-isolated cron 模式下，shell 的 `$HOME` **不是 `/Users/hua`**，而是 `/Users/hua/.hermes/profiles/<本session profile>/home`（实测：maodou profile 下 `$HOME=/Users/hua/.hermes/profiles/afu/home`）。这导致：
  - `python3 ~/.hermes/scripts/heartbeat_check.py 毛豆` **直接报 `[Errno 2] No such file or directory`** —— 因为 `~` 解析到错误的 home，脚本根本不存在
  - `ls ~/.hermes/profiles/maodou/` 也会指向错误的目录
  - **解决方案**：所有路径用**绝对路径** `/Users/hua/.hermes/profiles/maodou/...`，绝不用 `~` 简写
  - **验证命令**：`echo $HOME && pwd` 在 terminal 启动后**第一件事**先跑，确认 home 实际值
  - **同样适用**：任何依赖 `$HOME` 的脚本（pip/pnpm/conda/git config），在 cron 里都可能指向错误位置 — 必要时显式 `export HOME=/Users/hua` 后再执行

⚠️ **心跳脚本实际位置（2026-07-31 实测）**：`heartbeat_check.py` **不在** `~/.hermes/scripts/`，而在 `/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营/workspace/heartbeat_check.py` 和 `/Users/hua/yuxin-skills/hermes/scripts/heartbeat_check.py` —— 但这些是其他 agent 的心跳脚本。**毛豆应直接检查 `tasks.db`**（`sqlite3 /Users/hua/Desktop/渔芯科技/团队协作/tasks.db "SELECT ... WHERE assignee='毛豆'"`），比 heartbeat 脚本更直接可靠。

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

> ⚠️ **历史发现汇总已废弃（2026-07-30）**：本节原本汇总各次心跳的行业发现，但累计后与"错位清单 / 陷阱D"目标冲突——汇总条目本身成了下次心跳"复制粘贴"的素材库。
> **替代访问方式**：所有心跳报告按时间排序在 `~/.hermes/profiles/maodou/evolution/` 目录；新主题从 3 份最近报告中**主动**找"不在清单上的"主题，而非从本节复制。
> 详见 `references/maodou-self-evolution-protocol.md` 第三节"历史访问规范"。

### 对AquaForge/LookForge的建议（2026-07-13 原始版，长期有效）
1. 在仿真模块中增加"每日循环频率"参数优化功能
2. 建立固液分离技术组合选型工具
3. 增加超细颗粒去除效率的仿真分析

> **其他Agent对毛豆的支援**：老莫（技术资料）、小宝（市场调研推广）、黑豆（合规合同）、阿福（测试验收）
> 完整策略和Agent分工详见 `agent-overseer` skill。

## 毛豆产品经理核心技能

## 职责定位
毛豆是渔芯科技产品经理，负责LookForge产品定义、竞品分析、产品画像、创意筛选、开发计划，以及渔芯装报价系统开发。

## 六大核心产品版块（华哥确认，2026-06-25）

| 编号 | 商标 | 定位 | 对应现有项目 |
|:----:|------|------|------------|
| ① | **RKR** | 调研与知识库（版块间数据底座） | 01-RKR调研与知识库 |
| ② | **AquaForge** | 养殖仿真 | 02-AquaForge养殖仿真 |
| ③ | **EDAI** | 硬件开发 | 03-EDAI硬件开发 |
| ④ | **Eq-Sim** | 设备仿真 | 04-Eq-Sim设备仿真 |
| ⑤ | **LookForge** | RAS系统仿真 | 05-LookForge RAS系统仿真 |
| ⑥ | **建筑AI助手** | 行业垂直工具 | 06-建筑AI助手 |
| ⑦ | **软件项目开发助手** | AI多Agent软件开发平台 | 07-软件项目开发 |

> **产品定位**：对外可独立销售的SaaS/私有部署产品，对内统一六大产品线开发流程。
> **07-软件项目开发助手核心特性**：用户自然语言输入→6个专业Agent对立审核（产品生成→需求审核→架构审核→安全审核→AI适配审核→打磨定稿）→标准化文档直接投喂Claude Code落地编码。技术栈：Vue3+FastAPI+SQLite+SSE+Docker。
> 📐 完整开发规范和避坑指南：加载 `software-design-agent` skill（`skill_view('software-design-agent')`）

> **RKR定位（RKR是版块间数据底座）**：独立知识库运营平台，六大版块均可调用其向量检索和知识整理能力。

> **定位原则**：LookForge = RAS行业专用工具，非通用平台。
> **产品整合教训**：渔芯科技历史上存在6个涉及3D/仿真项目重复建设的问题。
> 新产品决策时必须先确认边界，避免与现有六大版块重叠。

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

### 3a. jtbd-discover-interviews（种子客户访谈）
当需要验证 LookForge 假设 / 做种子客户访谈时加载。
核心：关注"过去行为 + 工作情境 + 全流程"，避免"未来意愿 + 产品功能 + 单时刻"反模式。
完整 5 问模板 + 4 个反模式 + 访谈纪律见 `references/jtbd-discover-interviews.md`。
**与精益创业的组合用法**：Discover Interview 发现 Job → 修正假设 → 优化 MVE。

### 4. LookForge Phase1-7 流程（直接内置，无需外部skill）
- Phase1 市场调研 → 行业信息收集（research-collection）
- Phase2 竞品逆向 → 竞品功能/定价/策略分析
- Phase3 产品画像 → 9维度画像（目标用户/痛点/解决方案/价值主张等）
- Phase4 批量创意 → 50个产品创意方案
- Phase5 技术报告 → 精选方案技术可行性论证
- Phase6 硬件开发流程嵌入LookForge → 七环节标准化×仿真用例库×差异化配置（★RAS养殖专项仿真嵌入）
- **Phase7 开发计划书** → P0/P1/P2优先级路线图（见下方专项节）

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

## Phase 6 仿真交互范式（表单型 → 对话型演进）

### 当前问题：表单型API与用户认知存在鸿沟

现有 `POST /{project_id}/simulation/run` 要求用户填写 `case_id` + 结构化 `inputs` dict。
养殖户的真实表达是：**"我想养石斑鱼，1000方水体，预计多少钱回本"** — 而不是"选择水流场仿真→填写池体直径→填写深度……"。

Phase2 Sprint计划（P2-6）已规划"对话式追问界面"，但尚未实现。

### 三层架构（对话式仿真）

```
用户自然语言
    ↓ [LLM理解层] — 品种+区域+水体+预算四要素提取
结构化仿真参数（case_id + inputs）
    ↓ [仿真层] — 现有5个算法无需改动
中文报告 + ROI计算结果
```

### 对话式仿真 API 设计（★ 已实现 2026-05-06）

**实现文件**：
- `backend/app/services/simulation_service.py` — `chat_simulation()` + `_sim_roi()` + `_get_species_defaults()` + `_run_single_simulation()`
- `backend/app/api/simulation.py` — `POST /{project_id}/simulation/chat` 路由 + `ChatSimulationRequest` 模型

**核心逻辑**：
1. LLM 解析自然语言 → 品种/水体/预算/区域四要素
2. 自动选择仿真用例组合（sim_water_flow + sim_oxygen + sim_temperature，含投资时加 sim_roi）
3. `_sim_roi()` 算法：`年利润 = 水体×产量×单价 - 年运营成本，回本周期 = 投资/年利润`
4. ROI 分析返回：investment_wan / payback_months / annual_profit_wan / annual_roi_percent / conclusion

```python
# simulation_service.py — chat_simulation() 方法签名
async def chat_simulation(
    self,
    user_message: str,
    hw_subtype: str = "ras_aquaculture",
    project_id: Optional[str] = None,
) -> dict:
    """
    对话式仿真入口（Phase 7 差异化核心）
    - 内部同步执行：_run_single_simulation() 调用现有5个算法不变
    - ROI仿真：_sim_roi() 基于品种价格×产量计算回本周期
    """
```

```python
# simulation.py — async 路由（注意 async def）
@router.post("/{project_id}/simulation/chat")
async def chat_simulation(project_id: str, req: ChatSimulationRequest):
    result = await service.chat_simulation(
        user_message=req.message,
        hw_subtype=req.hw_subtype or "ras_aquaculture",
        project_id=project_id,
    )
    return {"project_id": project_id, **result}
```

**API 示例**：
```json
POST /api/projects/{id}/simulation/chat
{
  "message": "我在广东想养石斑鱼，1000方，投资200万，多久回本？",
  "hw_subtype": "ras_aquaculture"
}
```
```

### 最小可行对话流设计

**场景A — 设备商（简单场景）**：
```
用户: "客户要养加州鲈，500方，帮我仿真一下水流场和溶氧"
→ LLM解析: case_ids=[sim_water_flow, sim_oxygen], inputs={品种:加州鲈, 水体:500m³}
→ 调用2个仿真 → 合并报告
```

**场景B — 养殖户（ROI场景）**：
```
用户: "我在广东想养石斑鱼，1000方，投资200万，多久回本？"
→ LLM解析: 品种=石斑鱼, 区域=广东, 水体=1000m³, 预算=200万
→ 自动组合: sim_water_flow + sim_oxygen + sim_temperature（温控能耗）
→ ROI计算（调用知识库品种参数）
→ 输出: 回本周期 + 年利润 + 关键风险点
```

### 前端对话UI设计

- 类ChatGPT对话界面，底部输入框
- 每条消息可展开"仿真详情"折叠区（显示原始参数+图表）
- 支持追问："这个方案溶氧不够怎么办" → 自动关联上一轮仿真上下文
- 未来扩展：图片上传（养殖场景截图）+ 语音输入

### 竞品差异化

| 竞品 | 交互形态 |
|------|---------|
| AKVA Connect | 表单型 |
| Aquabyte | 表单型 |
| 东方仿真 | 表单型 |
| LookForge | **对话型 + ROI计算** ★ |

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

## Phase 6+ 3D流体仿真路线图（2026-05-10新增）

现有仿真为1D/0D计算模型（输入参数→输出标量结果），缺少三维可视化。
调研成果（全报告见 `references/fluid-dynamics-simulation-tools.md`）：

### 三阶段路线

| 阶段 | 技术栈 | 产出 | 时间 |
|------|--------|------|------|
| **Phase A: 可视化层** | Three.js + @react-three/fiber | 流线/粒子/切面云图/探针 | 2026Q2-Q3 (2-3人月) |
| **Phase B: 真实物理层** | OpenFOAM Docker + Celery | 工业级CFD计算 | 2026Q4-2027Q1 (3-4人月) |
| **Phase C: AI加速层** | PINNs (DeepXDE/NVIDIA Modulus) | 毫秒级实时预测 | 2027Q2+ (4-6人月) |

### 当前可启动（本周）
- Three.js 3D原型：把 `sim_water_flow` 输出映射到3D场景
- 探针API：`POST /simulation/{id}/probe?x=&y=&z=` → {velocity, pressure, do}
- 仿生知识卡片：10个RAS可用的生物流体原理→ChromaDB

### 关键发现
- **完全蓝海**：全球无RAS设备流体仿真SaaS产品
- **WebGPU粒子法**(WebGPU-Ocean/Splash)可实时60fps，短期首选
- **OpenFOAM** 工业标准，中期引入Docker化计算
- **仿生设计**：鲨鱼皮减阻8-12%/鱼鳃逆流交换/海绵多孔过滤等8+原理可直接对标HW-001/002/003

> 📐 完整技术选型对比、竞品分析、架构图、API设计 → `references/fluid-dynamics-simulation-tools.md`

## 水流场仿真（sim_water_flow）

## 滚筒微滤机仿真（sim_drum_filter）

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
from pydantic import BaseModel, Field
from typing import Optional, Any

router = APIRouter(tags=["xxx"])  # ← 不要加 prefix！

class ChatSimulationRequest(BaseModel):
    """对话式仿真请求"""
    message: str = Field(..., description="用户自然语言描述，如：'我想养石斑鱼，1000方水体，预计多少钱回本'")
    hw_subtype: Optional[str] = Field(default="ras_aquaculture", description="硬件子类型")

# 对话式仿真路由示例
@router.post("/{project_id}/simulation/chat")
def chat_simulation(project_id: str, req: ChatSimulationRequest):
    service = get_simulation_service()
    result = service.chat_simulation(
        user_message=req.message,
        hw_subtype=req.hw_subtype,
        project={"project_id": project_id}  # 可扩展为真实project对象
    )
    return result

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

## Phase 7 开发计划书方法论（LookForge核心输出）★ 已完成实现

**Phase 7 已完整实现**（2026-05-05）：`run_phase7()` + `CommercialPlan` 模型 + Phase 7 REST API。

### Phase 7 的本质定位
Phase 7 不是"功能堆砌"，而是**商业验证冲刺**——回答"卖什么、卖给谁、怎么卖、怎么赢"四个问题。
核心商业指标：LTV/CAC > 3（生死线），NRR > 110%（健康线）。

### Phase 7 必须回答的5个核心问题

| # | 问题 | 当前最佳答案 |
|---|------|-------------|
| 1 | 目标客户是谁？ | **设备商**（决策链短/付费能力强/青岛中科海/绿脉/崇睿） |
| 2 | 第一年目标多少客户？ | 3-5个种子设备商 + 50-100个试用养殖户 |
| 3 | 核心获客渠道？ | 设备商推荐 + 行业展会 + 学术论文背书 |
| 4 | 如何防止免费陷阱？ | 设备商工具定位 + 按次超额计费，无通用免费版 |
| 5 | 如何建立数据护城河？ | 每次仿真脱敏数据贡献行业基准，用户获鱼币奖励 |

### P0/P1/P2 优先级框架（2026落地路径）

**P0（2026-Q2，必须做）：**
- ROI计算器嵌入仿真流程（输入：品种+水体+设备→输出：回本周期+年利润）★ 已实现（chat_simulation + _sim_roi）
- **品种参数库L1完善（7个品种）** ⚠️ 当前仅5个品种（石斑鱼/加州鲈/南美白对虾/罗非鱼/虹鳟），**缺叉尾鮰/泥鳅** — `_sim_roi` 的 `price_per_jin` 字典需补充
- 1个种子设备商访谈（青岛中科海或绿脉，验证切入时机）

**P1（2026-Q3，应该做）：**
- 订阅定价方案V2（参照鱼乐宝¥598-2,499/月，设计三档套餐）
- 竞品追踪数据库（AKVAconnect/AQUA-SIST/Xylene/Aquabyte/eFishery）
- 差异化配置UI + 数据回流机制设计

**P2（2026-Q4，可以做）：**
- 按次超额计费API
- 多语言支持
- API开放平台

### "看见未来"品牌落地关键
- **仿得准 > 功能全**：水流场/溶氧/温度是RAS核心，5个算法已覆盖
- **ROI计算器是关键破局点**：让养殖户"算得出省钱"才能激活采购
- **设备商是最佳B端切入渠道**：决策链短（老板直接拍板），核心话术"你们客户在做RAS设计时，是否经常遇到参数选型错误？"

### Phase 7 开发计划书标准格式（OSM框架）
```
规模（Scale）：目标客户数/仿真次数/月活
模式（Model）：订阅+超额+设备商分成
时间线（Milestones）：Q2种子→Q3验证→Q4扩张
商业指标：CAC<¥2000、LTV/CAC>3、NRR>110%
```

## 硬件七步法与主动缺口识别

每个硬件设备（HW-001/HW-002/HW-003...）遵循七步标准流程：

| 阶段 | 目录 | 毛豆职责 |
|------|------|---------|
| 01_需求定义 | 需求定义.md | 老莫（毛豆复核） |
| 02_方案设计 | 方案设计.md | 毛豆 |
| 03_仿真验证 | 仿真验证.md | 毛豆 |
| 04_工艺设计 | 工艺设计.md | 毛豆 |
| 05_生产测试 | 生产测试.md | 毛豆 |
| 06_量产导入 | 量产导入.md | 毛豆 |
| 07_差异化 | 差异化配置.md | 毛豆 |

**主动缺口识别（任务池空时触发）**：
当 `in_progress=0` 且 `pending=0` 时，扫描硬件目录找缺口：
```python
import os
# 2026-08-03 实测路径：4-部门空间已迁移到 3-公司项目资料/301-智能体
base = "/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/"
devices = ["HW-001_滚筒微滤机", "HW-002_蛋白质分离器", "HW-003_生物移动床反应器"]
for dev in devices:
    for step in range(1, 8):
        step_dir = os.path.join(base, dev, f"{step:02d}_*")
        if not glob.glob(step_dir):
            print(f"{dev} 缺失阶段 {step:02d}")
            break  # 找第一个缺失的作为主动工作目标
```
**本 session 实操结果（2026-07-29 核实更新）**：HW-001~HW-009 **全部9个设备的7个阶段均完整**（每个子目录至少1个md文件）。HW-001 仍是范本（每个阶段≥2个文件）；HW-002~HW-009 均为标准7文件结构。批量检查命令：
```bash
for hw in HW-001_滚筒微滤机 HW-002_蛋白质分离器 HW-003_生物移动床反应器 HW-004_增氧曝气系统 HW-005_温控设备 HW-006_自动投喂设备 HW-007_循环水泵 HW-008_消毒设备 HW-009_配电柜; do
  base="/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/$hw"  # 2026-08-03 第二次迁移
  for step in 01_需求定义 02_方案设计 03_仿真验证 04_工艺设计 05_生产测试 06_量产导入 07_差异化; do
    [ ! -d "$base/$step" ] && echo "$hw 缺失:$step"
  done
done
# 2026-07-29 运行结果：全部✅完整，无缺失
```
⚠️ **硬件七步法历史状态警告**：本 skill 在 2026-05 多次更新 HW 状态描述（HW-002/003缺失 → 后续补全），但 2026-07-29 验证时**所有HW-001~009均已完整**。后续心跳检查时请重新运行批量命令，**不要相信 skill 内任何"缺失状态"的历史描述**——以当次实操为准。

**标准文档结构参考**：
- `仿真验证.md` 包含：仿真用例库表格（5个用例ID+名称）、LookForge 参数配置表、仿真类型映射表、关键技术指标行业对比
- `差异化配置.md` 包含：四类产品差异化路径表、关键参数表（气泡规格/填料选型等）

## Post-V2 项目健康检查清单

当返回一个已完成 V2 的项目进行后续优化时，按此顺序做健康检查：

### 1. 跑测试（确认当前状态）
```bash
# 检查测试是否仍然全部通过
cd ~/Desktop/渔芯科技/6-产品研发/07-渔芯养 && npm test 2>&1 | tail -10
# 关注：Test Files X passed / Tests Y passed
```

### 2. 对比 prd.json 与实际状态（⚠️ 常见陷阱）
```bash
# 实际测试数 vs prd.json 中的 testCoverage.passed
grep -A5 '"testCoverage"' prd.json
```
- RAS CAD 教训：prd.json 此前记录 56 tests，实际已增长到 365 tests — **prd.json 容易过时**
- 如果发现统计差异 → 更新 prd.json 中的 `testCoverage` 和 `p2Tasks` 状态

### 3. 检查所有跟踪文件的一致性
对比以下文件的状态描述是否一致：
- `prd.json` — 产品需求定义（容易过时）
- `progress.md` — 开发进度日志
- `TASKS_REMAINING.txt` — 剩余任务列表
- `TASKS.txt` — 任务清单
- `task_plan.md` — 任务计划

### 4. 启动服务验证运行
```bash
# Web版
npm run dev:web   # Vite 在 5175 端口
# 或 Electron版
npm run dev       # electron-vite
```

### 6. 浏览器视觉检查
- 页面是否完整渲染（导航栏/设备库/视图区/状态栏）
- 设备库分类和数量是否符合预期
- 是否有明显的控制台错误

### 7. React 渲染性能优化（★ 每次健康检查必做）

此步骤在浏览器零错误后执行，直接刷新整个前端的渲染效率：

#### 7a. Store 订阅审计（P0）
```bash
# 全量 store 订阅（反模式，每次任何状态变更都触发重渲染）
grep -rn "useStore()" src/renderer/components/ --include="*.tsx"
grep -rn "usePipeStore()" src/renderer/components/ --include="*.tsx"
# → 全部改为 selector：useStore(s => s.fieldName)
```

#### 7b. React.memo 补齐（P0）
```bash
# 扫描 >200 行且缺少 memo 的组件
for f in $(find src -name "*.tsx" -exec wc -l {} + | sort -rn | awk '$1>200{print $2}'); do
  if ! grep -q "React.memo\| = memo(" "$f"; then
    echo "MISSING MEMO: $f"
  fi
done
# → export default memo(Component) 或 export const X = memo((props) => {...
# 注意：需同步添加 memo 到 React import
```

#### 7c. console.log 清除（P1）
```bash
# 生产环境不应有 console.log — 每次渲染分配字符串模板，累积性能消耗
grep -rn "console\.log" src/ --include="*.tsx" --include="*.ts" | grep -v node_modules
```
⚠️ **重要**：不要直接用 `sed -i '/console\.log/d'` 全局删除 — 多行 console.log 语句会被截断导致语法错误（如 GLTFModel 的模板字符串）。改用逐文件手工删除或只删除单行模式。

#### 7d. 性能验证
- `npm test` 全部通过
- 浏览器加载无 JS 错误
- FPS 正常（>30fps 在常规设备上）

### 8. 输出优化方向

对 Electron+React+TypeScript 项目进行系统化扫描。**完整命令集见 `references/react-ts-audit-commands.md`**。

扫描必须覆盖以下维度，直接对 P0 致命问题进行 score 评估：

| 扫描项 | 命令入口 | 严重性 |
|--------|---------|--------|
| 大文件清单（>500行需关注，>1000行必须拆分） | `find src -name '*.tsx' \| xargs wc -l \| sort -rn` | 高 |
| React.memo 覆盖率（>200行缺memo = P0） | 遍历检查每个 tsx 是否含 `React.memo` / `memo(` | **致命** |
| Store 全量订阅（`useStore()` / `usePipeStore()`） | `grep -rn "useStore()\|usePipeStore()"` | **致命** |
| console.log 残留 | `grep -rn "console\.log" src/` | 中 |
| 内联 style 对象计数 | `grep -rn "style={{" src/ \| wc -l` | 中 |
| 内联 onClick 箭头函数 | `grep -rn "onClick={(" src/` | 中 |
| `: any` 类型使用 | `grep -rn ": any" src/ \| wc -l` | 低 |
| TODO/FIXME/HACK 残留 | `grep -rn "TODO\|FIXME\|HACK" src/` | 低 |

### 7. 输出优化方向

基于上述检查和深度扫描，产出 P0/P1/P2 三级优化清单。典型分类：
- **P0 致命** — 缺 memo 的组件（>300行）、全量 store 订阅
- **P1 性能** — console.log 清理、内联对象/函数 memo 化
- **P2 技术债** — TODO 实现、`: any` 收紧、文档同步

> 📐 **RKR知识库运营平台需求**：独立知识库运营平台（环境检测/项目列表/Hermes嵌入/流式日志/可视化架构/查询下载），见 `references/rkr-knowledge-platform-requirements.md`
> 📐 **3D渲染尺寸一致性**：如果发现布局模式（占位几何体）与模型模式（GLB模型）中设备尺寸不一致，参阅 `references/3d-model-sizing.md` 了解 auto-scale 修复方案。
> 🔧 **管道系统架构**：管道双自动模式、断管串联、连接件端口系统、面板分离规则，参阅 `references/ras-cad-pipe-architecture.md`。
> ⚡ **性能优化检查清单**：Post-V2 优化流程（store订阅、memo审计、console清理、CSS冲突），参阅 `references/ras-cad-optimization-checklist.md`。

## 精益创业在LookForge的应用（毛豆进化2026-07-29首次引入，2026-08-10_08 首次完整方法论化）

> 与JTBD互补：JTBD回答"用户雇我们做什么工作"，精益创业回答"我们怎么验证假设、最小化浪费"。
> **完整方法论（含 Build-Measure-Learn / Innovation Accounting / Pivot or Persevere / `/metrics` 端点设计 / 4 个 Sprint 假设重审 / 战略+战术方法论 6 层闭环）**：见 `references/lean-startup-methodology.md`。

### 历史脉络（保留——说明方法论是如何演进的）

- **2026-07-29**：在「精益创业在LookForge的应用」章节首次引入 Lean Startup 三件套（Build-Measure-Learn + Innovation Accounting + Pivot-or-Persevere），但**仅引用约 60 行**未作为正式方法论学习。
- **2026-07-30**：指标仪表盘 MVE 设计——`/metrics` 端点 + 5 字段最小可用版本（chat_total / species_distribution / region_distribution / roi_queried / pdf_exported）。
- **2026-08-10_08**：作为战术层第 10 个方法论**首次完整正式应用**，补全 7 字段（含 `pdf_shared` / `anoxia_warned` / `alkalinity_alert_triggered`）+ Pivot-or-Persevere 决策阈值表 + 与 Design Sprint 的组合用法。

## 进化心跳模式的关键陷阱（毛豆2026-07-29实测汇总）

### ⚠️ 陷阱A：Web搜索在cron模式下几乎全部超时
- Tavily API（`api.tavily.com`）：返回 401 Unauthorized（`VOLC_ARK_API_KEY` / `AUXILIARY_WEB_EXTRACT_API_KEY` 都不是 Tavily key）
- DuckDuckGo HTML（`html.duckduckgo.com`）：连接超时 15s
- Google / Bing / Bing CN：全部超时
- **唯一可用**：`baidu.com` 返回200但带安全验证（人机识别），无法解析搜索结果
- **subagent 委托搜索**：用 `delegate_task(toolsets=['web'])` 经常超时（600s），返回结果质量不稳定
- **解决方案**：**优先用本地知识库** `~/.hermes/skills/aquaculture/ras-aquaculture/references/ras-industry-news-2026.md` + AI论文库 + 老莫持续调研文件（`/Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/`，**⚠️ 2026-08-10 实测路径——1-通用知识 → 1-公共知识 第 3 次迁移**；旧 `/Users/hua/Desktop/渔芯科技/9-学习笔记/...` 和 `/Users/hua/rkr_staging/文档库/渔芯项目/04-学习笔记工作区/...` 均已不存在），老莫负责日常更新；进化心跳只整理归纳，不强求实时新闻
- **行业资讯引用规范**：若需引用 RAS 行业新闻/趋势/竞品数据，必须遵循 `ras-news-verification-playbook` skill（阿福 owner）—— 三件套（标题+日期+URL）+ 3 个可独立验证关键点 + 引用边界（单一企业 ≠ 行业整体）
- **兜底来源（2026-08-10_16 实测新增）**：当老莫调研 + 本地知识库 + 协作者当日产出**全部吸收耗尽时**（如本次心跳：08-02 调研 6 篇 + 07-23 调研 3 篇 DOI 均已被历史心跳吸收），可切换到 DuckDuckGo 摘要级公开市场数据（web_search 仍可用，但仅取 5 个搜索结果的标题/描述级数据，不深入提取原文）作为兜底新主题来源。**必须**：仅引用 ≥2 个独立来源的中位数数据 + 在报告中明确标注"摘要级未交叉验证"+ 在「局限性」节列出风险。

### ⚠️ 陷阱B：skill 内"当前开发文件"路径过期（2026-07-30 再次确认 + 2026-07-31 升级）
- maodou-product 历史上列出的 8 个后端文件路径（`/02-设备开发助手/backend/app/...`）**自 2026-07 已不存在**，2026-07-30 08:24 实测再次确认全部 404
- 项目实际位置：`/02-八卦预测工具-国际版/backend/`（极简结构，仅 `app/db/migrations/`）
- **历史备份位置**：`/0-基础架构/backups/鱼乐宝AI仿生养殖平台_v6.0/backend/app/api/v1/`
- **解决**：每次心跳先用 `find /Users/hua/Desktop/渔芯科技 -name "phase_orchestrator.py"` 实际定位，再在进化报告标注"skill 路径过期"提交任务给老莫确认
- ⚠️ **2026-07-31 升级**：用 `find /Users/hua/Desktop/渔芯科技 -name "phase_orchestrator.py"` 和 `simulation_service.py` **整个项目树都搜不到**——不是路径过期，是**当前活体代码根本不存在**。P0 必须按"代码独立性"原则绕开（见上方「P0 工作的'代码独立性'原则」节）
- ⚠️ **本节「当前开发文件」8 条路径表整体作废**——不要在心跳报告中复制该表，全部以当次实测为准

### ⚠️ 陷阱C：硬件七步法状态描述会过时
- skill 多次记录"HW-002/003缺失某些阶段"，但 2026-07-29 实测**所有 HW-001~009 均完整**
- **解决**：任何"HW 状态描述"必须以当次心跳 `for hw in HW-...; do ... done` 批量检查为准，**不复制 skill 旧描述**

### ⚠️ 陷阱D：进化报告内容同质化
- 近 7 天 6 次进化心跳，**5 次结论几乎相同**（LHO/AI投喂/微藻/数字孪生重复提及）
- **2026-07-29 改进**：聚焦2026-07-26新情报（央企/新渔业法/饲料暴涨），明确与历史心跳区分
- **2026-07-30 改进**：聚焦2026-07-25后 AI 论文库5篇新论文 + JTBD 访谈技巧，与07-29完全错位
- **2026-07-30 08:00 改进**：聚焦老莫当日整理的 3 篇论文（蛋白质分离器+MBBR非均匀生物污染+碱度-pH-硝化），错位清单表强制输出
- **2026-07-30 20:00 改进**：聚焦老莫当日整理的**第 4 份调研**（RAS 养殖池流场与 CFD 仿真研究进展），输出 5 个全新主题（D/H+L/W 几何参数化、RTD-死区分数、U_crit 物理约束、Taguchi 稳健设计、CFD 6 步法 SOP）；本日 4 次心跳零主题重复
- 已知错位来源：协作者当日产出扫描（标准步骤 2.5） + 战略/战术分层选方法论（2026-07-31 新增）
- **下次心跳要求**：先列"本次新发现 vs 历史重复项"，对重复项只做一句话索引，**不展开**
- **成功经验**：心跳前先 `read_file` 看上次进化报告，列出最近 3 次主题清单，**专门找不在清单上的新主题**——已升级为标准步骤 2「错位清单」
- **新发现（2026-07-30_20）**：错位清单之外还有第二个新主题来源——**扫描协作者当日产出**（标准步骤 2.5）。老莫/小宝/黑豆/阿福 每天持续调研，他们当天产生但本心跳没采用过的资料 = 现成的新主题池
- **格式模板**：见上方「错位清单标准格式」节

### ⚠️ 陷阱E：P0 任务过度依赖活体后端代码（2026-07-30_20 新增）
- 2026-07-30_20 心跳 4 次被"等老莫确认活体后端路径"阻塞（07-30_08/12/16/20），累计 12 小时无进展
- **错误模式**：P0 任务描述中要求"先确认活体代码位置再开工"
- **正确模式**：P0 任务优先选择不依赖活体代码的设计——确定性经验公式 / 5 行 patch / 文档 SOP / Excel 可验证
- **示例**：本次心跳 3 个新 P0（`sim_tank_geometry` v0.1 / U_crit 校验 / CFD SOP）均不依赖活体后端，2-3 人天可完成
- **判定**：写 P0 任务时如果出现"必须先找到 X 代码"等前置条件，**立即重写为不依赖 X 的等价任务**

### ⚠️ 陷阱F：workspace 目录已多次迁移到 rkr_staging（2026-07-30 实测 + 2026-08-03 第二次迁移）
- **第一次迁移（2026-07-30）**：毛豆交付目录从 `/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/` 迁移到 `/Users/hua/rkr_staging/文档库/渔芯项目/4-部门空间/毛豆-产品交付/`
- **第二次迁移（2026-08-03 实测发现）**：交付目录再次迁移到 **`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/`** —— 注意"4-部门空间"已变成"301-智能体"，"渔芯项目"已变成"3-公司项目资料"
- **`evolution_log.md` 当前位置（2026-08-03 实测）**：`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/evolution_log.md`
- **HW-001~009 设备目录当前路径**：`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/HW-XXX_*/`
- **协作者对应路径已同步迁移**（小宝/老莫/黑豆/阿福均在 `3-公司项目资料/301-智能体/<agent>-*/workspace/` 下）
- **老莫持续调研目录路径（已 2 次迁移）**：
  - 第 1 次（2026-07-30 之前）：`/Users/hua/rkr_staging/文档库/渔芯项目/04-学习笔记工作区/...`
  - 第 2 次（2026-07-30 ~ 2026-08-09）：`/Users/hua/rkr_staging/文档库/1-通用知识/114-项目开发与调研/持续调研/`
  - 第 3 次（**2026-08-10 实测**）：`/Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/` —— 注意"1-通用知识"已变成"1-公共知识"
  - 旧 `桌面/9-学习笔记/...` 路径早已废弃
- **已不存在的旧路径**：
  - `/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/`（已不存在）
  - `/Users/hua/rkr_staging/文档库/渔芯项目/4-部门空间/毛豆-产品交付/`（第二次迁移后也不存在——**之前 SKILL.md 记录的路径已过期**）
  - `/Users/hua/Desktop/渔芯科技/9-学习笔记/...`（已不存在）
- **核心教训**：本目录至少已迁移 2 次。**任何引用"4-部门空间"或"渔芯项目/4-部门空间"的路径都应立即用 `find` 重新定位**。SKILL.md 的步骤 7 + 进化日志格式要求 + 主动缺口识别 Python 代码 + 批量检查 bash 命令这 4 处路径描述需要随每次心跳实测更新。
- **预防性检查命令（每次心跳第一步）**：
  ```bash
  # 验证活体路径仍然存在
  find /Users/hua/rkr_staging -name "evolution_log.md" -path "*毛豆*" 2>/dev/null | head -1
  find /Users/hua/rkr_staging -name "HW-001_滚筒微滤机" -type d 2>/dev/null | head -1
  ```
- **不要再相信旧路径**——直接 `find` 验证，所有对路径的"我记得是这样"都是陷阱

### ⚠️ 陷阱G：老莫持续调研无新产出时的「深度挖掘」策略（2026-08-09_H2 新增）
- 08-09_H2 心跳时老莫 08-02 后已 7 天无新调研产出，传统做法是「略过行业研究节」——但这会使心跳退化为纯方法论学习，错位清单缩水
- **正确策略**：当老莫无新产出时，退回到**更早期的未吸收内容**：
  - 扫描 7-14 天前的调研文件（如 07-31 固液分离对比），查找**被后续心跳跳过的论文/数据**
  - 判断标准：论文 DOI 是否在任何心跳报告中出现过 → 未出现 = 可吸收
  - 08-09_H2 实操：从 07-31 老莫调研中发现了 Pfeiffer 2024（低盐度泡沫分馏）和 Gregersen 2024（鼓滤网孔五级定量）2 篇从未被任何心跳吸收的论文
- **不要**：在没有新产出的情况下强行编造行业动态 or 重复使用已多次引用的行业新闻（海大/央企/饲料）
- **检查命令**：
  ```bash
  # 找 7-14 天前的调研文件（注意 2026-08-10 后路径是 1-公共知识）
  find /Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/ -name "*.md" -mtime +7 -mtime -21 | sort
  # 逐一检查每篇论文 DOI 是否在心跳报告中出现过
  grep -l "DOI" ~/.hermes/profiles/maodou/evolution/2026-08-*.md
  ```

### ⚠️ 陷阱H：「备选清单」≠「实际使用」（2026-08-10 新增 — 元方法论陷阱）
- Porter 五力在「下次心跳要求」备选清单中出现 **6 次**（07-31_12 / 08-01_00 / 08-03_20 / 08-09_00 / 08-09_H2 / 08-09_16），但直到 2026-08-10_04 才被首次实际应用——前 6 次都被其他方法论「抢先」占用
- **根本原因**：分层原则（战略 vs 战术）原本是「选未使用过的层级」，但被错误实现为「选层级内第一个未用的方法论」——结果战略层 6 次都「应该」选 Porter，但实际都被 BCG/VCA/Blue Ocean 等其他战略方法论占用
- **修正规则**（已在「下次心跳要求」节追加）：
  - 轮换原则应基于「上次实际使用过的层级」（查 evolution_log.md 最近 3 次心跳）
  - **不要**仅基于备选清单判断「战略/战术哪个未用」——同一层级内还有 5-6 个方法论，必须按"该层级实际使用次数"判断
  - **新增校验命令**：
    ```bash
    # 最近 3 次心跳用了什么方法论？
    grep -E "^\- 0[78]-" ~/.hermes/profiles/maodou/evolution/2026-*.md | tail -10
    # 应有：3 次连续的层级交替（战略→战术→战略 或 战术→战略→战术）
    ```
- **本节自我引用**：本陷阱的发现正是 Porter 五力应用后产生的——**「战略方法论完整闭环」判断本身就需要 Porter 来验证**，这反过来证明 Porter 缺位会让「战略层判断」沦为盲人摸象

### ⚠️ 陷阱J：方法论 reference 文件实际位置陷阱（2026-08-10_20 新增 — SKILL.md 路径真实性）
- SKILL.md 引用 11 个方法论 reference 文件（如 `references/ansoff-matrix-methodology.md`）—— 此前心跳**误以为这些文件不存在**
- **2026-08-10_20 实测**：这些文件**真实存在**，但路径在 `/Users/hua/.hermes/skills/maodou-product/references/`（**Hub-installed skill 路径**），不是 `/Users/hua/.hermes/profiles/maodou/skills/maodou-product/references/`（profile 本地路径）
- **早期心跳误判**：「10 个 reference 文件不存在」→ 实际上 skill 的引用完全有效
- **修正规则**：
  - 检查方法论 reference 文件时，用 `skill_view(name='maodou-product', file_path='references/xxx.md')` 直接读取
  - **不要**用 `ls /Users/hua/.hermes/profiles/maodou/skills/...` 判断文件是否存在
  - Hub-installed skill 的文件结构：`/Users/hua/.hermes/skills/<skill-name>/SKILL.md` + `references/`
  - Profile 本地路径 `/Users/hua/.hermes/profiles/maodou/skills/` 只放**agent-specific** 内容，不放通用方法论 reference
- **2026-08-10_20 行动**：下次心跳前用 `skill_view` 完整读取已用方法论的 reference 文件，作为"方法论深度回顾"输入

### ⚠️ 陷阱L：DOI 池扫描 SOP 第二次实战验证（2026-08-13 新增）
- 2026-08-10_20 心跳已识别 122 个未吸收 DOI + 创建季度论文吸收 SOP
- **2026-08-13_12 心跳第二次实战**：扫描后 116 个未吸收 → 实际新吸收 3 个 → 剩余 113 个
- **关键观察**：DOI 池是**可持续新主题来源**——每次心跳 1-2 个，1-2 个月一轮清理
- **有效模式**：每次心跳先跑 `comm -23` → 选 3-5 个与 LookForge 设备/仿真直接对应的 DOI → 展开
- **错误模式**：按"调研文件"批量吸收（一个文件含 5-10 个 DOI 漏 80%+）；不区分 DOI 与 LookForge 相关性
- **新增 cron 任务建议**（季度自动跑）：
  ```bash
  # 每季度第一个 1 号自动跑（毛豆 cron）
  bash /Users/hua/.hermes/skills/maodou-product/references/quarterly-paper-absorption.sh > /tmp/doi_pool_status.txt
  # 输出剩余未吸收 DOI 数量 → 写入 MEMORY.md 备忘
  ```

### ⚠️ 陷阱M：战略方法论 8 层闭环 — 必须有"完整决策实例"才能算正式应用（2026-08-13 新增）
- 8 个战略方法论（Wardley/Chasm/BCG/VCA/Blue Ocean/Porter/Ansoff/GE McKinsey）每个单独学习 ≠ 闭环
- **错误模式**：方法论独立使用，战略叙事碎片化（如 BCG 给 4 象限 + Porter 给 5 力 + Ansoff 给 4 象限 = 3 个独立结论）
- **正确模式**：每个战略方法论必须有「具体决策实例」（如 GE McKinsey 给出 12 仿真用例 9 盒分布 + 60/15/5/20 资源三档聚焦）
- **闭环检验**：8 个方法论全部应用后必须有 1 张「协同图」（`references/strategic-frameworks-comparison.md`）说明如何组合使用
- **下次战略方法论引入规则**：必须先看 `references/strategic-frameworks-comparison.md` 现有协同图，找到未被覆盖的「战略空白」（如战略集团分析=设备商集团定位，PESTEL=央企政策环境）

### ⚠️ 陷阱K：战术层规则升级 — 允许引入全新战术方法论（2026-08-10_20 新增）
- 原规则（08-10_16 设定的「下次心跳要求」）：战术层 10 个全部覆盖完毕后，**必须**从已用方法论的"季度复盘/SOP 化"中提取新角度
- **2026-08-10_20 实操**：10 个战术方法论虽然全部已用，但**没有任何一个**做过"季度复盘"或"SOP 化"——这意味着原规则其实无法执行
- **修正规则**：
  - 战术层 10 个全部覆盖后，**优先**做"季度复盘/SOP 化"（如果该方法论应用时间 ≥1 个季度）
  - 但如果该方法论应用时间 <1 个季度（如 Lean Startup 08-10_08 引入），**直接引入新方法论**比"季度复盘"更有价值
  - 全新战术方法论候选清单（按 LookForge 战略契合度）：
    - **Storybrand Messaging**（品牌叙事 + Phase 7 商业指标）
    - **Influence Psychology**（Cialdini 6 原则 + 设备商谈判）
    - **TRIZ**（发明问题解决理论 + HW 创新）
    - **OKR**（目标对齐 + 团队管理）
    - **Eisenhower Matrix**（紧急/重要 + 任务优先级）
    - **MoSCoW**（Must/Should/Could/Won't + Sprint 范围）
    - **RACI Matrix**（角色责任 + 跨 Agent 协作）
- **2026-08-10_20 已选 Kano Model**：是战术层 11 个，覆盖"用户满意度分类 + Phase 7 P0/P1/P2 标准化"领域——与既有 10 个零重叠

### ⚠️ 陷阱I：多论文综述的"伪吸收"陷阱（2026-08-10 新增 — 老莫调研论文吸收规则）
- 老莫 07-23 调研 `2026-07-23_生物滤池_碱度化学品调控与动态优化建模最新进展.md` 是**单文件多论文综述**——包含 3 个独立 DOI：
  - Qi & Vielma 2026（DOI: 10.1016/j.aquaeng.2026.102726）— **碱度化学品对比**
  - Montjouridès et al. 2025（DOI: 10.1016/j.aquaeng.2024.102492）— **碱度动态建模**
  - Yang et al. 2026（DOI: 10.1016/j.aquaculture.2025.742941）— **微生物组繁荣状态**
- 08-09_16 心跳只吸收了 Montjouridès（碱度建模）一篇，**Qi 化学品对比 + Yang 微生物组繁荣完全未展开**
- **错误判断**：「07-23 调研已部分吸收」 → 跳过
- **正确判断**：把单文件多论文综述当作 **N 个独立吸收单元**，每个 DOI 独立计数
- **修正规则**：
  - 老莫的"持续调研"文件标题为 `YYYY-MM-DD_*最新进展.md` 或 `*研究进展*.md` 的，**几乎都是综述**——必须按 DOI 拆开评估
  - 心跳的「错位清单」表格必须按 DOI 行展开，**不是按老莫调研文件**
  - 检查命令（升级版）：
    ```bash
    # 提取所有心跳中引用过的 DOI
    grep -hoE "DOI: 10\.[0-9]+/[a-z0-9.]+" ~/.hermes/profiles/maodou/evolution/*.md | sort -u > /tmp/absorbed_dois.txt
    # 提取老莫调研中所有 DOI（按行提取）
    grep -hoE "10\.[0-9]+/[a-z0-9.]+" /Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/*.md | sort -u > /tmp/laomo_dois.txt
    # 差集 = 老莫调研中未被任何心跳吸收的论文
    comm -23 /tmp/laomo_dois.txt <(sed 's/DOI: //' /tmp/absorbed_dois.txt) | sort -u
    ```
- **2026-08-10_04 实操**：用上述命令发现 Qi 102726 + Yang 742941 + Pedersen 10499-025-02335-8 等 4 篇从未被任何心跳吸收的论文，全部纳入本次心跳展开
- **2026-08-10_20 实操（升级）**：用 `comm -23` 在 14 份老莫调研文件中扫描出 **122 个 DOI 完全未被任何心跳吸收**（远高于 08-10_04 的 4 个）——这表明：
  - **DOI 池是可持续新主题来源**：每次心跳只需展开 3-5 个精选 DOI，剩余 100+ 留作后续心跳
  - **从 DOI 池到主题的筛选标准**：仅选与 LookForge 设备/仿真用例**直接对应**的 DOI（HW-001~009 + 7 个 sim_xxx 用例）
  - **不要按"调研文件"吸收**：老莫一份综述含 5-10 个 DOI，每个 DOI 独立判断——按文件吸收会漏 80%+
  - **可持续节奏**：下次心跳可选 3-5 个展开，2-3 个月清理一轮 122 个 DOI 池
- **2026-08-10_20 新增"季度论文吸收 SOP"**（建议月度 cron 自动化）：
  ```bash
  # 每月 1 号自动跑 — 输出未吸收 DOI 清单
  grep -hoE "DOI: 10\.[0-9]+/[a-z0-9.\-]+" ~/.hermes/profiles/maodou/evolution/*.md 2>/dev/null | sed 's/DOI: //' | sort -u > /tmp/absorbed.txt
  grep -hoE "10\.[0-9]+/[a-z0-9.\-]+" /Users/hua/rkr_staging/文档库/1-公共知识/114-项目开发与调研/持续调研/*.md 2>/dev/null | sort -u > /tmp/laomo.txt
  comm -23 /tmp/laomo.txt /tmp/absorbed.txt | grep -v "\.\$" > /tmp/unabsorbed.txt
  echo "未吸收 DOI: $(wc -l < /tmp/unabsorbed.txt)"
  # 输出 → 毛豆下次心跳自动参考
  ```

**LookForge后端优化审计脚本**（`references/lookforge-backend-audit.md`）：
ChromaDB健康度检查、PostgreSQL连接验证、查询延迟测量、Category分布分析、Chunk长度分布、并发瓶颈点识别。2026-05-07完成优化报告，输出至 `/共享资料/LookForge优化报告/LookForge后端优化报告_2026-05-07.md`。

**GE McKinsey 9 盒矩阵方法论**（`references/ge-mckinsey-9box-methodology.md`，2026-08-13 新增）：
战略层第 8 个方法论——3 维度行业吸引力 × 3 维度竞争地位 = 9 象限 + 12 仿真用例 9 盒分布 + 60/15/5/20 资源三档聚焦 + 季度复盘 SOP（10/1 首次实施）+ 4 项反模式警示。**资源分配公式**：投资增长 60% / 选择性投资 15% / 收获退出 5% / 战略基础设施 20%。**4 个核心用例**：sim_drum_filter / sim_protein_skimmer / sim_alkalinity / sim_roi。**1 个极品蓝海**：sim_exergy。**4 个收获退出**：sim_temperature / sim_biosecurity / sim_oxygen_feeding_combined / sim_oxygen 弱差异化部分。

**战略方法论完整闭环 8 层框架**（`references/strategic-frameworks-comparison.md`，2026-08-13 新增）：
8 个战略方法论（Wardley/Chasm/BCG/VCA/Blue Ocean/Porter/Ansoff/GE McKinsey）的协同图 + 4 维度分类（地图/客户/行业/资源）+ LookForge 12 仿真用例完整决策实例 + 季度评审 SOP（3 小时/季度）+ 4 项反模式警示 + 未来战略方法论候选清单（战略集团分析/PESTEL/CAGE/ADL/麦肯锡 7S）。

**Sprint规划方法论**（`references/sprint-planning-methodology.md`）：
Sprint计划标准格式——Mon/Tue/Wed/Thu/Fri五天节奏 + Sprint目标/交付物/验收标准三件套。适用于Phase 6迭代开发（对话式UI/品种库/PDF导出等）。

**仿真算法参考**（`references/simulation-algorithms.md`）：
5个RAS仿真用例的物理模型、关键公式、判断标准和参数说明，供后续开发参考。

**RAS 碱度-pH-硝化三体耦合**（`references/ras-alkalinity-ph-coupling.md`，2026-08-09_16 新增）：
7.14g CaCO₃/g NH₃-N 化学计量定律 + 碱度安全区间 + 补碱剂选型 + 品种敏感度 + 碱度崩溃链式故障 + sim_alkalinity 参数化表。与已有 sim_mbbr/sim_drum_filter/sim_oxygen 的耦合拓扑图。

**产品决策工作流**（`references/feasibility-analysis-workflow.md`）：
扫描文件→生成可行性报告→分解任务看板→分配Agent→等待决策→启动。
完整执行案例：2026-06-25 六大产品版块确认（报告见 `团队协作/公司架构可行性分析报告_2026-06-25.md`）。

**SaaS免费转付费转化路径**（`references/saas-conversion-path.md`）：
eFishery信任建立模式、3档触发点设计、LTV/CAC指标、LookForge订阅管理嵌入方式。

**Phase 7 开发计划书方法论**（`references/phase7-development-plan.md`）：
P0/P1/P2优先级框架、5个核心问题、OSM格式、"看见未来"品牌落地策略。

**LookForge Jobs-to-Be-Done 分析**（`references/lookforge-jtbd-analysis.md`）：
应用 JTBD 框架分析 LookForge 的核心工作、三个维度、四个力量、Big/Little Hire，以及 Phase 7 应用建议。

- **JTBD 发现访谈（Discover Interviews）方法论**（`references/jtbd-discover-interviews.md`，2026-07-30 新增）：
4 个核心原则 + 6 个反模式 + 5 问设备商访谈模板 + 访谈执行纪律 + 与精益创业组合用法 + 输出物清单。适用于 LookForge 种子客户访谈（青岛中科海/绿脉/崇睿）。

- **Pugh Matrix 多技术横向选型方法论**（`references/pugh-matrix-methodology.md`，2026-07-31 新增）：
5 步标准流程（选基线 → 列准则 → +1/0/-1 打分 → 加权排序 → 敏感性分析）+ RAS 固液分离三技术实操案例（鼓滤/旋流/泡沫分馏 + 三者串联）+ LookForge API 设计 `POST /simulation/pugh_matrix` + 6 个复用场景（设备选型/品种选型/网孔尺寸/填料/排放/方法论本身）+ 5 个常见陷阱。适用于任何"多方案 × 多准则"决策场景。

**LookForge 指标仪表盘 MVE + AI 论文库洞察**（`references/lookforge-metrics-and-papers-2026-07.md`，2026-07-30 新增）：
Innovation Accounting Baseline 的具体端点设计（`/metrics` 5 字段）+ AI 论文库 2026-07-25 后新增 5 篇论文对 LookForge 的启示（YOLO26/大西洋鲑低氧/BFT 双微生物组/印度 IoT/鱼类应激预警）。

**进化心跳案例研究**（`references/evolution-heartbeat-case-2026-07-30.md`，2026-07-30 新增）：
当日 4 次心跳零主题重复的标杆案例，错位清单 + 协作者扫描 + P0 代码独立性 3 个新原则的实操样本。详见第 5 节"给未来心跳的可复用模板"。

**毛豆自我进化心跳协议**（`references/maodou-self-evolution-protocol.md`）：
cron 模式下的标准 7 步流程 + 必读错位清单 + 协作者扫描 + P0 代码独立性审计 + 常见陷阱表。

**季度论文吸收 SOP**（`references/quarterly-paper-absorption.sh`，2026-08-10_20 新增）：
可执行 bash 脚本——每月 1 号自动运行，输出老莫调研中未被任何心跳吸收的 DOI 清单（基于 trapI 的 `comm -23` 命令封装）。本次实测发现 122 个未吸收 DOI；建议月度 cron 自动化。直接执行：`bash references/quarterly-paper-absorption.sh`。

**Kano Model 完整方法论**（`references/kano-model-methodology.md`，2026-08-10_20 新增）：
战术层第 11 个方法论——M/O/A/I/R 5 类别 + Phase 7 P0/P1/P2 映射 + 9 个方法论协同表 + LookForge Kano 问卷 5 问模板 + 4 项反模式警示 + Kano × Lean Startup MVP 范围决策。

**竞品调研方法论**（`references/竞品调研方法.md`）：
直接导航优先于搜索引擎 + 竞品清单追踪 + 调研记录模板。关键发现：东方仿真官网（dongfangfangzhen.com）2026-05-06已下线，国内竞品真空确认。

**硬件开发任务子任务参考**（task_hw_05041523_*）：
- task_hw_05041523_1: 需求定义标准化（老莫）
- task_hw_05041523_2: 方案设计标准化（毛豆）
- task_hw_05041523_3: 仿真验证流程（毛豆）
- task_hw_05041523_6: LookForge嵌入（毛豆）★ 已完成

## 任务队列工作流（重要 — 曾导致分配错误）

渔芯团队使用共享任务库 `/Users/hua/rkr_staging/文档库/3-公司项目资料/团队协作/tasks.db`（**2026-08-10 实测路径**——旧 `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db` 已不存在；存在 5 个 tasks.db 文件，需要按 skill 路径准确引用，详见陷阱F）。

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

**陷阱3：`models/__init__.py` 与 `domain.py` 必须同步（2026-05-13 新增）**
- `domain.py` 定义了 `DesignDraft` 但 `models/__init__.py` 忘了导出 → `ImportError: cannot import name 'DesignDraft'`
- 每次在 `domain.py` 新增类时，**必须同步更新** `models/__init__.py` 的 import 和 `__all__` 列表
- 这是 FastAPI 项目中最常见的运行时错误，排查时先查 `models/__init__.py`

**陷阱4：`generate_development_details()` 仅被 `run_phase2` 调用但生成通用选项**
- `run_phase2` 在第197行调用了它，但 `generate_development_details()` 只生成通用硬件选项（外观设计/控制系统/结构设计/材料工艺/安全合规/功能规格），不结合具体硬件子类型
- 正确做法：Phase6 `run_phase6` 已用 `_build_simulation_cases(hw_subtype, project)` 等方法补充了RAS专项仿真用例，Phase2的通用选项 + Phase6的专项仿真结合使用

**陷阱4：`SimulationService` 算法注册 — 三处必须同步**

在 `simulation_service.py` 中实现 `_sim_xxx()` 算法后，**必须同时在两处注册**，缺一不可：

**注册点A**：`phase_orchestrator.py` → `_build_simulation_cases()` → case 列表
- 添加 `{id, name, applicable_to, description, inputs, outputs, lookforge_workflow}` 条目
- 不注册 → API `GET /api/projects/{id}/phase6` 看不到该用例

**注册点B**：`simulation_service.py` → `_run_single_simulation()` → dispatch if/elif 链
- 添加 `elif case_id == "sim_xxx": return self._sim_xxx(inputs)`
- 不注册 → `POST /api/.../simulation/run` 返回 `{"status": "unknown_case"}`

**已发生的真实场景**：
- `sim_mbbr`/`sim_protein_skimmer` → 算法存在，dispatch 存在，但 case 未在 `_build_simulation_cases` 注册 → API看不到 ✅ 已修复
- `sim_drum_filter` → case 已在 `_build_simulation_cases` 注册，但 `_sim_drum_filter()` 方法和 dispatch 均缺失 → 返回 unknown_case ✅ 2026-05-07已修复

**验证清单**（发现 unknown_case 时的排查顺序）：
```python
# 1. 算法方法存在？
assert "_sim_xxx" in simulation_service_source

# 2. dispatch 注册了？
dispatch = simulation_service_source[simulation_service_source.find("def _run_single_simulation"):]
assert 'case_id == "sim_xxx"' in dispatch

# 3. case 在 _build_simulation_cases 注册了？
orch_source = open(".../phase_orchestrator.py").read()
assert '"sim_xxx"' in orch_source and "_build_simulation_cases" in orch_source
```

**教训**：实现算法和注册用例是**三个独立步骤**（算法实现 + dispatch注册 + case列表注册），只做一项或两项 LookForge 就残缺。

**陷阱5：检查方法** — 确认每个 `run_phaseN` 都实际调用了它声明要做的所有工作，不要只看方法存在。搜索 `generate_development_details` 的所有调用点，确认调用上下文是否符合预期。

**陷阱6：`_build_simulation_cases` 的 `project` 参数未充分利用**
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

## 进化日志格式要求（每次必读）

进化日志路径：`/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/evolution_log.md`（**2026-08-03 第二次迁移后实测位置**——见陷阱F；旧 `/Users/hua/Desktop/渔芯科技/4-部门空间/...` 和 `/Users/hua/rkr_staging/文档库/渔芯项目/4-部门空间/...` 均已不存在）

**输出格式（简洁优先）：**
```markdown
## 进化记录 YYYY-MM-DD HH:MM

### 研究主题：[主题名称]

**核心发现：**
- 发现1（1句话）
- 发现2（1句话）

**具体行动计划：**
- 行动1
- 行动2
```

**要求：**
- 每个发现不超过2句话
- 行动计划必须有具体数字/时间，不能是"继续研究"
- 进化完成后：更新MEMORY.md + 飞书群发【毛豆进化】+ 简要结论（50字内）

**⚠️ Cron模式飞书通知注意：** 禁止对同一target二次send_message，统一走final response。

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

**保存 Checkpoint（毛豆cron在final response前必须执行）**：
```python
import sqlite3, hashlib, json, os

conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
c = conn.cursor()

c.execute("SELECT task_id FROM tasks WHERE status IN ('completed', 'done') ORDER BY done_at DESC")
completed = [r[0] for r in c.fetchall()]
pending = [r[0] for r in c.execute("SELECT task_id FROM tasks WHERE status='pending'").fetchall()]

current_hash = hashlib.md5(",".join(sorted(completed)).encode()).hexdigest()

checkpoint = {
    "completed": completed,
    "pending": pending,
    "hash": current_hash
}

os.makedirs("/Users/hua/.hermes/cron/output", exist_ok=True)
with open("/Users/hua/.hermes/cron/output/last_report.json", 'w') as f:
    json.dump(checkpoint, f)

conn.close()
# ✅ Checkpoint saved. 下次心跳时 hash 比对无变化 → 静默跳过
```

**增量汇报模板**：
- ✅ 新完成：[任务名]（负责人）
- 🔄 新进行：[任务名]（负责人）
- 📋 进行中：共N个任务
