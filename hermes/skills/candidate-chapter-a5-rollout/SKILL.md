---
name: candidate-chapter-a5-rollout
description: 销售方法论「候选章节 / canonical body 缺失 → 升 canonical」全谱落地 SOP。**3 种类型**：(1)「候选章节 → A5 话术卡 → 升 canonical」三段式（适用 §N+1 全新候选节，如 §四十 NRS / §四十一 承诺回探 / §四十二 假设成交）；(2)「政策信号战」合并讲（§四十二 与 §三十四 合并讲 30 min）；**🆕 (3) Canonical body gap 型（§三十三 案例：references/ 已实战 + SKILL.md body 缺失 + 多处 phantom 引用 ≥ 3 处 → 跳过 A5 卡 + 跳过 9/22 试点期，直接写 canonical body 草稿 + 配套公众号 1500 字 + 抖音 60s → 送玉芬 review → 9/23 升 canonical）**。适用：小宝/xiaobao-sales SKILL.md 中所有候选节从 evolution/ 升级到 SKILL.md canonical 的全谱路径。触发：cron 自进化档写了 § N+1 候选主档（>150 行）/ 发现 SKILL.md phantom 引用某 § 章节（grep ≥ 3 处）但 body 缺失 / 销售组晚间档单独讲解 § N+1 需要载体 / 9-10 月集中积累多个候选章节按节奏推进。
license: internal-yuxin
metadata:
  author: xiaobao
  version: "1.1"
  parent_skill: xiaobao-evolution-protocol
  created: "2026-09-17 05:05"
  first_use_case: "§41 候选 · 客户承诺自证法(2026-09-17 02:35 落地候选主档 + 05:05 落地 A5 话术卡)"
  changelog_v1_1:
      - "2026-09-17 08:40 上午档实测新增 § 八 C 「Canonical body gap 型」4 步 SOP（本档首测）：本档给 §三十三 Challenger Sale TTT 写 canonical body 草稿时，发现 v1.0 SOP 只覆盖 3 种类型（全新候选节 / 政策信号战 / 客户决策心理），**没覆盖**「references/ 已实战 + SKILL.md body 缺失 + 多处 phantom 引用 ≥ 3 处」这种特殊状态。**修复 = § 八 C 4 步 SOP**：(1) grep 确认 phantom 引用次数 ≥ 3 处 + references/ 已有 → (2) 写 canonical-ready body 草稿 280-300 行落 evolution/ → (3) 同步写配套公众号 1500 字 + 抖音 60s（推送日同期落地）→ (4) 进化报告说明 + 送玉芬 review → 升 canonical。**核心差异**：(1) **不需新建 A5 卡**（references/ 已有）；(2) **不需 9/22-9/30 试点期**（references/ 已实战）；(3) **直接送玉芬 review**，跳过候选节 T+18-21 天周期。**判定命令 30 秒**：`grep -c \"§三十三\" SKILL.md` ≥ 3 + `ls references/ | grep challenger` 命中 + `grep \"^## 🎯 三十三\" SKILL.md` 未命中 = canonical body gap 型。**触发场景**：cron 自进化档发现 SKILL.md phantom 引用某 § 章节 / 9-10 月集中推进多个章节升 canonical / 公众号/抖音推送日需要补 § 章节深度文。"
      - "更新一句话内核 + frontmatter description 增补「3 种类型」描述，让未来会话一眼看到 v1.1 升级"
      - "版本号 1.0 → 1.1"
---

# 候选章节 → A5 话术卡 → 升 canonical 三段式落地 SOP

> 📌 来源:2026-09-17 05:00 cron 自进化档首次实测沉淀
> 🎯 适用:xiaobao-sales SKILL.md 中所有「候选节」从 evolution/ → templates_proposed/ → SKILL.md 的三段式落地节奏
> 🚀 战略意义:填 xiaobao-evolution-protocol v1.14 Step 2.5「小宝销售专属→沉淀本地」原则中**缺失的「候选节何时落地为卡」的中间环节**

---

## 一句话内核

