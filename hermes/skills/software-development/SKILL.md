---
name: software-development
description: Engineering methodology and Hermes-specific development workflows — planning, debugging, testing, code review, subagent delegation, and Hermes skill authoring. Load when you're about to start a code task and need to pick the right workflow (TDD? spike? plan? subagent?), or when debugging within the Hermes Agent codebase itself.
version: 1.0.0
metadata:
  hermes:
    tags: [software-engineering, methodology, hermes, debugging, planning, testing]
---

# Software Development — Engineering Methodology

Class-level umbrella for engineering workflows. Choose a child skill based on where you are in the development cycle.

## When to load this skill

You're about to write code (or debug it) and need to pick the right workflow. Load this umbrella to find the child that matches your task.

## Child skills (by phase)

### Planning & exploration
- `plan/` — Write a markdown plan to `.hermes/plans/` (no execution yet).
- `writing-plans/` — Write implementation plans: bite-sized tasks, paths, code.
- `spike/` — Throwaway experiments to validate an idea before building.

### Methodology
- `test-driven-development/` — RED-GREEN-REFACTOR: tests before code.
- `systematic-debugging/` — 4-phase root-cause investigation: NO fixes without a hypothesis.
- `requesting-code-review/` — Pre-commit review: security scan, quality gates, auto-fix.
- `subagent-driven-development/` — Execute plans via `delegate_task` subagents (2-stage review).

### Debuggers
- `python-debugpy/` — Python debugging via `pdb` REPL + `debugpy` remote (DAP).
- `node-inspect-debugger/` — Node.js via `--inspect` + Chrome DevTools Protocol CLI.

### Hermes-specific development
- `hermes-agent-skill-authoring/` — Author in-repo SKILL.md: frontmatter, validator, structure.

## Reference files

### `references/hermes-runtime/`
Real-world Hermes runtime debugging recipes — load only when you have the matching symptom:

- `references/hermes-runtime/debugging-hermes-tui-commands.md` — Debug Hermes TUI slash commands (Python, gateway, Ink UI).
- `references/hermes-runtime/hermes-feishu-credential-update.md` — 更新 Hermes 飞书凭证的正确流程（config.yaml vs .env 双层配置）。
- `references/hermes-runtime/hermes-s6-container-supervision.md` — Modify / debug / extend the s6-overlay supervision tree in the Hermes Docker image.
- `references/hermes-runtime/openclaw-debug-feishu.md` — 排查 OpenClaw 飞书机器人无法接收消息的问题。
- `references/hermes-runtime/sandbox-python-debugging.md` — 诊断 Hermes sandbox 执行环境与终端 Python 环境不一致的问题。
- `references/hermes-runtime/e2e-test-recovery.md` — 当 subagent 超时或失败时，手动恢复 e2e 测试（Playwright/Cypress）。
