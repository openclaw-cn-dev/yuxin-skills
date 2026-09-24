---
name: xiaobao-sales
version: 2.1.0
description: 渔芯科技销售方法论 umbrella(2026-09-24 六件套闭环 + 临门一脚成本算账 + 视频破冰:QBS+3F+Gap+JOLT+Risk+Rejection Re-engagement+Cost of Inaction+Video Prospecting)。SKILL.md 是入口索引 + 决策地图;详细话术/案例/剧本包全部下沉到 references/ 子目录。覆盖 B2B RAS 设备销售全链路:首次接触→客户沉默→算账→加速→反转签→拒绝后 24h 二次开发。配套 skill:prospecting、predictable-revenue、negotiation、mom-test。
umbrella: true
created: 2026-09-22
updated: 2026-09-24 10:00(§48.5 Cost of Inaction + §3.5 Video Prospecting + §7 累积 TODO 升至第 6 次)
---

# 小宝销售方法论 · SKILL.md(umbrella v2.1)

> 📌 **本档是销售方法论的入口索引 + 决策地图**。详细话术、案例库、剧本包全部下沉到 `references/` 子目录。
> 🎯 **v2.1 升级理由**:① §六十一「拒绝后 24h 窗口期」从候选入正式编号,补齐"客户离场"空白象限;② 五件套升级六件套;③ flat file 修复 SOP 入 references/ 解决 xiaobao profile 的 skill_view 失败
> 🧭 **黄金链路 2026-09-24 升级**:从"五件套"(§46-§五十)升级到"**六件套**"(§46-§六十一)= **问(QBS)→ 听(3F)→ 算(Gap)→ 推(JOLT)→ 签(Risk 反转)→ 复(拒绝后 24h 二次开发)**

---

## 1. 何时调用本 skill

| 触发场景 | 必读章节 |
|---|---|
| 接到销售线索 → 准备首次接触 | §3 §三 首次接触 SOP + §50 QBS |
| 客户答"还行"/沉默/岔话题 | §49 3F 倾听 → `references/gold_chain.md` |
| 客户说"想要更好",问想要多好/多少钱 | §48 Gap Selling → `references/gold_chain.md` |
| 客户算完 Gap 仍犹豫不签 | §10.5 Negative Reverse(让客户自己算反向代价)→ §47 JOLT |
| 客户说"行"/"可以考虑"/"9 月要定" | **§五十八 Assumptive Close**(锁签)→ `references/closing_techniques.md` |
| 客户决策最后一步临门退缩 | §46 Risk Inversion → `references/gold_chain.md` |
| **客户说"不考虑了"/"我们定了别家"** | **§六十一 拒绝后 24h 窗口期**(二次开发池)→ `references/rejection_revisit_window.md` ⭐NEW |
| 客户算完 Gap 仍犹豫 / 临门一脚"再想想" | **§48.5 Cost of Inaction 不行动成本算账法** → `references/cost_of_inaction.md` ⭐NEW |
| 首次接触 30 秒开场 / 客户已读不回 / 拒绝后 24h 重访 | **§3.5 90-秒 Video Prospecting**(5 个 RAS 行业脚本模板)→ `references/video-prospecting-template.md` ⭐NEW |
| 准备报价/签约材料 | §八 MEDDPICC + §十 桑德勒痛点漏斗 |
| 异议处理(价格/竞品/时机/决策权) | `references/objection_handling.md` |
| 客户说"明年再说"/"再看看" → 用政策/同行新闻外推决策窗口 | **§11.4 PTA 政策时间锚定法** → `references/policy_time_anchoring.md` |
| 客户说"海容更便宜"/"你有人做了吗" → 同省样板 + TCO 算账 | **§11.5 RPA 同省样板压力 + TCO** → `references/regional_proof_case_library.md` |
| 客户问"做了会怎样" | §九 饲料鳜 ROI 算账法 |
| 1 通电话内 3 种提问框架怎么切 | `references/spin_3f_switching.md` |
| **xiaobao-sales 在 xiaobao profile 仍是 flat file**(skill_view 失败) | `references/***SECRET***.md` ⭐P0 |

