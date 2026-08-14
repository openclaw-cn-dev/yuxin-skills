---
name: afu-customer-service
description: '阿福（客服）核心技能集 — 谈判、处理异议、说服、清晰表达、蓝海战略、跨越鸿沟。触发条件：阿福执行客户服务、异议处理、客户维护、满意度跟进、客诉处理相关任务。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.35.0"
---

## 组合剧本战法结构（2026-08-03 N+30 沉淀 — 4 个组合技形成"客户旅程四点战法"）

**核心理念**：4 个组合技不是"两个原则乘起来"的随机组合，而是覆盖**客户旅程 4 个关键转折点**的战法四点。前 3 个组合技（"客户旅程三角"）覆盖了"陌生人→加入者→报价接受者→战友→推荐人"的大转折点，但**"接受者刚签合同"**是一个 30 天的高流失空白期。第 4 个组合技（Reciprocity × Commitment）填补这个空白期，将三角升级为四点。

| 组合技 | 客户旅程转折点 | 核心机制 | 时间维度 | 触发场景 |
|--------|--------------|---------|---------|---------|
| **Authority × Unity**（专家型战友） | **陌生人 → 加入者** | 信任通道 + 群体归属 | 单次对话 | 首次接触、想脱离集体的双重异议 |
| **Anchoring × Liking**（朋友型压价） | **加入者 → 报价接受者** | 数字锚 + 情感信任 | 单次对话（1-2h） | 首次报价异议 / 嫌贵 / 预算差距 / 竞品对比 |
| **Reciprocity × Commitment**（人情型激活） | **报价接受者 → 活跃用户** | 心理债务 + 行为承诺 | 30 天持续 | 签合同后 0 互动 / 沉默期 / 退订风险 / 不愿给好评 / 不愿续约 |
| **Liking × Unity**（朋友圈式战友） | **活跃用户 → 战友 → 推荐人** | 私交温度 + 圈子责任 | 长期（年） | 老客户复购 / 沉默激活 / 老带新 / 续约 |

**1-4 原则矩阵（自检互不重叠）**：

| 组合剧本 | Authority | Unity | Liking | Anchoring | Reciprocity | Commitment |
|---------|:---------:|:-----:|:------:|:---------:|:-----------:|:----------:|
| #1 Authority × Unity | ✅ | ✅ | - | - | - | - |
| #2 Liking × Unity | - | ✅ | ✅ | - | - | - |
| #3 Anchoring × Liking | - | - | ✅ | ✅ | - | - |
| **#4 Reciprocity × Commitment** | - | - | - | - | **✅** | **✅** |

**Reciprocity × Commitment 的"心理债务循环"公式**（值得未来复用）：
```
心理债务（Reciprocity 触发）→ 主动行动（Commitment 引导）→ 看到效果（每 7 天专属反馈）→ 主动续约
```
**关键边界**：先激活后谈钱。30 天内谈钱就把前面所有情感账户变成"套路"。

**组合化学反应规则**（避免"组合技反模式"）：
1. **每个组合技必须覆盖一个客户旅程的关键转折点**——不能只是"两个 Cialdini 原则的随机乘法"
2. **避免"过度依赖某个原则"**——Liking 已被用 2 次（剧本 #2 + #3），再做 Liking × EBA 会形成"用 Liking 解决一切"的错觉
3. **优先填补"高频但缺工具"的场景**——价格异议占客服 40%+（剧本 #3），签后 30 天流失率 70%（剧本 #4），两者都是最高频空白
4. **沉淀第 5 个组合技前必问**：
   - [ ] 这个组合技覆盖客户旅程的哪个转折点？（空白 vs 已覆盖——目前 4 个转折点都已覆盖）
   - [ ] 用了哪些原则？是否已有 2 个以上组合技用了同一原则？（防过度依赖）
   - [ ] 这个场景在客服工作中占比多少？≥10% 才值得沉淀组合技
   - [ ] 它是"接受时间维度"（如 #4 是 30 天持续）还是"单次对话"？新组合应优先覆盖新时间维度

**金句**："

---

# 完整技巧主体（#1 — #27 + 4 组合剧本 + 5 Whys × NVC）