> **候选主档是理论、A5 话术卡是工具、RP 演练是验证、canonical 是结论。中间任何一个环节跳过 = 候选节变「理论好看但没人会用」的死档。**
>
> **🆕 v1.1 增补**：canonical body gap 型（§三十三 案例）= references/ 已实战 + SKILL.md body 缺失 → **直接写 canonical body 草稿 + 配套公众号/抖音 → 送玉芬 review**，跳过 A5 卡 + 试点期。判定命令 30 秒。

---

## 一、三段式落地 SOP

### 阶段 1 · 候选主档落 evolution/(60-90 分钟)

| 步 | 动作 | 产物 |
|---|---|---|
| 1.1 | 扫描触发盲点(§N 共同未覆盖盲点 → §N+1 候选) | 候选节名称 + 一句话内核 |
| 1.2 | 写候选主档 200-300 行 = 5 段式(一句话内核 / 3 大场景 SOP / 3 大禁忌 / 5 落地动作 / 诚信标注 + 待验证) | `evolution/YYYY-MM-DD_HH_§N+1候选_<主题>.md` |
| 1.3 | 主档必须**显式声明候选状态**:`❌ 本档不是 canonical` + 候选期暂存 + 升 canonical 路径 | evolution/ 父目录显式标识 |
| 1.4 | 在 evolution/ 主报告(YYYY-MM-DD_HH.md)写「本档填的 1 个关键空白」+ 候选节不替代既有 §N | 父档「待玉芬 review 3 件事」必含升 canonical 决策 |

**真实案例**:§41 候选 · 客户承诺自证法(2026-09-17 02:35 cron 落地)
- 候选主档:`evolution/2026-09-17_02_§41候选_承诺回探.md` · 240 行
- 5 段式完整:一句话内核 / 3 大场景档期/预算/独占性回探 / 3 大禁忌 / 5 落地动作 / 诚信标注 5 项

### 阶段 2 · A5 话术卡落 templates_proposed/(30-45 分钟,本档新增)

| 步 | 动作 | 产物 |
|---|---|---|
| 2.1 | 把候选主档 3 大场景 SOP 压缩到 A5 双面正面 | 148×210mm 铜版纸打印版 |
| 2.2 | 反面 = 3 大禁忌 + 4 类客户适用性矩阵 + 3 段 RP 剧本(每段给评判点) | 销售组口袋装 |
| 2.3 | 文件落 `evolution/templates_proposed/script_card_<章节号>_<主题>_YYYY-MM-DD.md` | **不升** SKILL.md |
| 2.4 | 文件首行加 `⚠️ 状态:候选` + 9/22-9/30 试点期 + 9/28 Deal Review RP + 10/5 玉芬 review 升 canonical 路径 | 让 curator 知道是「实战工具」而非「升 canonical 章节」 |

**真实案例**:§41 A5 话术卡(2026-09-17 05:00 cron 落地)
- A5 卡:`evolution/templates_proposed/***SECRET***.md` · 198 行
- 正面 3 大场景 SOP(每场景 触发词 + ❌ 错误 + ✅ 黄金话术 + 关键技巧 + 联动章节)
- 反面 3 大禁忌 + 4 类客户适用性矩阵 + RP-1 苗种场改档期 / RP-2 政府项目压预算 / RP-3 A 级转介绍改供应商(每段给 ✅ 用了什么 / ❌ 不应出现什么评判点)

### 阶段 3 · 销售组 RP 验证 + 升 canonical(9/22-10/5 实战接力)

| 日期 | 动作 | 主责 |
|---|---|---|
| 候选主档落地 T+0 | 候选主档落 evolution/(本档阶段 1) | 小宝 |
| 候选主档 T+1-3 天 | A5 话术卡落 templates_proposed/(本档阶段 2) | 小宝 |
| 销售组晚 20:00 单独讲解 | 用 A5 卡讲 30 min,销售组读 3 遍 + 自选 1 客户演练 | 小宝 + 销售 A/B/C |
| T+7-15 天 | 销售组 S/A 级客户实跑候选节 | 销售 A/B/C |
| T+7 天(Deal Review) | RP 演练 3 场景(用 A5 卡反面 RP 剧本) + 即时反馈 | 全员 |
| T+18-21 天(玉芬 review) | 看 候选主档 + A5 卡 + 试点反馈 → 决策升 SKILL.md canonical | 玉芬 |
| 升 canonical | write_file xiaobao-sales SKILL.md 插入 §N+1 + 关联资源表加 A5 卡指针 | 小宝(玉芬授权后) |

