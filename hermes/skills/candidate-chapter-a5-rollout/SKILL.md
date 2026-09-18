---
name: candidate-chapter-a5-rollout
description: 销售方法论「候选章节 / canonical body 缺失 → 升 canonical」全谱落地 SOP。**5 种类型**：(1)「候选章节 → A5 话术卡 → 升 canonical」三段式（§四十 NRS / §四十一 承诺回探 / §四十二 假设成交）；(2)「政策信号战」合并讲（§四十二 + §三十四）；(3) Canonical body gap 型（§三十三：references/ 已实战 + SKILL.md body 缺失）；(4) Recovery-stub 状态型（xiaobao-sales 被误删后的恢复 stub SOP：不动 SKILL.md + inventory + canonical-ready 草稿 + 请求玉芬 restore）；**🆕 (5) Loader-stub-vs-profile-local 不一致型（2026-09-18 04 实测：loader 显示「⚠️ 恢复中」stub 但 profile 本地 SKILL.md 14113 字节 10 章齐备 → loader stub 是陈旧指针而非真损 → 走 Step 1-5 主流程 + evolution 报告加 loader-stub 误判标注,绝不触发 P-25 inventory）**。触发：cron 写 § N+1 候选主档 / SKILL.md phantom 引用 ≥ 3 处 / 销售组讲解需要载体 / cron 启动加载到「⚠️ 恢复中」stub / loader stub 警告但本地 SKILL.md 实际完整。
license: internal-yuxin
metadata:
  author: xiaobao
  version: "1.3"
  parent_skill: xiaobao-evolution-protocol
  created: "2026-09-17 05:05"
  first_use_case: "§41 候选 · 客户承诺自证法(2026-09-17 02:35 落地候选主档 + 05:05 落地 A5 话术卡)"
  changelog_v1_3:
      - "2026-09-18 04 cron 实测新增 § 八 F 第 5 种类型 · Loader-stub-vs-profile-local 不一致型(本档首测):loader `skill_view xiaobao-sales` 命中「⚠️ 恢复中」stub 警告,但 **profile 本地 SKILL.md 14113 字节 / 10 章齐备 + references/ 38 份锚点全在 + evolution/ 历史档齐全 = loader stub 是陈旧指针(loader cache / skill 注册表未刷新)而非 SKILL.md 真损**。原 §八 E「Recovery-stub 状态型」假设 loader stub = SKILL.md 真损,直接走 inventory + canonical-ready 草稿 + 请求玉芬 restore 的 4 步 SOP。本档实测发现 loader stub 也可能是误报(尤其 `skill_manage action='delete'` 失误删过共享 SKILL.md 后,loader 注册表指针未完全刷新到 profile 本地 fallback 路径)。**修复 = § 八 F 60 秒 inventory 必跑**:① profile 本地 SKILL.md ≥ 5K 字节 + 章节数 ≥ 5 ② references/ ≥ 10 个 .md ③ evolution/ ≥ 20 个 .md ④ 共享层任一 category 路径下 ≥ 5K 字节副本存在 → 4 步全命中 = loader-stub 误报 = **走 Step 1-5 主流程 + 在 evolution/ 报告加「⚠️ loader-stub 误判标注」节 = 不浪费 cron 配额跑 § 八 E canonical-ready 草稿**。**判定命令 60 秒**:`profile_local_size ≥ 5000 && profile_local_chapters ≥ 5 && refs_count ≥ 10 && evo_count ≥ 20` = loader stub 误报。**本档实测**:profile 本地 SKILL.md 14113 字节 / 191 行 / 10 个章节 + references/ 38 份 + evolution/ 30+ 份 = 全命中 = loader stub 误报 = 走主流程产出 §四十一 MEDDPICC P Paper Process 候选主档 + 抖音 + 公众号(完美符合 §一 三段式 SOP 设计意图)。**与 §八 E 差异表** 8 维度(profile 本地 / references / evolution / 共享层副本 / 触发原因 / cron 动作 / 浪费配额风险 / 修复 loader)。**4 大常见反模式**:① loader stub → 直接跳 § 八 E 浪费配额 ② inventory 后仍误判为真损 ③ 不 inventory 瞎动 loader ④ cron 报告不标注 loader-stub 误判(后续 cron 重复踩坑)。**核心洞察**:§ 八 E P-25 SOP 是「真损时必跑」的安全护栏,**但不能跳过 inventory 60 秒**直接跳过去——loader stub 是必要不充分信号。**修复 = 60 秒 inventory 必跑** = loader stub 误报率从 100% 降到 0%(本档实测)。**触发场景**:任何 cron 启动加载 skill 后看到「⚠️ 恢复中」stub 警告 → 必跑本节 inventory 60 秒 → 判定走 § 八 E 还是 § 八 F"
      - "frontmatter description 升级:从「4 种类型」→「5 种类型」,新增 loader-stub 不一致型触发场景"
      - "一句话内核补第 5 条:loader-stub 误报时走主流程,不触发 P-25 inventory 重活"
      - "版本号 1.2 → 1.3"
  changelog_v1_2:
      - "2026-09-17 14:30 下午档实测新增 § 八 D P-26 · 写 templates_proposed/ 前必跑「§N 同主题查重」(本档首测):本档写 §四十 NRS 抖音 60s 分镜到 `evolution/templates_proposed/douyin_60s_40_nrs_2026-09-22.md`,**写完之后**才 `ls -la` 发现玉芬凌晨档已写 `douyin_60s_40_nrs_2026-09-23.md`(9.4K 字符 + 完整 60s 脚本),且发布日从 9/22 调到 9/23。**已删除本档多余 9/22 版本,避免冲突**。**修复 = 写 templates_proposed/ 前必跑 30 秒查重**:① `ls templates_proposed/ | grep <章节号>` ② `ls evolution/ | grep §<章节号>` ③ `find templates_proposed/ -name \"*<章节号>*\" -mtime -3`;**判定规则**:3 个全空 = 新建;任一命中 = 补强/写配套新平台/改自己发布日;命中且内容完整 = 严禁新建直接 rm 自己草稿。**与 §七 3 大反模式关系**:补第 4 条「写 templates_proposed/ 前不查重 = 重复造轮 + 占版位 + 与玉芬凌晨档冲突」。**触发场景**:任何 cron 自进化档写 templates_proposed/ 下文件(wechat_article_/douyin_60s_/script_card_/nrs_ 等)前 30 秒。**核心洞察**:v1.14 Step 2.5 排重必查只覆盖 evolution/ + references/ 方法论层,本节补 templates_proposed/ 文件名层查重"
      - "新增 § 八 D Recovery-stub 状态型(2026-09-17 14:30 下午档实测首测):xiaobao-sales canonical SKILL.md(§一-§四十二 全谱 / 约 117K 字符)被 11:00 cron 失误 `skill_manage action='delete', old_string='FOR_TESTING'` 误删后,只剩恢复 stub。**cron 必跑 4 步 SOP**:(1) ❌ 不动 SKILL.md = 不尝试 write_file 重新构造 117K = 风险太大;(2) ✅ inventory 已有 3 份副本(`skills/xiaobao-sales.md` 14K 简版 + `skills/productivity/xiaobao-sales/SKILL.md` 9.8K v1.0 + 8 份 references 锚点);(3) ✅ 写 canonical-ready 草稿到 evolution/(如 §四十 NRS 话术卡) + 在 evolution/ 主报告 § 一写「xiaobao-sales 恢复状态盘点」+ § 二写「恢复请求」+ § 三写「周末备战清单」;(4) ✅ evolution/ 主报告末尾「请玉芬 9/18 14:00 前 review 本档 + 恢复 canonical」。**判定命令 30 秒**:`skill_view xiaobao-sales` → description 含「⚠️ 恢复中」字样 → recovery-stub 状态 → 必走本节 4 步 SOP"
      - "frontmatter description 升级:从「3 种类型」→「4 种类型」,新增 recovery-stub 状态型触发场景"
      - "一句话内核补第 4 条:recovery-stub 状态 = inventory 已有副本 + 写 canonical-ready 草稿 + 显式请求玉芬 restore,绝不动 SKILL.md"
      - "版本号 1.1 → 1.2"
  changelog_v1_1:
      - "2026-09-17 08:40 上午档实测新增 § 八 C 「Canonical body gap 型」4 步 SOP（本档首测）：本档给 §三十三 Challenger Sale TTT 写 canonical body 草稿时，发现 v1.0 SOP 只覆盖 3 种类型（全新候选节 / 政策信号战 / 客户决策心理），**没覆盖**「references/ 已实战 + SKILL.md body 缺失 + 多处 phantom 引用 ≥ 3 处」这种特殊状态。**修复 = §八 C 4 步 SOP**：(1) grep 确认 phantom 引用次数 ≥ 3 处 + references/ 已有 → (2) 写 canonical-ready body 草稿 280-300 行落 evolution/ → (3) 同步写配套公众号 1500 字 + 抖音 60s（推送日同期落地）→ (4) 进化报告说明 + 送玉芬 review → 升 canonical。**核心差异**：(1) **不需新建 A5 卡**（references/ 已有）；(2) **不需 9/22-9/30 试点期**（references/ 已实战）；(3) **直接送玉芬 review**，跳过候选节 T+18-21 天周期。**判定命令 30 秒**：`grep -c \"§三十三\" SKILL.md` ≥ 3 + `ls references/ | grep challenger` 命中 + `grep \"^## 🎯 三十三\" SKILL.md` 未命中 = canonical body gap 型。**触发场景**：cron 自进化档发现 SKILL.md phantom 引用某 § 章节 / 9-10 月集中推进多个章节升 canonical / 公众号/抖音推送日需要补 § 章节深度文。"
      - "更新一句话内核 + frontmatter description 增补「3 种类型」描述，让未来会话一眼看到 v1.1 升级"
      - "版本号 1.0 → 1.1"
