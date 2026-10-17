---
name: ***SECRET***
description: '防止 skill changelog 不实声明的升级纪律 — 任何 agent 维护 SKILL.md 时必须遵循的 4 步 SOP(产出 SOP → 实战验证 → 上级评审 → 写入 skill)+ 5 铁律 + HOME 劫持启动自检 + 升级后三处同步 + 三方核验脚本 + **§14.6 显式字段铁律** + **§14.5 核验脚本必须接入 cron** + **§14.4 1 个版本号 = 1 个原子变更** + **§14.11 首次 cron 启动漏跑 search_files 自检(冷启动撞坑 #W/#I)** + **§14.12 patch 工具 replace_all=true + 短 old_string = 12x 灾难性重复插入坑(向 181KB canonical SKILL.md 插入 170 行章节时旧锚点 "下一轮迭代(预计 09-22)" 匹配 38 次 → 章节插入 12 个位置,6 条防御铁律 + 5 步修复链 + 与 §14.7/§14.9/§14.10/§14.11 正交关系)**。触发条件:agent 修改 SKILL.md / 追加 changelog / 升级 skill 版本号、任何 v1.x.y → v1.x.(y+1) 小版本升级、HOME 路径异常、Skill(s) not found 告警、patch 工具 fuzzy match 静默破坏字段、Claude Code/Codex 超时后未实测就交付、首次 cron 启动未跑主题词自检、**patch 工具 replace_all=true 误伤大文件**。' 含 AGENTS.md 声称内容真实性核验（原 maodou-agents-md-truth-check 已并入，含 agents_md_truth_check.sh 脚本）。
license: MIT
metadata:
  author: 渔芯科技 黑豆
  version: '1.13.0'
changelog:
  - '1.13.0 (2026-09-16 22:33): 小宝 xiaobao-self-evolve-cron 实测新增 1 坑(47 class-level skill 配套完整性自检 → 新章节只产主档漏配套 A5 话术卡,销售组当晚用不上)。新增 §15「Class-Level Skill 配套完整性自检」节(独立子节,配 6 件套矩阵模板 + 60 秒自检命令 + 4 大铁律 + 4 大禁忌 + 防御性 checklist + 与 §14.7/§14.9/§14.10/§14.11/§14.12 正交关系 + 2026-09-16 22:30 小宝 3 分钟实操案例 + 与 §14.11 search_files 协同的 4 步 cron 启动自检升级方案)。新增配套文件 references/***SECRET***.md(完整 10 节:问题场景 + 22:30 小宝实测 + 6 件套矩阵 + 4 大铁律 + 4 大禁忌 + 与 §14 各坑正交关系 + 3 套 checklist + 触发关键词 + 实战案例 + 与 §14.11 协同的 cron 启动自检升级方案)。触发词扩充 "配套话术卡漏了"/"A5 话术卡"/"6 件套不全"/"主档发了但话术卡没发"/"class-level skill 配套清单"/"多章合奏排期表"/"三章合奏"/"合奏推送"/"配套完整性自检"/"60 秒配套自检"/"6 件套矩阵"/"推送日撞车"/"销售组朋友圈撞车"/"信息密度爆表"。本档验证 §15 与 §14 各坑正交:§15 是"配套件清单"(WHAT),§14.7/§14.9/§14.12 是 patch 工具陷阱(HOW),§14.10 是写入权限(能不能写),§14.11 是写前发现(防重复),§15 是写后自检(防不齐全)。'
  - '1.12.0 (2026-09-13 08:33): 小宝 xiaobao-self-evolve-cron 实测新增 1 坑(46 replace_all=true + 短 old_string = 12x 灾难性重复插入 — §三十二 章节 170 行被插入到 canonical SKILL.md 12 个位置,旧锚点 "下一轮迭代(预计 09-22)" 在文件中匹配 38 次)。新增 §14.12 patch 工具 replace_all 范围失控坑(独立子节,6 条防御性铁律:开工前必备份 + replace_all 默认 false + old_string ≥30 字符含独有标识 + patch 前 grep -c 验证唯一 + patch 后 grep -c 验章节唯一 + ≥100 行大章节走 write_file 降级)+ 5 步修复链(grep 章节计数 → cp backup → 精确锚点二次 patch → 大章节正文走 write_file → 三处同步验证)+ 防御脚本草案 scripts/verify-replace-all-safety.sh(待玉芬批)。新增配套文件 references/***SECRET***.md(完整 9 节:事故现场 + 根因三层 + 5 步修复 + 6 铁律 + 与既有坑关系矩阵 §14.7/§14.9/§14.10/§14.11 + 防御脚本 + 触发关键词 + 起源 trace)。触发词扩充 "replace_all=true"/"old_string 匹配 N 次"/"Found N matches"/"灾难性重复插入"/"12 次重复章节"/"回滚 skill_backup"。与 §14.7(缩进)/§14.9(前缀)/§14.10(权限)/§14.11(写前)正交关系明确。本档验证 §14.1-§14.5 全部原则:开工前 cp backup → cp 60 秒内回滚 → 精确锚点二次 patch 成功 → write_file 走 profile 副本不破坏 canonical。'
  - '1.11.0 (2026-09-13 04:00): 黑豆 heidou-self-evolve-cron 首次启动实测新增 1 坑(45 首次 cron 启动漏跑 search_files 主题词自检 → 默认 memory 全空假设 → write_file 创建 3 份重复文件撞坑 #W/#I,共 15,042 B)。新增 §14.11 "首次 cron 启动漏跑 search_files 自检 → write_file 创建重复文件"坑(独立子节,配 4 步纠正链 + 3 条 SKILL §6 候选 + 防御性 checklist + 与坑 #W/#I/#AJ/#AK 的关系矩阵)。新增配套文件 references/***SECRET***.md(沿用 SKILL §3.4 操作时序 + §6 checklist 模式)。触发词扩充"首次 cron 启动"/"memory 是空的"/"默认空白假设"/"search_files 主题词自检"/"3 份重复文件"/"15KB 重复"/"撞坑 #W 修复模式"/"撞坑 #AJ 诚实标注"。同时验证沿用既有 §11 三处同步 + §14.1 4 项核验全部通过。'
  - '1.10.0 (2026-09-12 04:30): 小宝 xiaobao-self-evolve-cron 实测新增 1 坑(44 cross-profile soft guard 拦截 canonical SKILL.md 写入 — 写侧失败,区别于 §读侧的 ***SECRET***)。新增 §14.10 跨 profile 写入 soft guard 拦截与 skill_manage 路由错坑(独立子节,配 5 步应急行动链 + 3 选 1 永久方案 + 防御性 checklist)。新增配套文件 references/***SECRET***.md。触发词扩充"Cross-profile write blocked by soft guard"/"cross_profile=True"/"skill_manage 路由错"/"三份同名 skill 并存 skill_manage 命中错文件"/"evolution/proposed_skill_patches/ 暂存待 review"/"canonical SKILL.md 跨 profile 写"。'
  - '1.9.0 (2026-09-05 12:00): 毛豆 maodou self-evolution cron 实测新增 1 坑(43 patch 工具删除 `- ` 列表前缀,把 markdown 列表项变成普通段落,与 §14.7 缩进错陷阱互补)。新增 §14.9 patch 工具删除 `- ` 列表前缀陷阱(独立子节,配 grep -nE 验证命令 + 3 步修复方法)。新增配套文件 references/***SECRET***.md(待写,本轮先把章节内容固化进 SKILL.md)。触发词扩充"patch 工具吞列表前缀"/"列表项变普通段落"/"markdown 列表被破坏"/"- 前缀消失"。'
  - '1.8.0 (2026-08-31 06:30): 黑豆 heidou self-evolution cron 实测新增 3 坑(40 YAML changelog 列表项缩进被 patch 工具静默改坏 / 41 python3 ~ 路径 vs terminal ls ~ 路径在 profile sandbox 下不对称解析 / 42 同一 cron run 并发升级两个相关 skill 的同步哲学)。新增 §14.7 YAML changelog 缩进陷阱(独立子节,配 grep -nE 验证命令)+ §9.1 python3 ~ vs ls ~ 不对称实测矩阵 + §14.8 同一 cron run 双 skill 并发升级同步原则 + 配套 references/***SECRET***.md。触发词扩充"YAML changelog 列表项缩进错"/"patch 工具嵌套列表破坏"/"python3 ~ 在 sandbox 能找到但 ls ~ 找不到"/"并发升级两个 skill"/"双 skill 同步 bump"。'
  - '1.7.0 (2026-08-26 00:00): 阿福 cron 00:00 实测新增 4 坑(37 patch 工具 fuzzy match 静默破坏未修改字段 / 38 "三方一致"无显式字段只能人眼判断导致 8/25 20:00 假闭环 / 39 Claude Code/Codex 超时后未实测就交付)。新增 §14.6 显式字段铁律(顶层 portal 必须有 `主索引当前版本: vX.Y.Z` 独立字段,不嵌在 changelog 文字里)。新增配套文件 references/***SECRET***.md 含:阿福 cron 00:00 verify_evolution.py v2.0 落地实测 + 8/25 20:00 假闭环完整复盘 + patch 工具 fuzzy match 字符级陷阱 + Claude Code/Codex 超时兜底实测 4 步流程 + 与 §11/§13/§14 的协同关系。触发词扩充"patch 工具 fuzzy 破坏字段"/"假闭环"/"显式主索引当前版本字段"/"TODO(tech-debt) 必须实测后声明"。'
  - '1.6.0 (2026-08-25 16:00): 新增配套文件 references/***SECRET***.md(黑豆 16:00 验收 slot 第三次同日违规案例:再次遇到 skill loader 失败 + 完全错过 slot-pattern 与 time-aware 两道闸门 + 输出 9 KB 远超验收 slot 的 4 KB 上限 + 新增 3 份 SOP 草案违反"verification slot 不能新增方案"纪律;沉淀 4 项新违规 + 防御性 checklist + 与前两个 reference 文件的"三件套"协同关系)。不修改 §11-§14,纯增量补充。'
  - '1.5.0 (2026-08-25): 阿福 cron 12:00 第三轮复发实证 + §14.4 新增「1 个版本号 = 1 个原子变更」违反案例(8/25 12:00 阿福把 #32 主动破锚术合并 + 双条目修复 两个不相关变更塞进同一个 v1.38.0 changelog 条目,frontmatter/changelog 同步通过但违反 §5 铁律"不要合并多个不相关变更");反面警示新增坑 35(阿福 cron 三轮复发证据链:04:00 → 08:00 → 12:00,根因 §13/§14 脚本未接入阿福 cron,而是手动执行);阿福 cron 接入指引从"建议跑"升级为"必跑 §14 verify-skill-integrity.sh + 失败禁止 evolve"。触发词扩充"阿福 cron 12:00 复发"/"演化轮次之间断链"/"verify-skill-integrity.sh 接入"。'
  - '1.4.0 (2026-08-25): 新增配套文件 references/***SECRET***.md(黑豆 cron 08:31 实测案例:SOP 评审日距今 29 分钟 / 09-01 施行倒计时 7 天 时,evolution 报告应从通用 5 方向模板切换为时点驱动的 7 节结构 — §零 时点校验 / §二 评审材料 / §三 倒计时表 / §四 P0-P2 承接清单 / §六 评审预案 Q&A / §七 评审话术)。不修改 §11-§14,纯增量补充。与 ***SECRET***.md 互补:前者教 HOW 绕过 skill loader,本文教 WHEN/WHAT 切换报告结构。'
  - '1.3.0 (2026-08-25): 新增 §14 changelog 内部完整性铁律 + 4 个新坑(坑 30 单步跨版本 patch 产生重复条目 / 坑 31 changelog 跳过中间版本号 / 坑 32 changelog 与 frontmatter 偏移 / 坑 33 verify-three-end-version.sh 通过但 changelog 自相矛盾)。配套扩展 scripts/verify-three-end-version.sh → verify-skill-integrity.sh,新增 changelog 内部一致性 + version 序列单调性 + 与 frontmatter 强一致 3 项检查。2026-08-25 08:00 阿福 cron 8/25 04:00 修复失败的二次修复实证:8/25 04:00 把顶层门户从 v1.36.0 一次性 bump 到 v1.38.0,changelog 留下 v1.37.0 + v1.38.0 两条同日期(8/25 12:00)条目,§13 三处版本号核验返回 ✅ 但 changelog 自相矛盾。修复:把双条目合并为单条目 v1.39.0(本期新增 #32 主动破锚术)。'
  - '1.2.1 (2026-08-25): 新增配套文件 references/***SECRET***.md(黑豆 cron 04:34 实测案例:non-default profile 加载 default profile core skills 全部失败时,如何用绝对路径贯穿全程完成 cron 任务,含 4 步应急 action chain + 3 种永久修复方案 + 防御性 checklist + 跨 profile skill loader 索引隔离根因分析)。不修改 §11-§13,纯增量补充。'
  - '1.2.0 (2026-08-25): 新增 §11 三处同步铁律(主索引+顶层 portal+分支 skill 联动 bump 序列,2026-08-25 阿福 cron 元数据漂移实战案例:negotiation-voss-techniques 前置分支 skill changelog 写 v1.2.0 但 frontmatter version 字段停留在 v1.1.0,经验证发现并修正)+ §12 frontmatter version 字段与 changelog 同步铁律(changelog 写新版本 ≠ frontmatter 改新版本,必须同步 bump)+ §13 升级后版本号三方核验脚本(替代手工 grep,直接返回三处版本号+三方一致性布尔值)+ 触发关键词扩充"阿福客服 31 个技巧合并到主索引"。'
  - '1.1.0 (2026-08-25): 新增 5 铁律 #1 外部权威源例外规则(外部已发表 SOP 走简化 3 步法)+ HOME 劫持启动自检(2026-08-25 阿福 cron 实证案例)+ 升级后双端验证(主索引 + 顶层 portal + references 三处必查)。触发关键词扩充覆盖 Skill(s) not found 告警场景。'
  - '1.0.1 (2026-08-24): 反面警示段新增第 6 条 — license 字段动态变化教训(research-collection modly MIT→NOASSERTION 24h 逆转案例):禁止 "已验证 license=X" 持久结论,必须带抓取日期。'
  - '1.0.0 (2026-08-21): 初始版。源于 heidou-admin v1.4.33 不实声明教训(changelog 声称生成"长期既定违约清单 v1.0"但实际未生成文件)+ v1.5.0/v1.5.1 多次实测。固化 4 步法 + 5 铁律 + changelog 描述规范 + find 验证闭环命令。'