---

## 二、为什么必须有「A5 话术卡」中间环节

### 没有 A5 卡会怎样

- ❌ 候选主档 200+ 行理论 → 销售组读不下去
- ❌ 销售组晚 20:00 单独讲解 = 讲理论 = 没人记得
- ❌ 9/28 Deal Review RP 演练 = 销售组即兴编 = 没评判点 = 流于形式
- ❌ 升 canonical 时实战数据空白 = 玉芬 review 没依据

### 有 A5 卡会怎样

- ✅ 销售组口袋装 = 拜访必带 = 真正进入实战
- ✅ 晚 20:00 讲解 = 拿卡读 = 30 min 讲完 3 场景 + 3 RP
- ✅ RP 演练 = A5 卡反面有评判点 = 即时反馈有依据
- ✅ 升 canonical 时 = 销售组实战胜率数据已有 + 评判点已跑通

---

## 三、A5 卡 5 大设计要素

| # | 元素 | 为什么必须 |
|---|---|---|
| 1 | **正面只放 SOP** | 销售组拜访现场 30 sec 内能翻到当前场景 |
| 2 | **反面放禁忌 + RP** | 晚 20:00 讲解 + 9/28 Deal Review RP 用 |
| 3 | **每场景给联动章节** | 销售组知道 §N+1 不是孤岛 = 与既有 §N 互补 |
| 4 | **每段 RP 给评判点** | RP 演完有反馈依据 = 避免「演完就忘」 |
| 5 | **文件首行声明候选状态 + 升 canonical 路径** | curator 一眼看出实战工具 vs 升 SKILL 章节 |

---

## 四、与 xiaobao-evolution-protocol v1.14 Step 2.5 关系

| v1.14 Step 2.5 原则 | 本档补完 |
|---|---|
| 「小宝销售专属 → 沉淀本地」| ✅ 候选主档落 evolution/(已有) |
| 「看着对但没把握 → 沉淀 evolution/,不要碰共享 SKILL.md」| ✅ 候选主档 + A5 卡都落本地,不动 SKILL.md |
| **本档补完的中间环节** | **「候选主档落完,何时 / 怎样落地为卡」** —— 没有这步 = 候选主档永远停理论 |

**关键洞察**:v1.14 Step 2.5 只规定「不要乱动 SKILL.md」,**没规定**「候选主档落地后下一步是什么」。本档填这个空白 = 候选节从「理论好看」到「实战能用」的关键过渡。

---

## 五、与 xiaobao-sales SKILL.md § 二十八 Skill 维护 pitfall 关系

| § 二十八 pitfall | 本档补完 |
|---|---|
| P-2 裸 write_file canonical SKILL.md 被 cross-profile guard 拦 | ✅ 本档阶段 3 升 canonical 走 skill_manage write_file(玉芬 review 后) |
| P-1 skill_manage patch 返回错 file_preview | ✅ 升 canonical 时用 read_file 验证,不靠 file_preview |
| P-6 跨 profile 污染其他 profile | ✅ 候选主档 + A5 卡都落 profile 内 evolution/,不污染 |

---

## 六、9 月集中落地节奏(2026-09-17 至 10-05)