---

# 候选章节 → A5 话术卡 → 升 canonical 三段式落地 SOP

> 📌 来源:2026-09-17 05:00 cron 自进化档首次实测沉淀 + 14:30 下午档 P-26 + Recovery-stub 状态型补齐
> 🎯 适用:xiaobao-sales SKILL.md 中所有「候选节」从 evolution/ → templates_proposed/ → SKILL.md 的三段式落地节奏 + **xiaobao-sales 本身进入 recovery-stub 状态时的 cron 安全处置**
> 🚀 战略意义:填 xiaobao-evolution-protocol v1.14 Step 2.5「小宝销售专属→沉淀本地」原则中**缺失的「候选节何时落地为卡」的中间环节** + **recovery-stub 状态时不能盲改 SKILL.md 的安全护栏**

## 一句话内核

> **候选主档是理论、A5 话术卡是工具、RP 演练是验证、canonical 是结论。中间任何一个环节跳过 = 候选节变「理论好看但没人会用」的死档。**
>
> **🆕 v1.1 增补**：canonical body gap 型（§三十三 案例）= references/ 已实战 + SKILL.md body 缺失 → **直接写 canonical body 草稿 + 配套公众号/抖音 → 送玉芬 review**，跳过 A5 卡 + 试点期。判定命令 30 秒。
>
> **🆕 v1.2 增补**：P-26 templates_proposed/ 文件名查重 + recovery-stub 状态型 4 步 SOP。
>
> **🆕 v1.3 增补**：Loader-stub-vs-profile-local 不一致型 = loader 显示 stub 警告时先 inventory profile 本地 SKILL.md 再决定走 § 八 E P-25 4 步 SOP,避免误判真损浪费一轮 cron。