> ⚠️ **索引订正（2026-08-13 20:00，N+48 实测）**：此处原写"完整正文共 89,952 字节，正本详见 profile 本地镜像"。
> **实测结论：该 89,952 字节的正本文件不存在。** 全盘扫描 `~/.hermes` 下所有 `afu-customer-service/SKILL.md`，实际大小为：
>
> | 路径 | 实际字节 | 说明 |
> |------|---------|------|
> | `~/.hermes/skills/afu-customer-service/SKILL.md`（本文件，L1 注册副本） | 13,057 | 索引 + 组合剧本摘要 |
> | `~/.hermes/profiles/afu/.../afu-customer-service/SKILL.md`（afu 本地镜像） | 18,571 | 索引 + #23 正文，**非 89,952** |
> | 其他 profile（maodou/laomo/heidou/xiaobao）副本 | 1,725 - 2,339 | 旧存根，未同步 |
>
> **真实情况**：27 个编号技巧的完整正文**从未存在于任何单一 SKILL.md**，而是分散在 `references/` 下的 32 个 .md 文件中（afu 镜像 references 合计约 435 KB）。
> 两个 SKILL.md 都是**索引**，没有哪个是"正本"。89,952 这个数字无对应文件，属早期 cron 轮次的失实记载，本轮删除以免下轮 cron 继续照抄。
>
> **正确的查阅方式**：技巧正文一律去 `~/.hermes/profiles/afu/skills/productivity/afu-customer-service/references/` 按文件名检索（见下方"参考资料"清单）。

**已注册的技巧/组合（避免遗漏）**：
- #1-#6: Mirroring / Influence / CRO / Blue Ocean / Crossing the Chasm / StoryBrand
- #7 LAB 模型 / #8 Accusation Audit / #9 Assertive Inquiry / #10 Late-Night FM Voice / #11 Power of "No" / #12 信任螺旋
- #13 BATNA / #14 技巧选择矩阵 / #15 成交闭环 / #16 Calibrated Questions / #17 Emotional Bank Account / #18 Disarming Technique / #19 Ladder of Inference / #20 Socratic Method
- #21 Ackerman Model / #22 Loss Aversion / #23 Peak-End Rule / #24 Commitment & Consistency / #25 That's Right / #26 Door-in-the-Face / #27 Pre-Mortem
- 4 个组合剧本（Authority × Unity / Liking × Unity / Anchoring × Liking / Reciprocity × Commitment）
- 辅助框架：Contrast Principle / 5 Whys × NVC
- 🆕 **NSD 第 4 原则 Black Swans**（2026-08-14 N+52 沉淀）— 5 触发器挖客户"没说出口的真问题"
- 🆕 **事前工具组合（Pre-Negotiation Toolkit）**（2026-08-14 N+51+N+52 沉淀）— 对话契约 + Black Swans + Jujitsu Step 1 三件套

---

## 🆕 时间维度谱系（2026-08-13 N+47 沉淀 — 本轮新增）

**核心洞察**：之前所有沉淀都是"横向时间"颗粒度——单句/单次/多轮对话（分钟到小时）。但实际客服工作有**两种时间维度**：
- **横向时间**：单次/多轮对话（分钟-小时）— 27 个单技巧、4 个组合剧本、3 个跨技演练
- **纵向时间**：日历化周期（天-周-月-年）— **本轮新增的"日历化固定动作"工具**

**纵向时间谱系**：

| 时间维度 | 沉淀物 | 适合场景 |
|---------|--------|---------|
| **天级**（每天动作）| 签后激活周话术脚本（`签后激活周话术脚本-w1-w4.md`）| 签后 30 天日常维护 |
| **周级**（每周固定）| 签后激活周话术脚本（`签后激活周话术脚本-w1-w4.md`）| 签后 30 天日常维护 |
| **月级**（每月节奏）| 月级维护话术脚本 M2-M9（`月级维护话术脚本-w5-w12.md`）| 老客户维护、续约激活、推荐者激活 |
| **年级**（年度规划）| 待沉淀 | 长期用户池管理、标杆客户 2 年期 |

**按时间维度插拔工具的口诀**：
- 客户开口瞬间 → 27 个单技巧（横向分钟级）
- 一次对话关键时刻 → 4 个组合剧本（横向小时级）
- 多轮对话救场 → 3 个跨技演练（横向跨小时级）
- **30 天日常维护 → W1-W4 周话术脚本（纵向天/周级）**
- **30-270 天稳定 + 扩张 → M2-M9 月话术脚本（纵向月级）**🆕