| 日期 | 阶段 | 候选节 | 主档 | A5 卡 |
|---|---|---|---|---|
| 09-13 03:00 | 已升 canonical | §三十 假设成交法 | evolution/2026-09-13_03 | templates_proposed/assumptive_close_30 |
| 09-13 04:33 | 已升 canonical | §三十一 失单再激活 | references/***SECRET*** | templates_proposed/***SECRET*** |
| 09-14 02:35 | 已升 canonical | §四十 NRS(Negative Reverse Selling) | references/negative-reverse-selling-ras | templates_proposed/***SECRET*** |
| 09-17 02:35 | 候选主档已落地 | §四十一 承诺回探 | evolution/2026-09-17_02_§41候选_承诺回探.md | (待 A5 卡) |
| 09-17 05:00 | A5 卡落地(本档首测) | §四十一 承诺回探 | 同上 | **templates_proposed/***SECRET***.md ✅** |
| **09-17 06:00** | **候选主档落地(新)** | **§四十二 首都级政策信号增补包** | **evolution/***SECRET***.md ✅** | (待 A5 卡 · 06:30 cron 出) |
| 09-22 晚 20:00 | 销售组单独讲解 | §四十一 承诺回探 | — | 用 A5 卡 |
| 09-22 晚 20:30 | 销售组单独讲解 | §四十二 首都级(与 §三十四合并讲 30 min) | — | 待 A5 卡 |
| 09-28 周一 | Deal Review RP 演练 | §四十一 承诺回探 | — | 用 A5 卡反面 RP-1/2/3 |
| 10-05 周日 | 玉芬 review + 升 canonical | §四十一 承诺回探 + §四十二 首都级 | 写 SKILL.md §四十一 + §四十二 | A5 卡入关联资源表 |

---

## 七、3 大常见反模式 ⚠️

| ❌ 反模式 | 后果 | ✅ 正解 |
|---|---|---|
| 候选主档直接写 SKILL.md canonical | 玉芬没 review = 跳过验证 + 污染共享 skill | 主档暂存 evolution/ → A5 卡暂存 templates_proposed/ → 实战接力 → 玉芬 review → 升 canonical |
| 候选主档落地后**不写 A5 卡** | 销售组晚 20:00 讲解无载体 = 候选节永远停理论 | 主档落完 T+1-3 天必出 A5 卡 |
| A5 卡写得很详细但**没有评判点** | RP 演完没反馈 = 流于形式 | 每段 RP 必给「✅ 用了什么 / ❌ 不应出现什么」 |

---

## 八、诚信标注(本档首测待验证)

- ⚠️ **A5 卡 vs A4 卡**:本档默认 A5 双面(148×210mm)。若 RP 演练场景超 5 段,可升级 A4 单页(210×297mm)装销售组桌面上
- ⚠️ **9/22 销售组单独讲解 §41 用 A5 卡效果**:首次实跑,9/22-9/30 试点期回填
- ⚠️ **9/28 RP 演练 3 段剧本命中率**:本档主观设计,需 9/28 实跑后微调
- ⚠️ **A5 卡 vs 公众号草稿 vs 抖音脚本 三者关系**:本档不展开,留待下次 cron

### 八 C、§三十三 例外类型 · Canonical body 缺失型(2026-09-17 08:40 新增)

> 📌 **新发现的第 4 种候选节类型**：**Canonical body gap** —— SKILL.md 多处引用某 § 编号，但 body 章节本身缺失（在 `references/` + `evolution/` 有完整内容，但 canonical 章节不存在）。
> ⚠️ 本节填空白：原 § 一-§ 八 SOP 默认候选节是"全新内容"型（§N+1 未存在），**没明确**「已存在 references/ 但 body 章节缺失」这种特殊落地路径。

**判定准则**（何时按"canonical body 缺失型"处理）：

```
在 xiaobao-sales SKILL.md 中 grep "§三十三"
   ↓
命中 ≥ 3 处（说明该章节被多处引用）
   ↓
ls /Users/hua/.hermes/profiles/xiaobao/references/ | grep "challenger\|TTT"
   ↓
命中（说明 references/ 已有完整内容）
   ↓
ls /Users/hua/.hermes/skills/sales/xiaobao-sales/SKILL.md | grep "^## 🎯 三十三"
   ↓
未命中（说明 canonical body 缺失）
   ↓
= Canonical body gap 类型
```

**与既有 3 种类型的差异**：

| # | 维度 | 全新内容型（§三十/§四十）| 政策信号战型（§四十二）| **Canonical body gap 型（§三十三，本档首测）** |
|---|---|---|---|---|
| 1 | **references/ 状态** | 无 | 无 | **有完整内容**（已沉淀 9/15）|
| 2 | **SKILL.md 引用** | 0 处 | 0 处 | **≥ 3 处（§三十/§三十一/§三十四 多处引用 §三十三）** |
| 3 | **canonical body** | 缺失 | 缺失 | **缺失（phantom 引用）** |
| 4 | **升级路径** | 候选→A5→升 canonical（§六 流程）| 候选→合并既有章 | **canonical-ready body 草稿（不需走候选）→ 玉芬 review → 升 canonical** |
| 5 | **配套产出** | A5 卡 + 销售组 RP | A5 卡（合并讲）| **canonical body + 公众号 1500 字 + 抖音 60s 三件套（9/22 推送同期）** |
| 6 | **timeline** | 候选 T+18-21 天（玉芬 review）| 与 §三十四 合讲 | **canonical body 写完即可送 review（不等 18 天）** |

**4 步 SOP（本档首测沉淀）**：

| 步 | 动作 | 产物 |
|---|---|---|
| 1 | grep 确认 SKILL.md 引用次数 ≥ 3 处 + references/ 已有完整内容 | 缺口确认 |
| 2 | 写 canonical-ready body 草稿（参考 references/ 主档结构，280-300 行） | `evolution/skill_section_<章节号>_<主题>_canonical_body_<日期>.md` |
| 3 | 同时写配套公众号 1500 字 + 抖音 60s（推送日提前预告）| `evolution/templates_proposed/wechat_article_<章节号>_<主题>_<推送日>.md` + `douyin_60s_<章节号>_<主题>_<推送日>.md` |
| 4 | 进化报告说明本档填的空白 + 建议升 canonical 时间 | evolution/YYYY-MM-DD_HH.md |

**本档首测案例**：§三十三 Challenger Sale TTT（2026-09-17 08:40 cron）
- grep SKILL.md 命中 §三十三 引用 ≥ 5 处（§三十/§三十一/§三十四/§二十二/§二十六/§三十五/§四十二）
- references/ 已有 `***SECRET***.md` 201 行
- SKILL.md body 缺失 → canonical body 草稿 280 行（`evolution/***SECRET***.md`）
- 配套公众号 1500 字 + 抖音 60s（9/22 推送）
- 建议 9/22 玉芬 review 后 9/23 写入 canonical

**与本档原 §一-§七 SOP 关系**：
- 阶段 1（候选主档落 evolution/）= 本档 step 2（canonical body 草稿）
- 阶段 2（A5 卡落 templates_proposed/）= 本档 step 3（公众号 + 抖音）+ 已有 references/ = A5 卡（无需新建）
- 阶段 3（销售组 RP + 升 canonical）= 本档 step 4（送玉芬 review）
- **本质差异**：本类型**不需新建 A5 卡**（references/ 已有），**不需 9/22-9/30 试点期**（references/ 已实战），**直接送玉芬 review 升 canonical**

**3 大常见反模式 ⚠️**：

| ❌ 反模式 | 后果 | ✅ 正解 |
|---|---|---|
| 直接 write_file SKILL.md 写 § 三十三 body | 跨 profile guard 拦截（P-6）+ 污染其他 profile | 写 canonical body 草稿 evolution/，等玉芬 review |
| canonical body 写完就以为工作结束 | § 三十三 还是没销售组实战 = 死档 | 同步写公众号 + 抖音（9/22 推送）= 实战验证 |
| 等候选节 T+18-21 天升 canonical 流程 | 浪费 18 天（references/ 已有 = 已实战）| 直接送玉芬 review（无需 9/22 试点期）|

**触发判定命令**（30 秒）：

```bash
# 1. 查 SKILL.md 引用某 § 的次数
grep -c "§三十三" /Users/hua/.hermes/skills/sales/xiaobao-sales/SKILL.md
# 命中 ≥ 3 = candidate body gap 类型

# 2. 查 references/ 是否有完整内容
ls /Users/hua/.hermes/profiles/xiaobao/references/ | grep -i "challenger\|TTT"
# 命中 = 已实战，可直接写 canonical body 草稿

# 3. 查 SKILL.md 是否已有该章节 body
grep "^## 🎯 三十三" /Users/hua/.hermes/skills/sales/xiaobao-sales/SKILL.md
# 未命中 = canonical body 缺失
```

### 八 B、§四十二 例外类型 · 政策信号战候选(2026-09-17 06:00 新增)

> 📌 §四十二「首都级」政策信号增补包 = §四十一「承诺回探」之外的**第二种候选节类型** ——「政策/信号战」型(不像 §三十/§三十一/§四十一 那种"客户决策心理"型,更像 §二十六/§三十四「信号工程」型)。
> ⚠️ **本节填空白**:本档原 §一-§七 SOP 默认候选节是"客户决策心理型"(承诺/成交/失单再激活),**未明确**政策信号战型候选节的差异落地路径。

| # | 维度 | 客户决策心理型(§三十 / §三十一 / §四十一) | 政策信号战型(§二十六 / §三十四 / §四十二) |
|---|---|---|---|
| 1 | **触发场景** | 客户说"再考虑"/"我们选了别家" | 政策印发/巨头入场/竞品爆款 |
| 2 | **销售动作** | 话术换框 + 客户心理侧 | 借势锚定 + 政策杠杆 |
| 3 | **候选主档内容** | 3 大场景话术 + 客户反对点 | 3 招借势 + 政策窗口期 |
| 4 | **A5 卡设计** | 正面场景 SOP / 反面 RP 剧本 | 正面借势话术 / 反面客户话术对比 + 销售组 RP(同 §四十一) |
| 5 | **升 canonical 路径** | 销售组单练 → 9/22 单独讲解 → 9/28 RP | **与既有政策信号章合并讲解**(§四十二 与 §三十四 合讲 30 min) |
| 6 | **联动关系** | 替代/升级既有异议处理章 | **与既有信号章成"双子星"**(不替代,补强) |

> 📌 **实操结论**:政策信号战型候选节升 canonical 时,**不单独占一节**,而是**与既有信号章合并讲解**(节省 Deal Review 议程时间)。§四十二 候选 → 若玉芬 review 通过 → 升 canonical 时建议并入 §三十四(双国资版:山东 + 首都),而非独立 §四十二。

---

## 九、关联文件

| 文件 | 用途 |
|---|---|
| `xiaobao-evolution-protocol` SKILL.md v1.14 | Step 2.5「不强行 PATCH skill」工作流原则 |
| `xiaobao-evolution-protocol/references/skill-rotation-table.md` | 5 大类 × 已建 × 待建矩阵(候选节归哪一类用) |
| `xiaobao-sales` SKILL.md § 二十八 | Skill 维护 pitfall 实测升级版(候选升 canonical 的工具路径) |
| `xiaobao-sales` SKILL.md § 四十 NRS | 已升 canonical 候选节实战案例(本档首测前) |
| `evolution/2026-09-17_02_§41候选_承诺回探.md` | §四十一 候选主档(本档首测源材料) |
| `evolution/templates_proposed/***SECRET***.md` | §四十一 A5 话术卡(本档首测产物) |

---

> 📝 最后更新:2026-09-17 05:05 v1.0 · 候选章节 → A5 话术卡 → 升 canonical 三段式 SOP 首测落地
> 📝 最后更新:2026-09-17 08:40 v1.1 · 增补 § 八 C 「Canonical body gap 型」4 步 SOP（§三十三 Challenger Sale TTT 首测案例）+ 一句话内核 + frontmatter description 同步升级
> 📌 暂存:`~/.hermes/profiles/xiaobao/evolution/2026-09-17_05.md`(本档主报告)
> 📌 配套:`~/.hermes/profiles/xiaobao/evolution/templates_proposed/***SECRET***.md`(§41 A5 卡首测产物)
> 🔄 下一轮迭代(预计 09-22 晚 20:30):§41 销售组单独讲解反馈 + A5 卡微调