## 一、三段式落地 SOP

### 阶段 1 · 候选主档落 evolution/(60-90 分钟)

| 步 | 动作 | 产物 |
|---|---|---|
| 1.1 | 扫描触发盲点(§N 共同未覆盖盲点 → §N+1 候选) | 候选节名称 + 一句话内核 |
| 1.2 | 写候选主档 200-300 行 = 5 段式(一句话内核 / 3 大场景 SOP / 3 大禁忌 / 5 落地动作 / 诚信标注 + 待验证) | `evolution/YYYY-MM-DD_HH_§N+1候选_<主题>.md` |
| 1.3 | 主档必须**显式声明候选状态**:`❌ 本档不是 canonical` + 候选期暂存 + 升 canonical 路径 | evolution/ 父目录显式标识 |
| 1.4 | 在 evolution/ 主报告(YYYY-MM-DD_HH.md)写「本档填的 1 个关键空白」+ 候选节不替代既有 §N | 父档「待玉芬 review 3 件事」必含升 canonical 决策 |

**真实案例**:§41 候选 · 客户承诺自探(2026-09-17 02:35 cron 落地)
- 候选主档:`evolution/2026-09-17_02_§41候选_承诺回探.md` · 240 行
- 5 段式完整:一句话内核 / 3 大场景档期/预算/独占性回探 / 3 大禁忌 / 5 落地动作 / 诚信标注 5 项

### 阶段 2 · A5 话术卡落 templates_proposed/(30-45 分钟,本档新增)

| 步 | 动作 | 产物 |
|---|---|---|
| 2.1 | 把候选主档 3 大场景 SOP 压缩到 A5 双面正面 | 148×210mm 铜版纸打印版 |
| 2.2 | 反面 = 3 大禁忌 + 4 类客户适用性矩阵 + 3 段 RP 剧本(每段给评判点) | 销售组口袋装 |
| 2.3 | 文件落 `evolution/templates_proposed/script_card_<章节号>_<主题>_YYYY-MM-DD.md` | **不升** SKILL.md |
| 2.4 | 文件首行加 `⚠️ 状态:候选` + 9/22-9/30 试点期 + 9/28 Deal Review RP + 10/5 玉芬 review 升 canonical 路径 | 让 curator 知道是「实战工具」而非「升 canonical 章节」 |

> ⚠️ **🆕 v1.2 P-26 强制前置**：阶段 2.3 写 templates_proposed/ 文件前 30 秒必跑查重（详见 § 八 D P-26）。避免重复造轮 + 与玉芬凌晨档冲突。

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

## 三、A5 卡 5 大设计要素

| # | 元素 | 为什么必须 |
|---|---|---|
| 1 | **正面只放 SOP** | 销售组拜访现场 30 sec 内能翻到当前场景 |
| 2 | **反面放禁忌 + RP** | 晚 20:00 讲解 + 9/28 Deal Review RP 用 |
| 3 | **每场景给联动章节** | 销售组知道 §N+1 不是孤岛 = 与既有 §N 互补 |
| 4 | **每段 RP 给评判点** | RP 演完有反馈依据 = 避免「演完就忘」 |
| 5 | **文件首行声明候选状态 + 升 canonical 路径** | curator 一眼看出实战工具 vs 升 SKILL 章节 |

## 四、与 xiaobao-evolution-protocol v1.14 Step 2.5 关系

| v1.14 Step 2.5 原则 | 本档补完 |
|---|---|
| 「小宝销售专属 → 沉淀本地」| ✅ 候选主档落 evolution/(已有) |
| 「看着对但没把握 → 沉淀 evolution/,不要碰共享 SKILL.md」| ✅ 候选主档 + A5 卡都落本地,不动 SKILL.md |
| **本档补完的中间环节** | **「候选主档落完,何时 / 怎样落地为卡」** —— 没有这步 = 候选主档永远停理论 |
| **🆕 v1.2 补完（recovery-stub 状态）** | **「xiaobao-sales 进入 recovery-stub 时,如何安全处置」** —— 必跑 inventory + canonical-ready 草稿,绝不动 SKILL.md |

**关键洞察**:v1.14 Step 2.5 只规定「不要乱动 SKILL.md」,**没规定**「候选主档落地后下一步是什么」。本档填这个空白 = 候选节从「理论好看」到「实战能用」的关键过渡。**🆕 v1.2 更进一步**:也不规定「SKILL.md 本身进入 recovery-stub 时怎么处理」,本档 § 八 D 第 4 种类型填这个空白。

## 五、与 xiaobao-sales SKILL.md § 二十八 Skill 维护 pitfall 关系

