---
name: afu-customer-service
description: '渔芯科技阿福客服顶层门户（portal）— Voss 战术全图 / 异议处理决策树 / 渔芯客服剧本入口。触发条件：阿福执行客户服务、异议处理、客户维护、满意度跟进、客诉处理、RAS 行业客户咨询、报价异议、退订风险场景；或 cron 进化模式需要快速定位客服知识入口。'
version: 1.51.0
author: 渔芯科技 / 阿福
tags: [客服, 阿福, 谈判, Voss, RAS, 异议处理, 情绪降级, 顶层门户]
mirror_of: '~/.hermes/profiles/afu/skills/afu-customer-service/SKILL.md (afu profile 本地副本)'
---

# 阿福客服剧本 · 顶层门户（v1.51.0）

> ⚠️ **本文件是顶层 portal**。历史主体内容（v1.50.0，40+ references）保留在 afu profile 本地 `~/.hermes/profiles/afu/skills/afu-customer-service/`。Hermes session loader 不递归找 profile 深层的 skill，必须在 `~/.hermes/skills/` 顶层建轻量门户。本门户仅含触发决策树 + 技巧全图 + 资源链接，主体内容不复制避免双写漂移。

---

## 1. 1 分钟触发决策树

```yaml
客户说: "嫌贵 / 报价高"
  → 加载 references/voss-techniques.md 战术四（真假辨别 + 价值重构）
  → "您说的对，单价我们确实贵 20%。我特别好奇，您指的'值'是什么？"

客户说: "数据安全担忧 / 观望不决"
  → 加载 references/voss-techniques.md 战术三（Accusations Audit）
  → 替客户说出 3 条他还没说出口的负面指控

客户说: "投诉 / 愤怒 / 威胁退订"
  → 加载 references/emotion-deescalation-playbook.md 三级降级流程
  → 二级以上立即升级到上级 + 技术负责人

客户说: "RAS 行业趋势 / 国标 / 合规"
  → 加载 references/ras-2026-facts.md + 8/20 天下渔仓 19.6 亿信号
  → 引用 6 大事实（A 级央媒一手信源）

客户说: "适合养什么鱼 / 选型"
  → 加载 references/ras-2026-facts.md 品类适配速查表
  → 推 LookForge 仿真试跑（先看效果再投钱）

客户说: "再考虑考虑"（敷衍 / Black Swan 没浮出）
  → 加载 references/voss-techniques.md 战术五（Question Stacking 三阶追问）
  → 宽→聚焦数字→场景化，逼出真问题

客户说: "Black Swan 浮出"（老板不批 / 我觉得不值 / 别人也有）
  → 加载 references/voss-techniques.md 战术六（That's Right vs You're Right）
  → 用 That's Right 接住，让客户感到被完全听见
```

---

## 2. Voss 6 大战术全图（编号 #1-#6 + 触发场景）

| # | 战术 | 一句话 | 触发场景 | Reference |
|---|---|---|---|---|
| 1 | Mirroring（镜像） | 重复客户最后 3 个关键词 + 沉默 4 秒 | 客户首次开口 / 敷衍 | voss-techniques §1 |
| 2 | Labeling（标注） | "听起来您觉得..." | 客户表达情绪 | voss-techniques §2 |
| 3 | Accusations Audit（指控审计）| 主动替客户说出 3 条没说出口的负面想法 | 客户观望 / 防御 | voss-techniques §3 |
| 4 | 真假辨别 + 价值重构 | "客户嘴上说的，不是心里要的" | 价格异议 / 比价 | voss-techniques §4 |
| 5 | Question Stacking（问题堆叠）| 宽→聚焦数字→场景化，三阶追问逼出 Black Swan | 客户首次回答敷衍 | voss-techniques §5 |
| 6 | **That's Right vs You're Right** � | "You're Right 让客户赢了对话，That's Right 让客户赢了理解" | Black Swan 浮出后接住 | voss-techniques §6（沉淀中，待 v2.2 升版合并入主体）|

---

## 3. 渔芯两大品牌话术锚点（必对齐）

- **品牌一 AI 赋能全链条**：「客户买的是行业进化门票，设备随 AI 升级而升级」
- **品牌二 看见未来 LookForge**：「客户可以先在 LookForge 仿真测试，降低决策风险」

---

## 4. 三大禁忌（每个会话必守）

1. **不要否定客户情绪** — "您先别生气" ❌ → "我能理解您为什么这么生气" ✅
2. **不要在情绪爆发时给细节解释** — 记下来，事后再讲
3. **不要在没有授权时承诺退款/赔偿** — 用时间承诺 + 选择权替代

---

## 5. 关联子技能清单

- `references/voss-techniques.md` — Voss 6 大战术详细话术（Mirroring/Labeling/AA/真假辨别/Question Stacking/That's Right）⭐ v2.1（含战术五）+ 战术六自主沉淀中
- `references/ras-2026-facts.md` — RAS 行业 6 大事实 + 8/20 天下渔仓 19.6 亿信号 + 客户高频问答 + 品类适配速查表
- `references/emotion-deescalation-playbook.md` — 三级情绪降级流程 + 禁忌清单 + 复盘 checklist
- `references/cron-evolution-playbook.md` — Cron 进化模式规范（适用于所有 8 同事 profile 的无任务进化模式）

---

## 6. 资源链接（主体路径）

- **本主体（afu profile 本地副本）**：`~/.hermes/profiles/afu/skills/afu-customer-service/SKILL.md`
- **进化报告**：`~/.hermes/profiles/afu/evolution/{YYYY-MM-DD_HH}.md`
- **嵌入式训练 memory**：`~/.hermes/profiles/afu/memory/`

---

## 7. 自我修复自检（30 秒 SOP，每次心跳必跑）

```bash
# 1. 列全局 skill 顶层入口
ls ~/.hermes/skills/*/SKILL.md 2>/dev/null | head -20
# ✅ 顶层 SKILL.md 存在 + 内容 ≥ 1 KB = 入口正常
# ⚠️ 顶层 SKILL.md 缺失 + 深层 profile/skills/ 存在 = 必须建 portal（本文件即此场景的产物）
# ❌ 完全没有 SKILL.md 内容 = 内容缺失（不是 portal 缺失，分开处理）
```

**本门户存在原因**：2026-08-24 / 08-29 cron 多次触发"afu-customer-service skill not found"告警 → 实际内容在 afu profile 本地 `skills/afu-customer-service/` → 修复：在 `~/.hermes/skills/afu-customer-service/SKILL.md` 建 v1.51.0 顶层门户（含 1 分钟决策树 + 6 战术全图 + 5 资源链接）。

---

## 8. 待补 references（未来进化方向）

- [x] ~~战术五 Question Stacking / 问题堆叠~~ → **已沉淀 voss-techniques §5**
- [x] ~~战术六 That's Right vs You're Right~~ → **已沉淀 memory/voss-tactic-6-thats-right.md（自主沉淀 #44，8/29 16:00）**，待 9 月底合并升版 voss-techniques.md 至 v2.2
- [ ] `references/customer-mistakes-log.md` — 客户常见误区与纠正话术
- [ ] `references/lookforge-demo-script.md` — LookForge 仿真演示标准流程
- [ ] `references/evolution-report-template.md` — 阿福 cron 进化报告模板

---

> 🤖 阿福维护 · 2026-08-29 16:00 v1.51.0
> 📌 修复历史 bug：afu-customer-service 顶层入口连续 N+ 期被 loader 跳过（详见 §7）
> 📌 不复制主体内容，避免双写漂移
> 📌 战术六 That's Right 沉淀在 memory/，待 v2.2 合并入主体