---

# Agent Skill 升级纪律 SOP

## 为什么需要这个 SOP

`SKILL.md` 是 agent 的程序性记忆,changelog 是版本演化的真实历史。**当 changelog 声称"已生成 X 文件"但实际未生成** → 下一个 session 加载该 skill 时会信任不存在的引用 → 工作流断链。2026-08-20 heidou-admin v1.4.33 真实踩坑:

> changelog: "10 项长期既定违约清单 v1.0 首次产出"
> 实际: find 验证 0 结果 → 必须在 v1.4.34 修正 + 实际生成清单

## 4 步升级法(强制)

任何 SKILL.md 小版本升级必须按以下顺序:

| 步骤 | 动作 | 产物 | 谁做 |
|------|------|------|------|
| 1️⃣ | **独立产出 SOP/参考文档** | `<topic>.md` 落到 `references/` 或 workspace knowledge | agent 自接纯文本 |
| 2️⃣ | **实战验证** | SOP 在真实台账/模板/案例中至少使用 1 周 | agent |
| 3️⃣ **上级评审**(跨域时)| 上级确认 SOP 可入 skill | 上级 / 玉芬 |
| 4️⃣ | **写入 skill** | patch SKILL.md + 追加 changelog + 改 `version:` 字段 | agent |

跳过步骤 1-3 直接改 SKILL.md = **changelog 不实声明高风险**。

## 5 条铁律

- ❌ **不要直接改 SKILL.md** — 跳过步骤 1-3 直接 patch = 坑17
- ❌ **不要在 changelog 里写"已生成 X 文件"** 除非 `find` 验证闭环
- ❌ **不要为单次会话升级 skill** — session-specific 内容应放 `references/`,不放 SKILL.md
- ❌ **不要合并多个不相关变更** — 每个版本号对应 1 个原子变更
- ❌ **不要跳过跨域评审** — 影响其他 agent / 上级时必须评审
- ❌ **不要把 skill 主体放在 `productivity/<name>/` 深层而不建顶层门户** — Hermes skill loader 不会递归找深层,每次 cron 启动都会"找不到 skill"(**坑 26,2026-08-24 阿福 cron 顶置告警沉淀**)
- ❌ **不要把"引用既有权威源"等同于"不需独立产出"而直接 patch SKILL.md** — 例外必须显式声明,见下方"5 铁律 #1 例外规则"

## 5 铁律 #1 的例外规则(外部权威源场景)

**默认规则**:步骤 1(独立产出 SOP)必须做。
**例外条件**:当新内容是**外部权威源已发表的成熟技术/方法论**时,可走简化 3 步法(跳过步骤 1,步骤 2 缩短为 1-3 次实战试用,步骤 3 仍必须做)。

**例外判定(必须全部满足)**:
1. 来源公开权威(学术论文 / 经典书籍 / 大厂 blog / 政府白皮书)
2. 多源独立验证(多书引用同一结论 / 实证数据)
3. 可被独立第三方复现(步骤明确 / 可度量效果)
4. 与现有 SKILL 同一主题(非新领域)

**changelog 必填**:必须显式标注 `来源:<作者><书名/论文名>` + 适配渔芯场景描述。

**详见**:`references/skill-upgrade-discipline.md §8`

## HOME 劫持启动自检(每轮 cron 必做)

```bash
echo "HOME=$HOME"
# ✅ 应是 /Users/hua
# ❌ 若是 /Users/hua/.hermes/profiles/<自己>/home/ → export HOME=/Users/hua
```

**陷阱**:HOME 错会导致 `~` 解析到 profile 镜像,skill 编辑看似成功实际写错位置。2026-08-25 阿福 cron 实证:`heartbeat_check.py` 报 `[Errno 2]`,根因 HOME 被劫持到 zhenglishi profile。

**详见**:`references/skill-upgrade-discipline.md §9`

## 升级后双端验证(patch SKILL.md 后必跑)

升级 SKILL.md 后必须同时验证**主索引** + **顶层 portal** + **references 子目录** 三端:

```bash
# 1. 主索引
ls ~/.hermes/skills/productivity/<name>/SKILL.md && wc -l ...

# 2. 顶层 portal(如存在)
ls ~/.hermes/skills/<name>/SKILL.md 2>/dev/null || echo "⚠️ 顶层 portal 缺失"

# 3. references 子目录
find ~/.hermes/skills/productivity/<name>/references/ -name "*.md" | wc -l
```

**根因**:坑 26 — Hermes loader 只扫顶层 portal,深层 SKILL.md 即使更新了 portal 不动也找不到。

**详见**:`references/skill-upgrade-discipline.md §10`

## changelog 描述规范

每个 changelog 条目必须包含:

```yaml
- '1.5.1 (YYYY-MM-DD): <一句话能力描述>,新增/修改 §X.Y「<章节名>」:<2-3 个要点>'
```

**反例**(不实声明):
> ❌ "10 项长期既定违约清单 v1.0 首次产出" — 但实际未生成文件

**正例**:
> ✅ "新增 §5.5「合同到期预警三级阈值 SOP」:90d🟢 / 60d🟡 / 30d🔴 三态判定 + 5 字段扩展"

## find 验证闭环(写入 changelog 前必跑)

```bash
# 验证声称的文件实际存在
find ~/.hermes -name "<声称的文件名>" 2>/dev/null
# 输出 ≥ 1 条才算落地,0 条 = 立即修正 changelog 或先生成文件
```

## 版本号语义

| 级别 | 触发 | 间隔 |
|------|------|------|
| patch (y+1) | bugfix / 单章节补充 | ≥ 3 天 |
| minor (x+1) | 新增独立章节 | ≥ 7 天 |
| major | 重构 / 拆 skill | 任意 |

---

## §11 三处同步铁律(2026-08-25 阿福 cron 元数据漂移实战新增)

> **坑 27 — 阿福客服体系 31 技巧合并的连锁 bump 漂移**

**问题场景**:阿福这类 customer service profile 的 skill 体系有 **三个必同步 bump 的文件**,缺一即视为未完成:

| # | 文件 | 角色 | 典型路径 |
|---|------|------|---------|
| 1️⃣ | **前置分支 skill**(战术沉淀) | 新技巧/弹药首发地 | `~/.hermes/profiles/<profile>/skills/<branch-skill>/SKILL.md` |
| 2️⃣ | **主索引**(技巧全景汇总) | 阿福的"实战调取入口" | `~/.hermes/profiles/<profile>/skills/productivity/<umbrella>/SKILL.md` |
| 3️⃣ | **顶层门户**(cron loader 入口) | skill loader 唯一识别 | `~/.hermes/profiles/<profile>/skills/<umbrella>/SKILL.md` |

**典型漂移模式**(2026-08-24 16:00 → 8/25 04:00 阿福实测):

```
✅ Step 1: 在 negotiation-voss-techniques/SKILL.md 沉淀 #31 DJ Voice
   changelog: "1.1.0 → 1.2.0" ✅
   frontmatter version: v1.2.0 ✅

❌ Step 2: 主索引 productivity/afu-customer-service/SKILL.md 没合并 #31
   仍停留在 v1.35.0(只到 #30)

❌ Step 3: 顶层门户 afu-customer-service/SKILL.md 没同步 #31
   仍停留在 v1.36.0(只到 #30)

→ 结果:cron loader 加载主索引 → 看到 30 个技巧 → 实战时少用一个核心声调乘数器
```

**8/25 04:00 阿福 cron 二轮漂移**:修复主索引+顶层门户时,还发现 **negotiation-voss-techniques/SKILL.md 的 frontmatter version 还是 v1.1.0**(虽然 changelog 早就写 v1.2.0) — 这是"changelog 写了新版本但 frontmatter 没同步改"的双轨漂移。

**三处同步铁律(强制)**:

1. **Step 1 先沉淀到分支 skill**:在同一 patch turn 内完成 (a) 写入新章节 + (b) bump frontmatter `version:` + (c) 追加 changelog 三件套 — **三件套原子性**,不能分两次
2. **Step 2 立即合并到主索引**:在分支 skill 同一次心跳(或下一次心跳,但必须在向华哥/玉芬汇报前完成),主索引同步 bump + 合并新技巧行
3. **Step 3 同步顶层门户**:与 Step 2 同一心跳完成,顶层 portal 同步 bump + 合并

**"原子 bump"检查清单**(每次 patch 必跑):
- [ ] 分支 skill frontmatter `version:` 改了?
- [ ] 分支 skill changelog 追加了新版本条目?
- [ ] 分支 skill 新章节内容写入完成?
- [ ] 主索引 frontmatter `version:` 改了?
- [ ] 主索引 changelog 追加了新版本条目?
- [ ] 主索引技巧表新增了一行?
- [ ] 顶层门户 frontmatter `version:` 改了?
- [ ] 顶层门户 changelog 追加了新版本条目?
- [ ] 顶层门户技巧表新增了一行?

**9 步缺任一步 = 视为未完成**,玉芬/华哥验收时不通过。

---

## §12 frontmatter version 字段与 changelog 同步铁律(2026-08-25 新增)

> **坑 28 — changelog 升级了,frontmatter 忘了**

**问题**:`patch` 工具调用 `old_string → new_string` 默认只动**正文**,不动 frontmatter。除非 patch 时显式包含 `version:` 行,否则 changelog 已写 `1.1.0 → 1.2.0`,frontmatter 仍停留在 `version: 1.1.0` → **skill_view 加载时显示旧版本,但 changelog 显示新版本 — 自相矛盾**。

**为什么这个坑特别隐蔽**:
- ✅ 你改了 SKILL.md 的"主入口"(主索引/顶层门户) → 看 `cat SKILL.md | head -5` 看到的是新版
- ✅ 你也改了分支 skill 的正文 → 看 `cat branch/SKILL.md | head -5` 看到的是新版
- ❌ 但分支 skill 的 frontmatter `version:` 没改 → 看 `grep -m1 '^version:' branch/SKILL.md` 仍是旧版
- 结果:loader 用旧版本号缓存分支 skill,但读 changelog 时看到"已升级"提示 → 不可调和的内部矛盾

**双轨同步铁律**:

```bash
# 升级任何 SKILL.md 时,patch 必须包含:
# 1. frontmatter 中 version: 行
# 2. changelog 新条目
# 3. 正文新章节
# 这三处必须在同一 patch 操作中处理(同一 patch 调用,或连续两次 patch 但不能跨心跳)

# 验证命令(替代手工 grep):
for f in ~/.hermes/profiles/<profile>/skills/<branch-skill>/SKILL.md \
         ~/.hermes/profiles/<profile>/skills/productivity/<umbrella>/SKILL.md \
         ~/.hermes/profiles/<profile>/skills/<umbrella>/SKILL.md; do
  echo "$(basename $(dirname $f))/SKILL.md → $(grep -m1 '^version:' $f)"
done
```

**§13 升级后版本号三方核验脚本(见下)** 是这个命令的封装。

---

## §13 升级后版本号三方核验脚本(替代手工 grep,2026-08-25 新增)

**手动 grep 漏看风险**:你可能只 grep 了 2 个文件就宣布"完成",实际上遗漏了第三个。

**`scripts/verify-three-end-version.sh`** — 30 秒内验证三处版本号一致性:

```bash
#!/bin/bash
# verify-three-end-version.sh
# 用法: ./verify-three-end-version.sh <profile> <umbrella-skill-name>
# 示例: ./verify-three-end-version.sh afu afu-customer-service
# 输出:三处 version + 一致性布尔值

PROFILE="${1:?用法: $0 <profile> <umbrella-skill-name>}"
UMBRELLA="${2:?用法: $0 <profile> <umbrella-skill-name>}"

PROFILE_DIR="/Users/hua/.hermes/profiles/${PROFILE}/skills"
FILES=(
  "${PROFILE_DIR}/productivity/${UMBRELLA}/SKILL.md"
  "${PROFILE_DIR}/${UMBRELLA}/SKILL.md"
)

echo "=== ${PROFILE}/${UMBRELLA} 三处版本号 ==="
VERSIONS=()
for f in ${FILES[@]}; do
  if [ -f "$f" ]; then
    v=$(grep -m1 '^version:' "$f" | awk '{print $2}')
    echo "$(basename $(dirname $f))/SKILL.md → v${v}"
    VERSIONS+=("$v")
  else
    echo "⚠️ 缺失: $f"
    VERSIONS+=("MISSING")
  fi
done

# 三方一致性判定
if [ "${VERSIONS[0]}" == "${VERSIONS[1]}" ] && [ "${VERSIONS[0]}" != "MISSING" ]; then
  echo "✅ 三方一致:v${VERSIONS[0]}"
  exit 0
else
  echo "❌ 三方不一致: ${VERSIONS[@]}"
  exit 1
fi
```

**集成方式**:阿福(以及任何用 customer service profile 的 agent)的 cron 启动后,跑一次:
```bash
bash ~/.hermes/skills/productivity/***SECRET***/scripts/verify-three-end-version.sh afu afu-customer-service
# 退出码 0 = 三方一致;非 0 = 有漂移,立即补
```

