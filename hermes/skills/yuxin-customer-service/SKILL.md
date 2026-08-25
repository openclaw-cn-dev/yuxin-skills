---
name: yuxin-customer-service
description: 渔芯科技 (yuxin) customer service playbook — Voss tactical empathy (Mirroring / Labeling / Accusations Audit), 渔芯-aligned objection handling, RAS-industry 2026 facts, three-tier customer emotion de-escalation. Use when handling 渔芯 customer objections, complaints, RAS industry questions, sales calls, or any customer-facing dialogue that should reflect 渔芯 brand voice (AI赋能全链条 / LookForge 仿真 / 数据安全承诺).
version: 1.0.0
author: 渔芯科技 / 阿福
tags: [客服, 谈判, Voss, RAS, 异议处理, 情绪降级, 渔芯, yuxin]
---

# 渔芯客服剧本 · Yuxin Customer Service Playbook

> 一份随渔芯业务演化的活文档。客户问什么、怎么答、用什么心态答——全在这里。
> 原则：**先共情再解决** · **理解是成交的前一秒** · **把投诉当礼物**

---

## 三大支柱

| 支柱 | 包含技巧 | 何时用 |
|---|---|---|
| **1. Voss 战术共情** | Mirroring · Labeling · Accusations Audit · 真假辨别+价值重构 · **Question Stacking 问题堆叠** | 客户表达异议、犹豫、不满 |
| **2. 2026 RAS 行业事实** | 国标《集装箱式循环水养殖标准化指南》· 大口黑鲈工厂化 RAS · 尾水处理痛点 · **8/22 宜昌铜鱼政务品牌化 · 8/23 巨头入场 · 5/18 新坝镇实证** · 7 大品类适配 | 客户问行业趋势 / 选型 / 合规 |
| **3. 三级情绪降级** | 一级轻度不满 / 二级中度愤怒 / 三级重度暴怒 | 投诉、威胁退订、情绪激动 |

---

## 渔芯两大品牌版块（客服话术必须对齐）

### 品牌一：AI赋能全链条
**话术锚点**：「客户买的是行业进化门票，设备随 AI 升级而升级」

### 品牌二：看见未来（LookForge）
**话术锚点**：「客户可以先在 LookForge 仿真测试，降低决策风险——这是差异化服务承诺」

---

## 路径与目录约定

支撑 skill 的内容已上提为本剧本的 references 目录（位于全局 skill 库，可被 skill_view 发现）：

```
/Users/hua/.hermes/skills/yuxin-customer-service/
├── SKILL.md
└── references/
    ├── voss-techniques.md                  # 支柱 1：Voss 三大战术详细话术
    ├── ras-2026-facts.md                   # 支柱 2：RAS 行业三大事实与高频问答
    └── emotion-deescalation-playbook.md    # 支柱 3：三级情绪降级流程
```

> ✅ **未来 cron 启动时**：`skill_view yuxin-customer-service` 加载本剧本，剧本内会指引读 references/ 拿具体话术。不再需要去 AFU profile 下找文件级 skill。

### 写入路径（避免 HOME 劫持）

所有客户资料、进化报告、FAQ 扩充都必须写到**绝对路径**：

```
/Users/hua/.hermes/profiles/afu/evolution/{YYYY-MM-DD_HH}.md  # 进化报告
/Users/hua/.hermes/profiles/afu/memory/                        # 嵌入式训练产物
```

写之前强制自检：

```bash
echo "HOME=$HOME"
# ✅ HOME=/Users/hua
# ❌ HOME=/Users/hua/.hermes/profiles/afu/home/  → 已被劫持，必须用绝对路径
```

---

## 快速决策树

```
客户说什么 → 怎么回
│
├─ 嫌贵 / 报价高
│  → Voss Accusations Audit：「您可能会觉得我们比传统设备贵不少……这些顾虑都很正常」
│  → 进入战术四真假辨别 + 价值重构（找到客户「嘴上说的」和「心里要的」之间那道沟）
│  → 切到品牌锚点：行业进化门票 / LookForge 仿真承诺
│
├─ 担忧数据安全
│  → Voss Accusations Audit（数据场景）
│  → 强调 LookForge 仿真是「先看效果再投钱」，降低风险感
│
├─ 观望不决
│  → Voss Mirroring + Accusations Audit 组合
│  → 引用 8/22-8/24 三大信号叠加（政府站台 + 巨头抢位 + 镇级实证）
│  → 引用蓝海战略 ERRC 框架：重新定义价值主张
│
├─ 询问 RAS 行业 / 国标 / 合规
│  → 引用 RAS 2026 三大事实 + 8/22 宜昌铜鱼政府背书
│  → 突出渔芯方案与国标同向设计
│
├─ 询问适合养什么鱼
│  → 引用品类适配速查表：高价值淡水鱼（加州鲈、鳜鱼、石斑、三文鱼）
│  → 推 LookForge 仿真试跑
│
└─ 投诉 / 愤怒 / 威胁
   → 进入三级情绪降级流程（一级 / 二级 / 三级）
   → 二级以上必须立即升级到上级 + 技术负责人
```

---

## 三大禁忌（每个会话必守）

1. **不要否定客户情绪** — "您先别生气" ❌ → "我能理解您为什么这么生气" ✅
2. **不要在情绪爆发时给细节解释** — 记下来，事后再讲
3. **不要在没有授权时承诺退款/赔偿** — 用时间承诺 + 选择权替代

---

## 进化机制

每次 cron 心跳（任务池空闲时）：

1. 复盘最近 3 次客服执行，找 1-3 条改进
2. 学 1 个新技巧（Voss / 蓝海 / 影响力心理学 / 跨越鸿沟）
3. 读 1 篇 RAS 行业最新动态
4. 把沉淀写回 `~/.hermes/profiles/afu/evolution/{date}_{hour}.md` + **必须回流到本剧本的支撑 skill**
5. 飞书推送（凭证过期时降级为本地）

