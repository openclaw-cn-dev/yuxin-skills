---
name: hermes-ops
description: 'Hermes 自身运维类级入口（umbrella）— 把 Hermes 生态的三大运维面收敛到一个入口：① hermes-agent 本体升级/GitHub 同步（→ hermes-agent、agent-tool-sync）② 多 profile gateway 运维（→ hermes-gateway-profile-ops）③ state.db 会话库瘦身（→ hermes-state-db-maintenance）。触发条件：Hermes 升级/update/同步、gateway 不回/502/巡检、state.db 磁盘告警、profile 启停、以及任何「Hermes 自身坏了/满了/旧了」类任务。先从本 skill 判断该进哪个子 skill，再加载对应 SKILL.md。'
version: 1.0.0
author: curator consolidation 2026-10-16
tags: [hermes, ops, umbrella, gateway, sync, state-db]
---

# Hermes Ops — 类级入口（Umbrella）

Hermes 自身（CLI、skills、plugins、cron、gateway、state.db）的运维知识分散在三个子 skill 里。本 skill 是它们的路由层：命中任务后按下面的分类表跳转，不要在这里重复子 skill 的 SOP。

## 1. 升级 / 同步 / 版本管理 → `hermes-agent` + `agent-tool-sync`

- Hermes 本体的安装、升级、`hermes update`、config/config.yaml 修改、模型与 provider 切换 → **`hermes-agent`**（bundled，权威 API 面）
- 任意 AI 编码工具（Codex / Claude Code / Hermes）的「定期升级 + 状态导出 + 脱敏 + GitHub 私仓备份」cron 管线搭建 → **`agent-tool-sync`**（含 hermes-sync-cron-ops 运维 SOP、yuxin-skills 仓库推送）
- 判断规则：改 Hermes 配置/行为 = hermes-agent；给工具加自动升级+备份管线 = agent-tool-sync。

## 2. Gateway / profile 运维 → `hermes-gateway-profile-ops`

- 网关不回、502/402/429/401、profile 启停/拉起、launchd plist、每小时巡检、模型切换、Codex CLI SSE、LLM Gateway :18888 → **`hermes-gateway-profile-ops`**（第一步先读其 references/gateway-online-detection.md，全正常回 [SILENT]）

## 3. 会话库 / 磁盘 → `hermes-state-db-maintenance`

- state.db 数 GB、磁盘守护 cron 告警、prune vs 摘要归档决策、FTS/trigram 结构 → **`hermes-state-db-maintenance`**（核心结论：state.db 是一族不是单文件；根因 sessions.auto_prune: false；trigram 表绝不能删；cron 会话 ~90% 可直接 prune）

## 3.5 模型 / provider / 多云 LLM 配置 → `multi-cloud-llm-architecture`

- Hermes 多 provider 架构、模型切换、免费额度 provider 池、401/402/429 余额与限流、provider 健康检查 → **`multi-cloud-llm-architecture`**（gateway 层面的故障定位仍在 `hermes-gateway-profile-ops`；本条只管「配置哪个模型/用哪家 provider」这一层；minimax→ollama fallback 验证/切换/健康检查脚本 2026-10-30 起也在该 skill 的 references/minimax-fallback-to-ollama/）

## 4. 沉淀区（未来吸收位）

后续新发现的 Hermes 自身运维类坑，若不足以独立成 skill，先落在本节；积累成体系后再拆子 skill。

- （空 — 2026-10-16 初版）

## 5. 相邻 umbrella 边界（curator 2026-10-30 划定）

| 域 | umbrella | 分工 |
|---|---|---|
| 团队架构（搭建/扩编/协作机制） | `productivity/multi-agent-team-architecture` | 改架构、加 agent、协作框架 → 那边 |
| 团队日常运营（派单/验收/扫描） | `devops/company-ops-agent-management` | 玉芬每日管理动作 → 那边 |
| 多 LLM provider / 模型切换 | `devops/multi-cloud-llm-architecture` | 配置哪个模型/哪家 provider（含 2026-10-30 并入的 minimax-fallback-to-ollama 验证包）→ 那边 |
| macOS 本机自动化/磁盘健康 | `devops/macos-automation` | 系统层自动化与磁盘审计清理 → 那边 |
| Docker 容器/自愈巡检 | `devops/docker-management` | 容器生命周期 + auto-remediation → 那边 |
| cron 自进化协议 | `cron-self-evolution-toolkit` | 任何 agent 写 cron 自进化 SOP（含 afu/heidou/laomo/升级纪律四子库）→ 那边 |
