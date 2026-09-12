---
name: ***SECRET***
description: Cron 自我进化模式 — 滚动表/催办清单/路线图诊断模板
license: MIT
metadata:
  author: 渔芯科技
  version: "0.1.0"
---

# Cron Evolution Appendices

> ⚠️ 本 skill 由毛豆自我进化模式创建（2026-09-11）。
> 📌 注意：之前 evolution 报告中曾引用过此 skill 名，但实际不存在。本 skill 是事后补建，避免下次再自创引用。

## 用途

毛豆 cron 自我进化模式（maodou-product §cron 自我进化模式）需要：
1. **Decision-Tracking 滚动表** — Pattern 2（决策挂起 ≥24h → 催办门槛）
2. **催办清单 V1.x** — 已超 24h 的决策清单
3. **路线图诊断模板** — §D 现状盘点 + §D 缺口诊断 + §D 决策建议
4. **Skill 体检表** — 上次状态 / 本次观察 / 行动 三栏

## 滚动表模板

| 决策 | 发起 | 当前时长 | Pattern 2 | 状态 |
|---|---|---|:---:|---|
| ... | YYYY-MM-DD HH | ~Nh | ✅ 适用 / ❌ 临界 | 可催办 / 跨 agent / 待华哥 |

**Pattern 2 判定**：决策提出 ≥24h 仍 0 异议 → 升级催办门槛。

## 催办清单模板

> **催办清单 V1.x**（YYYY-MM-DD HH:MM 校准）：N 项已超 24h 0 异议 — <项1> / <项2> / ...

## 路线图诊断模板

```
§D.X {产品} v1.x → v1.y 路线图缺口诊断（YYYY-MM-DD HH时档）

§D.1 现状盘点（事实，不杜撰）
§D.2 已知未解（net P0）
§D.3 用户旅程盲区
§D.4 增量决策表（# / 项 / 优先级 / 工时）
§D.5 跨决策依赖图
```

## Skill 体检表模板

| Skill | 上次状态 | 本次观察 | 行动 |
|---|---|---|---|
| ... | vX.Y.Z | ... | patch / 不动 / 跳过 |

## Pitfall

❌ **不要在 evolution 报告中引用尚未存在的 skill**（如曾误引用"***SECRET***"）。
✅ 引用前用 `find ~/.hermes -name "<skill 名>"` 验证存在。

---

> 🤖 毛豆 · 2026-09-11 12:00 · cron evolution appendices v0.1