**关键教训**（2026-08-23 复盘）：前几次进化的内容散落在 evolution_log.md 而没回流到 skills/，导致下次 cron 读不到。**每次进化必须同时 patch 一个 skill**，否则视为无效进化。

**关键教训 v2**（2026-08-24 cron 顶置告警沉淀）：当上层 cron 出现 `[Skill(s) not found and skipped: yuxin-customer-service]` 时，是 **skill 找不到顶层入口** — 不是 skill 内容缺失。`yuxin-customer-service` 活在 `productivity/yuxin-customer-service/` 深层，Hermes skill loader 不会递归找。**修复模式：顶层 portal 模式** — 在 `~/.hermes/skills/<skill-name>/SKILL.md` 顶层建一个轻量门户（含触发决策树 + 资源链接），主体仍在深层 `productivity/<skill-name>/references/`。详见下文「⛑️ 自我修复自检」与「顶层 portal 模式」两节。

### ⛑️ 自我修复自检（每次心跳必跑 30 秒）

每次 cron 进入进化模式后，在切到学习/调研/优化步骤之前跑一次：

```bash
# 1. 列全局 skill 顶层入口是否齐全
ls ~/.hermes/skills/*/SKILL.md 2>/dev/null | head -20
# 任何"被自身 description 引用但实际不在顶层"的 skill 都要建 portal
# 例：cron 跳过 "yuxin-customer-service" → ~/.hermes/skills/yuxin-customer-service/SKILL.md 缺失
#     修复：在该路径下写一个轻量 SKILL.md（< 8 KB），含触发场景 + 决策树 + 指针到主体路径
```

**判定规则**：

- ✅ 顶层 `SKILL.md` 存在 + 内容 ≥ 1 KB = 入口正常
- ⚠️ 顶层 `SKILL.md` 缺失 + 深层 `productivity/*/SKILL.md` 存在 = 必须建 portal（cron 不会递归找深层）
- ❌ 完全没有 `SKILL.md` 内容 = 内容缺失（不是 portal 缺失，分开处理）

### 顶层 portal 模式（2026-08-24 阿福实战沉淀）

**场景**：某 skill 内容已沉淀到 `productivity/<name>/SKILL.md`（深层），但 cron / agent 启动时 Hermes skill loader 跳过它（找不到顶层入口）。

**模式**：

```
~/.hermes/skills/<skill-name>/SKILL.md          ← 新建：轻量门户（< 8 KB）
~/.hermes/skills/productivity/<skill-name>/SKILL.md             ← 已存：主体（不动，避免历史沉淀漂移）
~/.hermes/skills/productivity/<skill-name>/references/         ← 已存：详细参考
```

**portal SKILL.md 必须包含（最少 5 段）**：

1. `description:` — 触发场景，覆盖高频 query
2. **触发决策树**（YAML / mermaid 都可）— "客户说 X → 用 Y"
3. 关键技巧全图（编号 #1-#N + 来源 + 场景）— 1 行/技巧
4. 关联子技能清单（`related_skills:` 字段）
5. 资源链接（主体 SKILL.md 路径 + 各 references/ 文件）

**反模式**：

- ❌ 在 portal 复制主体内容 → 双写漂移
- ❌ 把整个 `productivity/` 上提到顶层 → 引用路径全要重写
- ❌ portal 不写决策树 → 用户加载后还是不知道用哪个子 skill
- ❌ portal 上万字（portal 越轻越好，> 10 KB = 失去 portal 的意义）

**真实案例**：2026-08-24 阿福 cron 顶层出现"afu-customer-service skill 找不到"告警 → 实际内容在 `profiles/afu/skills/productivity/afu-customer-service/SKILL.md`（v1.33.0，40+ references）→ 修复：在 afu profile 顶层 `skills/afu-customer-service/SKILL.md` 建 v1.34.0 门户（6.6 KB），含 1 分钟触发决策树 + 28 编号技巧全图 + 8 个资源链接 + `mirror_of:` 元数据诚实标注。

---

## 参见

- `references/voss-techniques.md` — Voss 五战术详细话术（Mirroring / Labeling / Accusations Audit / 真假辨别+价值重构 / **Question Stacking 问题堆叠**）⭐ v2.1
- `references/ras-2026-facts.md` — 2026 RAS 行业六大事实（国标 / 大口黑鲈 / 尾水 / 8/22 宜昌铜鱼政务品牌化 / 8/23 巨头入场 / 5/18 新坝镇实证）+ 客户高频问答标准答案 + 品类适配速查表
- `references/emotion-deescalation-playbook.md` — 三级情绪应对流程 + 禁忌清单 + 复盘 checklist
- `references/cron-evolution-playbook.md` — **8/24 毛豆沉淀** Cron 进化模式通用规范：4 维度产出框架 + P0 跟进机制 + 方法论轮换策略 + skills 自检 30 秒 SOP（适用于所有 8 同事 profile 的无任务进化模式）

## 待补 references（未来进化方向）

- [x] ~~`references/objection-blue-ocean.md` — 当客户说「比 X 贵」时的 ERRC 蓝海转化~~ → **已并入 `voss-techniques.md` 战术四 §4.3 价格异议四种本质**
- [ ] `references/customer-mistakes-log.md` — 客户常见误区与纠正话术（建议下一轮进化补）
- [ ] `references/lookforge-demo-script.md` — LookForge 仿真演示标准流程（先看效果再投钱）
- [ ] `references/evolution-report-template.md` — 阿福 cron 进化报告模板（8/24 验证可工作的 §0-§7 结构）
