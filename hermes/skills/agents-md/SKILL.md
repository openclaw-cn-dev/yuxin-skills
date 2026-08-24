---
name: agents-md
description: Creates and maintains concise AGENTS.md and CLAUDE.md project instruction files. Use when asked to create AGENTS.md, update AGENTS.md, maintain agent docs, set up CLAUDE.md, document repository agent conventions, or keep coding-agent instructions minimal and reference-backed.
---

# Maintaining AGENTS.md

Goal: concise, actionable agent instructions. Target under 60 lines; never exceed 100.

## Workflow

1. Inspect before writing:
   - package manager: lock files and manifests
   - commands: `package.json`, `Makefile`, task runners, CI workflows
   - docs/specs/policies: `README.md`, `CONTRIBUTING.md`, `docs/`, `specs/`, `policies/`, `SECURITY.md`, `.github/`
   - conventions: current code patterns, test layout, generated files, legacy areas to avoid
2. Choose scope:
   - root `AGENTS.md`: repo-wide defaults
   - nested `AGENTS.md`: only when a subtree has different commands or rules
   - closest instruction file wins; keep narrower files shorter than root files
3. Write the smallest useful file.
4. Verify exact paths and commands exist.

## File Setup

- Create `AGENTS.md` at the repository root.
- If a Claude-compatible entrypoint is required, symlink `CLAUDE.md` to `AGENTS.md`.
- Do not maintain divergent `AGENTS.md` and `CLAUDE.md` copies.

## Default Sections

Use only sections that add non-obvious value.

````markdown
# Agent Instructions

## Package Manager
- Use **pnpm**: `pnpm install`

## Commands
| Task | Command |
|------|---------|
| Test file | `pnpm vitest run path/to/file.test.ts` |
| Lint file | `pnpm eslint path/to/file.ts` |

## External References
| Need | File |
|------|------|
| Setup | `CONTRIBUTING.md` |
| Architecture | `docs/architecture.md` |
| Security policy | `SECURITY.md` |

## Key Conventions
- Generated files: update with `pnpm generate`; do not edit by hand.

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent's name and attribution byline)
```
````

## Writing Rules

- Use headings, bullets, and tables; avoid paragraphs.
- Use repo-relative paths; avoid vague references like "see docs".
- Reference existing docs/specs/policies instead of copying them.
- List exact external files for setup, architecture, API specs, security, release, and policy docs when they exist.
- Prefer file-scoped test/lint/typecheck commands; include full builds only when no narrower command exists.
- Put commands in tables when there is more than one.
- Keep one rule per bullet.
- Keep rationale out unless it prevents a likely mistake.
- Do not restate linter, formatter, or typechecker config.
- Do not list installed skills or plugins.
- Do not include generic quality slogans.

## External Reference Rules

Good:

```markdown
## External References
| Need | File |
|------|------|
| API contract | `docs/api.md` |
| Release process | `docs/releasing.md` |
```

## Anti-Patterns

- welcome text, intros, conclusions, or pleasantries
- long prose explaining why instructions matter
- duplicated content from `README.md`, `CONTRIBUTING.md`, or policy docs
- project-wide commands when file-scoped commands are available
- nested `AGENTS.md` files that repeat root instructions

## Profile-Isolated Agent Pitfall — `$HOME` Hijack (2026-08-23)

When writing or maintaining an `AGENTS.md` for a **profile-isolated agent** (a non-default Hermes profile, e.g. `afu`, `laomo`), verify the actual filesystem path before assuming:

```bash
# CRITICAL: never trust `~` blindly
echo "HOME=$HOME"

