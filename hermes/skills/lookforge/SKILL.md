---
name: lookforge
description: "LookForge 多阶段产品研发平台类级技能 — Phase 1-7 全流程总纲 + Phase 1 完成后的智能推荐方向 prompt（JTBD 标签注入 + 智能排序 V1.0 模板）+ P0/P1 路线图包的市场侧重估技术（4 类外部信号 × 真实成本/失败案例交叉校验）+ Phase 3 创意落地 3 步法（JTBD 标签注入 + 前端分组视图 + 智能排序）。触发：LookForge Phase 1/3 落地、Phase 1 完成后选方向、路线图 P0/P1 估时复核、JTBD 标签注入、创意分组/排序前端视图。"
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
  created: "2026-09-17 curator consolidation"
  absorbed: [phase1-recommend-prompt, market-reweight-p0, jtbd-phase3-landing-sop]
  related: [maodou-product, multi-phase-pipeline, product-launch-playbook]
---

# LookForge 多阶段产品研发平台

## §0 平台总纲

- **路径**：`/Users/hua/6-产品研发/渔芯独角兽/02-产品开发综合平台/00-综合开发平台/`（Phase 1-7 全实装 v1.1.1）
- **Phase 1** 调研 → **Phase 3** 创意落地 → **Phase 7** 交付/维护（完整 7 阶段见 skill `multi-phase-pipeline`）
- 净 P0（9/7 实测）：#8 专利 API 真实化、#5 ChromaDB 架构 B1/B2
- 方法论联动：BMC/Lean Canvas/JTBD/Kano/Service Blueprint 六件套见 `maodou-product`

## §1 Phase 1 完成后 → 智能推荐方向

Phase 1 调研收口后用推荐 prompt 生成候选方向：读 Phase 1 调研数据 → JTBD 标签注入（功能/情感/社交 Job 分层）→ 四维打分（市场吸引力/技术可行性/协同效应/资源匹配）→ 输出 Top-N 推荐卡给华哥拍板。完整 prompt 模板照抄 `references/phase1-recommend-prompt-v1.0.md`。

## §2 P0/P1 路线图市场侧重估（估时复核）

内部估时完成后，用 4 类外部信号重估市场侧权重：① 真实成本数据（报价单/招标价）② 失败案例 ×3 ③ 竞品动向 ④ 客户付费信号；任一信号与内部假设冲突即触发 P0 重排。案例复盘见 `references/market-reweight-p0-case-study.md`。

## §3 Phase 3 创意落地 3 步法

1. **JTBD 标签注入** — 给每个创意打 job 标签（对齐 §1 的标签体系）
2. **前端分组视图** — 按 job 类型分组展示创意
3. **智能排序** — RICE/影响力排序落位（复用 `maodou-methodology-toolbox` 的 rice_score.py）

完整 SOP 与界面规格见 `references/jtbd-phase3-landing-sop.md`。

## §4 关联

- 运维/部署/验证 SOP：`devops/lookforge-ops`（Docker 端到端验证、路径权威真相）
- ChromaDB 排障：`product-debugging/lookforge-chromadb-debug`
- MCP 集成：`productivity/lookforge-mcp-hermes`
