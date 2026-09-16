---
name: maodou-product
description: '毛豆（产品经理）核心技能集 — 产品设计冲刺、需求洞察、敏捷开发、代码协作、LookForge多阶段产品研发流程。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.3.0"
  changelog: "v1.3.0 (2026-09-15): 索引表升级 5 件套 → 6 件套（新增 Service Blueprint 渔芯版 v1.0）；新增 §六 Service Blueprint 嵌入 Sprint Day 3 + Phase 7 + 长期维护闭环；新增 §七 与其他方法论一句话定位表。"
---

# 毛豆产品经理核心技能

## 职责定位
毛豆是渔芯科技产品经理，产品部负责人。

### 产品部三大核心职责
1. **公司项目软件开发** — LookForge、鱼乐宝SaaS、渔芯装
2. **公司项目硬件开发** — RAS循环水养殖设备（HW-001～HW-018）
3. **其它客户订单** — 外部软/硬件定制订单

## ⚠️ 任务存储真相（2026-09-08 校准 — 实测确认）

**`tasks.db` 已废弃为零字节文件**（自 2026-08-26 起）。当前任务真实存储是 **`kanban.db`**：

| 存储 | 路径 | 状态 |
|---|---|---|
| ❌ tasks.db | `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db` | **0 bytes 空文件** |
| ✅ kanban.db | `/Users/hua/.hermes/profiles/maodou/kanban.db` | 活跃 |

**kanban.db `tasks` 表字段**：`id`（不是 `task_id`）、`assignee`、`status`、UNIX 秒时间戳。

**标准查询模板**（替换所有"查 tasks.db"的旧代码）：
```bash
sqlite3 /Users/hua/.hermes/profiles/maodou/kanban.db \
  "SELECT id, title, status, priority, datetime(created_at,'unixepoch')
   FROM tasks WHERE assignee='毛豆' AND status='in_progress'
   ORDER BY created_at DESC LIMIT 10"
```

## ❌ heartbeat_check.py 已坏（2026-09-08 实测）

`python3 ~/.hermes/scripts/heartbeat_check.py 毛豆` 报错指向 `/Users/hua/.hermes/profiles/zhenglishi/home/.hermes/scripts/heartbeat_check.py`，路径错乱（沙盒 $HOME 劫持）。

**修法**：忽略该脚本，直接 sqlite3 查 kanban.db，5 秒搞定。

## 核心技能调用

1. **design-sprint**（设计冲刺）：5天流程
2. **jobs-to-be-done**（需求洞察）：功能 vs 情感
3. **lean-startup**（敏捷开发）：Build-Measure-Learn
4. **multi-phase-pipeline**（多阶段产品开发）：Phase1-7

## 方法论 6 件套索引（v1.3.0 — 2026-09-15 升级）

渔芯落地版 = 母方法论 × 渔芯改造。所有渔芯版文档落位 `/Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/maodou/methodology/`，**不重复造轮子**。

| # | 方法论 | 角色 | 何时调用 | 文档 |
|---|--------|------|----------|------|
| 1 | **BMC 渔芯版 v1.0** | 商业模式层（做什么） | 新项目立项 / LookForge Phase 1 调研收口 | `2026-09-13_BMC渔芯版_v1.0.md` |
| 2 | **JTBD Canvas 渔芯版 v1.0** | 需求洞察层（为什么） | 客户访谈 / 种子客户画像 / 痛点分级 | skill `lookforge-jtbd-canvas` + `JTBD-渔芯版_v1.0_2026-09-15.md` |
| 3 | **HW-Design Sprint v1.0 渔芯版** | 快速验证层（怎么试） | HW-001~018 硬件 3 天冲刺 | `HW-Design-Sprint_v1.0_渔芯版_2026-09-15.md` |
| 4 | **Lean Canvas 渔芯版 v1.0** | 项目假设层（值不值得做） | 新 HW/SaaS 项目立项 Day 1-2 填完 | `2026-09-15_Lean-Canvas_渔芯版_v1.0.md` |
| 5 | **Kano 渔芯版 v1.0** | 需求质量层（该不该做） | Sprint Day 1 末 30min 速分 / HW 功能取舍 | `Kano-渔芯版_v1.0_2026-09-15.md` |
| 6 | **Service Blueprint 渔芯版 v1.0** ★ | 全生命周期层（怎么服务 10 年） | Sprint Day 3 末 + LookForge Phase 7 + 长期维护 | `Service-Blueprint_渔芯版_v1.0_2026-09-15.md` |
| 7 | **multi-phase-pipeline** | 项目执行层（怎么做） | LookForge Phase 1-7 全流程 | skill `multi-phase-pipeline` |