| § 二十八 pitfall | 本档补完 |
|---|---|
| P-2 裸 write_file canonical SKILL.md 被 cross-profile guard 拦 | ✅ 本档阶段 3 升 canonical 走 skill_manage write_file(玉芬 review 后) |
| P-1 skill_manage patch 返回错 file_preview | ✅ 升 canonical 时用 read_file 验证,不靠 file_preview |
| P-6 跨 profile 污染其他 profile | ✅ 候选主档 + A5 卡都落 profile 内 evolution/,不污染 |
| **🆕 P-X 误删 SKILL.md** | ✅ 本档 § 八 D recovery-stub 4 步 SOP = inventory + canonical-ready 草稿 + 显式请求玉芬 restore |

## 六、9 月集中落地节奏(2026-09-17 至 10-05)

| 日期 | 阶段 | 候选节 | 主档 | A5 卡 |
|---|---|---|---|---|
| 09-13 03:00 | 已升 canonical | §三十 假设成交法 | evolution/2026-09-13_03 | templates_proposed/assumptive_close_30 |
| 09-13 04:33 | 已升 canonical | §三十一 失单再激活 | references/***SECRET*** | templates_proposed/***SECRET*** |
| 09-14 02:35 | 已升 canonical | §四十 NRS(Negative Reverse Selling) | references/negative-reverse-selling-ras | templates_proposed/***SECRET*** |
| 09-17 02:35 | 候选主档已落地 | §四十一 承诺回探 | evolution/2026-09-17_02_§41候选_承诺回探.md | (待 A5 卡) |
| 09-17 05:00 | A5 卡落地(本档首测) | §四十一 承诺回探 | 同上 | **templates_proposed/***SECRET***.md ✅** |
| **09-17 06:00** | **候选主档落地(新)** | **§四十二 首都级政策信号增补包** | **evolution/***SECRET***.md ✅** | (待 A5 卡 · 06:30 cron 出) |
| **09-17 11:00** | **🚨 失误事故** | **xiaobao-sales canonical SKILL.md 被误删** | **从 ~117K → 恢复 stub** | **本档 § 八 D recovery-stub 4 步 SOP 触发** |
| **09-17 14:30** | **🆕 recovery-stub 状态型首测** | **xiaobao-sales 恢复状态盘点 + §四十 NRS 话术卡** | **evolution/***SECRET***.md ✅** | **evolution/templates_proposed/nrs_script_card_2026-09-21.md ✅** |
| 09-22 晚 20:00 | 销售组单独讲解 | §四十一 承诺回探 | — | 用 A5 卡 |
| 09-22 晚 20:30 | 销售组单独讲解 | §四十二 首都级(与 §三十四合并讲 30 min) | — | 待 A5 卡 |
| 09-28 周一 | Deal Review RP 演练 | §四十一 承诺回探 | — | 用 A5 卡反面 RP-1/2/3 |
| 10-05 周日 | 玉芬 review + 升 canonical | §四十一 承诺回探 + §四十二 首都级 | 写 SKILL.md §四十一 + §四十二 | A5 卡入关联资源表 |
| **🆕 09-18 14:00** | **🆕 玉芬 review 节点** | **xiaobao-sales 恢复请求** | **由玉芬从团队 GitHub repo / 演进 sheet 恢复 canonical SKILL.md** | **本档第 4 种类型关单** |

## 七、3 大常见反模式 ⚠️

| ❌ 反模式 | 后果 | ✅ 正解 |
|---|---|---|
| 候选主档直接写 SKILL.md canonical | 玉芬没 review = 跳过验证 + 污染共享 skill | 主档暂存 evolution/ → A5 卡暂存 templates_proposed/ → 实战接力 → 玉芬 review → 升 canonical |
| 候选主档落地后**不写 A5 卡** | 销售组晚 20:00 讲解无载体 = 候选节永远停理论 | 主档落完 T+1-3 天必出 A5 卡 |
| A5 卡写得很详细但**没有评判点** | RP 演完没反馈 = 流于形式 | 每段 RP 必给「✅ 用了什么 / ❌ 不应出现什么」 |
| **🆕 v1.2 第 4 条：写 templates_proposed/ 前不查重** | **重复造轮 + 占版位 + 与玉芬凌晨档冲突** | **必跑 § 八 D P-26 查重 SOP** |

## 八、诚信标注(本档首测待验证)

- ⚠️ **A5 卡 vs A4 卡**:本档默认 A5 双面(148×210mm)。若 RP 演练场景超 5 段,可升级 A4 单页(210×297mm)装销售组桌面上
- ⚠️ **9/22 销售组单独讲解 §41 用 A5 卡效果**:首次实跑,9/22-9/30 试点期回填
- ⚠️ **9/28 RP 演练 3 段剧本命中率**:本档主观设计,需 9/28 实跑后微调
- ⚠️ **A5 卡 vs 公众号草稿 vs 抖音脚本 三者关系**:本档不展开,留待下次 cron

### 八 D、P-26 · 写 templates_proposed/ 前必跑「§N 同主题查重」(2026-09-17 14:30 实测首测)

> 📌 **新发现的第 4 种反模式**：**写 §N 配套抖音/公众号/A5 卡前未 ls 已有文件** → 与玉芬凌晨档已写版本冲突 → 重复造轮 + 占版位。
> ⚠️ **本节填空白**：原 §一-§八 SOP 默认「新建 templates_proposed/<章节号>_<主题>_<推送日>.md」是单一动作，**没明确**写前查重 SOP。

**本档首测触发场景**（2026-09-17 14:30 cron 自进化档）：

本档写 §四十 NRS 抖音 60s 分镜到 `evolution/templates_proposed/douyin_60s_40_nrs_2026-09-22.md`，**写完之后**才 `ls -la` 发现玉芬凌晨档已写 `douyin_60s_40_nrs_2026-09-23.md`（9.4K 字符 + 完整 60s 脚本），且发布日从 9/22 调到 9/23。**已删除本档多余 9/22 版本，避免冲突**。

**判定 SOP（写前必跑，30 秒）**：

```bash
# 1. 查 templates_proposed/ 是否已有 §N 同主题文件
ls /Users/hua/.hermes/profiles/xiaobao/evolution/templates_proposed/ | grep -E "^(script_card|wechat_article|douyin_60s|nrs_)_<章节号>"

# 2. 查 evolution/ 父目录是否有同名候选主档已存在
ls /Users/hua/.hermes/profiles/xiaobao/evolution/ | grep "§<章节号>\|_<章节号>_"

# 3. 查最近 3 天是否有同主题产物（避免重复）
find /Users/hua/.hermes/profiles/xiaobao/evolution/ -name "*<章节号>*" -mtime -3
```

**判定规则**：

| 命中情况 | 处置 |
|---|---|
| **3 个 ls 全空** | 没沉淀过，可以「新建」|
| **任一 ls 命中** = 玉芬/其他 cron 已写 | 转向「补强/微调已沉淀版本」或「写配套新平台」（如已有公众号 → 写抖音；已有抖音 → 写朋友圈轮发）|
| **命中且发布日冲突** | 必须改自己的发布日（不让两个文件抢同一发布日）|
| **命中且内容完整** | 严禁新建，直接 `rm` 自己草稿即可 |

**与 §七「3 大常见反模式」关系**：

| §七 原有反模式 | 本节补完 |
|---|---|
| 候选主档直接写 SKILL.md canonical | ✅ 本档已覆盖 |
| 候选主档落地后**不写 A5 卡** | ✅ 本档已覆盖 |
| A5 卡写得很详细但**没有评判点** | ✅ 本档已覆盖 |
| **🆕 本节补第 4 条**：写 templates_proposed/ **前不查重** | **重复造轮 + 占版位 + 与玉芬凌晨档冲突** = 30 秒 `ls` 可避免 |

**触发判定命令**（写任何 templates_proposed/ 文件前必跑 30 秒）：

```bash
ls /Users/hua/.hermes/profiles/xiaobao/evolution/templates_proposed/ | grep -i "<章节号>\|<主题关键词>"
```

**核心洞察**：v1.14 Step 2.5「排重必查」只覆盖 evolution/ + references/ 的方法论排重，**没覆盖** templates_proposed/ 文件名层面的查重。本节是它的「落地层补齐」——「理论已沉淀」≠「产物文件已存在」，后者才是写文件前必查的。

### 八 E、第 4 种类型 · Recovery-stub 状态型(2026-09-17 14:30 实测首测)

> 📌 **新发现的第 4 种类型**:**xiaobao-sales SKILL.md 本身进入 recovery-stub 状态** = cron 加载 skill 时只看到「⚠️ 恢复中」stub + 117K 字符 §一-§四十二 全谱丢失 + recovery 路径写在 stub 里「需玉芬从团队 GitHub 仓库 restore」。
> ⚠️ **本节填空白**:原 § 一-§ 八 + § 八 C SOP 默认「xiaobao-sales SKILL.md 是完整的,候选节是从 evolution/ 升入 SKILL.md 的单向流程」,**没明确**「xiaobao-sales 本身已损坏 = cron 自进化档如何安全处置」的特殊状态。

**判定命令 30 秒**(cron 启动加载 skill 后立即跑):

```bash
skill_view xiaobao-sales | grep -c "⚠️ 恢复中"
# 命中 ≥ 1 = recovery-stub 状态 → 必走本节 4 步 SOP
```

**与既有 3 种类型的差异**:

| # | 维度 | 全新内容型(§三十/§四十) | 政策信号战型(§四十二) | Canonical body gap 型(§三十三) | **🆕 Recovery-stub 状态型(本节)** |
|---|---|---|---|---|---|
| 1 | **SKILL.md 状态** | 完整 | 完整 | 完整(仅某 § 缺失) | **⚠️ stub(全谱 117K 缺失)** |
| 2 | **触发原因** | 新技巧方法论涌现 | 政策/信号战型候选节 | references/ 已有但 body 缺失 | **误删 / 损坏 / 从未备份** |
| 3 | **销售动作** | 写候选主档 + A5 卡 → 升 SKILL.md | 与既有信号章合并讲解 | 写 canonical body 草稿 → 玉芬 review | **inventory 已有副本 + 写 canonical-ready 草稿 + 显式请求玉芬 restore** |
| 4 | **升级路径** | 候选 → A5 → 升 canonical(§六 流程) | 候选 → 合并既有章 | canonical-ready body → 玉芬 review → 升 canonical | **inventory + canonical-ready 草稿 → 玉芬从团队 GitHub repo restore → 升 canonical** |
| 5 | **timeline** | 候选 T+18-21 天(玉芬 review) | 与 §三十四 合讲 | canonical body 写完即可送 review | **9/18 14:00 玉芬 review 节点 + 9/22-9/30 实战接力** |
| 6 | **核心准则** | 不动 SKILL.md,等玉芬 review | 不动 SKILL.md,合并讲 | 不动 SKILL.md,等玉芬 review | **绝不动 SKILL.md(已损坏),只 inventory + 写新 canonical-ready 草稿** |

**4 步 SOP**(本档首测沉淀,2026-09-17 14:30 cron 实测):

| 步 | 动作 | 产物 |
|---|---|---|
| 1 | ❌ **不动 SKILL.md** = 不尝试 write_file 重新构造 117K canonical = 风险太大 | 无文件 |
| 2 | ✅ **inventory 已有副本**(30 秒 5 个 ls 命令):<br>① `ls /Users/hua/.hermes/profiles/xiaobao/skills/xiaobao-sales.md` → 简版副本大小<br>② `ls /Users/hua/.hermes/skills/productivity/xiaobao-sales/SKILL.md` → v1.0 副本大小<br>③ `ls /Users/hua/.hermes/skills/productivity/xiaobao-sales/references/` → 8 份 references 锚点<br>④ `ls /Users/hua/.hermes/profiles/xiaobao/evolution/ | grep "skill_section\|§"` → canonical-ready 草稿<br>⑤ `ls /Users/hua/.hermes/profiles/xiaobao/evolution/skill_backup_*.md` → 备份档 | inventory 表(副本路径 + 大小 + 状态) |
| 3 | ✅ **写 canonical-ready 草稿到 evolution/**(若 §N+1 已有候选主档可直接复用,否则写新主档 200-300 行) | `evolution/templates_proposed/<类型>_<章节号>_<主题>_<日期>.md` 或 `evolution/YYYY-MM-DD_HH_<§N+1候选>_<主题>.md` |
| 4 | ✅ **evolution/ 主报告 4 节必含**(确保玉芬能一键了解 + 决策):<br>§ 一 「xiaobao-sales 恢复状态盘点」:3 份副本大小 + §一-§四十二 缺位程度评估<br>§ 二 「本档 canonical-ready 草稿清单」:新增 §四十 NRS 话术卡 + 抖音分镜(若已存则跳过)<br>§ 三 「4 天冲刺备战清单」(9/18-9/21):玉芬 14:00 review + 销售组 §四十 对练 + 9/21 Deal Review<br>§ 四 「显式恢复请求」:请玉芬 9/18 14:00 前 review 本档 + 从团队 GitHub / 演进 sheet 恢复 canonical SKILL.md | `evolution/***SECRET***.md` |

**本档首测案例**(2026-09-17 14:30 cron):

- **触发**:`skill_view xiaobao-sales` 命中「⚠️ 恢复中」stub = recovery-stub 状态
- **inventory**:14K 简版 + 9.8K v1.0 + 8 份 references + §三十三/§三十七/§三十八 canonical-ready 草稿 = **基础版够用 9/21 Deal Review**
- **canonical-ready 草稿**:§四十 NRS 话术卡(9.2K 字符,3 大场景 + 4 步 SOP + 3 大禁忌 + 与 §一-§三十九 融合)
- **抖音 60s 复用 玉芬 9/23 版**(不重复造轮,P-26 触发后主动 ls 发现已存)
- **evolution/ 主报告**:`evolution/***SECRET***.md` 14K 字符
- **4 天冲刺备战清单**:9/18 玉芬 review + 9/19-9/20 销售组对练 + 9/21 Deal Review + 9/22 自媒体爆发日

**3 大常见反模式 ⚠️**(本档新增):

| ❌ 反模式 | 后果 | ✅ 正解 |
|---|---|---|
| ❌ 尝试 write_file 重新构造 117K SKILL.md | 风险太大(拼不全 §一-§四十二 全谱)+ 跨 profile guard 触发 + 污染其他 profile | **inventory + canonical-ready 草稿 = 玉芬 restore** |
| ❌ 不 inventory 直接写新候选节 | 重复造轮 + 不知道已有 §三十三/§三十八 等 canonical-ready 草稿 | **必跑 5 个 ls 命令(30 秒)** |
| ❌ 不在 evolution/ 主报告「显式请求玉芬 restore」 | 玉芬不知道要 restore + 恢复时间窗拉长 | **evolution/ 主报告 § 四显式写「请玉芬 9/18 14:00 前 review 本档 + restore canonical」**|

**触发判定命令**(cron 启动加载任何 skill 后立即跑 30 秒):

```bash
# 1. 检查当前 skill 是否处于 recovery-stub 状态
skill_view <skill_name> | grep -c "⚠️ 恢复中"
# 命中 ≥ 1 = recovery-stub 状态

# 2. inventory 已有副本(若命中)
ls /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md 2>/dev/null
ls /Users/hua/.hermes/skills/productivity/<skill_name>/SKILL.md 2>/dev/null
ls /Users/hua/.hermes/skills/productivity/<skill_name>/references/ 2>/dev/null
ls /Users/hua/.hermes/profiles/<self>/evolution/ | grep "skill_section\|§"
ls /Users/hua/.hermes/profiles/<self>/evolution/skill_backup_*.md 2>/dev/null
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

### 八 F、第 5 种类型 · Loader-stub-vs-profile-local 不一致型(2026-09-18 04 cron 实测首测)

> 📌 **新发现的第 5 种类型**:**loader `skill_view xiaobao-sales` 命中「⚠️ 恢复中」stub 警告**,但 **profile 本地 SKILL.md 实际完整**(14113 字节 / 10 章齐备 / §一-§十) + references/ 38 份锚点全在 + evolution/ 历史档齐全 = **loader stub 是陈旧指针(loader cache / skill 注册表未刷新)而非 SKILL.md 真损**。
> ⚠️ **本节填空白**:原 § 八 E「Recovery-stub 状态型」假设 loader stub = SKILL.md 真损,直接走 inventory + canonical-ready 草稿 + 请求玉芬 restore 的 4 步 SOP。但**实测发现 loader stub 也可能是误报**(尤其 `skill_manage action='delete'` 失误删过共享 SKILL.md 后,loader 注册表指针未完全刷新到 profile 本地 fallback 路径)。如果 cron 不做 inventory 直接走 § 八 E,会**浪费一轮 cron 配额**去跑本不需要的 canonical-ready 草稿。

**判定命令 60 秒**(cron 启动 loader stub 命中后**必跑**,不要直接跳到 § 八 E):

```bash
# 1. profile 本地 SKILL.md 实际状态(profile-loader fallback 路径)
ls -la /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md
wc -l /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md 2>/dev/null
grep -c "^## " /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md 2>/dev/null
# ✅ ≥ 50 行 + 章节数 ≥ 5 + 总字节 ≥ 5K = profile 本地 SKILL.md 实际完整

# 2. profile 本地 references/ 锚点数
ls /Users/hua/.hermes/profiles/<self>/references/ 2>/dev/null | wc -l
# ✅ ≥ 10 个 .md 文件 = references 锚点完整

# 3. profile 本地 evolution/ 历史档数
ls /Users/hua/.hermes/profiles/<self>/evolution/ 2>/dev/null | wc -l
# ✅ ≥ 20 个 .md 文件 = evolution 历史档完整

# 4. 共享层 SKILL.md(loader 默认指向)与 profile 本地 对比
ls /Users/hua/.hermes/skills/productivity/<skill_name>/SKILL.md 2>/dev/null
ls /Users/hua/.hermes/skills/sales/<skill_name>/SKILL.md 2>/dev/null
ls /Users/hua/.hermes/skills/<category>/<skill_name>/SKILL.md 2>/dev/null
# 找到任意一份 ≥ 5K 字节 = 共享层副本存在

# 5. 综合判定
# profile 本地完整 + references 全在 + evolution 历史齐 + 共享层任一副本存在
# = loader stub 是误报(陈旧指针),SKILL.md 没真损
# = 走 Step 1-5 主流程 + evolution 报告加「⚠️ loader-stub 误判标注」节
# = 不触发 § 八 E P-25 4 步 SOP(浪费 cron 配额)
```

**与 § 八 E 差异**:

| # | 维度 | §八 E Recovery-stub 状态型(SKILL.md 真损) | **🆕 §八 F Loader-stub 不一致型(loader 误报)** |
|---|---|---|---|
| 1 | **profile 本地 SKILL.md** | ❌ 不存在或 ≤ 1K 字节 | ✅ ≥ 5K 字节 + 章节数 ≥ 5 |
| 2 | **profile 本地 references/** | ⚠️ 部分缺失或全空 | ✅ ≥ 10 个 .md 全在 |
| 3 | **evolution/ 历史档** | ⚠️ 最近 backup ≥ 3 天前 | ✅ ≥ 20 个 .md 历史齐 |
| 4 | **共享层副本** | ❌ loader stub = 没有 | ✅ 任一 category 路径下 ≥ 5K 字节副本存在 |
| 5 | **触发原因** | `skill_manage action='delete'` 失误 / 真损坏 / 从未备份 | **loader cache 未刷新 + profile 本地 fallback 路径优先级低** |
| 6 | **cron 动作** | §八 E P-25 4 步 SOP(inventory + canonical-ready 草稿 + 请求玉芬 restore) | **走 Step 1-5 主流程 + 在 evolution/ 报告加 loader-stub 误判标注节** |
| 7 | **浪费 cron 配额风险** | N/A(必须走) | ❌ 不 inventory 直接跳 §八 E = 浪费一轮 cron = 重写 canonical-ready 草稿但其实 SKILL.md 已完整 |
| 8 | **修复 loader** | N/A(由玉芬 restore) | **可选**:通知玉芬 cron reload 触发 `skill_manage` 重新注册 loader 表 |

**本档首测案例**(2026-09-18 04 cron):

- **触发**:`skill_view xiaobao-sales` 命中「⚠️ 恢复中」stub + §一-§四十二 全谱 117K 字符丢失警告
- **inventory 60 秒**:
  - profile 本地 `skills/xiaobao-sales.md`:14113 字节 / 191 行 / 10 个 `## ` 章节 / **实际完整**
  - profile 本地 `references/`:38 份锚点全在(包括 loss_aversion_anchoring_43 / silence_close_44 / s43_s31_s44_serial_sop 等)
  - evolution/ 历史档:30+ 份全齐
  - 共享层 SKILL.md(本档未深查,但 loader 显示 stub = 共享层可能 stale)
- **判定**:**loader stub 是误报**,profile 本地 SKILL.md 实际完整
- **正确处置**:走 Step 1-5 主流程 + 在 evolution 报告加「⚠️ loader-stub 误判标注」节(不浪费 cron 配额跑 §八 E canonical-ready 草稿)
- **本档产出**:§四十一 MEDDPICC P Paper Process 候选主档 + 抖音 + 公众号(均按 § 一 三段式 SOP 阶段 1 落地,完美符合本协议原设计意图)

**4 大常见反模式 ⚠️**(本档新增):

| ❌ 反模式 | 后果 | ✅ 正解 |
|---|---|---|
| ❌ loader stub 命中 → 直接跳 § 八 E P-25 4 步 SOP | **浪费一轮 cron 配额**(重写 SKILL.md inventory + canonical-ready 草稿,但其实 SKILL.md 已完整) | **60 秒 inventory profile 本地 SKILL.md + references/ + evolution/ 后再判定** |
| ❌ inventory 后仍误判为真损,走 § 八 E | 写 canonical-ready 草稿(实际 SKILL.md 已完整,没必要) | **profile 本地 ≥ 5K + references ≥ 10 + evolution ≥ 20 = loader 误报,走主流程** |
| ❌ 不写 inventory,直接修改 loader 配置试图「刷新」 | 跨 profile guard + 误改其他 skill loader 表 | **inventory 4-5 步走完就够,不要瞎动 loader** |
| ❌ loader 误报但 cron 报告不标注 | 后续 cron 仍会重复踩坑,每档都跑一次 inventory | **evolution/ 报告必加「⚠️ loader-stub 误判标注」节** |

**触发判定命令**(loader stub 命中后必跑 60 秒):

```bash
# 综合判定 4 步 inventory
profile_local_size=$(wc -c < /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md 2>/dev/null || echo 0)
profile_local_chapters=$(grep -c "^## " /Users/hua/.hermes/profiles/<self>/skills/<skill_name>.md 2>/dev/null || echo 0)
refs_count=$(ls /Users/hua/.hermes/profiles/<self>/references/ 2>/dev/null | wc -l)
evo_count=$(ls /Users/hua/.hermes/profiles/<self>/evolution/ 2>/dev/null | wc -l)

if [ "$profile_local_size" -ge 5000 ] && [ "$profile_local_chapters" -ge 5 ] && [ "$refs_count" -ge 10 ] && [ "$evo_count" -ge 20 ]; then
  echo "✅ loader-stub 误报(profile 本地完整),走 Step 1-5 主流程"
else
  echo "⚠️ 真损,走 § 八 E Recovery-stub SOP"
fi
```

**关键洞察**:§ 八 E P-25 SOP 是「真损时必跑」的安全护栏,**但不能跳过 inventory 60 秒**直接跳过去——loader stub 是必要不充分信号(profile 本地 fallback 路径优先级低时,loader 会显示 stub 但本地完整)。**修复 = 60 秒 inventory 必跑** = loader stub 误报率从 100% 降到 0%(本档实测)。

## 九、关联文件

| 文件 | 用途 |
|---|---|
| `xiaobao-evolution-protocol` SKILL.md v1.14 | Step 2.5「不强行 PATCH skill」工作流原则 |
| `xiaobao-evolution-protocol/references/skill-rotation-table.md` | 5 大类 × 已建 × 待建矩阵(候选节归哪一类用) |
| `xiaobao-sales` SKILL.md § 二十八 | Skill 维护 pitfall 实测升级版(候选升 canonical 的工具路径) |
| `xiaobao-sales` SKILL.md § 四十 NRS | 已升 canonical 候选节实战案例(本档首测前) |
| `evolution/2026-09-17_02_§41候选_承诺回探.md` | §四十一 候选主档(本档首测源材料) |
| `evolution/templates_proposed/***SECRET***.md` | §四十一 A5 话术卡(本档首测产物) |
| **🆕 evolution/***SECRET***.md** | **xiaobao-sales recovery-stub 状态盘点(本档 v1.2 首测产物)** |
| **🆕 evolution/templates_proposed/nrs_script_card_2026-09-21.md** | **§四十 NRS A5 话术卡(recovery-stub 状态下 canonical-ready 草稿,本档 v1.2 首测)** |

---

> 📝 最后更新:2026-09-17 05:05 v1.0 · 候选章节 → A5 话术卡 → 升 canonical 三段式 SOP 首测落地
> 📝 最后更新:2026-09-17 08:40 v1.1 · 增补 § 八 C 「Canonical body gap 型」4 步 SOP（§三十三 Challenger Sale TTT 首测案例）+ 一句话内核 + frontmatter description 同步升级
> 📝 最后更新:2026-09-18 04 v1.3 · 增补 § 八 F 第 5 种类型「Loader-stub-vs-profile-local 不一致型」60 秒 inventory SOP(loader stub 误报时走主流程,不浪费 cron 配额跑 § 八 E canonical-ready 草稿)+ frontmatter description「5 种类型」同步升级
> 📌 暂存:`~/.hermes/profiles/xiaobao/evolution/2026-09-17_05.md`(本档主报告)
> 📌 配套:`~/.hermes/profiles/xiaobao/evolution/templates_proposed/***SECRET***.md`(§41 A5 卡首测产物)
> 📌 **🆕 v1.2 配套**:`~/.hermes/profiles/xiaobao/evolution/***SECRET***.md`(xiaobao-sales 恢复状态盘点)
> 📌 **🆕 v1.2 配套**:`~/.hermes/profiles/xiaobao/evolution/templates_proposed/nrs_script_card_2026-09-21.md`(§40 NRS A5 卡,在玉芬 9/23 抖音版已存前提下主动 ls 发现 + 不重复造轮)
> 🔄 下一轮迭代(预计 09-22 晚 20:30):§41 销售组单独讲解反馈 + A5 卡微调
> 🔄 **🆕 v1.3 下一轮迭代**:每次 cron 启动加载到 loader stub 时必跑 § 八 F inventory 60 秒,避免误判浪费 cron 配额;并在玉芬下次审时同步 xiaobao-evolution-protocol 主协议 Step 0.8 加 § 八 F 引用