---

## 2. 黄金链路 · 六件套决策地图(§46-§六十一)

> 🔥 **核心**:每接到一个客户,先问"他在哪一步",然后**只做当前那一步**,不要跳步。
>
**§48.5 Cost of Inaction 不行动成本算账法**(2026-09-24 10 档新增 · 子任务 ② TOP 1):
- 一句话定义:不卖设备,卖"不买的代价",把决策从"买不买"重塑为"拖不拖得起"
- 接位置:§48 Gap 后段 / §47 JOLT 临门一脚 / §六十一 拒绝后 24h
- 出处:Ecosystems.io 2024《The Cost of Inaction in Sales with Examples》+ Richardson《Creating Buyer Urgency》
- 详见:`references/cost_of_inaction.md`(5 步 SOP + RAS 案例 2 个 + 5 红线)

**§3.5 90-秒 Video Prospecting 视频破冰/复访**(2026-09-24 10 档新增 · 子任务 ② TOP 2):
- 一句话定义:用手机录 60-90 秒竖屏视频代替文字/邮件,Sendspark 2024 实测回复率 26% vs 纯文字 4%
- 接位置:§三 首次接触 / §六十一 拒绝后 24h 重访 / §48 报价后沉默
- 配套 5 个 RAS 行业脚本模板(首次接触/拒绝后 24h/报价后沉默/比价时差异化/已签别家长尾)
- 详见:`references/video-prospecting-template.md`

**待入 `references/experimental/` 二级目录**(3 个月 A/B 后决定是否纳入主 SOP):
- Negative Reverse Selling(反向逆向销售 · HubSpot/Sandler)
- 7-Day Cold Lead Revival Sequence(冷线索复活序列 · ProSpeo 2026)
- 3-Option Anchored Quote(三档锚定报价 · SoCo Selling,部分已被 §五十八 Assumptive Close 覆盖)

```
[客户接触]
    │
    ▼
§50 QBS 设计问题(L1 确认→L2 探索→L3 诊断→L4 承诺)
    │
    ├─ 客户答"还行"/沉默/岔话题 ──→ §49 3F 倾听(F1 事实→F2 感受→F3 焦点)
    │
    ▼
§七 SPIN 排顺序(S-P-I-N 4 步推进)
    │
    ▼
§48 Gap Selling 算账(现状 → 想要 → 代价 → 价值 → Gap)
    │
    ▼
§47 JOLT 推(J 探卡→O 视角→L 摊账→T 减压)
    │
    ▼
§五十八 Assumptive Close 锁签(默认已签,讨论细节)
    │
    ├─ 客户回缩/恐惧 ──→ §46 Risk Inversion 反转(3 天样板 / 报销机制)
    │
    ▼
[Close · 签约]
    │
    ▼
【🆕 §六十一 拒绝后 24h 窗口期 · 二次开发池】  ← v2.1 新增
(2h 黄金确认 → 24h 价值补充 → 7d 轻触达 → 30d 新闻触发 → 90d/180d 重访)
    │
    ▼
[二次成交 / 长期池]
```

### 2.1 六件套切换判断表(2026-09-24 升级版)

