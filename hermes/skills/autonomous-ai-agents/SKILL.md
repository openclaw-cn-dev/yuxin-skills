---
name: autonomous-ai-agents
description: Skills for delegating coding tasks to autonomous AI agents — Claude Code, OpenAI Codex, OpenCode, and the Hermes Kanban routing system. Load when you need to delegate implementation work to a sub-agent or coordinate multiple agent runtimes inside Hermes.
version: 1.0.0
metadata:
  hermes:
    tags: [multi-agent, delegation, claude-code, codex, opencode, kanban, hermes-agent]
---

# Autonomous AI Agents — Delegation & Multi-Agent Workflows

Class-level umbrella for **delegating work to autonomous AI coding agents**. Each child skill targets a different agent runtime or coordination pattern.

## When to load this skill

You're about to delegate implementation work to a sub-agent, route work through Hermes Kanban, or configure an external agent runtime.

## Child skills

### Agent runtimes (pick one)
- `hermes-agent/` — Configure, extend, or contribute to Hermes Agent itself.
- `claude-code/` — Delegate coding to Claude Code (Anthropic's CLI agent).
- `codex/` — Delegate coding to OpenAI Codex CLI.
- `opencode/` — Delegate coding to OpenCode CLI.
- `coding-agents/` — Router/dispatcher for choosing the right agent backend.

### Kanban coordination
- `kanban-codex-lane/` — Use Codex CLI as an isolated implementation lane inside a Kanban worker.

## How to choose

- **I want Hermes to do work itself** → `hermes-agent/`
- **I want to delegate to Claude Code** → `claude-code/`
- **I want to delegate to OpenAI Codex** → `codex/`
- **I want to delegate to OpenCode** → `opencode/`
- **I want a router that picks the right backend** → `coding-agents/`
- **I want Kanban to fan out to Codex in parallel** → `kanban-codex-lane/`

## Related skills

- `devops/kanban-orchestrator/` — The Kanban orchestrator role (decomposes work and routes it).
- `devops/kanban-worker/` — The Kanban worker role (executes a single task).
- `software-development/subagent-driven-development/` — Generic subagent delegation patterns.
