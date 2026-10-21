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


## 已外置章节索引

以下 10 节已外置到 references/split_overflow.md（超90KB瘦身，内容零丢失）：
- §11 三处同步铁律(2026-08-25 阿福 cron 元数据漂移实战新增)
- §12 frontmatter version 字段与 changelog 同步铁律(2026-08-25 新增)
- §13 升级后版本号三方核验脚本(替代手工 grep,2026-08-25 新增)
- §14 changelog 内部完整性铁律(2026-08-25 新增)
- 启动 30 秒自检(强制,首次 cron 必跑)
- 配套文件
- 反面警示
- 触发关键词
- 适用范围
- 顶层可见性铁律(坑 26,2026-08-24 阿福 cron 顶置告警)
