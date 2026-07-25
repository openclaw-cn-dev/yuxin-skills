---
name: github
description: GitHub workflow skills — CLI and REST API patterns for working with GitHub from a terminal or scripted agent. Each child skill is a distinct workflow (auth, issues, PRs, code review, repo management, codebase inspection). Load the umbrella when you need to choose which child skill fits your GitHub task.
version: 1.0.0
metadata:
  hermes:
    tags: [github, git, cli, rest-api, devops, workflow]
---

# GitHub Workflow Skills

Class-level umbrella for working with GitHub from Hermes. All skills use the `gh` CLI or REST API and work with HTTPS tokens, SSH keys, or the `gh auth` flow.

## When to load this skill

You're about to do something with GitHub and need to pick the right workflow. Load the umbrella, then load the matching child.

## Child skills (load the matching one)

- `github-auth/` — HTTPS tokens, SSH keys, `gh auth login` setup. Load first if you've never authenticated.
- `github-repo-management/` — Clone, fork, create repos, manage remotes, releases.
- `github-issues/` — Create, triage, label, assign issues via `gh` or REST.
- `github-pr-workflow/` — PR lifecycle: branch, commit, open, CI, merge.
- `github-code-review/` — Review PRs: diffs, inline comments via `gh` or REST.
- `codebase-inspection/` — Inspect a codebase's structure with `pygount`: LOC, languages, ratios.

## Common patterns

- **Auth first** — `github-auth/` is the prerequisite for the others.
- **Issue → PR flow** — `github-issues/` (find/create issue) → `github-pr-workflow/` (branch + PR) → `github-code-review/` (review + merge).
- **Repo setup once** — `github-auth/` + `github-repo-management/` covers new project bootstrap.

## Tooling

All children prefer `gh` CLI when available (auto-detected), fall back to direct REST API calls with curl. Both work in scripts and inside Hermes agent sessions.