**调用顺序（产品立项 + 长生命周期流水线）**：

```
BMC（立项 Day 0）→ Lean Canvas（Day 1-2 假设验证）→ JTBD（Day 3-5 用户）
→ HW-Sprint（Day 6-9 原型）→ multi-phase-pipeline（Day 10+ 落地）
        ↑                                      ↑
Kano 嵌入 Sprint Day 1 末                Service Blueprint 嵌入 Sprint Day 3 末 + Phase 7 + 长期维护
```

**升级机制**：每补全 1 个方法论 → 升 skill 一次 v(N+1)。0.1 minor bump 用于文档增量；1.0 major 用于方法论体系重构。

## 五、Kano × Sprint × RICE 三角闭环（v1.2.0 新增 — 2026-09-15）

渔芯 5 件套不是平铺，而是 **3 维决策矩阵**：

| 维度 | 方法论 | 回答 |
|------|--------|------|
| **该做什么** | BMC / Lean Canvas | 立项 / 商业模式 |
| **该不该做** | **Kano**（需求质量分级） | 功能是基本/期望/兴奋/反向/无差异 |
| **先做哪个** | RICE（Reach/Impact/Confidence/Effort） | 排序执行 |

**Sprint Day 1 嵌入 Kano 流程**（30min 速分）：

1. 列出 Day 1 HMW 产出的所有功能点（通常 8-15 个）
2. 团队投票（每人对每个功能打 M/O/A/I/R 5 类）
3. 取众数 → Kano 类别
4. **强约束**：
   - M（基本型）必须全部做 → 列入 Backlog P0
   - O（期望型）取 RICE 分数 Top 50%
   - A（兴奋型）**≤2 个**（资源保护）
   - I / R **剔除**

**保鲜期机制**：每类标 `shelf_life`（6/12/24 月），到期自动触发重分类（IoT 类兴奋型 12 个月就过时）。

**实战记录**：Kano 渔芯版首次落地 → HW-001 滚筒微滤机 Day 1 Sprint（2026-09-15 16 时档 cron 进化产出）。

## 六、Service Blueprint 嵌入 Sprint + Phase 7 + 长期维护（v1.3.0 新增 — 2026-09-15）

渔芯 6 件套不是平铺，而是 **4 维决策矩阵**（v1.2.0 三角 + 第 4 维）：

| 维度 | 方法论 | 回答 |
|------|--------|------|
| **该做什么** | BMC / Lean Canvas | 立项 / 商业模式 |
| **该不该做** | Kano | 功能 M/O/A/I/R 分类 |
| **先做哪个** | RICE | 排序执行 |
| **★ 怎么做售后** | **Service Blueprint** | 设备 10 年 MOT + 触点 + RACI |

**Service Blueprint 渔芯版 5 大改造维度**（vs 原版）：

1. **横轴** = 设备生命周期（10 年切片），非客户旅程
2. **纵轴** = 5 道跨部门泳道（客户/销售/产品/售后/技术），非 2 道客户/后台
3. **MOT 加权** = 经济损失 ¥ + 恢复时间 h + SOP 编号 + 兜底责任人
4. **触点工具分层** = 4 类（人工/IoT/SaaS/文档），非 2 类（线上/线下）
5. **生命周期叠加** = 调试 0-3 月 / 磨合 3-12 月 / 稳定 1-5 年 / 老化 5-10 年

**3 个嵌入时点**：

| 时点 | 动作 | 责任人 |
|------|------|--------|
| Sprint **Day 3 末** | 画蓝图 v0.1 草图（售前+调试+磨合 3 阶段） | 毛豆 |
| LookForge **Phase 7 交付** | 升级 v1.0 完整 6 阶段 | 毛豆 + 售后 |
| 设备**售出 3/12 个月 + 3/5/7 年** | 复盘升级 v1.1 / v2.0 / v3.0 | 毛豆 + 玉芬 |

