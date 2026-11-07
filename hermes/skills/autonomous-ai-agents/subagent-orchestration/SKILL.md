---
name: subagent-orchestration
description: "Multi-agent work dispatch umbrella — plan→delegate→verify execution patterns and subagent tooling pitfalls. Load when: breaking a plan into delegate_task subagent calls, designing 2-stage review gates, running parallel workstreams, subagent returns 'tool not found' / stripped toolsets / empty results, or context budget blows up mid-orchestration. Covers: subagent-driven development (execute plans via delegate_task with spec-first + verify gates — full method in references/subagent-driven-development/), the 30-second toolset probe recipe (send_message/web_search/terminal commonly stripped in leaf subagents), context-budget discipline (probe before dump, subset reads), gates taxonomy (which review gate at which stage), and writing-plans template (the artifact delegates execute). Sibling skill kanban-orchestrator covers the persistent-queue orchestrator role (kanban.db routing); this skill covers in-conversation delegate_task dispatch."
version: 1.0.0
author: 渔芯科技 / curator consolidation 2026-10-23
tags: [subagent, delegate_task, orchestration, multi-agent, plan-execution, context-budget]
---

# Subagent Orchestration（类级入口）

把计划拆给 delegate_task 子代理执行、并在会话内验收结果的知识都在这里。两种派工范式的分工：

| 范式 | 用哪个 skill | 特征 |
|---|---|---|
| **会话内派工**（delegate_task，本轮发起、同步收结果） | 本 skill | 计划→规格→并发子代理→验收门 |
| **持久队列派工**（kanban.db 跨会话任务路由） | `kanban-orchestrator` | orchestrator profile 常驻、任务跨天、KANBAN_GUIDANCE 自动注入 |

## 1. 子代理执行计划（subagent-driven development）

完整方法整档收纳于 `references/subagent-driven-development/`（原独立 skill，2026-10-23 并入；README.md 即原 SKILL.md，含 references/ 四件套）：

- `references/subagent-driven-development/README.md` — 2-stage review 执行法：先写 plan 规格 → 逐项 delegate（每项带 spec + acceptance criteria）→ implementer 子代理产出 → 独立 reviewer 子代理对照 spec 验收 → 汇总。
- `references/subagent-driven-development/references/writing-plans.md` — 给子代理执行的 plan 模板（任务粒度、依赖排序、验收标准写法）。
- `references/subagent-driven-development/references/gates-taxonomy.md` — 门类型学：spec gate / implement gate / verify gate 各管什么、何时跳过。
- `references/subagent-driven-development/references/context-budget-discipline.md` — 会话上下文预算纪律（见 §3）。
- `references/subagent-driven-development/references/subagent-toolset-probe.md` — 30 秒探针配方（见 §2）。

## 2. 子代理工具集陷阱（30 秒探针）

Leaf 子代理默认拿不到父会话的完整工具面。常见被剥离：`send_message`、`web_search`（部分配置）、`terminal` 后台模式、`clarify`（永远不可用——子代理不能向用户提问）。

**探针配方（30 秒）**：派工前在子代理 goal 里加一句"先列出你可用的工具名再开工"；或首轮派一个 10 秒微任务（`echo ok`）验证 terminal 可用性。命中剥离时：把该能力移回父会话做（父会话收尾发消息/搜索），或改派 orchestrate 之外的工具面（见 writing-plans.md 的降级矩阵）。

**铁律**：需要用户交互的步骤（clarify、确认、拍板）永远留在父会话，子代理 goal 里写死假设并标注"假设不成立时返回 BLOCKED"。

## 3. 上下文预算纪律

- 子代理最终 summary 是唯一回流物——中间 tool 结果不进父会话。让子代理在 summary 里给**可验证句柄**（绝对路径 / URL / HTTP status / commit SHA），父会话抽查而非信任。
- 父会话传 context 要自包含：文件路径、报错原文、约束、语言要求全写进 goal/context 字段（子代理看不到你的会话历史）。
- 并发上限（本环境 3 个）：超过 3 个独立子任务时按依赖分批，I/O 密集（调研×3）可满发，代码改动×3 容易合并冲突，改按模块串行。

## 4. 何时不用本 skill

- 任务能用 1-3 个普通工具调用直接完成 → 直接做，别派子代理。
- 长时间后台任务 / 需要跨轮存活 → 用 terminal(background=true) 或 cronjob，不是 delegate_task（父轮被中断时子代理会被取消）。
- 跨会话、跨天的团队任务路由 → `kanban-orchestrator`。

## 5. 沉淀区

后续子代理派工类坑先落本节，攒成体系再拆 references。

- （2026-10-23 初版：内容自 subagent-driven-development 并入，见 §1）