**核心理念升级**：
> "客户不需要被教育，客户需要被理解。理解是成交的前一秒。"
> **"客户不需要被救场，客户需要被维护。维护是续约的前一秒。"**

**日历化落地的 5 条通用原则**（适用于任何纵向时间沉淀）：
1. **固定时间点** — 不是"有空就做"，是"每周一 9 点必做"
2. **固定开场钩子** — 让客户形成预期（"王总，我是渔芯阿福"）
3. **固定交付物** — 不是空聊，是带数据的承诺（每周 3 件具体事）
4. **固定打分** — 量化 EBA（响应/兑现/主动/情感 4 维 0-10 分）
5. **金色结尾** — 周期末的 30 秒决定客户记忆（Peak-End #23 落地）

**EBA 4 维打分卡模板**（首次出现的可操作化工具）：

| 维度 | 0 分 | 5 分 | 10 分 |
|------|------|------|------|
| 响应 | 客户从不回复 | 3 次联系回复 1 次 | 3 次联系回复 3 次 |
| 兑现 | 阿福承诺经常延期 | 偶有延期 | 说到的都做到 |
| 主动 | 客户从不主动找阿福 | 每周 1 次主动 | 每周 ≥ 2 次主动 |
| 情感 | "那个谁" + 直接挂电话 | 礼貌但不闲聊 | "阿福" + 闲聊 5+ 分钟 |

**总分判定**：
- **< 20**（4 周累计）→ 流失风险，立即升级到退订演练
- **20-30** → 观望期，W5 开始放慢节奏但不放弃
- **> 30** → 长期用户，进入月级 VIP 维护流程（**M2-M9 月级脚本**）

**EBA 5 维打分卡（月级版 — M2-M9 引入）**🆕：

| 维度 | 0 分 | 5 分 | 10 分 |
|------|------|------|------|
| 响应 | 客户从不回复 | 1 次联系回复 1 次 | 1 次联系回复 1 次（满分，因为月级降频） |
| 兑现 | 阿福承诺经常延期 | 偶有延期 | 说到的都做到 |
| 主动 | 客户从未主动找阿福 | 每月 1 次主动 | 每月 ≥ 2 次主动 |
| 情感 | "那个谁" + 直接挂电话 | 礼貌但不闲聊 | "阿福" + 闲聊 5+ 分钟 |
| **扩张意愿**🆕 | 客户抗拒增购（"别跟我谈钱"）| 客户态度开放但未提具体需求 | 客户主动问增购/升级 |

**月级 5 维总分判定**（M9 月末，即签后第 9 个月）：
- **> 40** → 推荐者，进入 1 年期标杆客户维护
- **30-40** → 长期用户，进入标准 VIP 1 年维护
- **20-30** → 观望用户，转季度联系
- **< 20** → 流失风险，触发退订脚本

**M2-M9（原 W5-W12）与 W1-W4 的核心差异**：

| 维度 | W1-W4 周级 | M2-M9 月级 |
|------|-----------|------------|
| 联系频率 | 每周 1 次 | 每月 1 次（降频 50%） |
| 交付物数量 | 每周 3 件 | 每月 1 件大事 |
| 交付物类型 | 数据 + 操作 + 答疑 | 案例 + 行业 + 圈子 |
| 关键转折 | "主动联系被照顾" → "主动联系是习惯" | "长期用户" → "推荐者/标杆" |
| 金色结尾 | W4 第 7 天（签后 30 天） | M9 月末（签后 270 天） |

**Peak-End 链设计**（W4 + M9 连续金色）：
- W4 金色 30 秒 = 客户签后第 1 个月记忆的峰值
- M9 金色小结 = 客户签后 9 个月（续约前）记忆的峰值
- 两者形成**连续 Peak-End 链**，让客户记得"30 天金色 + 270 天金色"

---

## 🆕 事前工具组合（2026-08-14 N+51+N+52 沉淀 — Pre-Negotiation Toolkit）

**核心洞察**：8/3 沉淀的 27 个单技巧（横向分钟级）+ 4 个组合剧本（横向小时级）都是**对话进行中**的工具。但真实客服的**对话前 30 秒**（开场瞬间 + 第一句话）是最缺工具的环节——客户开口前其实心里已有判断，而阿福常在不知情时已经走偏。