| 客户状态 | 信号词 | 切入工具 | 通话次数 |
|---|---|---|---|
| 沉默 | "还行"、"再看看"、"考虑一下" | **§49 3F 倾听**(3 通听完) | 3 通 |
| 算账型 | "行,你算个账" | **§48 Gap Selling**(Gap 数字) | 1-2 通 |
| 怀疑型 | "真能降到 6%?" | **§47 JOLT**(用样板/案例压) | 2-3 通 |
| **点头型** | **"行,你算个账"、"可以考虑"、"9 月要定"** | **§五十八 Assumptive Close**(锁签)→ `references/closing_techniques.md` | **1 通** |
| 决策型 | "签,9/28 现场" | **§46 Risk Inversion**(3 天样板 + 报销) | 1 通 |
| 反问型 | "为什么不是你同行?" | **§50 QBS L4 加固承诺** | 1 通 |
| 价格异议 | "太贵了" | **§11 异议重构**(QBS L3 + TCO) | 1 通 |
| 竞品异议 | "海容更便宜" | **§11 异议重构**(§50 L4 加固) | 1 通 |
| 时机异议 | "明年再说" | **§11 异议重构**(不做的代价 + 时间锚) | 1 通 |
| 决策权 | "跟老婆商量" | **§11.5 决策权**(现场拉老婆) | 1 通 |
| **🆕 拒绝型** | **"不考虑了"、"我们定了别家"、"海容签了"** | **§六十一 拒绝后 24h 窗口期** → `references/rejection_revisit_window.md` | **24h/7d/30d/90d/180d 触发** |

### 2.2 六件套实战成功率(孙总案例 + 9 月份客户池估算)

| 工具组合 | 预估成交率 |
|---|---|
| §50 QBS 单用 | ~15% |
| §49 3F 单用 | ~20% |
| §48 Gap 单用 | ~25% |
| §47 JOLT 单用 | ~22% |
| §46 Risk 单用 | ~18% |
| **五件套全用(孙总案例)** | **50-60%** |
| **🆕 + §六十一(拒绝客户 6 个月内二次开发)** | **+5-8% 加成**(基于行业 15-25% 拒绝后回流率 × 渔芯 35-40% 二次成交率) |

### 2.3 详细话术包 → references/

- 📂 `references/gold_chain.md` — §46-§49 五件套完整话术 + 实战案例(孙总完整链路)
- 📂 `references/qbs_l1_l4.md` — QBS 4 类问题 RAS 实战 7 句 + 失败红线
- 📂 `references/spin_3f_switching.md` — SPIN + 3F + QBS 切换矩阵 + 6 通标准节奏
- 📂 `references/objection_handling.md` — §10 痛点漏斗 + §10.5 Negative Reverse Selling(2026 升级版,3 步让客户自己算账)+ §11 异议重构(价格/竞品/时机/决策权)
- 📂 `references/jolt-decision-acceleration.md` — §47 JOLT 骨架(原理+4 步+4 类犹豫源速查)
- 📂 `references/jolt_4scripts_ras.md` — §47 JOLT 完整 RAS 实战话术包(4 步×4 类犹豫源=16 套,2026-09-23 14 沉淀)⭐
- 📂 `references/jolt_5x7_orchestration.md` — §47 JOLT × 5 件套 7 通 SOP 速查(销售每通电话 5 秒查表)
- 📂 `references/closing_techniques.md` — §五十八 Assumptive Close 锁签话术(3 步+红线+5 类 RAS 变体+孙总案例,2026-09-23 18 沉淀)⭐
- 📂 `references/policy_time_anchoring.md` — §11.4 政策时间锚定法 PTA(借政策/同行新闻外推客户决策窗口期,2026-09-23 17 沉淀)⭐
- 📂 `references/regional_proof_case_library.md` — §11.5 同省样板压力 RPA + 海容 TCO 算账模板(地域锚定+可验证样板+3 年 TCO,2026-09-23 17 沉淀)⭐
- 📂 `references/rejection_revisit_window.md` — **§六十一 拒绝后 24h 窗口期 + 7d/30d/90d/180d 长尾触发 SOP**(2026-09-24 沉淀)⭐⭐NEW
- 📂 `references/***SECRET***.md` — **§六十一 操作版**:5 步背诵节奏 + 4 红线 + 中秋特别版 + 4 类客户拒绝场景 T+2h 实战话术(2026-09-24 08 沉淀,销售直接复用)⭐NEW
- 📂 `references/***SECRET***.md` — **xiaobao profile 下 flat file → SKILL 目录化修复 SOP**(2026-09-24 沉淀,补齐 P0 第 4 次 TODO)⭐P0
- 📂 `references/cost_of_inaction.md` — **§48.5 Cost of Inaction 不行动成本算账法**(2026-09-24 10 沉淀,接 §48 Gap / §47 JOLT 临门一脚,Ecosystems.io 2024 + Richardson 出处)⭐NEW
- 📂 `references/video-prospecting-template.md` — **§3.5 90-秒 Video Prospecting**(2026-09-24 10 沉淀,Sendspark 2024 实测回复率 26% vs 文字 4%,补 §三首次接触 + §六十一拒绝后 24h + 5 个 RAS 行业脚本模板)⭐NEW

