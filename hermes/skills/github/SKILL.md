---
name: github
description: "GitHub workflow — repositories, auth, pull requests (open/review/merge), issues, code review, CI, repo inspection. Load this when the user asks to interact with GitHub via gh CLI or git (HTTPS/SSH), create or review a PR, triage issues, audit a repository, run a code review, or work with the GitHub API. Covers both `gh` CLI usage and git-only HTTPS/SSH authentication paths."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, gh-cli, git, PR, code-review, issues, CI, auth, repo-management]
    related_skills: [hermes-agent]
---

# GitHub Workflow Hub

Comprehensive GitHub workflow knowledge for agents — authentication, repository management, PRs, issues, code review, and codebase inspection. Each subsection below is condensed; the full content lives in `references/<topic>.md`.

## Quick Routing

| Task | Reference |
|------|-----------|
| Set up `gh` CLI login / SSH keys / HTTPS tokens | → `references/github-auth.md` |
| Log into GitHub via browser (device verification flow) | → `references/github-browser-login.md` |
| Discover existing credentials on macOS (no gh CLI) | → `references/macos-credential-discovery.md` |
| Write a GitHub onboarding guide for non-technical colleagues | → `references/github-onboarding-guide.md` |
| Clone, fork, create repos, manage remotes/releases | → `references/github-repo-management.md` |
| Open, review, merge pull requests / rebase / CI runs | → `references/github-pr-workflow.md` |
| Triage, label, assign, create issues via REST API | → `references/github-issues.md` |
| Review PRs (diff, inline comments via gh/REST) | → `references/github-code-review.md` |
| Inspect a codebase (LOC, languages, ratio) | → `references/codebase-inspection.md` |

## Decision Tree — Which Tool Path?

1. **Need to do an action** (create PR, comment, merge, label, file issue) → prefer `gh <subcommand>` (richer, returns structured output). See `references/github-auth.md` if `gh` isn't authenticated yet.
2. **Need to fetch data** (list PRs, view issue body, view commit diff) → `gh <subcommand> --json …` or REST API via curl with `Authorization: Bearer $(gh auth token)`.
3. **`gh` not installed / doesn't work** → fall back to `git` + curl + GitHub REST. See `references/github-repo-management.md` and `references/github-api-cheatsheet.md`.
4. **No terminal access at all** → WebFetch (browser) or post-facto logging.

## Common Patterns

### Detect Authentication
```bash
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```
Full flow + alternatives (SSH key, HTTPS PAT, gh CLI login): `references/github-auth.md`.

### Repo Bootstrap From Scratch
```bash
gh repo create <name> --public --clone --add-readme
gh repo clone owner/repo
gh repo fork owner/repo --clone
```
Full flag matrix + git-only fallback: `references/github-repo-management.md`.

### PR Lifecycle
```bash
gh pr create --base main --title "..." --body-file .github/pr-body.md
gh pr status --json number,title,state,mergeable,checks
gh pr review <num> --approve --body "LGTM"
gh pr merge <num> --squash --delete-branch
```
Full conventions + CI troubleshooting: `references/github-pr-workflow.md`.

### Issues
```bash
gh issue create --title "..." --body-file bug.md --label "bug" --assignee me
gh issue list --label "priority/high" --state open --json number,title,labels
```
Bug/feature templates: `templates/bug-report.md`, `templates/feature-request.md`.

### Code Review
```bash
gh pr diff <num>                    # raw diff
gh api repos/{owner}/{repo}/pulls/{n}/files | jq '.[].filename'   # changed files
gh pr review <num> --request-changes --body-file review.md
```
Full inline-comment + REST patterns: `references/github-code-review.md`.

## Templates (`templates/`)

- `bug-report.md` — issue body for bug reports
- `feature-request.md` — issue body for new features
- `pr-body-bugfix.md` — PR body for bug-fix PRs
- `pr-body-feature.md` — PR body for feature PRs

## Scripts (`scripts/`)

- `github-auth-gh-env.sh` — exports `GH_TOKEN` and `GITHUB_API_URL` from a chosen GitHub host (Enterprise support)

## Reference Files (`references/`)

- `github-auth.md` — HTTPS/SSH/gh-CLI auth, token rotation, multi-account
- `github-browser-login.md` — browser-based login with device verification flow (email code, ref ID pitfalls, fallback to API auth)
- `macos-credential-discovery.md` — discover existing GitHub credentials on macOS (SSH, Chrome, keychain, env vars) before asking the user
- `github-onboarding-guide.md` — write a beginner-friendly GitHub usage guide for colleagues with mixed technical backgrounds
- `github-repo-management.md` — clone/fork/create/release/tag/branch/remote mgmt + git-only fallback
- `github-pr-workflow.md` — PR open/review/merge + `references/ci-troubleshooting.md` + `references/conventional-commits.md`
- `github-issues.md` — issue CRUD + label/assignee/milestone + REST pagination
- `github-code-review.md` — diff review, inline API comments, review events + `references/review-output-template.md`
- `codebase-inspection.md` — LOC / language ratios via pygount
- `github-api-cheatsheet.md` — REST endpoint quick-reference
- `ci-troubleshooting.md` — debug failing GitHub Actions
- `conventional-commits.md` — commit-message spec
- `review-output-template.md` — formatted review-comments template