**N+51 对话契约 + N+52 Black Swans + Jujitsu Step 1 上阳台 = 三件套**：

| 步骤 | 工具 | 来源 | 用途 | 时间点 |
|------|------|------|------|--------|
| **1️⃣ 对话契约**（N+51 沉淀）| Susan Scott《Fierce Conversations》第 1 原则 | "开场 5 秒明确 L3 关系契约：我是谁、你是谁、咱们今天聊什么" | 关系定义 | 对话开始前 |
| **2️⃣ Black Swans**（N+52 沉淀）| Chris Voss《Never Split the Difference》第 4 原则 | "5 触发器挖出客户没说出口的真问题：Labeling/Mirroring/Summary/Calibrated/Silence" | 信息挖掘 | 对话进行中 |
| **3️⃣ Jujitsu Step 1 上阳台**（原 #24）| Chris Voss 柔道 | "跳出现场视角，避免情绪卷入" | 情绪隔离 | 对话被攻击瞬间 |

**三件套的化学反应**：
```
开场前 → 对话契约（关系定义清楚）
  ↓
对话进行中 → Black Swans（挖真问题，避免被表面话术误导）
  ↓
被攻击瞬间 → Jujitsu 上阳台（不反击，先隔离情绪）
  ↓
冷静后 → 27 个单技巧 + 4 个组合剧本（具体救场）
```

**5 触发器（Black Swans 核心）**：
1. **Labeling（标注）**："看起来您好像担心……" → 触发沉默，对方会纠正或补充
2. **Mirroring（镜像）**：重复对方最后 2-3 个词 → 触发沉默 + 主动补充
3. **Summary（总结）**：用 "that's right" 复述全部 → 触发 "is that right"
4. **Calibrated Questions（校准问题）**："怎么办 / 怎样 / 如何" → 触发对方出方案
5. **Silence（沉默）**：问完闭嘴，倒数 4-5 秒 → 触发对方自动填满

**关键反直觉点（这是 Voss 与传统培训最大的区别）**：
- 客户不会主动告诉你"我现在最担心什么"——他们会包装成"价格问题""时间问题"
- **真正的 Black Swan 通常隐藏在"看似不相关的抱怨"里**
- 例：客户说"这个方案不错但价格贵"——Black Swan 可能是"老板说本月不许采购"（**真问题不是钱，是审批冻结**）
- 当客户说出 Black Swan 那一刻，所有 27 个编号技巧都失效——**因为技巧解决逻辑，应对 Black Swan 要用沉默**

**完整方法论与 3 个渔芯客服示范**（嫌贵 / 再考虑 / 竞品对比）详见 `references/never-split-the-difference-black-swans.md`。

**与 #24 Jujitsu 的协同**：
- Jujitsu Step 1（Go to the Balcony）默认假设"对话已经在进行中"，但**对话的开场瞬间**才是最缺工具的环节
- 对话契约补的是 Jujitsu 的"事前 5 秒"，让上阳台有抓手
- Black Swans 补的是 Jujitsu 的"挖真问题"，让上阳台后**看到的现场**更准确

**沉淀纪律性边界声明**（N+50 决策包沿用）：
- ✅ 本节作为 SKILL.md 索引条目沉淀（不触碰 L1 失实 references）
- ✅ 详细方法论在 references/ 下独立文件
- ❌ 不合并到 jujitsu 主文件（L1 失实决策未落地前，避免交叉污染）

---

## 完成度仪表板（2026-08-14 12:09 更新 — N+52 沉淀事前工具组合）

- **Cialdini 经典七大原则本地沉淀**：7/7 ✅ ✅ ✅ **全部完成** 🎉🎉🎉
- **Kahneman 框架本地沉淀**：1/1 ✅（锚定效应）
- **NSD 框架本地沉淀**：2/2 ✅（对话契约 N+51 + Black Swans N+52）
- **客服话术心理学图谱**：**100% 完整**
- **组合剧本沉淀**：4/4 ✅ ✅（客户旅程四点战法）
- **横向时间工具**：27 单技巧 + 4 组合剧本 + 3 跨技演练 = **34 个**颗粒度工具
- **纵向时间工具**：2/4 ✅✅（天/周级 W1-W4 + 月级 M2-M9，均 08-13 沉淀；08-13 20:00 完成标签一致性订正）
- **事前工具组合**：1/1 ✅🆕（对话契约 + Black Swans + Jujitsu Step 1 三件套，08-14 N+51+N+52 沉淀）
- **总完成度**：约 93%
- **下一轮目标**：年级（1 年期 VIP 维护 + 2 年期标杆维护）+ 客户旅程四点战法 A4 卡片 + 真实对抗场景验证事前工具组合