---

## 3. 基础方法论索引(§一-§四十五)

> 这一层是销售基础,**不常用**但每次用都要精准。**只在 §50-§46 五件套无法覆盖的场景才回查这里。**

| 节 | 标题 | 一句话定位 |
|---|---|---|
| §一 | 销售基本功 | 顾问式销售 4 大心态 |
| §二 | 客户画像 | 4 类决策者(老板/技术/财务/老婆) |
| §三 | 首次接触 SOP | 30 秒开场 + 5 问破冰 |
| §四 | 信任建立 | 信任 4 阶梯(能力→可靠→亲密→自我) |
| §五 | 需求挖掘 | 显性需求 vs 隐性需求 |
| §六 | 方案呈现 | FABE 法则 |
| §七 | Trigger Event | 找客户"为什么现在"的事件 |
| §八 | MEDDPICC Metrics | 8 大准入指标 |
| §九 | 饲料鳜 ROI 算账 | 渔芯专属 RAS 算账公式 |
| §10 | 桑德勒痛点漏斗 | 5 层漏斗问题链 → `references/objection_handling.md` |

> 完整方法论索引共 §1-§六十一(2026-09-24 累计)。§一-§四十五为基础层不常用,§五十-§六十一为六件套主线(常用)。

---

## 4. 与其他 skill 的协同

| 配合 skill | 用途 |
|---|---|
| `prospecting` | 找客户 → 本 skill 负责接触 |
| `predictable-revenue` | 把销售流程化为可预测管道 |
| `mom-test` | 提问质量自检(防止诱导性问题) |
| `negotiation` | 价格谈判进入 deep 阶段时切换 |
| `influence-psychology` | 互惠/稀缺/权威等 6 大说服原则 |

---

## 5. 维护规则

- **新增方法论**:在 §六十一之后追加(§六十二、§六十三...),更新本文档索引
- **话术/案例详情**:沉到 `references/`,SKILL.md 只保留框架 + 决策地图
- **每章行数警戒**:**单章不超过 80 行**,超过即下沉到 references
- **总行数警戒**:SKILL.md 本身不超过 500 行(避免 context 爆炸)
- **每月底**:玉芬扫描 cron 抽出可蒸馏的话术包,生成 `memory/sales_techniques_<date>_<method>.md`
- **umbrella v2.x 路线图**:持续回填六件套详情到 references/,保持 SKILL.md 极简;**xiaobao profile 下 flat file 必修**(P0,详见 `references/***SECRET***.md`)

---

## 6. 版本历史