**实战记录**：Service Blueprint 渔芯版首次落地 → HW-001 滚筒微滤机（含 4 个 MOT：D7 反冲洗堵塞 ¥5万 / M3 滤网破损 ¥1万 / Y2 PLC 老化 ¥2万 / Y7 整机翻新 ¥3万）。

## 七、与其他方法论一句话定位（v1.3.0 新增 — 2026-09-15）

| 方法论 | 一句话定位 | 渔芯场景 |
|--------|-----------|----------|
| **BMC** | 商业模式（客户/价值/成本/收入） | 立项 Day 0 |
| **Lean Canvas** | 项目假设（问题/解决方案/指标） | Day 1-2 |
| **JTBD Canvas** | 用户为什么雇佣/解雇产品 | Day 3-5 |
| **HW-Sprint** | 5 天原型验证（理解-定义-设想-原型-测试） | Day 6-9 |
| **Kano** | 需求该不该做/做哪类（M/O/A/I/R） | Sprint Day 1 末 |
| **Service Blueprint ★** | **设备全生命周期服务怎么做（售前-调试-磨合-稳定-老化-退役）** | **Sprint Day 3 + Phase 7 + 长期维护** |
| **multi-phase-pipeline** | Phase 1-7 软件/产品执行流程 | Day 10+ 落地 |

## 公司两大品牌版块

**品牌一：AI赋能全链条** — 让水产养殖行业与AI深度绑定
**品牌二：看见未来** — LookForge 让设备开发在网上仿真验证

## cron 自我进化模式（华哥铁律）

> **华哥原话**："如果我没有帮你确定下一步的任务，并且在各个选项不冲突的情况下。你就默认按顺序执行。"

**空闲时进化路径**（决策挂起 ≥24h 触发）：
1. 查 kanban.db 确认无任务
2. 写 evolution 报告到 `~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md`
3. **阻塞 vs 非阻塞路径切分**（详见 references/cron-self-evolution-patterns.md）
4. **催办清单 V1.0** 模板
5. 走 cron auto-delivery 推送飞书群（**不要** send_message）

## 飞书消息发送

- APP_ID: `cli_a964873dd7b8dbda`
- APP_SECRET: `***REDACTED***`
- **大群 chat_id**: `***SECRET***` ✅
- ❌ 产品部-毛豆群 `***SECRET***`（Bot未加入）

**Cron 报告防重复**：final response 通过 origin auto-delivery 自动送达。手动 `send_message` 同 target 会触发 `duplicate_target`。

## LookForge 项目状态

**路径**：`/Users/hua/6-产品研发/渔芯独角兽/02-产品开发综合平台/00-综合开发平台/`

**Phase 1-7 全实装**（v1.1.1，commit `50f1b9ee`）

**净 P0 = 2 项真实未解**（9/7 20:00 实测）：
- #8 专利 API（占位符 → 真 API）
- #5 ChromaDB 架构（B1/B2）

## RAS硬件开发清单（HW-001～HW-018）

滚筒微滤机 / 生物滤池 / 纯氧增氧系统 / UV杀菌器 / 蛋白质分离器 / 移动床生物滤池 / 脱气塔 / 制氧机 / 纳米曝气机 / 射流增氧机 / 臭氧发生器 / 养殖水箱 / 鱼马桶 / 一体化RAS系统 / 磁悬浮热泵温控 / 循环水泵 / 生化滤池填料 / 氧锥

## 硬件开发标准流程（7环节）

需求定义 → 方案设计 → 仿真验证 → 工艺设计 → 生产测试 → 量产导入 → 差异化标记

## 工作流偏好

- **默认不复制资料到桌面**（华哥 2026-07-03 明确）
- **默认顺序自动执行**（华哥 2026-07-02 明确）
- **阶段汇报每 5-10 步一次**，不逐步请示

## references 索引

- `references/cron-self-evolution-patterns.md` — 决策挂起期处理范式（2026-09-08 新增）
- `references/simulation-algorithms.md`
- `references/cad-verification.md`
- `references/hw-batch-development.md`
- `references/saas-conversion-path.md`
- `references/lookforge-optimization-report.md`
- `references/blueprint-am-tech-intel.md`
- `references/v2.1.1-bug-fix-case.md`
- `references/fmea-methodology.md`
