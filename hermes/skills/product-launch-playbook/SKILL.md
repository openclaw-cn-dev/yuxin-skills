---
name: product-launch-playbook
description: 渔芯新产品从 Stage 0 立项到上线收费的全流程类级 playbook — 三画布产品定义 + 种子客户调研、JTBD-4C 立项决策过滤、HTML 原型大样、全平台脚手架搭建、上线合规手续（ICP/软著/备案）、收款与发票基建。触发条件：华哥/产品经理说"立项/做新产品/新功能定义/出大样/出原型/参考同类产品/要不要做 X/上线要办什么手续/ICP/软著/怎么收费/开发票"，或任何渔芯产品 Stage 0 → launch 流程。
---

# 产品立项到上线全流程 Playbook（类级）

渔芯新产品 **Stage 0 决策 → 定义 → 原型 → 搭建 → 合规 → 收费** 的类级入口。2026-09-02 curator 合并：6 个原独立 skill 整档收纳于 `references/`（SKILL.md + 配套 scripts/templates 原样保留），按阶段取用。

## 阶段路由

| 阶段 | 读什么 | 内容 |
|---|---|---|
| 1. 立项决策（做不做） | `references/jtbd-4c-product-launch/` | JTBD Canvas 8 维度 + 4C Viability Test（Akash Rathi）双视角过滤 + 渔芯 3 大实战案例索引（HW-007/Oceanloop/鱼乐宝 v2.0）+ 5 步应用 SOP |
| 2. 产品定义（做什么） | `references/***SECRET***/` | 三画布方法论（JTBD 客户需求洞察 / Lean Canvas 商业模式 / Design Sprint 原型验证）+ 种子客户 4 步筛选漏斗 + 试点客户获取 SOP |
| 3. 原型大样（长什么样） | `references/product-mockup/` | HTML 可视化原型大样 + 竞品调研先行 + 手机 App 风格 HTML 骨架模板（templates/） |
| 4. 快速搭建（做出来） | `references/yuxin-product-bootstrap/` | 从零到全平台（桌面 PWA + 移动端 + Chrome 插件）或轻量单文件 MVP；编号查重（根目录+渔芯独角兽两处）+ 端口验证 + UI 验收四步法（navigate→click→vision→console） |
| 5. 合规手续（能不能上） | `references/product-compliance/` | 上线证照速查：ICP 备案/许可证、软著、收费合规、APP 上架；**核心判断线：产品出现在线支付按钮即触发 ICP 许可证义务** |
| 6. 收款发票（怎么收钱） | `references/payment-invoice-setup/` | 可复用发票 widget + 法务合规 + 三阶段开票路线图 |

## 使用纪律

- 新立项一律先过阶段 1（JTBD-4C 过滤），Stage 0 未通过不要进入定义/搭建——避免拍脑袋立项。
- 各阶段细节（模板、脚本、实战案例）全部在对应 `references/` 子目录内；本 SKILL.md 只做路由，不重复内容。
- 原各 skill 的全部触发词已并入本 description；若 description 未命中，直接按上表翻 references/ 对应子目录。