# If HOME ends in `.hermes/profiles/<name>/home`, you are in a hijacked mirror.
# Use absolute paths everywhere; `ls ~/.hermes/...` will show a different tree than the real one.
```

Symptoms of hitting this:
- `ls ~/.hermes/profiles/<you>/skills/` returns a tiny list (only `devops`, `software-development`)
- Absolute path `ls /Users/hua/.hermes/profiles/<you>/skills/` returns the full 80+ skill tree
- Concluding "skills directory is empty" → WRONG; you saw the mirror

Mandatory rules for profile agents:
- ✅ All file writes: use `/Users/hua/.hermes/profiles/<name>/...` absolute paths
- ✅ Add a 30-second `echo $HOME` self-check to AGENTS.md "写资料前必做" section
- ❌ Never use `~/` or `Path.home()` in scripts that touch the profile tree
- ❌ Never trust the result of `ls ~/.hermes/...` without absolute-path cross-check

This lesson is profile-wide; encode it in every profile's `AGENTS.md` under a "路径自检" section, not just as one-off memory.

## Profile-Local Skills Don't Auto-Load from Registry (2026-08-24)

The Hermes skill registry loads skills from `~/.hermes/skills/` (L1, global). Skills under `~/.hermes/profiles/<name>/skills/` (L3, profile-local) are **NOT** automatically loaded into the agent context — even if the skill's `SKILL.md` exists and is well-formed.

Symptom: a profile agent's `AGENTS.md` lists `maodou-product` (or similar) as a "core skill", but `skill_view(name='maodou-product')` returns "Skill not found" every cron cycle. The file is there at `~/.hermes/profiles/<name>/skills/<skill>/SKILL.md` (52KB, valid YAML frontmatter), but the registry never picks it up.

This is a known loading-scope limitation, not a skill-file bug. Do NOT keep re-loading hoping it works; do NOT conclude the skill is broken.

Workarounds (in priority order, require profile-write authorization):

1. **Recommended**: `hermes curator add-skill --profile <name> --path ~/.hermes/profiles/<name>/skills/<skill>/ --scope profile` (if supported)
2. **Fallback**: copy `SKILL.md` to `~/.hermes/skills/<skill>/SKILL.md` (cross-profile write — requires华哥/玉芬 authorization per AGENTS.md 铁律)
3. **Last resort**: continue evolution reports with a "⚠️ skill failed to load" warning as known noise; do not let the missing skill block deliverable work

When documenting a profile's `core_skills` in `AGENTS.md`, mark each entry with its actual registry scope (L1/L3) so future sessions know which are reliable:

```markdown
| # | skill | 必读原因 | registry 范围 |
|---|-------|---------|---------------|
| 1 | maodou-workflow | 毛豆工作流骨架 | L1 (已注册) |
| 2 | maodou-product | 产品定位 + 主力职责 | L3 (需 curator 注册, 当前未注册) |
```

## Skill 腐化 (Stale Skill) Detection Probe (2026-08-24)

When a profile agent's bootstrap (AGENTS.md, core_skills list) names a skill as "core/必读", verify it's not silently腐化. A skill is stale if: (a) it hasn't been touched in 90+ days, AND (b) the agent's daily work has accumulated new knowledge that the skill doesn't carry.

Detection commands (run during self-evolution / cron health check):

```bash
# 1. List all profile-local skills sorted by mtime, newest first
ls -lt /Users/hua/.hermes/profiles/<name>/skills/*/SKILL.md 2>/dev/null | head -10

# 2. For a specific candidate, show exact mtime + age
stat -f "%Sm  %N" /Users/hua/.hermes/profiles/<name>/skills/<skill>/SKILL.md

# 3. Rough age in days (for the human-readable report)
echo "scale=0; ($(date +%s) - $(stat -f %m /path/to/SKILL.md)) / 86400" | bc

# 4. Compare against profile's evolution/ output to spot drift
ls -lat /Users/hua/.hermes/profiles/<name>/evolution/*.md | head -5
```

Threshold table:

| Last-update age | Status | Action |
|-----------------|--------|--------|
| 0-30 days | fresh | none |
| 31-90 days | aging | scan for missing topics, queue update |
| 91-180 days | stale | **update required** — flag in cron report, request华哥/玉芬 authorization |
| 180+ days | 腐烂 | hard-block — skill cannot be trusted for "core" claims, downgrade to on-demand |

Example real finding (2026-08-24): `ras-aquaculture` skill last touched 2026-04-26 (120 days), but weekly HW-006/007 reports and 7-species JTBD work have generated substantial new knowledge that's nowhere in the skill. The cron evolution report flagged this; **never silently rewrite** — encode it as a recommendation in the deliverable, then wait for华哥/玉芬 authorization to actually patch the skill.

Pattern: every self-evolution cron cycle should run the 30-day mtime scan once and report any profile skill with `mtime > 90 days`.

## Support Files

- `references/profile-isolated-agent-hygiene.md` — full playbook for the three profile-agent failure modes (HOME hijack / registry scope / stale skill腐化) with worked examples and threshold tables.
- `scripts/skill-health-check.sh <profile-name>` — automated probe; runs the mtime scan, lists stale skills (>90 days), and reminds about L1 vs L3 registry scope. Exit code 1 if any stale skill detected.