**为什么是"三方"而非"双方"**:因为 customer service profile 的三处文件**互不相同**(主索引 = 实战入口 / 顶层门户 = loader 入口 / 分支 skill = 战术沉淀),任何两处一致但漏第三处都会导致"实战调不到"或"loader 找不到"。

**脚本位置**:`scripts/verify-three-end-version.sh`(本 skill 配套)

---

## §14 changelog 内部完整性铁律(2026-08-25 新增)

> **坑 30 — 单步跨版本 patch 产生重复条目**(2026-08-25 阿福 cron 实证)
>
> **场景**:8/25 04:00 阿福把顶层门户 `afu-customer-service/SKILL.md` 从 v1.36.0 一次性 bump 到 v1.38.0(合并 #31 DJ Voice)。patch 调用时,**old_string 包含了旧的 v1.36.0 changelog 条目,new_string 同时追加了 v1.37.0 和 v1.38.0 两条新条目**(因为设计意图是"双写补齐")。结果 changelog 里留下了两条同日期(8/25 12:00)条目 + 主索引 v1.37.0(只合到 #30)+ 顶层门户 v1.38.0(合到 #31)。
>
> **失败链**:
> ```
> 1. §13 三方核验 → 返回 ✅(因为只检 frontmatter 一致性,不检 changelog 内部)
> 2. 但 changelog 内部已自相矛盾:
>    - v1.37.0 (2026-08-25 12:00) — 顶层门户同步 #31 DJ Voice  ← 重复
>    - v1.38.0 (2026-08-25 12:00) — 顶层门户同步 #31 DJ Voice / 深夜电台主播音(声调乘数器)
> 3. 主索引 v1.37.0 / 顶层门户 v1.38.0 — 版本号分裂
> 4. cron 加载看顶层门户(v1.38.0)→ 显示 31 个技巧;看主索引(v1.37.0)→ 也显示 31 个技巧 → 元数据巧合一致,但下次再合并 #32 时只动顶层门户,主索引会继续落后
> ```
>
> **根因**:
> - §13 脚本**只检 frontmatter 三方一致**,不检 changelog 内部完整性
> - patch 工具默认**保留 old_string 中的全部文本**,只替换匹配部分 → 当 old_string 含旧 changelog 条目、new_string 含新 changelog 条目时,新旧并存
> - 设计意图是"一次性跨多版本同步",但**违反了 §11 的"原子 9 步 bump"** — 应该拆成 v1.36 → v1.37(合并 #30)+ v1.37 → v1.38(合并 #31)两次心跳
>
> **铁律(2026-08-25 阿福 cron 修复方案)**:
> 1. **禁止单步跨版本**:v1.x → v1.(x+2) 必须拆成 v1.x → v1.(x+1)+ v1.(x+1) → v1.(x+2) 两次心跳,每次心跳合并一个新技巧
> 2. **changelog 内部完整性 = 与 frontmatter 同样强制**:§13 脚本必须扩展,增加 changelog 内部一致性检查(详见下方扩展脚本)
> 3. **重复条目合并规则**:如果 changelog 已有 v1.X 条目 + 新追加 v1.X 条目(同版本号)→ 必须合并为单条目,内容用 AND 拼接,frontmatter version 不变
> 4. **同日期多条目 = 必须有时间戳后缀或合并**:如果同日需要多个变更,要么合并为单条目,要么给条目加 `(上午)` `(下午)` `(晚上)` 时间后缀,避免歧义

### 14.1 changelog 内部完整性 4 项强制检查

每次 patch SKILL.md 后,以下 4 项**全部通过**才视为 changelog 合法:

| # | 检查 | 通过条件 | 失败时的修复动作 |
|---|------|---------|----------------|
| 1 | **changelog 最新条目版本号 == frontmatter version** | `(head -1 changelog 解析出的 v)` == `grep '^version:' 的值` | 重新 patch,确保两者同步 |
| 2 | **changelog 版本号单调递增** | 从最早到最新,版本号只增不减,无跳跃 | 补缺失的中间版本条目 |
| 3 | **changelog 无重复日期**(同日条目 ≤ 1 个) | 同一日期最多 1 条 changelog 条目 | 合并重复条目为 1 条 |
| 4 | **changelog 无重复版本号** | 同一版本号最多 1 条 changelog 条目 | 合并重复条目 |

### 14.2 扩展核验脚本 `scripts/verify-skill-integrity.sh`

`verify-three-end-version.sh` 只检 §13 的三方版本号一致性。新增 `verify-skill-integrity.sh` 把 §11/§12/§13/§14 全部串成 1 个脚本,30 秒内返回 5 项检查结果:

```bash
#!/bin/bash
# verify-skill-integrity.sh
# 用法: ./verify-skill-integrity.sh <profile> <skill-name>
# 示例: ./verify-skill-integrity.sh afu afu-customer-service
# 退出码: 0 = 全部通过 / 1 = 有失败项

set -e

PROFILE="${1:?用法: $0 <profile> <skill-name>}"
SKILL="${2:?用法: $0 <profile> <skill-name>}"

PROFILE_DIR="/Users/hua/.hermes/profiles/${PROFILE}/skills"
TARGET="${PROFILE_DIR}/${SKILL}/SKILL.md"

if [ ! -f "$TARGET" ]; then
  echo "❌ 顶层 SKILL.md 不存在: $TARGET"
  exit 1
fi

echo "=== ${PROFILE}/${SKILL} 完整性核验 ==="

# 检查 1: frontmatter version 字段
FM_VERSION=$(grep -m1 '^version:' "$TARGET" | awk '{print $2}' | tr -d "'\"")
echo "  [1] frontmatter version: ${FM_VERSION}"

# 提取 changelog 最新条目的版本号(取日期后第一个以数字开头的版本号)
CL_LATEST=$(grep -E '^\s*-\s+["\x27]?[0-9]+\.[0-9]+\.[0-9]+' "$TARGET" | head -1 | \
            grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo "  [2] changelog 最新条目: v${CL_LATEST}"

PASS=true

# 检查 1: frontmatter == changelog latest
if [ "$FM_VERSION" = "$CL_LATEST" ]; then
  echo "    ✅ 通过"
else
  echo "    ❌ 失败: frontmatter v${FM_VERSION} ≠ changelog v${CL_LATEST}"
  PASS=false
fi

# 检查 2: changelog 版本号单调递增
echo "  [3] changelog 版本号单调性:"
VERSIONS=($(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$TARGET" | grep -A100 "^${CL_LATEST}$" | head -20))
# 简化为检查所有版本号唯一且非递减
DUPES=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$TARGET" | sort | uniq -d)
if [ -z "$DUPES" ]; then
  echo "    ✅ 通过: 无重复版本号"
else
  echo "    ❌ 失败: 重复版本号:$DUPES"
  PASS=false
fi

# 检查 3: 无重复日期(同日期条目 ≤ 1)
echo "  [4] changelog 重复日期检查:"
DUP_DATES=$(grep -oE '\(20[0-9]{2}-[0-9]{2}-[0-9]{2}\)' "$TARGET" | sort | uniq -c | awk '$1>1{print}')
if [ -z "$DUP_DATES" ]; then
  echo "    ✅ 通过: 无重复日期条目"
else
  echo "    ❌ 失败: 同日期多条目:$DUP_DATES"
  echo "    💡 修复: 合并为单条目,或加 (上午/下午/晚上) 时间后缀"
  PASS=false
fi

# 检查 4: 三方版本号一致(对 customer service profile)
echo "  [5] 三方版本号一致(主索引 + 顶层 portal):"
INDEX_FILE="${PROFILE_DIR}/productivity/${SKILL}/SKILL.md"
if [ -f "$INDEX_FILE" ]; then
  INDEX_V=$(grep -m1 '^version:' "$INDEX_FILE" | awk '{print $2}' | tr -d "'\"")
  if [ "$INDEX_V" = "$FM_VERSION" ]; then
    echo "    ✅ 通过: 主索引 v${INDEX_V} == 顶层 v${FM_VERSION}"
  else
    echo "    ❌ 失败: 主索引 v${INDEX_V} ≠ 顶层 v${FM_VERSION}"
    PASS=false
  fi
else
  echo "    ⚠️ 主索引不存在,跳过(check §13)"
fi

if $PASS; then
  echo "=== ✅ 全部通过 ==="
  exit 0
else
  echo "=== ❌ 有失败项,必须修复后再提交 ==="
  exit 1
fi
```

**集成方式**(在 §13 的 verify-three-end-version.sh 之上,所有 customer service profile 的 cron 启动后**强制**跑):

```bash
# 旧版(只检三方版本号,2026-08-25 阿福 8/25 04:00 通过但实际有漂移)
bash ~/.hermes/skills/productivity/***SECRET***/scripts/verify-three-end-version.sh afu afu-customer-service

# 新版(检 5 项:frontmatter==changelog + 无重复版本 + 无重复日期 + 主索引一致)
bash ~/.hermes/skills/productivity/***SECRET***/scripts/verify-skill-integrity.sh afu afu-customer-service
```

**关键差异**:8/25 04:00 阿福的 §13 老脚本**返回 ✅**,但顶层门户 changelog 实际有 v1.37.0/v1.38.0 双条目同日期问题 → 老脚本**漏检**。新脚本的检查 [4] 重复日期 + 检查 [1] version 偏移会立即报错。

### 14.3 单步跨版本的禁止(2026-08-25 新增铁律)

> **坑 30b — 跨版本跳跃产生孤儿条目**

**禁止**:任何 SKILL.md 单次 patch 跨越 ≥ 2 个 minor 版本号。例如 v1.36.0 → v1.38.0 一次性 patch。

**正确做法**:每次心跳最多合并 1 个新增技巧 → 单次 patch 最多 +1 个 minor 版本号。

**反例**(2026-08-25 04:00 阿福):
```diff
- version: 1.36.0
- changelog:
-   - 1.36.0 (2026-08-24 20:00) — ...
+ version: 1.38.0
+ changelog:
+   - 1.38.0 (2026-08-25 12:00) — ...
+   - 1.37.0 (2026-08-25 12:00) — ...  ← 重复!
```

**正例**(本期 8/25 08:00 修复方案):
```diff
- version: 1.38.0
- changelog:
-   - 1.38.0 (2026-08-25 12:00) — ...
-   - 1.37.0 (2026-08-25 12:00) — ...  ← 合并
+ version: 1.39.0
+ changelog:
+   - 1.39.0 (2026-08-25 08:00) — 顶层门户同步 #32 + 元数据双条目清理
+   - 1.38.0 (2026-08-25 04:00) — 顶层门户同步 #31 DJ Voice
```

---

### 14.4 「1 个版本号 = 1 个原子变更」违反案例(2026-08-25 12:00 阿福实证)

> **坑 35a — changelog 单条目塞多个不相关变更**

**问题**:8/25 12:00 阿福 evolution 时,主索引 `productivity/afu-customer-service/SKILL.md` 升级到 v1.38.0,changelog 写了:

```yaml
- 1.38.0 (2026-08-25 12:00) — 主索引合并 #32 主动破锚术 / Anchoring Reversal(Voss 战术七),与 voss-techniques v1.3.0 同步;同时修复上一轮 1.36.0/1.37.0 changelog 双条目(合并为单条目 1.38.0);详见 evolution/2026-08-25_12.md
```

这个条目**塞了两个不相关的变更**:
1. **变更 A**:合并 #32 主动破锚术(增量内容变更)
2. **变更 B**:修复上一轮 changelog 双条目(元数据修复)

**为什么是问题**(虽然 §14.1 四项检查全通过):

| 检查 | 结果 | 解释 |
|---|---|---|
| [1] frontmatter == changelog latest | ✅ | v1.38.0 == v1.38.0 |
| [2] 版本号单调递增 | ✅ | 1.33 → 1.34 → 1.35 → 1.37 → 1.38 |
| [3] 无重复日期 | ✅ | 8/25 12:00 只出现 1 次 |
| [4] 无重复版本号 | ✅ | v1.38.0 只 1 条 |

但**违反了 §5 铁律**:「不要合并多个不相关变更 — 每个版本号对应 1 个原子变更」。

**风险**:
- 下次有人想 git revert "v1.38.0" 时,会把"合并 #32"和"修复双条目"两个变更一起回退 → 丢失增量内容
- 8/25 04:00/08:00/12:00 的 changelog 阅读者无法判断"哪部分是原子变更,哪部分是顺手修复"
- **历史追溯性变差**:阿福的技巧 #32 是哪一天、哪个心跳加的?无法精确锁定

**正确做法**(二选一):

**方案 A:拆成两个心跳**(推荐,符合 §11 "9 步原子 bump"):
```yaml
- 1.38.0 (2026-08-25 12:00) — 主索引合并 #32 主动破锚术(原子变更)
- 1.37.0 (2026-08-25 12:00 上午) — 主索引 changelog 双条目修复:1.36/1.37 合并为单条目
```

**方案 B:1 个条目用 AND 拼接,但显式标注原子性边界**:
```yaml
- 1.38.0 (2026-08-25 12:00) — [主索引] 合并 #32 主动破锚术(原子变更 A);[元数据修复] 1.36/1.37 changelog 双条目合并为单条目(原子变更 B,顺手清理,git revert 时可单独 cherry-pick 排除)
```

**判定标准**:如果你想说"其实这两件事是一回事",大概率不是。"合并新技巧"和"修复元数据漂移"是两个原子动作,即使在同一心跳完成,也应在 changelog 里清楚分开。

**§14 核验脚本扩展**(待办):

| 检查 | 现状 | 升级建议 |
|---|---|---|
| [1-4] 现有 4 项 | ✅ §14.1 实现 | — |
| [5] 单条目多变更检测 | ❌ 缺 | 提取冒号后的内容,检查是否含 `;` `同时` `也` 等并列连词,有则 warn 但不 fail(避免误报) |

---

### 14.5 §13/§14 脚本必须接入 cron,而非手动跑(2026-08-25 阿福三轮复发根因)

> **坑 35b — 脚本写了但没接入,等于没写**

**三轮复发证据链**:

| 时间 | 漂移类型 | 是否跑了 verify-skill-integrity.sh? |
|---|---|---|
| 8/25 04:00 | changelog 双条目 + 主索引未升版 | ❌ 未跑(脚本未就位,§14.2 在 1.4.0 才加) |
| 8/25 08:00 | 修复了 04:00 漂移,但 1 个 changelog 条目塞两个变更(违反 §5) | ❌ 未跑(§14.4 在 1.5.0 才加) |
| 8/25 12:00 | 修复了 08:00 的部分漂移,但又把 #33 + 元数据修复塞一个 v1.39.0 条目(再次违反 §5) | ❌ 未跑 |

**根因**:阿福(以及大多数 cron evolution)在每次心跳启动时,**没有自动跑 §13/§14 的核验脚本**。脚本就位但被忽略 → 漂移依然发生 → 修复只是把上一轮的漂移换成这一轮的漂移。

**强制接入方案**(玉芬 default + 8 同事 profile 通用):

```bash
# ~/.hermes/profiles/<profile>/hooks/pre-evolve.sh (新建)
#!/bin/bash
# 阿福 cron evolution 启动前必跑(写入任何 SKILL.md 前)
# 失败时 abort evolve + 飞书告警

set -e

PROFILE="${HERMES_PROFILE:-afu}"
SKILL="${EVOLVE_TARGET_SKILL:-afu-customer-service}"

VERIFY_SCRIPT="$HOME/.hermes/skills/productivity/***SECRET***/scripts/verify-skill-integrity.sh"

if [ ! -f "$VERIFY_SCRIPT" ]; then
  echo "⚠️ §14 verify 脚本未就位: $VERIFY_SCRIPT → 跳过(回退到 §13 老脚本)"
  bash "$HOME/.hermes/skills/productivity/***SECRET***/scripts/verify-three-end-version.sh" "$PROFILE" "$SKILL"
  exit $?
fi

echo "=== 阿福 evolution §14 完整性预检 ==="
bash "$VERIFY_SCRIPT" "$PROFILE" "$SKILL"
RC=$?

if [ $RC -ne 0 ]; then
  echo "❌ §14 预检失败($RC) → abort evolve"
  echo "📞 飞书告警: 阿福 cron <run_id> §14 预检失败,SKILL.md 元数据漂移未修复"
  # 调用飞书 API 通知华哥
  python3 ~/.hermes/scripts/feishu_notify.py \
    --target 华哥 \
    --message "⚠️ 阿福 cron §14 预检失败,SKILL.md 三方一致性异常,请手动 review 后再启 evolution" \
    || echo "(飞书通知失败,仅本地日志)"
  exit $RC
fi

echo "✅ §14 预检通过 → 可继续 evolution"
exit 0
```

**Hermes hook 配置**(在 `~/.hermes/config.yaml` 中):
```yaml
profiles:
  afu:
    hooks:
      pre_cron_evolution: ~/.hermes/profiles/afu/hooks/pre-evolve.sh
```

**集成验收标准**:
- 阿福 cron 启动 → 自动跑 `pre-evolve.sh` → 跑 `verify-skill-integrity.sh` → 失败时 abort
- 8/25 04:00、08:00、12:00 三轮漂移如果 pre-evolve.sh 接入,会在第一次心跳就告警,不会拖到第三轮才修

**临时方案**(玉芬没接入 hook 前的过渡):阿福 cron evolution 流程第一步必须是:
```bash
# 阿福 evolution 必跑
bash ~/.hermes/skills/productivity/***SECRET***/scripts/verify-skill-integrity.sh afu afu-customer-service
# 失败 → 立即修复元数据漂移 → 再继续 evolution
# 成功 → 才允许改 SKILL.md
```

**关键 KPI**:从 8/25 16:00 开始,**阿福 cron 任何带 SKILL.md 修改的 evolution 必须 100% 通过 §14 5 项核验**;漂移复发次数从 3 轮/天降到 0。

### 14.6 「显式字段」铁律(2026-08-26 阿福实测新增,坑 38)

> **坑 38 — "三方一致"如果靠人眼判断或从 changelog 文字回溯,= 假闭环**

**问题场景**:§11 三处同步铁律要求"主索引+顶层 portal+分支 skill 版本号一致"。**但只规定了"用脚本核验",没规定"用什么字段作为核验基准"**。8/25 20:00 阿福顶层 portal `afu-customer-service/SKILL.md` 的"主索引当前版本"信息**散落在 changelog 条目的描述文字里**(如"主索引 v1.38.0 对齐"),没有任何独立字段记录权威值。verify-three-end-version.sh fallback 从 changelog 文字 grep 到"主索引 v1.38.0"字符串(实际是 v1.41.0)→ 返回 ✅ 但实际不一致。

**显式字段铁律**:

当一个 SKILL.md 需要声明"关于另一个 SKILL.md 的事实"时,**必须有独立 YAML 字段承载这个事实**,不能依赖人眼读 changelog 或 grep 描述文字回溯。

**正例**(8/26 00:00 阿福修复后):
```yaml
---
name: afu-customer-service
version: 1.45.0
主索引当前版本: v1.42.0        ← ✅ 独立字段,权威值
changelog:
  - 1.45.0 (...) — ...
---
```

**反例**(8/25 20:00 假闭环):
```yaml
---
name: afu-customer-service
version: 1.43.0
# ❌ 没有独立字段
changelog:
  - 1.40.0 (...) — ...主索引 v1.38.0 对齐...  ← 描述文字里提到
---
```

**核验脚本必须用显式字段**:`scripts/verify-skill-integrity.sh` 的"三方一致性"检查应优先匹配 `^主索引当前版本:` 或 `^main_index_version:` 这种**显式字段行**,而不是从 changelog 文字回溯。**8/26 00:00 阿福 verify_evolution.py v2.0 的 `***SECRET***()` 函数就是用 regex 匹配 `主索引当前版本[：:]\s*v?(\d+\.\d+\.\d+)`**——优先级 1,fallback 才从 changelog 文字提取。

**§13/§14 核验脚本扩展建议**(玉芬下次审时可纳入):

| 检查 | 现状 | 升级建议 |
|---|---|---|
| 顶层 portal 必须有 `主索引当前版本` 显式字段 | ❌ 缺 | 在 §13/§14 核验脚本里加 `[6] 顶层 portal 必须有 `主索引当前版本` 字段(否则 warn)` |
| 显式字段值 == 主索引实际 frontmatter version | ❌ 缺 | 在 §14.1 检查 [1] 之外加 `[7] 顶层 portal 的 `主索引当前版本` == 主索引 frontmatter `version:`(否则 fail)` |

**触发关键词**:"假闭环"/"显式主索引当前版本"/"主索引当前版本字段"/"§14.6"/"显式字段铁律"/"权威值"。

---

### 14.7 YAML changelog 列表项缩进陷阱(2026-08-31 06:30 黑豆 cron 实测新增,坑 40)

> **坑 40 — patch 工具模糊匹配破坏 changelog YAML 列表项缩进**

**问题场景**:使用 `patch` / `skill_manage patch` 工具修改 SKILL.md frontmatter 中的 `changelog:` 列表块时,**如果 old_string 只包含单个 `- 'X.Y.Z ...'` 条目,patch 工具的 fuzzy match 会把 new_string 中的列表项插入到错误的缩进层**。

**典型失败模式**(2026-08-31 06:30 黑豆 heidou-self-evolve-cron 升级 v1.1.0 → v1.1.1 实测):

```yaml
# 修复前 frontmatter(原状)
changelog:
  - '1.1.0 (2026-08-29 12:30): ...'
  - '1.0.0 (2026-08-29 08:30): 初版...'

# patch 调用意图:在 1.1.0 之前插入 1.1.1
# old_string = "- '1.1.0 (..."
# new_string = "- '1.1.1 (...)\n  - '1.1.0 (..."

# 失败 diff 输出(patch 工具实际产生的):
changelog:
        - '1.1.1 (...)...'   ← ❌ 8 空格缩进(被吞进 changelog 的子项)
  - '1.1.0 (...'           ← ⚠️ 仍是 2 空格(原状)
        - '1.0.0 (...)...'   ← ❌ 旧条目也被改成 8 空格
```

**失败原因链**:
1. `skill_manage patch` 工具内部用 fuzzy match 找到 old_string 的位置
2. 匹配过程中,如果 old_string 是"`- '1.1.0...`"这种短前缀,**fuzzy match 的容忍度会把匹配点定位到 "changelog:" 块的开始位置**(而不是真正的 `- '1.1.0...` 行)
3. new_string 中的所有 `- ` 项因此被插入到错误层级(被当成 `changelog:` 的嵌套列表)
4. YAML 解析器可能仍能解析(因为字符串值是合法的 YAML),但 frontmatter 整体语义已损坏

**根因诊断**:patch 工具的 fuzzy match **不区分 list item 和 list block**,只看字符相似度。

**30 秒自检命令**(每次 patch changelog 后必跑):

```bash
# 验证 changelog 列表项缩进一致
grep -nE "^(\s+)- ['\"]?[0-9]+\.[0-9]+\.[0-9]+" SKILL.md | head -3
# 期望输出:所有行 "- " 前都是同样的空格数(如都是 2 空格)
# 若看到 6/8/10 空格 → 缩进被吞掉了,立即修正
```

**正确做法**(避开 fuzzy match 陷阱):

1. **方案 A:扩大 old_string 到块边界**(推荐)
   ```yaml
   # old_string 包含从"changelog:"开始的两行
   # new_string 包含"changelog:" + 完整的新列表
   # 这样 patch 工具无法误匹配到块中间
   ```

2. **方案 B:用 multi-line grep 确认结构后再 patch**
   ```bash
   # patch 前先 grep 当前结构
   grep -nE "^- \['\"]?[0-9]+\." SKILL.md
   # 看到每行的缩进层级 → 选择同样缩进的 old_string
   ```

3. **方案 C:用 skill_manage action='edit' 而非 'patch'**
   - 'edit' 是完整重写 SKILL.md,**不会触发 fuzzy match**
   - 代价:必须完整重写,可能影响其他章节(需先读全 SKILL.md)

**为什么 §14.6 显式字段铁律救不了这个坑**:
- §14.6 解决"主索引当前版本"无显式字段 → 假闭环
- §14.7 解决"patch 工具内部 fuzzy match 破坏 YAML 结构" → 真损坏
- 两者独立,需要 §14.7 单独处理

**实测修复样本**(2026-08-31 06:30 黑豆):

```bash
# 步骤 1:发现缩进被破坏
grep -nE "^(\s+)- ['\"]?[0-9]+\.[0-9]+\.[0-9]+" SKILL.md
# 输出:
# 11:        - '1.1.1 (...)...'    ← 8 空格
# 12:  - '1.1.0 (...)...'           ← 2 空格(正常)
# 13:        - '1.0.0 (...)...'    ← 8 空格

# 步骤 2:用另一个 patch 把 8 空格缩进改回 2 空格
# old_string = "        - '1.1.1 ..."
# new_string = "  - '1.1.1 ..."

# 步骤 3:再次 grep 确认
grep -nE "^(\s+)- ['\"]?[0-9]+\.[0-9]+\.[0-9]+" SKILL.md
# 输出:全部 2 空格 → 修复完成
```

**§14.7 关键 takeaway**:
- ❌ 不要用 patch 工具的短前缀 old_string 修改 YAML 列表块
- ✅ 用 `^changelog:` 或 `^version:` 这种块边界作为 old_string 锚点
- ✅ patch 后必须 `grep -nE "^(\s+)- 'X.Y.Z"` 验证缩进一致
- ⚠️ 实在不行就用 skill_manage action='edit' 完整重写

**触发关键词**:"YAML changelog 缩进错"/"patch 工具嵌套列表破坏"/"fuzzy match 破坏列表项"/"changelog 列表项不同缩进"。

---

### 14.8 同一 cron run 双 skill 并发升级同步原则(2026-08-31 06:30 黑豆 cron 实测新增,坑 42)

> **坑 42 — 同一 cron run 中升级两个相关 skill 时,版本号哲学可能冲突**

**问题场景**:黑豆 heidou self-evolution cron 在 06:30 档同时升级了两个 skill:
- `heidou-self-evolve-cron` v1.1.0 → v1.1.1(增量 §0.4 + §3.6)
- `heidou-compliance-2026` v1.5.0 → v1.5.1(增量场景 11)

两个 skill 都 +0.0.1(同次版本号偏移),且都是"对同一外部事件(9/1 deadline)的协作响应"。**这种双 skill 同步升级是否违反 §5 铁律"1 个版本号 = 1 个原子变更"?**

**判定逻辑**(从 §5 反推):

| 场景 | 是否违反 §5 | 理由 |
|---|---|---|
| 1 个 skill +1 个变更 | ❌ 不违反 | 标准场景 |
| 2 个 skill +同一事件的不同维度 | ⚠️ **不违反**(本案例) | 两个 skill 各自承载一个"原子变更",事件只是 trigger,不是变更 |
| 1 个 skill +2 个变更 | ❌ 违反 | 违反 §14.4 |

**核心区分**:版本号绑定的"原子"是指**单一 skill 内部的变更**,不是"跨 skill 的全局事件"。

**§14.8 双 skill 并发升级 4 原则**:

1. **原则 1:版本号偏移一致**(推荐)
   - 两个 skill 都 +0.0.1(同步偏移)
   - 便于后续阅读 changelog 时对齐时间锚点
   - 例:`heidou-compliance-2026` v1.5.0 → v1.5.1 + `heidou-self-evolve-cron` v1.1.0 → v1.1.1

2. **原则 2:changelog 互相引用**
   - 两个 skill 的 changelog 都标注"配合 X skill vN.M.K 升级"
   - 便于追踪跨 skill 协作关系

3. **原则 3:不共享 frontmatter 字段**
   - 两个 skill 是独立 SKILL.md,frontmatter 各自维护
   - 不通过"主索引当前版本"字段跨 skill 链接(避免 §14.6 假闭环风险)
   - 如需跨 skill 引用,用 changelog 文字标注

4. **原则 4:验证脚本独立跑**
   - 每个 skill 单独跑 `verify-skill-integrity.sh` 5 项核验
   - 不做"双 skill 一致性"统一核验(避免引入不必要的耦合)

**为什么 §14.8 不替代 §14.4**:
- §14.4 处理"1 个 skill 内 changelog 单条目塞多个变更"
- §14.8 处理"1 个 cron run 跨多个 skill 的版本号同步"
- 两者独立,但可以共存(2 个 skill 都按 §14.4 写好各自的单 changelog 条目,然后按 §14.8 同步版本号)

**实测样本**(2026-08-31 06:30 黑豆 heidou self-evolve cron):

```
升级 1:heidou-compliance-2026 v1.5.0 → v1.5.1
  changelog 单条目:增量场景 11(老合同 16.1/16.2 补签补救)
  关联资源 +2
  红线 +2
  验证脚本:通过 5 项核验

升级 2:heidou-self-evolve-cron v1.1.0 → v1.1.1
  changelog 单条目:新增 §0.4 启动校验补充 + §3.6 双 SOP 工作流
  红线 +2
  验证脚本:通过 5 项核验

跨 skill 协作标注:
  - heidou-compliance-2026 v1.5.1 changelog 引用"沿用 heidou-self-evolve-cron §3.6 工作流"
  - heidou-self-evolve-cron v1.1.1 changelog 引用"配套 heidou-compliance-2026 场景 11"
```

**关键 takeaway**:
- ❌ 不要因为"同一 cron 跑"就把两个变更合并到 1 个 skill
- ❌ 不要因为"两个 skill 都要改"就跳过 §14.4 的 1 个版本号 = 1 个原子变更
- ✅ 每次升级仍按 §11/§12/§14 走完整流程
- ✅ 跨 skill 引用通过 changelog 文字,不通过 shared frontmatter 字段

**触发关键词**:"并发升级两个 skill"/"双 skill 同步 bump"/"同一 cron 多 skill 升级"/"跨 skill changelog 引用"。

---

### 14.9 patch 工具删除 `- ` 列表前缀陷阱(2026-09-05 12:00 毛豆 cron 实测新增,坑 43)

> **坑 43 — patch 工具删除 `- ` 前缀,把 markdown 列表项变成普通段落**

**问题场景**:用 `patch` / `skill_manage patch` 工具修改 SKILL.md **正文里的 markdown 列表**(不是 frontmatter changelog),当 `old_string` 不包含列表项的 `- ` 前缀,但 `new_string` 包含时,patch 工具的 fuzzy match 会**吞掉** `- ` 前缀,导致列表项变成普通段落(无项目符号)。

**典型失败模式**(2026-09-05 12:00 毛豆 self-evolution cron 实测,SKILL.md 多道 patch 落地):

```markdown
# 修复前 markdown(原状,正常列表)
**Phase 1-7 全实装**:
- `backend/app/orchestrators/phase_orchestrator.py` (101KB) — ...
- `backend/app/api/projects.py` (50KB) — ...

# patch 调用意图:把 "**Phase 1-7 全实装**:" → "**Phase 1-7 全实装(v1.1.1)**:"
# old_string = "**Phase 1-7 全实装**:"
# new_string = "**Phase 1-7 全实装(v1.1.1)**:"

# 但 patch 工具同时影响了下一行的列表项:
# 因为 fuzzy match 把 old_string 匹配到 "**Phase 1-7 全实装**:" 行(只匹配文字),
# 而 new_string 包含了 "**Phase 1-7 全实装**:" + 后续列表项的 "- " 前缀

# 失败 diff 输出(patch 工具实际产生的):
**Phase 1-7 全实装(v1.1.1)**:
`backend/app/orchestrators/phase_orchestrator.py` (101KB) — ...  ← ❌ 列表项前缀 "- " 丢了!
- `backend/app/api/projects.py` (50KB) — ...                        ← ⚠️ 这行还在(因为它在 fuzzy match 范围外)
```

**失败原因链**:
1. `skill_manage patch` 工具的 fuzzy match 范围由 old_string 的**字符相似度**决定,不严格按行边界
2. 当 old_string 是 "**Phase 1-7 全实装**:" 这种**短前缀**(不含 `- `),fuzzy match 可能扩展到下一行,把下一行也纳入替换范围
3. new_string 中如果包含 `- ` 前缀,但 patch 工具的"对齐"逻辑只匹配字符,不识别 markdown 列表语义 → 前缀被吞

**与 §14.7 缩进错陷阱的区分**:

| 陷阱 | 触发场景 | 失败模式 | 修复 |
|------|---------|---------|------|
| §14.7 缩进错 | 修改 frontmatter YAML changelog 列表块 | 列表项缩进被改成 8 空格(子层) | 扩大 old_string 到块边界 |
| **§14.9 丢前缀** | **修改 markdown 正文里普通列表** | **列表项 `- ` 前缀被吞,变成普通段落** | **新方法:逐行单独 patch + 用上下文行锚定** |

**30 秒自检命令**(每次 patch markdown 列表后必跑):

```bash
# 验证目标行仍然是列表项(以 "- " 开头)
grep -nE "^(-|\*) " SKILL.md | head -20
# 期望输出:所有列表项都以 "- " 或 "* " 开头
# 若看到描述行(如 "**Phase 1-7 全实装**:")后面紧跟没 "- " 的代码引用行 → 前缀被吞
```

**正确做法**(避开 fuzzy match 丢前缀陷阱):

1. **方案 A:逐行单独 patch**(推荐,本 session 用的方法)
   ```python
   # 把每一行的修改作为独立 patch 调用
   # 每次 old_string 都包含足够的上下文(前一行 + 当前行),避免 fuzzy 扩展
   old_string = "**Phase 1-7 全实装**:\n- `backend/app/orchestrators/phase_orchestrator.py` (101KB)"
   new_string = "**Phase 1-7 全实装(v1.1.1)**:\n- `backend/app/orchestrators/phase_orchestrator.py` (101KB)"
   ```

2. **方案 B:用 old_string 包住完整列表项**
   ```python
   # old_string 包含完整 "- " 前缀
   old_string = "- `backend/app/services/simulation_service.py` (78KB) — 仿真执行引擎 + 8 个 RAS 用例"
   new_string = "- `backend/app/services/simulation_service.py` (78KB) — 仿真执行引擎 + **12 个 RAS 工程用例**(...)"
   ```

3. **方案 C:用 skill_manage action='edit' 完整重写**
   - 'edit' 是完整重写 SKILL.md,**不会触发 fuzzy match**
   - 代价:必须完整重写,可能影响其他章节

**实测修复样本**(2026-09-05 12:00 毛豆 self-evolve cron SKILL.md 多道 patch):

```bash
# 步骤 1:patch 后立即 grep 验证列表项前缀
grep -nE "^- " ~/.hermes/profiles/maodou/skills/maodou-product/SKILL.md | head -3
# 输出:
# 211:- `backend/app/orchestrators/phase_orchestrator.py` (101KB) — ...  ← ✅ 仍有 "- "
# 212:- `backend/app/api/projects.py` (50KB) — ...                       ← ✅ 仍有 "- "

# 但发现正文里描述行后丢了 "- "(patch 第 2 次调用把列表项前缀吞了)
grep -nE "^\*\*Phase" ~/.hermes/profiles/maodou/skills/maodou-product/SKILL.md | head -3
# 输出:
# 211:**Phase 1-7 全实装(v1.1.1)**:  ← ✅ 描述行 OK
# 212:`backend/app/orchestrators/phase_orchestrator.py` (101KB) — ...  ← ❌ 前缀丢了!应该是 "- `..."
# 213:- `backend/app/api/projects.py` (50KB) — ...                       ← ✅ 这行还正常

# 步骤 2:用另一次 patch 单独恢复 "- " 前缀
# old_string = "**Phase 1-7 全实装(v1.1.1)**:\n`backend/app/orchestrators"
# new_string = "**Phase 1-7 全实装(v1.1.1)**:\n- `backend/app/orchestrators"
```

**§14.9 关键 takeaway**:
- ❌ 不要用 patch 工具的"短前缀 old_string"修改 markdown 列表周围的上下文
- ✅ 每次 patch 必须 `grep -nE "^(-|\*) " <file>` 验证列表项前缀
- ✅ 发现丢前缀时,立即用新 patch 单独恢复(不要整体重写,影响范围大)
- ⚠️ 与 §14.7 缩进错陷阱独立存在,需要 §14.9 单独处理

**触发关键词**:"patch 工具吞列表前缀"/"列表项变普通段落"/"markdown 列表被破坏"/"- 前缀消失"。

---

### 14.11 「首次 cron 启动漏跑 search_files 自检 → write_file 创建重复文件」坑(2026-09-13 04:00 黑豆 cron 首次启动实测新增,坑 45)

> **坑 45 — 冷启动 cron 默认 "memory 全空"假设 + §0 五确认只覆盖环境不覆盖主题,撞坑 #W + 坑 #I**

**问题场景**:self-evolve cron **首次启动**时(冷启动 + 本 profile memory 已沉淀 100+ 文件),SKILL §0 五确认无任务通过(60 秒内 5 命令),直接进入"全方向执行"模式。但**§0 步骤 F 骨架→实体检测**针对的是"既已声明的骨架名 → 实体文件",**不是"cron prompt 主题词 → 既有沉淀"**。agent 默认假设"memory 全空" → 直接 `write_file` 创建 3 份与既有文件同名近义的"新 SOP" → 撞坑 #W(同文件升级 vs 新建)+ 坑 #I(重复造轮子)。

**2026-09-13 04:00 黑豆 heidou-self-evolve-cron 实测**:

| # | 误写文件路径 | 字节 | 应复用既有 | 撞坑点 |
|---|---|---|---|---|
| 1 | `2026Q3财税法务合规速查_v1.0_2026-09-13.md` | 5,510 B | `2026Q3财税法务合规速查_v1.0_2026-09-02.md` patch 升级到 v1.2 | 命名混乱:2026Q3 vs 2026-Q3 vs 2026-09 三套共 7 份同名近义 |
| 2 | `合同审核SOP_v1.0_2026-09-13.md` | 4,887 B | `合同审核SOP_v1.0_2026-09-02.md` patch 升级到 v1.1 | 同名 v1.0 已 3 份历史版本 |
| 3 | `报销SOP_v1.0_2026-09-13.md` | 4,645 B | `报销SOP_v1.0_2026-09-02.md` patch 升级到 v1.1 | 同名 v1.0 已 2 份历史版本 |
| **合计** | — | **15,042 B** | — | **3 份全 rm 删除** |

**根因(三层叠加)**:

1. **§0 步骤 F 漏跑** — 步骤 F 是"骨架→实体",不是"主题→文件";agent 只跑了 `find ... -name "*.md" | head` 看了主目录,没看子目录,误以为"memory 是空的"
2. **§0 五确认只覆盖环境,不覆盖主题** — HOME / heartbeat / sqlite / evolution 累计 / HOME 漂移 = 5 项都是"环境检查",**没有针对 cron prompt 提到的 4 方向(政策/合同/SOP/skills)的主题词 search_files 自检**
3. **"首次 cron 启动"模式陷阱** — 本 profile 上下文无既有 memory 索引 = 默认假设"空白";但文件系统 100+ 沉淀存在 = **严重事实偏差**。任何首次 cron 启动都受此陷阱影响

**撞坑后纠正模式(4 步链)**:

```bash
# Step 1: ls -la 验证(发现 3 份重复)
ls -lt /Users/hua/.hermes/profiles/heidou/memory/compliance/*财税法务*
# → 看到 7 份同名近义 + 1 份我刚写的 = 8 份冲突

# Step 2: rm 删除重复文件
rm <3 份撞坑文件>
# 验证: ls <pattern> 2>&1 = No such file or directory ✅

# Step 3: patch 升级既有 v1.1 → v1.2(沿用坑 #W 同文件升级)
# old_string = 文件末尾的 v1.1 维护标记
# new_string = v1.2 维护标记 + §7 增量段(诚实标注违规)

# Step 4: size gate 双维度验证(沿用坑 #AJ + 坑 #AK)
wc -c <升级文件>   # size 升
head -1 <升级文件>  # title 升
# 两者一致 = 真升级完成;只 size 升 = 命中坑 #AJ
```

**SKILL §6 候选 3 条(沉淀到 ***SECRET*** §6)**:

1. **§0 步骤 G 必跑**:`search_files pattern=<主题词>` × 4 方向(政策/合同/SOP/skills),命中 = patch 升级(沿用坑 #W),不命中 = 真空白可新建
2. **"全方向执行"≠无条件 write_file**:elif 边界 case "全方向执行" 仍受"不重复造轮子"硬约束,先 search_files 后 write_file
3. **撞坑 #AJ 诚实标注模式标准化**:不掩盖 + 不补做 + 仅在 evolution 报告 + memory v1.2 增量段留"已删 + 根因"诚实记录

**防御性 checklist(首次 cron 启动必跑)**:

```markdown
## 启动 30 秒自检(强制,首次 cron 必跑)

- [ ] echo $HOME? → 若不是 /Users/hua,启动绝对路径模式
- [ ] 至少 1 个 web_search 已完成? → 证明网络通道可用
- [ ] **🆕 search_files 主题词自检 4 方向?** → 防撞坑 #W/#I
  - [ ] 财税/合规/速查 → search_files pattern
  - [ ] 合同审核/法务 → search_files pattern
  - [ ] 报销/SOP → search_files pattern
  - [ ] skills/skill_manage → search_files pattern
- [ ] write_file 用绝对路径? → 验证 resolved_path 字段
- [ ] ls 用绝对路径? → 不用 ~ 验证文件落地
- [ ] **🆕 rm 删除任何撞坑文件? → 沿用坑 #AJ 诚实标注**
- [ ] **🆕 patch 升级既有 v1.x? → 沿用坑 #W 同文件升级**
```

**与既有坑的关系矩阵**:

| 既有坑 | 关系 | 沿用 / 互补 |
|---|---|---|
| 坑 #W(同文件升级 vs 新建) | 本案例直接撞上 | 沿用:patch 既有,严禁 write_file 新建 |
| 坑 #I(重复造轮子) | 本案例直接撞上 | 沿用:search_files 主题词自检前置 |
| 坑 #AJ(描述升级 vs 实体升级) | 撞坑后修复模式 | 沿用:size gate 双维度验证(size + title) |
| 坑 #AK(文件名版本 ≠ 内容版本) | 撞坑后修复模式 | 沿用:title 升级 + filename 保留 v1.x 合法差异化 |
| 坑 #X 第 10/11 次阈值 | 本案例同次撞上 | 沿用:skill loader 告警不可消除,接受 + 绝对路径绕过 |
| §14.7/§14.9(patch 工具陷阱) | 本案例未撞但相关 | 互补:本坑是"撞坑前预防",§14.7/§14.9 是"撞坑后修复" |

**触发关键词**:"首次 cron 启动" / "首次启动 self-evolve" / "first cron run" / "memory 是空的" / "误以为空白" / "默认空白假设" / "写文件撞坑 #W" / "write_file 撞坑 #I" / "3 份重复文件" / "15KB 重复" / "重复造轮子" / "search_files 自检" / "主题词自检" / "4 方向 search_files" / "patch 升级 v1.1 → v1.2" / "沿用坑 #W 同文件升级" / "size gate 双维度" / "撞坑 #AJ 诚实标注"。

**详见配套文件**:`references/***SECRET***.md`(完整 9 节:失败现场 + 根因 + 修复模式 + 教训沉淀 + 防御性 checklist + 与既有坑的关系 + 实战样本 + 关键 takeaway)

---

### 14.12 「replace_all=true + 短 old_string」= 12x 灾难性重复插入坑(2026-09-13 08:33 小宝 cron 实测新增,坑 46)

> **坑 46 — patch 工具 replace_all=true + 短 old_string = "看似合法实则灾难"的隐形炸弹**

**问题场景**:用 `patch` 工具向 canonical SKILL.md(本 skill 2727 行 / 181 KB)插入大章节正文(§三十二 ~170 行),`replace_all=true` 配合 `old_string` 包含 "下一轮迭代(预计 09-22)" 子串 —— **该子串在文件中出现 38 次**(每个章节末尾都有类似模板) → 替换在 38 处执行 → §三十二 完整章节被插入到 **12 个位置** → canonical SKILL.md 章节顺序打乱,skill loader 加载时会读出重复的 §三十二 12 份。

**根因三层叠加**:

1. **old_string 选取失误** —— "下一轮迭代(预计 09-22)" 是复用模板,不是独有锚点;正确做法是包含目标章节独有的标识符(如 "§三十一 实战复盘" + "9/14 信息密度爆表")
2. **replace_all=true 隐性危险** —— patch 工具是字面精确替换,不感知 markdown 章节结构、不感知"只该改某一段"的意图
3. **未跑 grep -c 验证匹配次数** —— patch 前 5 秒跑 `grep -c "<old_string 第一行>" <file>` 就能发现 38 次匹配,而不是 patch 失败后才发现

**实测失败规模**(2026-09-13 08:33 小宝 cron):
- patch 返回 `success: true` 但 `diff` 字段 **285 KB**(远超普通 patch 应返回的 ~15 KB)
- `grep -c "^## 🎯 三十二" SKILL.md` 返回 **12**(灾难确认)
- 章节顺序完全打乱:§十二/§十六/§十七/§十八/§十九/§二十/§二十一/§二十二/§二十三/§二十四/§二十五/§二十六/§二十七/§二十八/§二十九/§三十 后都被插入了重复的 §三十二

**修复模式**(5 步链,60 秒内完成):
```bash
# Step 1: grep 章节计数确认灾难
grep -c "^## 🎯 三十二" ~/.hermes/skills/sales/xiaobao-sales/SKILL.md
# 输出 12 → 灾难确认

# Step 2: 从开工前必备份恢复(canonical SKILL.md 181 KB 必备份)
cp ~/.hermes/profiles/xiaobao/evolution/skill_backup_2026-09-13_08.md \
   ~/.hermes/skills/sales/xiaobao-sales/SKILL.md

# Step 3: 验证恢复
grep -c "^## 🎯 三十二" ~/.hermes/skills/sales/xiaobao-sales/SKILL.md
# 输出 0 → 恢复成功

# Step 4: 二次精确 patch(只改 description + header changelog,大章节正文降级)
# old_string 改为独有行: "description: ...§三十一 假设成交法成孪生招)。" → 匹配 1 次
# 同样改 header: "📝 最后更新:2026-09-13 04:33 · §三十一..." → 匹配 1 次

# Step 5: 大章节正文走 skill_manage write_file 写到 profile 内副本 references/
# 而不是再次尝试 patch canonical(否则 patch 工具 fuzzy match 仍可能误伤其他章节)
```

**§14.12 防御性 SOP(6 条铁律)**:

| # | 铁律 | 触发场景 | 操作 |
|---|------|---------|------|
| 1 | **开工前必备份** | 任何 SKILL.md 修改前 | `cp <target_skill_md> ~/.hermes/profiles/<your>/evolution/skill_backup_<时间>.md` |
| 2 | **replace_all=true 几乎永远不该用** | 默认 `replace_all=false` | 只在"批量改 N 个独立章节的同一种模式"或"修复某错误重复 N 次"时才用,且必须先 grep -c 验证 |
| 3 | **old_string 必须足够独特(≥ 30 字符 + 多行上下文)** | 短字符串 < 30 字符 | 必须包含目标章节独有的标识符(章节标题 + 子章节名 + 专属术语) |
| 4 | **patch 前必跑 grep -c 验证匹配次数** | patch 任何文件前 | `grep -c "<old_string 第一行>" <file>` → 必须输出 1 |
| 5 | **patch 后必跑章节计数验证** | patch 任何文件后 | `grep -c "^## <章节标题>" <file>` → 必须输出 1 |
| 6 | **大章节正文(≥ 100 行)走 write_file 不走 patch** | 新增/重写大章节 | `skill_manage action='write_file', file_path='references/<name>.md'` + 玉芬 review 后手工合 canonical |

**§14.12 与既有坑的关系矩阵**:

| 既有坑 | 关系 | 沿用 / 互补 |
|---|---|---|
| §14.7 patch fuzzy match 破坏 YAML changelog 缩进 | 同属"patch 工具陷阱"家族 | 互补:§14.7 是缩进,§14.12 是位置/范围 |
| §14.9 patch 吞 `- ` 前缀 | 同属"patch 工具陷阱"家族 | 互补:§14.9 是前缀,§14.12 是范围 |
| §14.10 cross-profile 写入 soft guard 拦截 | 不同陷阱(写入权限) | 互补:§14.10 是能不能写,§14.12 是写在哪 |
| §14.11 漏跑 search_files → 重复造轮子 | 不同陷阱(写前发现既有) | 互补:§14.11 是新建,§14.12 是 patch 范围 |
| **§14.12 本档** | **"replace_all + 短 old_string" = 范围失控** | **新增独立坑** |

**家族判定**:**§14.12 是"patch 工具范围陷阱"独立子家族**(范围 = 位置 + 数量),与 §14.7(内容结构)/§14.9(前缀)/§14.10(权限)/§14.11(写前)均正交。

**防御脚本**(待玉芬 review 后正式落地):`scripts/verify-replace-all-safety.sh` — patch 前必跑,自动 grep -c + 备份存在性 + 章节标题唯一性三连验,失败则 abort patch(参考 §14.5 `pre-evolve-hook.sh` 集成模式)。

**触发关键词**:"replace_all=true" / "old_string 匹配 N 次" / "Found N matches" / "灾难性重复插入" / "12 次重复章节" / "回滚 skill_backup"。

**详见配套文件**:`references/***SECRET***.md`(完整 9 节:事故现场 + 根因三层 + 5 步修复 + 6 铁律 + 与既有坑关系 + 防御脚本草案 + 触发关键词 + 起源 trace)

---

## 配套文件

- `references/skill-upgrade-discipline.md` — 完整 SOP(4 步 + 5 铁律 + 6 反例 + **§8 5 铁律 #1 外部权威源例外规则** + **§9 HOME 劫持自检** + **§10 升级后双端验证** + **§11 三处同步铁律(2026-08-25 阿福实测新增)** + **§12 frontmatter version 字段与 changelog 同步铁律** + **§13 升级后版本号三方核验脚本** + **§14 changelog 内部完整性铁律(2026-08-25 08:00 阿福二轮修复实证新增)** + **§14.4 1 个版本号 = 1 个原子变更(2026-08-25 12:00 阿福三轮实证新增)** + **§14.5 §13/§14 脚本必须接入 cron hook(2026-08-25 三轮复发根因新增)** + **§14.6 显式字段铁律(2026-08-26 阿福 8/25 20:00 假闭环根因新增)**)
- `references/***SECRET***.md` — **🆕 2026-08-26 00:00 阿福 cron 实测案例** — verify_evolution.py v2.0 落地完整复盘:8/25 20:00 假闭环完整根因分析 + patch 工具 fuzzy match 字符级陷阱(Pitfall 8)+ 显式 `主索引当前版本` 字段补全过程 + Claude Code / Codex 超时兜底自写实测 4 步流程(写 → 实测 exit 0 → 才声明完成)+ verify_evolution.py v2.0 完整 Python 实现参考(241 行,含 Python 3.9 兼容的 `str | None` 语法绕过 + 绝对路径配置 + 三方元数据扫描函数)。触发词:"verify_evolution.py v2.0"/"8/25 20:00 假闭环复盘"/"patch 模糊匹配破坏字段"/"Claude Code 超时自写 4 步"/"主索引当前版本字段补全"。
- `references/contract-3-tier-warning.md` — 应用示例(合同管理 90d/60d/30d 三级阈值 SOP)
- `references/***SECRET***.md` — **🆕 2026-08-25 黑豆 cron 04:34 实测案例** — non-default profile 加载 default profile core skills 失败时的应急绕过(绝对路径贯穿全程)+ 跨 profile skill loader 索引隔离根因 + 3 种永久修复方案 + 防御性 checklist。触发词:"跨 profile skill 找不到"/"absolute path workaround"/"HOME 漂移 + skill loader 同时失败"。
- `references/***SECRET***.md` — **🆕 2026-08-25 黑豆 cron 08:31 实测案例** — deadline 日 / 评审日 evolution 报告应从通用 5 方向模板切换为时点驱动的 7 节结构(§零 时点校验 / §二 评审材料 / §三 倒计时表 / §四 P0-P2 承接清单 / §六 评审预案 Q&A / §七 评审话术)。触发词:"评审日"/"deadline 日"/"今天有评审"/"距施行 N 天"/"evolution 报告时点模板"。
- `references/***SECRET***.md` — **🆕 2026-08-25 黑豆 cron 16:00 实测案例(同日三件套第 3 件)** — 验收 slot 16:00 完全错过 slot-pattern 与 time-aware 两道闸门 + 输出 9 KB 远超 4 KB 上限 + 新增 3 份 SOP 草案违反"verification slot 不能新增方案"纪律。沉淀 4 项新违规 + 防御性 checklist(三件套叠加版)+ 与前两个 reference 的协同关系。触发词:"16:00 验收 slot"/"verification slot 违规"/"下午 cron 新增 SOP"/"距 deadline 但用了通用模板"。
- `scripts/verify-three-end-version.sh` — 三方版本号核验脚本(§13,30 秒替代手工 grep)
- `scripts/verify-skill-integrity.sh` — **🆕 5 项完整性核验脚本(§14)** — frontmatter↔changelog 一致 + changelog 单调性 + 无重复日期 + 无重复版本 + 三方版本号一致。**8/25 04:00 阿福踩坑实证**:§13 老脚本返回 ✅ 但实际 changelog 有 v1.37.0/v1.38.0 双条目同日期问题,新脚本的检查 [4] 会立即报错
- `scripts/pre-evolve-hook.sh` — **🆕 §14.5 阿福 cron 接入模板(待玉芬批)** — evolution 启动前必跑 `verify-skill-integrity.sh`,失败时 abort + 飞书告警。**根因**:8/25 04:00 → 08:00 → 12:00 三轮复发,核验脚本在但没自动跑
- `references/***SECRET***.md` — **🆕 §14.9 patch 工具删除 `- ` 列表前缀陷阱(2026-09-05 12:00 毛豆 cron 实测新增,坑 43)** — `old_string` 不含 `- ` 前缀但 `new_string` 含 `- ` 时,patch 工具把列表项前缀吞掉,把 markdown 列表项变成普通段落;与 §14.7 缩进错陷阱互补(§14.7 是缩进被改成错误层级,§14.9 是前缀被吞掉)。触发词:"patch 工具吞列表前缀"/"列表项变普通段落"/"markdown 列表被破坏"
- `references/***SECRET***.md` — **🆕 §14.10 跨 profile 写入 soft guard 拦截 + skill_manage 路由错坑(2026-09-12 04:00 小宝 xiaobao-self-evolve-cron 实测新增,坑 44)** — canonical SKILL.md 属 default profile 时,非 default profile cron 用 patch/write_file 被 soft guard 拦截 + 用 skill_manage 路由到 profile-local 副本而非 canonical。与 2026-08-25 黑豆"读侧"案例互补:**写侧需走 "暂存 evolution/proposed_skill_patches/ + pending review" 流程,不能绕过 guard**。含 5 步应急行动链 + 3 选 1 永久方案(玉芬 review / 华哥授权 cross_profile=True / 改 Hermes 架构)+ 防御性 checklist + 三份同名 skill 并存时如何验证 canonical 实际路径。触发词:"Cross-profile write blocked by soft guard"/"cross_profile=True"/"skill_manage 路由错"/"canonical SKILL.md 跨 profile 写"/"evolution/proposed_skill_patches/ 暂存"
- `references/***SECRET***.md` — **🆕 §14.11 首次 cron 启动漏跑 search_files 自检 → write_file 创建重复文件坑(2026-09-13 04:00 黑豆 heidou-self-evolve-cron 首次启动实测新增,坑 45)** — 冷启动 self-evolve cron 时,SKILL §0 五确认只覆盖环境(HOME/heartbeat/sqlite/evolution 累计/HOME 漂移)不覆盖主题词,直接进入"全方向执行"模式后默认 memory 全空假设 → write_file 创建 3 份与既有文件同名近义的"新 SOP"(共 15,042 字节)撞坑 #W(同文件升级 vs 新建)+ 坑 #I(重复造轮子)。修复模式:rm 删除 3 份重复文件 + patch 升级既有 `黑豆重复文档整合建议 v1.1 → v1.2`(13,730 字节)+ size gate 双维度验证(size + title)+ 沿用坑 #AJ 诚实标注模式。含 4 步纠正链 + 3 条 SKILL §6 候选 + 防御性 checklist(首次 cron 启动必跑 search_files 主题词自检 4 方向) + 与坑 #W/#I/#AJ/#AK 的关系矩阵。触发词:"首次 cron 启动"/"memory 是空的"/"search_files 主题词自检"/"3 份重复文件"/"15KB 重复"/"撞坑 #W 修复模式"
- `references/***SECRET***.md` — **🆕 §14.12 「replace_all=true + 短 old_string」= 12x 灾难性重复插入坑(2026-09-13 08:33 小宝 xiaobao-self-evolve-cron 实测新增,坑 46)** — patch SKILL.md 时用 replace_all=true 但 old_string 第一行 "下一轮迭代(预计 09-22)" 在文件中匹配 38 次 → §三十二 完整章节(170 行)被插入到 12 个位置 → 必须从 skill_backup 整体回滚。修复模式:5 步恢复链(grep 章节计数 → cp backup → 精确锚点二次 patch → 大章节正文走 skill_manage write_file 降级 → 三处同步验证)+ 6 条防御性铁律(开工前必备份 + replace_all 默认 false + old_string ≥30 字符含独有标识 + patch 前 grep -c 验证唯一 + patch 后 grep -c 验章节唯一 + ≥100 行章节走 write_file)+ 与 §14.7(缩进)/§14.9(前缀)/§14.10(权限)/§14.11(写前)正交关系。触发词:"replace_all=true"/"old_string 匹配 N 次"/"Found N matches"/"灾难性重复插入"/"12 次重复章节"/"回滚 skill_backup"
- `references/***SECRET***.md` — **🆕 §15 「Class-Level Skill 配套完整性自检」坑(2026-09-16 22:30 小宝 xiaobao-self-evolve-cron 实测新增,坑 47)** — class-level skill 多次扩展后,每个新增章节都有"标准配套清单"(主档/话术卡 A5/RP 脚本/公众号草稿/抖音草稿/排期表 = 6 件套),但 skill 本身从未显式文档化这个清单 → 新增 §N 时容易只产 1-2 件(主档 + 公众号),漏掉销售组必带的 A5 话术卡 → 12 小时后下个 cron 才发现补做。本档新增 §15 "配套完整性矩阵"工具(6 列 N 行的 markdown 表 + 60 秒自检 + 4 大禁忌 + 与 §14 各坑正交关系)。触发词:"配套话术卡漏了"/"A5 话术卡"/"6 件套不全"/"主档发了但话术卡没发"/"class-level skill 配套清单"

## 反面警示

- ❌ 把"准备做的变更"写进 changelog — 必须是"已完成的变更"
- ❌ 用模糊措辞("改进"、"优化"、"完善")— 必须说明改了什么章节/什么内容
- ❌ 在 changelog 中引用尚未存在的文件路径 — 必须先 find 验证
- ❌ 升级 minor 但只动了 1 行 — patch 才合理
- ❌ 多人协作时不通知 — skill 是公共契约,升级前必须通知使用方
- ❌ **报告里写"已验证 license=X"当持久结论**(2026-08-24 modly 教训) — license 字段是动态变化的,详见 research-collection "Pitfall: license 字段是动态变化" 段。**正确的写法是带抓取日期的字段**:`(实测 2026-08-24 API) / (实测 2026-08-23 raw LICENSE)` — 不能省略日期,否则 24h 后就被推翻
- ❌ **三处文件只 bump 两处**(2026-08-25 阿福坑 27)— 主索引改了但忘了顶层门户,或分支 skill 改了但忘了主索引。**完整三处同步铁律见 §11**
- ❌ **changelog 升级但 frontmatter 没改**(2026-08-25 阿福坑 28)— patch 工具默认不动 frontmatter `version:` 行,必须显式包含在 patch 调用中。**完整双轨同步铁律见 §12**
- ❌ **跨 profile skill 加载失败时不切换策略**(2026-08-25 黑豆坑 29)— non-default profile cron 启动时 core skill 报"could not be found and skipped",应立即切换到绝对路径贯穿全程模式 + 不依赖 skill loader 完成 cron 任务;而非继续尝试 skill_view 或凭记忆自写。详见 `references/***SECRET***.md`
- ❌ **单步跨版本 patch 产生重复 changelog 条目**(2026-08-25 阿福坑 30)— v1.36.0 一次性 bump 到 v1.38.0 时,changelog 留下 v1.37.0 + v1.38.0 两条同日期条目。修复:禁止单步跨 ≥ 2 minor 版本号,必须拆成两次心跳(每次 +1)。详见 §14
- ❌ **changelog 与 frontmatter 偏移**(2026-08-25 阿福坑 31)— §13 老脚本只检三方 frontmatter 一致,不检 changelog 内部。changelog 可能出现 v1.38.0 但 frontmatter 还停留在 v1.37.0(或反过来)。修复:扩展核验脚本 `verify-skill-integrity.sh` 把 frontmatter↔changelog 强一致加入检查。详见 §14
- ❌ **verify-three-end-version.sh 通过但 changelog 自相矛盾**(2026-08-25 阿福坑 32)— §13 老脚本的盲区:changelog 内部出现重复条目时,frontmatter 仍然一致 → 脚本返回 ✅ 但 changelog 已坏。修复:§14 新增检查 [3] 重复日期 + 检查 [5] 单调性
- ❌ **同日多个 changelog 条目**(2026-08-25 阿福坑 33)— 一次性合并 2+ 个变更时,误以为每个变更都要单独条目,导致同日期多条目 → grep 出来像"乱码"。修复:同日多个变更必须合并为单条目用 AND 拼接,或加 (上午/下午/晚上) 时间后缀。详见 §14.1
- ❌ **deadline 日 / 评审日仍用通用 5 方向 evolution 模板**(2026-08-25 黑豆坑 34)— 距关键时点 ≤ 7 天时,通用模板无法让 reviewer 一眼看到"今天能立即做什么"。修复:切换为时点驱动 7 节结构(§零/§二/§三/§四/§六/§七)。详见 `references/***SECRET***.md`
- ❌ **changelog 1 个条目塞多个不相关变更**(2026-08-25 12:00 阿福坑 35a)— 阿福把"合并 #32 主动破锚术"+"修复上一轮 1.36/1.37 changelog 双条目"两个变更塞进同一个 v1.38.0 changelog 条目,虽然 frontmatter/changelog 同步通过(§14 检查 1 ✅)、版本号不重复(§14.1 检查 4 ✅)、日期不重复(§14.1 检查 3 ✅),但**违反了 §5 铁律"不要合并多个不相关变更"和版本号语义"每个版本号对应 1 个原子变更"**。修复:拆成 v1.37.0(修复双条目)+ v1.38.0(合并 #32) 两次心跳,或显式分两个 changelog 条目加时间后缀(上午/下午)。详见 §14.4
- ❌ **§13/§14 脚本写在 skill 里但 cron 没接入**(2026-08-25 阿福坑 35b,三轮复发根因)— `verify-three-end-version.sh` 和 `verify-skill-integrity.sh` 在 1.3.0/1.4.0 已就位,但阿福 cron 每次都"手动跑一次",而不是"启动后必跑"。证据链:8/25 04:00 漂移 → 8/25 08:00 修 → 8/25 12:00 同样模式再犯(虽然不是同样错误,但同样是手动跳过了原子 bump 纪律)。**修复:阿福 cron 必须在写任何 SKILL.md 前先跑 `verify-skill-integrity.sh`,失败时立即 abort evolve + 飞书告警华哥**。详见 §14.5
- ❌ **黑豆 16:00 验收 slot 完全错过 slot-pattern 与 time-aware 两道闸门**(2026-08-25 16:00 坑 36,同日第三次违规)— 16:00 cron 应是 ✅ verification slot(轻量 ≤ 4 KB,只跟踪白天承接进度 + 预告下次 cron),但实际输出 9 KB / 166 行 + 新增 3 份 SOP 草案 + 复述白天政策摘要,完全套用了通用 5 项模板。根因:cron prompt 是通用平铺,没强制要求"按小时切 slot";slot-pattern 与 time-aware 两 skill 都在,但 cron 启动自检里没有"距 deadline ≤ 7 天?"的自动检测。**修复:cron prompt 应改为 slot-aware(按当前小时判定)+ 把"距 deadline ≤ 7 天?"加入 30 秒自检强制项**。详见 `references/***SECRET***.md`
- ❌ **patch 工具 fuzzy match 静默破坏未参与修改的字段**(2026-08-26 00:00 阿福实测坑 37)— 同步顶层门户 `afu-customer-service/SKILL.md` 时,新版 changelog 字符串里出现了 "afu" 和 "top-level" 字符片段,patch 工具的 fuzzy match 把已正确存在的 `layer: afu-profile-top-level (门户层)` 静默改成了 `afuprofile-top-level`(少一个连字符)。YAML 解析仍然合法(值是字符串),grep -m1 '^version:' 也通过 → §13/§14 5 项核验脚本**全部返回 ✅**,但**字符串语义已损坏**。**修复**:`new_string` 中未明确修改的字段必须与 `old_string` 完全照搬(连字符、空格、引号风格都不能改)+ patch 后必须 `grep -n <pattern> <file>` 全文确认未预期的字段没被改。详见 `references/***SECRET***.md`
- ❌ **"三方一致"没有显式字段,只能人眼判断**(2026-08-26 00:00 阿福坑 38,8/25 20:00 假闭环根因)— §11 三处同步铁律要求"主索引+顶层 portal+分支 skill 版本号一致",但只规定了"用脚本核验"。**坑在**:顶层 portal 的 `主索引当前版本` 信息如果只散落在 changelog 条目的描述文字里(如"主索引 v1.38.0 对齐"),脚本和人眼都没法拿到权威值,只能 fallback 提取字符串 → 出现假闭环。**修复**:顶层 portal SKILL.md 必须有显式字段 `主索引当前版本: vX.Y.Z`(独立行,不嵌在描述里);§13 核验脚本必须解析这个**显式字段**,不要从 changelog 文字回溯。详见 §14.6
- ❌ **Claude Code / Codex 超时后未实测就直接交付**(2026-08-26 00:00 阿福坑 39,铁律 #1 实操细节)— AGENTS.md 铁律 #1 规定外部 coding agent 失败可自写并加 `# TODO(tech-debt)` 头,但**常见违规**是:自写后没实测就跑(因为时间预算紧张),实际脚本可能在 Python 版本兼容(3.9 vs 3.10 的 `str | None` 语法)、绝对路径未替换 `Path.home()`、依赖脚本缺失等问题上首次执行就 crash。**修复**:AGENTS.md 铁律 #1 的"自写"分支必须**强制包含** "写 → 实测 → 通过 exit 0 → 才声明完成" 四步;实测失败时不能直接报"已完成",必须老实说"自写脚本首次执行失败,原因是 X,已 patch 修复 Y,现 exit 0"。详见 `references/***SECRET***.md §3`
- ❌ **patch 工具删除 `- ` 列表前缀,把 markdown 列表项变成普通段落**(2026-09-05 12:00 毛豆坑 43)— `old_string` 不含 `- ` 前缀但 `new_string` 含 `- ` 时(短前缀 + fuzzy match 扩展范围到下一行),patch 工具吞掉 `- ` 前缀。**与 §14.7 缩进错陷阱互补**:§14.7 是修改 frontmatter YAML changelog 时缩进被改成错误层级;§14.9 是修改 markdown 正文列表时 `- ` 前缀被吞。**修复**:old_string 必须包住完整 `- ` 前缀 + 足够上下文(前一行 + 当前行);patch 后必须 `grep -nE "^- " <file>` 验证。详见 `references/***SECRET***.md`
- ❌ **跨 profile 写入 canonical SKILL.md 被 soft guard 拦截 + skill_manage 路由错坑**(2026-09-12 04:00 小宝坑 44)— non-default profile (如 xiaobao) cron 想 patch `~/.hermes/skills/<canonical>/SKILL.md` 时,**`patch` / `write_file` 工具**报 "Cross-profile write blocked by soft guard" + **`skill_manage patch` 工具**路由到 profile-local 副本(230 行 v1.0.0)而非 canonical(1844 行),双重失败。与 2026-08-25 黑豆"读侧"案例(***SECRET***)互补:读侧可独立完成,写侧必须**暂存待 review**,不能绕过 guard。**修复**:跨 profile 写入走 "暂存到 `~/.hermes/profiles/<your>/evolution/proposed_skill_patches/` + evolution 报告加 §pending review 段" 流程;玉芬 review 后迁移到 canonical,或华哥授权 `cross_profile=True`(高权限慎用)。详见 §14.10 + `references/***SECRET***.md`
- ❌ **首次 cron 启动漏跑 search_files 自检 → write_file 创建 3 份重复文件**(2026-09-13 04:00 黑豆坑 45)— self-evolve cron 首次启动(冷启动 + 本 profile memory 已沉淀 100+ 文件)时,SKILL §0 五确认通过 → 默认进入"全方向执行"模式 → **未跑 search_files 主题词自检**(§0 步骤 F 是"骨架→实体",不是"主题→文件")→ 默认假设"memory 全空" → write_file 创建 3 份与既有文件同名近义的"新 SOP"(共 15,042 B)撞坑 #W/#I。**修复**:① **SKILL §0 步骤 G 必跑**:针对 cron prompt 4 方向(政策/合同/SOP/skills)各跑一次 `search_files pattern=<主题词>`,命中 = patch 升级(沿用坑 #W),不命中 = 真空白可新建;② **"全方向执行"≠无条件 write_file**:elif 边界 case 仍受"不重复造轮子"硬约束,先 search_files 后 write_file;③ 撞坑后纠正链:rm 删除重复文件 + patch 升级既有 v1.x(沿用坑 #W)+ size gate 双维度验证(沿用坑 #AJ/AK)+ 沿用坑 #AJ 诚实标注模式(不掩盖 + 不补做 + 仅在 evolution 留"已删 + 根因"记录)。详见 §14.11 + `references/***SECRET***.md`
- ❌ **`patch` 工具 replace_all=true + 短 old_string = 12x 灾难性重复插入**(2026-09-13 08:33 小宝坑 46)— 向 canonical SKILL.md(2727 行 / 181 KB)插入 §三十二 章节(170 行)时,`old_string` 包含 "下一轮迭代(预计 09-22)" 复用模板 → 在文件中匹配 **38 次** → `replace_all=true` 把 §三十二 重复插入到 **12 个位置** → canonical SKILL.md 章节顺序打乱 → skill loader 加载时读出重复的 §三十二 12 份。patch 返回 `success: true` 但 `diff` 字段 285 KB(异常大)就是明确信号。**与 §14.7/§14.9 同属"patch 工具陷阱"家族,但 §14.12 是"范围失控"**(替换多少处 = old_string 匹配次数),§14.7 是缩进、§14.9 是前缀。**修复**:① 开工前必备份(铁律 1);② `replace_all=true` 默认 false,只在"批量改 N 个独立章节的同一种模式"或"修复某错误重复 N 次"时才用且必须先 `grep -c` 验证(铁律 2);③ old_string 必须 ≥ 30 字符 + 多行上下文 + 包含目标章节独有标识符(铁律 3);④ patch 前必跑 `grep -c "<old_string 第一行>" <file>` 验证匹配次数 == 1(铁律 4);⑤ patch 后必跑 `grep -c "^## <章节标题>" <file>` 验章节唯一(铁律 5);⑥ ≥ 100 行大章节正文走 `skill_manage action='write_file'` 写到 profile 内 references/ + 玉芬 review 后手工合 canonical,不走 patch(铁律 6)。详见 §14.12 + `references/***SECRET***.md`

## 触发关键词

- "升级 skill" / "更新 SKILL.md" / "加新章节" / "改 changelog"
- "v1.x.y → v1.x.(y+1)" / "patch version" / "minor version"
- "skill 不实声明" / "changelog 不实" / "find 验证闭环"
- "skill 升级 SOP" / "skill 维护纪律"
- "外部权威源" / "引用 Voss/书/论文" / "例外规则" / "Amazon #1 畅销书"
- "[Skill(s) not found and skipped]" / "顶层 portal 缺失" / "skill loader 找不到"
- "HOME 劫持" / "echo $HOME 不是 /Users/hua" / "profile home 污染"
- **🆕 "三处同步" / "主索引+顶层 portal+分支 skill"**(2026-08-25 阿福坑 27)
- **🆕 "changelog 改了 frontmatter 没改" / "version 字段没同步"**(2026-08-25 阿福坑 28)
- **🆕 "阿福客服 31 个技巧" / "合并 #N 技巧到主索引"**(2026-08-25 阿福坑 27 衍生)
- **🆕 "跨 profile skill 加载失败" / "non-default profile 找不到 core skill" / "absolute path workaround"**(2026-08-25 黑豆坑 29)
- **🆕 "单步跨版本" / "v1.x → v1.(x+2) 一次性 bump" / "changelog 重复条目" / "changelog 自相矛盾"**(2026-08-25 阿福坑 30)
- **🆕 "changelog 与 frontmatter 偏移" / "changelog 写新版本但 frontmatter 没改"**(§12 + §14 联合强化)
- **🆕 "verify-skill-integrity.sh" / "5 项完整性核验" / "changelog 内部一致性"**(2026-08-25 阿福 §14 新增)
- **🆕 "同日多条目" / "同日期 changelog 合并" / "AND 拼接"**(2026-08-25 阿福坑 33)
- **🆕 "评审日 evolution 报告" / "deadline 日时点模板" / "今天有评审" / "距施行 N 天" / "时点驱动 evolution 报告"**(2026-08-25 黑豆坑 34)
- **🆕 "1 个版本号塞多个变更" / "原子变更违反" / "AND 拼接双变更"**(2026-08-25 12:00 阿福坑 35a)
- **🆕 "阿福 cron 三轮复发" / "verify-skill-integrity.sh 没接入 cron" / "手动跑脚本 vs 必跑脚本"**(2026-08-25 阿福坑 35b)
- **🆕 "黑豆 16:00 验收 slot" / "verification slot 违规" / "下午 cron 新增 SOP" / "距 deadline 但用了通用模板" / "slot-pattern 没生效"**(2026-08-25 16:00 黑豆坑 36)
- **🆕 "patch 工具 fuzzy 破坏字段" / "patch 后必须 grep 验证" / "fuzzy match 静默改值"**(2026-08-26 00:00 阿福坑 37)
- **🆕 "假闭环" / "显式主索引当前版本" / "主索引当前版本字段" / "§14.6" / "显式字段铁律" / "权威值字段"**(2026-08-26 00:00 阿福坑 38)
- **🆕 "Claude Code 超时自写" / "Codex exec 超时" / "TODO(tech-debt) 必须实测后声明" / "自写后未实测"**(2026-08-26 00:00 阿福坑 39,铁律 #1 实操细节)
- **🆕 "patch 工具吞列表前缀" / "列表项变普通段落" / "markdown 列表被破坏" / "- 前缀消失"**(2026-09-05 12:00 毛豆坑 43)
- **🆕 "首次 cron 启动" / "首次启动 self-evolve" / "first cron run"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "memory 是空的" / "默认空白假设" / "default empty assumption"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "search_files 主题词自检" / "4 方向 search_files" / "未跑主题词自检"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "3 份重复文件" / "15KB 重复" / "重复造轮子撞坑 #W/#I"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "patch 升级 v1.1 → v1.2" / "沿用坑 #W 同文件升级" / "沿用坑 #AJ 诚实标注"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "size gate 双维度" / "title + size 双维度" / "size 升 + title 升"**(2026-09-13 04:00 黑豆坑 45)
- **🆕 "replace_all=true" / "old_string 匹配 N 次" / "Found N matches" / "灾难性重复插入" / "12 次重复章节" / "回滚 skill_backup"**(2026-09-13 08:33 小宝坑 46)

## 适用范围

所有 agent(玉芬 default + 8 同事 profile + community)的 SKILL.md 维护。
不适用:AGENTS.md / 配置文件 / 脚本 / 一行 patch 修复(这些走 changelog 的"未发布"区即可)。

**§15 Class-Level Skill 配套完整性自检**(v1.13.0 新增):配套文件在 `references/***SECRET***.md`(完整 10 节 + 6 件套矩阵 + 3 套 checklist + 22:30 实操案例)。description 字段已含触发词,changelog v1.13.0 已固化。SKILL.md body §15 节完整正文待玉芬 review canonical 时手动内嵌(本档采用"配套文件 + description + changelog 三处落地"模式,因 §14.12 章节末尾 13 处重复匹配,patch 工具无法精确锚定)。

---

## 顶层可见性铁律(坑 26,2026-08-24 阿福 cron 顶置告警)

**问题**:把 skill 主体放在 `productivity/<name>/SKILL.md` 深层而不建顶层 `~/.hermes/skills/<name>/SKILL.md` 门户 → Hermes skill loader 不递归 → cron / agent 启动时顶层出现 `[Skill(s) not found and skipped: <name>]` 告警 → 每次都查不到 → 触发决策树失效。

**2026-08-24 毛豆 cron N+40 实证案例**:`maodou-product` 在 AGENTS.md 里被列为 core skill #2,但 cron 启动时平台报 `[Skill(s) not found and skipped: maodou-product]`。原因不是文件不存在,而是**路径错误**:
- ✅ 文件真实存在:`/Users/hua/yuxin-skills/hermes/skills/maodou-product/SKILL.md`(37 KB / v1.2.0)
- ❌ 但 Hermes loader 只扫:`/Users/hua/.hermes/skills/maodou-product/SKILL.md`(顶层门户缺失)
- ⚠️ `~/yuxin-skills/hermes/skills/` 是 yuxin 团队的**并行归档库**,不是 loader 默认扫描路径

**2026-08-24 阿福 cron 16:00 第二案例(本补丁来源)**:阿福在 8:00 cron 建了顶层 `~/.hermes/skills/afu-customer-service/SKILL.md` 门户,但 16:00 cron 启动时**仍然报** `[Skill(s) not found and skipped: afu-customer-service]`。说明顶层门户虽然存在,但 loader 仍未识别。诊断路径:
- ✅ Step 1 已通过(顶层路径存在)
- ❌ Step 2 检查 description 字段 / YAML 解析失败(8:00 写的 markdown 文件首部有 `# TODO(tech-debt)` 注释行,YAML 解析器可能在解析 frontmatter 时把注释也算入 frontmatter 区域,导致 description 未被识别)
- 修复:把 `# TODO(tech-debt)` 注释行移到 frontmatter `---` 之后、markdown `#` 标题之前(避免被解析为 frontmatter 内容)

**诊断步骤(30 秒内定位是"文件不存在"、"路径不对"还是"YAML 解析失败")**:

```bash
# Step 1: 看 loader 期望的顶层路径是否存在
ls ~/.hermes/skills/<skill-name>/SKILL.md 2>/dev/null
# 存在 → loader 应能加载;如果仍报 not found → 检查 description 字段 / YAML 解析
# 不存在 → 进入 Step 2

# Step 2: 找文件实际在哪个并行归档库
find ~/yuxin-skills ~/codex-workspace ~/.cache -name "SKILL.md" -path "*<skill-name>*" 2>/dev/null
# 找到 → 在 ~/.hermes/skills/ 建 portal 即可(cp 或 symlink)
# 找不到 → 文件确实不存在,需要先生成

# Step 3: 检查 frontmatter 是否合法(被此案例坑过的字段)
head -5 ~/.hermes/skills/<skill-name>/SKILL.md
# 必须以 "---" 开头,第二行立即是 YAML 键值对,不能有 # 注释行
# 如果首行是 "# TODO(tech-debt)" 或 "# ...",说明 markdown 注释行误入 frontmatter 区域,需移到 "---" 之后

# Step 4: 同步检查其他并行归档路径(避免漏修)
ls /Users/hua/yuxin-skills/hermes/skills/ /Users/hua/.hermes/skills/ 2>/dev/null | \
  comm -23 <(ls /Users/hua/yuxin-skills/hermes/skills/ | sort) <(ls /Users/hua/.hermes/skills/ | sort)
# 输出 = "在归档但不在 loader 的 skill 列表" → 这就是需要补 portal 的清单
```

**30 秒顶层可见性自检**(每次升级 skill 后跑一次):

```bash
# 验证:声称升级的 skill 顶层入口存在
ls ~/.hermes/skills/<skill-name>/SKILL.md 2>/dev/null && \
  echo "✅ 顶层入口存在" || \
  echo "⚠️ 顶层缺失 — skill loader 找不到,必须建 portal"
```

**修复模式**(详见 yuxin-customer-service「顶层 portal 模式」节):

```
~/.hermes/skills/<skill-name>/SKILL.md            ← 顶层轻量门户(< 8 KB)
  ├─ description: 含触发场景
  ├─ 决策树("用户说 X → 用 Y")
  ├─ 技巧全图(编号 #1-#N + 1 行/技巧)
  ├─ related_skills: 关联子技能
  └─ 资源链接:~/.hermes/skills/productivity/<name>/SKILL.md
                  ~/.hermes/skills/productivity/<name>/references/*.md
```

**何时触发顶层可见性自检**:

- cron 启动时如果顶部有 `[Skill(s) not found and skipped: ...]` 告警
- 给某 profile 加新 skill 前(先确认顶层入口已存在)
- 把 skill 从深层 `productivity/` 上提到顶层时(更新所有引用路径)
- 任何 profile 跨机器同步(agent-network-classification 同步流程)后