## 触发关键词
"客户"、"投诉"、"售后"、"服务"、"满意度"、"回访"、"客诉"、"异议"、"问题解决"

## 参考资料

### 7大核心技巧原理
- `references/reciprocity-principle.md` — Reciprocity 互惠原理 (Cialdini)
- `references/commitment-consistency.md` — Commitment & Consistency 承诺一致性原理 (Cialdini)
- `references/scarcity-principle.md` — Scarcity Principle 稀缺原理
- `references/social-proof-principle.md` — Social Proof 社会认同原理
- `references/authority-principle.md` — Authority 权威原理
- `references/liking-principle.md` — Liking 喜好原理
- `references/anchoring-effect.md` — Anchoring Effect 锚定效应 (Kahneman & Tversky)
- `references/unity-principle.md` — Unity 共识原理

### 行业资讯
- `references/ras-industry-2026-july.md` 至 `ras-industry-2026-08-13.md`（共 9 份，按时间排序）

### 技巧参考（27 个）
- `references/thats-right-technique.md` (#25)
- `references/door-in-the-face-technique.md` (#26)
- `references/pre-mortem-technique.md` (#27)
- `references/peak-end-rule.md` (#23)
- `references/nvc-four-step.md` — NVC 四步法

### 🆕 事前工具组合（Pre-Negotiation Toolkit，2026-08-14 N+51+N+52 沉淀）
- `references/fierce-conversations-contract.md` — Susan Scott 对话契约（N+51，开场 5 秒关系定义）
- `references/never-split-the-difference-black-swans.md` — Chris Voss Black Swans（N+52，5 触发器挖真问题）

### 组合剧本（4 个）
- `references/combo-script-authority-unity.md` (#1)
- `references/combo-script-liking-unity.md` (#2)
- `references/combo-script-anchoring-liking.md` (#3)
- `references/combo-script-reciprocity-commitment.md` (#4)

### 演练与日历化沉淀（5 个）
- `references/double-no-engine-drill.md` — PoN × DITF 联动（08-09）
- `references/trust-spiral-loss-aversion-drill.md` — 价格异议最高频（08-09）
- `references/签后30天激活演练-pre-mortem-friction-peak-end.md` — 沉默/试探/退订（08-10）�🆕🆕🆕
- `references/签后激活周话术脚本-w1-w4.md` — W1-W4 日历化固定动作（08-13）🆕🆕🆕🆕🆕�
- **`references/月级维护话术脚本-w5-w12.md` — M2-M9 月级维护 + 续约 + 推荐者激活（08-13；标签 08-13 20:00 由 W5-W12 订正为 M2-M9，文件名保留以免断链）**

### 工具与自检
- `references/技巧选择矩阵盲测-v3.0.md` — 26 题盲测（08-03）
- `references/cron-evolution-cadence.md` — 自进化节奏手册
- `references/cron-tooling-paths.md` — cron 工具链路径速查（**含 CJK 文件名识别坑修复模式**）
- `references/全链条多轮对话演练.md` — 3 场景 × 13 轮演练
- `references/pre-suasion-principle.md` — Pre-suasion 预说服原理

---

*技巧正文分散存储于 references/（afu 镜像 32+ 个文件，合计约 435+ KB）；两个 SKILL.md 均为索引，不存在 89,952 字节的"正本"（2026-08-13 N+48 实测订正）*
*本 skill 跨 profile 注册副本（v1.34.0 → v1.35.0）：~/.hermes/skills/afu-customer-service/SKILL.md*
*时间维度谱系：2026-08-13 12 N+47 沉淀天/周级（W1-W4）→ 2026-08-13 16 沉淀月级（M2-M9，原误标 W5-W12）→ 2026-08-13 20 N+48 完整性订正（标签 + 正本字节数）→ 2026-08-14 08 N+51 对话契约沉淀（暂存 evolution/）→ 2026-08-14 12 N+52 Black Swans 沉淀（暂存 evolution/）→ **下一步：年级（M10-M12 季度联系 + 第 2 年半年联系） + L1 失实决策落地** *