| 版本 | 日期 | 关键变更 |
|---|---|---|
| v1.0 | 2026-08 前 | §一-§六 基础方法论(100 行) |
| v1.1 | 2026-08-28 | +§七 Trigger Event |
| v1.2 | 2026-09-09 | +§八 MEDDPICC + §九 饲料鳜 ROI |
| v1.3 | 2026-09-10 | +§十 桑德勒痛点漏斗 |
| v1.4 | 2026-09-18 | +§四十六 Risk Inversion |
| v1.5 | 2026-09-21 | +§四十七 JOLT + §四十八 Gap |
| v1.6 | 2026-09-21 23 | +§四十九 3F 倾听(585 行) |
| **v2.0** | **2026-09-22 02** | **umbrella 重构**:SKILL.md 化 + references/ 拆分(4 个文件) + +§五十 QBS 五件套闭环 |
| **v2.0.1** | **2026-09-23 14** | **+JOLT 完整话术包**(4 步×4 类犹豫源=16 套)+ 中秋前 36h 推送时间表 + 销售 7 通 JOLT SOP + 第 3 次 TODO 累积:`xiaobao-sales.md` 单文件格式未转 SKILL 目录 |
| **v2.0.2** | **2026-09-23 14** | **新增 references/jolt_4scripts_ras.md**(本轮 18.7KB 话术包)+ references/jolt_5x7_orchestration.md(7 通 SOP 速查) |
| **v2.0.3** | **2026-09-23 17** | **+§10.5 Negative Reverse Selling**(让客户自己算反向代价,L4 已用仍犹豫时升级到 §10.5);objection_handling.md 增补 §10.5 章节;SKILL.md 索引同步 |
| **v2.0.4** | **2026-09-23 18** | **+§五十八 Assumptive Close 锁签法**(默认已签→讨论细节,补齐 JOLT→Close→Risk 链路最后闭环);新增 `references/closing_techniques.md`(3 步话术+红线+5 类 RAS 变体+孙总实战对比);SKILL.md §2 决策地图 / §2.1 切换表 / §1 触发表 / §2.3 references 列表 全部同步;§59「样板复刻」候选话术挂入 closing_techniques.md 末尾待玉芬 review |
| **v2.0.5** | **2026-09-23 17** | **+§11.4 政策时间锚定法 PTA**(把客户决策挂到外部时间锚:政策/同行新闻,降低抗拒)+ **§11.5 同省样板压力 RPA**(地域锚定+可验证样板)+ **海容 TCO 算账模板**(设备 -8 万 vs 3 年多收 30 万);新增 `references/policy_time_anchoring.md`(3 步话术+行业政策时间锚速查表)+ `references/regional_proof_case_library.md`(同省样板库江苏/广东/重庆/宁夏 4 省 + TCO 算账表 5 小时步);SKILL.md §2.3 references 列表同步;§11 时机异议 C 段升级路径(标准 §11 → PTA → Assumptive Close) |
| **v2.1.0** | **2026-09-24 00:30** | **+§六十一 拒绝后 24h 窗口期**(六件套闭环:补齐"客户离场"象限)+ `references/rejection_revisit_window.md`(5 步话术 + 3 心理机制 + 9 月拒绝客户池)+ `references/***SECRET***.md`(xiaobao profile flat file 修复 SOP,P0 第 4 次 TODO);SKILL.md 五件套→六件套决策地图升级 / §2.1 切换表新增「拒绝型」/ §2.2 成功率新增「§六十一 二次开发 +5-8%」/ §2.3 references 列表同步 |
| **v2.2.0** | **2026-09-24 10:00** | **+§48.5 Cost of Inaction 不行动成本算账法**(接 §48 Gap / §47 JOLT 临门一脚,Ecosystems.io 2024 + Richardson 出处,5 步 SOP + RAS 案例 2 个)+ **§3.5 90-秒 Video Prospecting**(Sendspark 2024 实测回复率 26% vs 文字 4%,5 个 RAS 行业脚本模板,补 §三首次接触 + §六十一拒绝后 24h + 比价时差异化);新增 `references/cost_of_inaction.md` + `references/video-prospecting-template.md`;SKILL.md §1 触发场景表新增 2 行 / §2.3 references 列表新增 2 行 / §7 累积 TODO 升至第 6 次 / 决策不擅自执行 flat file 修复(推下一档 cron) |

---

## 7. ⚠️ 累积 TODO(2026-09-24 10:00 · 第 6 次累积 · 进度 4/7)

