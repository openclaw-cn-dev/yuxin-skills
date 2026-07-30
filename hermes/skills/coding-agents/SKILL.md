---
name: coding-agents
description: "Unified guide for AI coding agents: Claude Code, OpenAI Codex CLI, and OpenCode. Covers orchestration patterns, tool integration, PTY handling, print mode, and multi-agent coordination."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agent, claude-code, codex, opencode, automation, pty, delegation]
    related_skills: [hermes-agent, autonomous-ai-agents]
---

# Coding Agents — Unified Skill

Three AI coding agents are available for delegating programming tasks. All share common patterns for Hermes orchestration (terminal invocation, PTY handling, workdir management, session continuation).

| Agent | Provider | Best For | Invocation |
|-------|----------|----------|------------|
| Claude Code | Anthropic | Features, refactoring, PR review, iterative coding | `claude -p 'task'` |
| Codex CLI | OpenAI | Code completion, quick fixes, PR review | `codex 'task'` |
| OpenCode | OpenCode | General coding, debugging | `opencode 'task'` |

---

## Claude Code (primary)

Claude Code is the most fully-featured coding agent. Delegates coding tasks to [Claude Code](https://code.claude.com/docs/en/cli-reference) (Anthropic's autonomous coding agent CLI) via Hermes terminal.

For the full Claude Code skill, see `references/claude-code-full.md`.

### Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** `claude` once to log in (browser OAuth), or set `ANTHROPIC_API_KEY`
- **Check:** `claude auth status --text`

### Two Orchestration Modes

**Mode 1: Print Mode (`-p`) — PREFERRED for most tasks**

Non-interactive one-shot. No PTY needed.

```bash
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**Mode 2: Interactive PTY via tmux**

For multi-turn sessions. Requires tmux orchestration.

```bash
# Start tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")
# Launch Claude Code
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")
# Handle trust dialog (Enter = default "Yes, I trust this folder")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")
# Send task
terminal(command="sleep 2 && tmux send-keys -t claude-work 'Refactor auth module' Enter")
# Monitor
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p` | Print mode (non-interactive) |
| `--max-turns N` | Limit agentic loops (print mode only) |
| `--allowedTools 'Read,Edit,Bash'` | Whitelist tools |
| `--dangerously-skip-permissions` | Auto-approve all tool use |
| `--output-format json` | Structured JSON output |
| `--resume <id>` | Continue a session |
| `-w <name>` | Isolated git worktree |
| `--bare` | Skip hooks/plugins for fast CI mode |

### Dialog Handling (Critical)

Claude Code shows two dialogs on first launch:
1. **Trust dialog** — `Enter` selects default "Yes, I trust this folder"
2. **Permissions bypass dialog** — must send `Down` then `Enter` to select "Yes, I accept"

```bash
# Trust dialog
tmux send-keys -t <session> Enter
# Permissions dialog
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### Structured Output

```bash
claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5
# Returns: {type, subtype, result, session_id, num_turns, total_cost_usd, ...}
```

### Session Continuation

```bash
# Start task
claude -p 'Start refactoring' --output-format json --max-turns 10 > /tmp/session.json
# Resume
claude -p 'Continue' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["session_id"])')
```

### OpenClaw vs Claude Code

| Task | Tool |
|------|------|
| Planning, memory, scheduling, Feishu | Hermes (direct) |
| Daily briefings, weekly reports, ops | OpenClaw Standing Orders |
| Code generation, refactoring, PR review | Claude Code |

---

## OpenAI Codex CLI

OpenAI's Codex CLI is a lightweight coding agent. See `references/codex-full.md` for the full skill.

### Basic Usage

```bash
# One-shot task
terminal(command="codex 'Fix the login bug in auth.py'", timeout=120)

# Interactive mode
terminal(command="codex", pty=true, workdir="/path/to/project")
```

### Key Features

- Direct file editing and creation
- Git integration (commit, diff, status)
- Shell command execution
- Context-aware code completion

### Common Flags

| Flag | Purpose |
|------|---------|
| `--model` | Model selection (e.g., `gpt-4o`, `gpt-4o-mini`) |
| `--temperature` | Creativity level (0.0-2.0) |
| `--max-tokens` | Response length cap |

---

## OpenCode

OpenCode is a general-purpose coding agent. See `references/opencode-full.md` for the full skill.

### Basic Usage

```bash
# One-shot task
terminal(command="opencode 'Implement the cache layer'", timeout=120)

# Interactive mode
terminal(command="opencode", pty=true, workdir="/path/to/project")
```

### Key Features

- Multi-file project understanding
- Test generation and running
- Documentation generation
- Bug detection and fixing

---

## Reference Files

| File | Content |
|------|---------|
| `references/claude-code-full.md` | Full Claude Code skill |
| `references/codex-full.md` | Full Codex CLI skill |
| `references/opencode-full.md` | Full OpenCode skill |
