---
name: lookforge-ops
description: LookForge 项目运维类级入口 — 路径与任务库权威真相、Docker 端到端验证 SOP、端口冲突解决、API 健康检查、git dirty 监测、evolution 报告路径、ChromaDB 向量库问题排查入口。触发条件：任何 cron 心跳检查 LookForge、引用 LookForge 源码路径、查询 kanban.db / tasks.db、docker 启动/验证、端口占用排查、Claude Code 调用 LookForge、毛豆验证 LookForge 是否可用。2026-09-09 curator 合并原 lookforge-paths-canonical + lookforge-verify 两个独立 skill。**待办任务侦察：#23「PostgreSQL 强一致」已判幽灵任务（原目标 2026-05 已完成），剩余真实工作 = 4 个持久化缺陷补全 ~2-2.5 天，先读 references/task23-ghost-recon-2026-09-26.md 再动 Sprint W。#22「ChromaDB」同日完成前置侦察（2026-09-26 23 时档毛豆）：接线真实非幽灵，但老莫 9/20-9/22 重建的 `ras_knowledge_zh`(89 docs) + `lookforge_knowledge_zh`(197 docs) BGE-zh 512 维中文库是孤儿数据（服务端 0 处接线，4 个月检索缺口）；#22 实际工作 = 服务端 collection 切换改造 0.5-1 天（挂 BGE-zh 单例 + 成对切 embedding function 否则 384/512 维度运行时报错），**不依赖 #23 可提前做**；报告见部门空间 maodou/LookForge_ChromaDB向量库前置侦察_2026-09-26.md。**
version: 1.0.0
author: 渔芯科技 · curator 合并
tags: [lookforge, 路径真相, docker, 验证, 端口冲突, 健康检查, 任务库, cron]
---

# LookForge 运维（类级）

LookForge 的运维知识分为两类：**静态真相**（路径/任务库落点——任何 cron 引用 LookForge 前必读）与**动态验证**（端到端实测 SOP——怀疑服务不可用时执行）。两者原为两个独立 skill，2026-09-09 curator 合并为本类级入口。

## 1. 路径与任务库权威真相 → `references/lookforge-paths-canonical/SKILL.md`

原 `lookforge-paths-canonical`（2026-09-04 02:xx cron 实测固化）整档收纳于 `references/lookforge-paths-canonical/`：

- §1 LookForge 源码/项目真实路径（先看这个，勿信旧文档路径）
- §2 任务库（kanban.db / tasks.db）真实落点与查询方式
- `references/***SECRET***.md` — EQSim 与 LookForge 并行时的坑
- `templates/prd-decision-record-template.md` — PRD 决策记录模板

**触发**：cron 心跳检查、引用 LookForge 源码路径、查 kanban.db/tasks.db、监测 git dirty、写 evolution 报告引用路径、Claude Code 调用 LookForge。

## 2. 端到端实测验证 SOP → `references/lookforge-verify/SKILL.md`

原 `lookforge-verify`（v1.1.1，2026-09-04 06:00 cron 实测）整档收纳于 `references/lookforge-verify/`：

- Docker 启动 + 端口冲突解决 + API 健康检查的完整 SOP
- 实测踩坑档案：`references/lookforge-pitfalls-2026-09-04.md`、`references/***SECRET***.md`、`references/***SECRET***.md`

**触发**：毛豆需要验证 LookForge 当前是否可用、启动 docker 容器、排查端口问题。

## 3. 快速判定表

| 症状 | 加载哪个分册 |
|---|---|
| 不确定路径/DB 落点，要写 SQL 或 cd | §1 paths-canonical |
| 服务疑似挂了/要启动/端口被占 | §2 verify |
| 向量库（ChromaDB）相关报错 | 见 skill `lookforge-chromadb-debug`（独立 skill） |
| MCP 接入/双端调用 | 见 skill `lookforge-mcp-hermes`（独立 skill） |

## 4. 关联 skill

- `lookforge-chromadb-debug` — ChromaDB 向量库问题排查
- `lookforge-mcp-hermes` — MCP Server 双端接入
- `kanban-orchestrator` — 任务编排与任务库操作通用纪律
- `***SECRET***` — 跨 session 数据核验铁律（引用路径前先 ls 验证）