> 📅 **本档(2026-09-24 10:00 self-evolution cron)实际进展**:
> - [x] 备份 flat file → `evolution/***SECRET***.md`(36,640 bytes,09-24 08 档)
> - [x] 创建目录 `~/.hermes/profiles/xiaobao/skills/xiaobao-sales/` + `references/` 子目录(09-24 08 档)
> - [x] 写 `skills/xiaobao-sales/TODO.md`(5 步详细 SOP + 15 个章节拆分清单,09-24 08 档)
> - [x] **本档(09-24 10)新增 2 个 references/**(子任务 ② 沉淀):`references/cost_of_inaction.md` + `references/video-prospecting-template.md`
> - [ ] 拆 15 个章节到 references/(§一 / §二 / §三 / §四 / §五 / §六 / §七 / §八 / §九 / §十 / §四十六 / §四十七 / §四十八 / §四十九 / §五十)
> - [ ] 写新 SKILL.md(框架 + 索引,行数 ≤ 200)
> - [ ] 删 flat file
> - [ ] 验证 `skill_view('xiaobao-sales')` 可用
>
> 🚨 **flat file 现状**(09-24 10 档复检):658 行 flat file 仍位于 `/Users/hua/.hermes/profiles/xiaobao/skills/xiaobao-sales.md`,**未变更**
>
> 🆕 **本档(09-24 10)新增发现**:
> 1. **本档决策**:**cron 中不擅自执行 flat file 删除**(不可逆操作 + 删除+写新 SKILL.md 一次到位风险高)。明确推下一档 cron(09-24 12:00 或 09-24 16:00)执行拆分。
> 2. **新增 2 个 references/**(本档子任务 ② 沉淀):
>    - `references/cost_of_inaction.md`(Cost of Inaction 不行动成本算账法,Ecosystems.io 2024 + Richardson,接 §48 Gap / §47 JOLT 临门一脚)
>    - `references/video-prospecting-template.md`(90-秒 Video Prospecting,Sendspark 2024,补 §三首次接触 + §六十一拒绝后 24h)
> 3. **2026 Q3-Q4 行业情报已落盘**(池州 19.6 亿鳜鱼项目 + 饲料鳜冲 50 元/斤闭口症 + 渔光一体 + AI 循环水养虾),可直接用于 §11.4 PTA 政策时间锚定法的话术素材库
> 4. **5 方向标准进化模板**(任务库空 → 行业 → 销售技巧 → 短视频 → skills 健康 → 进化报告)已写入 `evolution/2026-09-24_10.md`,下次 self-evolution cron 可直接复用
>
> 🆕 **沿用前 5 档的执行风险**(09-23 14/17/18 + 09-24 00:30/08):
> 1. **execute_code 在 cron 中被禁用**:下次 cron 跑 SOP 只能走 `terminal` + `write_file` + `read_file` 组合。
> 2. **sibling subagent 文件冲突**:write_file 同一 `evolution/<date>_<hour>.md` 会被 sibling agent 覆盖,下次需先 `read_file` 验证。
> 3. **flat file 内容陈旧**:658 行只覆盖到 §五十,缺 §五十一-§六十一(已在 default umbrella 已沉淀)。拆分时**新 SKILL.md 必须以 umbrella v2.1 框架为准**,旧章节作为 references/ 历史档案保留。
>
> 📌 **下次 cron(09-24 12:00 / 16:00 档)优先级 P0**:执行 `skills/xiaobao-sales/TODO.md` 5 步 SOP,完成拆分 → 验证 `skill_view('xiaobao-sales')` 可用 → 通知华哥 P0 闭环
>
> 📌 **玉芬月底蒸馏前必修 + 第 6 次累计**(前 5 次分别在 2026-09-23 14/17/18 + 2026-09-24 00:30/08/10)

---

> 🤖 维护:小宝 · 玉芬审
> 父 AGENTS.md:核心 2(`xiaobao-sales`,启动必读)
