---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review). Includes subagent tool-set pitfalls (send_message, web_search, terminal commonly stripped) and 30-second probe recipe."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context:

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec:

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes:

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. Final Review

After ALL tasks are complete, dispatch a final integration reviewer:

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues
- **Redispatch a timed-out subagent before autopsying the disk** — check output files first;
  the work may already be 90% landed (see "If Subagent Reports Timeout")
- **Dispatch web-heavy research subagents in parallel during a provider rate-limit recovery
  window** — local-material synthesis survives where web multi-source research dies

## Handling Issues
## Subagent Tool-Set Pitfalls

**Subagents do not always inherit the orchestrator's full tool set.** This is the most common silent failure when designing cross-task prompts.

### What's commonly stripped vs kept

| Usually available in subagent | Often STRIPPED in subagent | Why it matters |
|---|---|---|
| `read_file`, `write_file`, `patch`, `search_files` | `send_message` (cross-platform messaging) | Subagent can't deliver its own report to Feishu/Telegram/Slack. |
| `skill_view`, `skills_list`, `todo` | `web_search`, `web_extract` | Research prompts silently degrade to "I don't have web." |
| `skill_manage` (read-only paths) | `terminal`, `execute_code`, `process` | Code-execution tasks can't actually run code. |
| `cronjob` (read) | `kanban_*`, `delegate_task` (recursive) | Subagent can't fan out further; intentional. |
| Memory tool depends on profile | `write_file` outside allowed roots | Path-policy sandboxes write locations. |

**Rule of thumb:** The subagent's available tool list is whatever is in the prompt's "Available tools" block at dispatch time, minus anything the parent explicitly removed. Don't ask the subagent to do something its tool block doesn't list — it will either fail silently or fabricate a plausible answer.

### Pitfall: "send the report to Feishu" tasks

A subagent prompt that says "produce the report and send it to Feishu via `send_message`" is a broken pattern when the subagent doesn't have `send_message`. Two real-world failures:

1. **Silent fabrication** — subagent invents a fake `send_message` "success" output (looks correct, never delivered).
2. *****SECRET***** — subagent writes the file and pretends delivery happened.

**Rule:** If the task ends with "report back to X" or "deliver to Y," do the delivery yourself in the orchestrator session. Subagents do the work; orchestrator does the talking.

### Pitfall: Web/research tasks that look like they can fetch URLs

Subagents without `web_search`/`web_extract` cannot fetch arXiv, HF Spaces, or any external API. They may either hallucinate sources or, worse, return `[SILENT]` because they have no way to investigate.

**Fix in the orchestrator prompt:** either (a) give the subagent `toolsets=['terminal', 'web']` explicitly, or (b) pre-fetch the research yourself and paste the source material into `context=`.

### Pitfall: Cron job subagents are especially restricted

Cron subagents often run with the **minimum tool set** (`read_file`, `write_file`, `skill_view`, `skill_manage`, `search_files`) and **no web/terminal/messaging**. The "Your final response will be automatically delivered to the user" boilerplate is the system promising delivery — not the subagent's responsibility. Don't include "send_message" in cron subagent prompts at all.

### Worked example — AI-CAD research cron failure (2026-08-26)

> **Pattern that broke:** Cron prompt said "summarize today's research and send to 玉芬 (default feishu user) via `send_message`."
>
> **What happened:** Subagent had only `file` + `skill` tools. It could not call `send_message`. It wrote the report to the correct path and reported honestly that `send_message` was unavailable, then suggested the orchestrator do the delivery.
>
> **Lesson encoded above:** Treat subagents as write-only workers; delivery belongs to the orchestrator or the cron boilerplate.

## Handling Issues
## Subagent Tool-Set Pitfalls

**Subagents do not always inherit the orchestrator's full tool set.** This is the most common silent failure when designing cross-task prompts.

### What's commonly stripped vs kept

| Usually available in subagent | Often STRIPPED in subagent | Why it matters |
|---|---|---|
| `read_file`, `write_file`, `patch`, `search_files` | `send_message` (cross-platform messaging) | Subagent can't deliver its own report to Feishu/Telegram/Slack. |
| `skill_view`, `skills_list`, `todo` | `web_search`, `web_extract` | Research prompts silently degrade to "I don't have web." |
| `skill_manage` (read-only paths) | `terminal`, `execute_code`, `process` | Code-execution tasks can't actually run code. |
| `cronjob` (read) | `kanban_*`, `delegate_task` (recursive) | Subagent can't fan out further; intentional. |
| Memory tool depends on profile | `write_file` outside allowed roots | Path-policy sandboxes write locations. |

**Rule of thumb:** The subagent's available tool list is whatever is in the prompt's "Available tools" block at dispatch time, minus anything the parent explicitly removed. Don't ask the subagent to do something its tool block doesn't list — it will either fail silently or fabricate a plausible answer.

### Pitfall: "send the report to Feishu" tasks

A subagent prompt that says "produce the report and send it to Feishu via `send_message`" is a broken pattern when the subagent doesn't have `send_message`. Two real-world failures:

1. **Silent fabrication** — subagent invents a fake `send_message` "success" output (looks correct, never delivered).
2. *****SECRET***** — subagent writes the file and pretends delivery happened.

**How to handle in the orchestrator prompt:**

> ✅ **Correct pattern** — separate the work from the delivery:
>
> ```python
> delegate_task(
>     goal="Write the report file to <path>",
>     context="Write the report to <path>. Do NOT try to deliver or send the report yourself — the orchestrator session will handle delivery.",
>     toolsets=['file', 'skill']   # explicitly omit 'messaging'
> )
> ```
>
> ❌ **Broken pattern** — combine work + delivery in one subagent:
>
> ```python
> delegate_task(
>     goal="Write the report and send it to Feishu",
>     context="...",
>     toolsets=['file', 'messaging']  # 'messaging' won't be available
> )
> ```

**Rule:** If the task ends with "report back to X" or "deliver to Y," do the delivery yourself in the orchestrator session. Subagents do the work; orchestrator does the talking.

### Pitfall: Web/research tasks that look like they can fetch URLs

Subagents without `web_search`/`web_extract` cannot fetch arXiv, HF Spaces, or any external API. They may either hallucinate sources or, worse, return `[SILENT]` because they have no way to investigate.

**Fix in the orchestrator prompt:** either (a) give the subagent `toolsets=['terminal', 'web']` explicitly, or (b) pre-fetch the research yourself and paste the source material into `context=`.

### Pitfall: Cron job subagents are especially restricted

Cron subagents often run with the **minimum tool set** (`read_file`, `write_file`, `skill_view`, `skill_manage`, `search_files`) and **no web/terminal/messaging**. The "Your final response will be automatically delivered to the user" boilerplate is the system promising delivery — not the subagent's responsibility. Don't include "send_message" in cron subagent prompts at all.

### How to verify before dispatching

1. Look at the toolset you pass in `toolsets=...`. Each name must match a real Hermes toolset (e.g. `'messaging'`, `'web'`, `'terminal'`, `'file'`, `'skill'`).
2. If unsure whether a tool is included, dispatch a one-line test prompt: `"List every tool available to you and respond with the list."` and inspect.
3. When in doubt, separate work from side-effects: subagent does file work, orchestrator does messaging/web/cron.

### Worked example — the AI-CAD research cron failure (2026-08-26)

> **Pattern that broke:** Cron prompt said "summarize today's research and send to 玉芬 (default feishu user) via `send_message`."
>
> **What happened:** Subagent had only `file` + `skill` tools. It could not call `send_message`. It wrote the report to the correct path and reported honestly that `send_message` was unavailable, then suggested the orchestrator do the delivery.
>
> **Lesson encoded above:** Treat subagents as write-only workers; delivery belongs to the orchestrator or the cron boilerplate.

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.
- **`references/subagent-toolset-probe.md`** — 30-second probe to inventory a subagent's actual tools before dispatching real work. Read this whenever you're about to dispatch a subagent for a task that depends on `send_message`, `web_search`, `terminal`, or other tools that are commonly stripped from cron-style subagent contexts.

- **`references/subagent-toolset-probe.md`** — 30-second probe to inventory a subagent's actual tools before dispatching real work. Read this whenever you're about to dispatch a subagent for a task that depends on `send_message`, `web_search`, `terminal`, or other tools that are commonly stripped from cron-style subagent contexts.

`context-budget-discipline.md` and `gates-taxonomy.md` adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
- **Assume the subagent has your full tool set** — see [Subagent Tool-Set Pitfalls](#subagent-tool-set-pitfalls) below

## Subagent Tool-Set Pitfalls

**Subagents do not always inherit the orchestrator's full tool set.** This is the most common silent failure when designing cross-task prompts.

### What's commonly stripped vs kept

| Usually available in subagent | Often STRIPPED in subagent | Why it matters |
|---|---|---|
| `read_file`, `write_file`, `patch`, `search_files` | `send_message` (cross-platform messaging) | Subagent can't deliver its own report to Feishu/Telegram/Slack. |
| `skill_view`, `skills_list`, `todo` | `web_search`, `web_extract` | Research prompts silently degrade to "I don't have web." |
| `skill_manage` (read-only paths) | `terminal`, `execute_code`, `process` | Code-execution tasks can't actually run code. |
| `cronjob` (read) | `kanban_*`, `delegate_task` (recursive) | Subagent can't fan out further; intentional. |
| Memory tool depends on profile | `write_file` outside allowed roots | Path-policy sandboxes write locations. |

**Rule of thumb:** The subagent's available tool list is whatever is in the prompt's "Available tools" block at dispatch time, minus anything the parent explicitly removed. Don't ask the subagent to do something its tool block doesn't list — it will either fail silently or fabricate a plausible answer.

### Pitfall: "send the report to Feishu" tasks

A subagent prompt that says "produce the report and send it to Feishu via `send_message`" is a broken pattern when the subagent doesn't have `send_message`. Two real-world failures:

1. **Silent fabrication** — subagent invents a fake `send_message` "success" output (looks correct, never delivered).
2. *****SECRET***** — subagent writes the file and pretends delivery happened.

**How to handle in the orchestrator prompt:**

> ✅ **Correct pattern** — separate the work from the delivery:
>
> ```python
> delegate_task(
>     goal="Write the report file to <path>",
>     context="Write the report to <path>. Do NOT try to deliver or send the report yourself — the orchestrator session will handle delivery.",
>     toolsets=['file', 'skill']   # explicitly omit 'messaging'
> )
> ```
>
> ❌ **Broken pattern** — combine work + delivery in one subagent:
>
> ```python
> delegate_task(
>     goal="Write the report and send it to Feishu",
>     context="...",
>     toolsets=['file', 'messaging']  # 'messaging' won't be available
> )
> ```

**Rule:** If the task ends with "report back to X" or "deliver to Y," do the delivery yourself in the orchestrator session. Subagents do the work; orchestrator does the talking.

### Pitfall: Web/research tasks that look like they can fetch URLs

Subagents without `web_search`/`web_extract` cannot fetch arXiv, HF Spaces, or any external API. They may either hallucinate sources or, worse, return `[SILENT]` because they have no way to investigate.

**Fix in the orchestrator prompt:** either (a) give the subagent `toolsets=['terminal', 'web']` explicitly, or (b) pre-fetch the research yourself and paste the source material into `context=`.

### Pitfall: Cron job subagents are especially restricted

Cron subagents often run with the **minimum tool set** (`read_file`, `write_file`, `skill_view`, `skill_manage`, `search_files`) and **no web/terminal/messaging**. The "Your final response will be automatically delivered to the user" boilerplate is the system promising delivery — not the subagent's responsibility. Don't include "send_message" in cron subagent prompts at all.

### How to verify before dispatching

1. Look at the toolset you pass in `toolsets=...`. Each name must match a real Hermes toolset (e.g. `'messaging'`, `'web'`, `'terminal'`, `'file'`, `'skill'`).
2. If unsure whether a tool is included, dispatch a one-line test prompt: `"List every tool available to you and respond with the list."` and inspect.
3. When in doubt, separate work from side-effects: subagent does file work, orchestrator does messaging/web/cron.

### Worked example — the AI-CAD research cron failure (2026-08-26)

> **Pattern that broke:** Cron prompt said "summarize today's research and send to 玉芬 (default feishu user) via `send_message`."
>
> **What happened:** Subagent had only `file` + `skill` tools. It could not call `send_message`. It wrote the report to the correct path and reported honestly that `send_message` was unavailable, then suggested the orchestrator do the delivery.
>
> **Lesson encoded above:** Treat subagents as write-only workers; delivery belongs to the orchestrator or the cron boilerplate.
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues
- **Assume the subagent has your full tool set** — see [Subagent Tool-Set Pitfalls](#subagent-tool-set-pitfalls) below

## Subagent Tool-Set Pitfalls

**Subagents do not always inherit the orchestrator's full tool set.** This is the most common silent failure when designing cross-task prompts.

### What's commonly stripped vs kept

| Usually available in subagent | Often STRIPPED in subagent | Why it matters |
|---|---|---|
| `read_file`, `write_file`, `patch`, `search_files` | `send_message` (cross-platform messaging) | Subagent can't deliver its own report to Feishu/Telegram/Slack. |
| `skill_view`, `skills_list`, `todo` | `web_search`, `web_extract` | Research prompts silently degrade to "I don't have web." |
| `skill_manage` (read-only paths) | `terminal`, `execute_code`, `process` | Code-execution tasks can't actually run code. |
| `cronjob` (read) | `kanban_*`, `delegate_task` (recursive) | Subagent can't fan out further; intentional. |
| Memory tool depends on profile | `write_file` outside allowed roots | Path-policy sandboxes write locations. |

**Rule of thumb:** The subagent's available tool list is whatever is in the prompt's "Available tools" block at dispatch time, minus anything the parent explicitly removed. Don't ask the subagent to do something its tool block doesn't list — it will either fail silently or fabricate a plausible answer.

### Pitfall: "send the report to Feishu" tasks

A subagent prompt that says "produce the report and send it to Feishu via `send_message`" is a broken pattern when the subagent doesn't have `send_message`. Two real-world failures:

1. **Silent fabrication** — subagent invents a fake `send_message` "success" output (looks correct, never delivered).
2. *****SECRET***** — subagent writes the file and pretends delivery happened.

**Rule:** If the task ends with "report back to X" or "deliver to Y," do the delivery yourself in the orchestrator session. Subagents do the work; orchestrator does the talking.

### Pitfall: Web/research tasks that look like they can fetch URLs

Subagents without `web_search`/`web_extract` cannot fetch arXiv, HF Spaces, or any external API. They may either hallucinate sources or, worse, return `[SILENT]` because they have no way to investigate.

**Fix in the orchestrator prompt:** either (a) give the subagent `toolsets=['terminal', 'web']` explicitly, or (b) pre-fetch the research yourself and paste the source material into `context=`.

### Pitfall: Cron job subagents are especially restricted

Cron subagents often run with the **minimum tool set** (`read_file`, `write_file`, `skill_view`, `skill_manage`, `search_files`) and **no web/terminal/messaging**. The "Your final response will be automatically delivered to the user" boilerplate is the system promising delivery — not the subagent's responsibility. Don't include "send_message" in cron subagent prompts at all.

### Worked example — AI-CAD research cron failure (2026-08-26)

> **Pattern that broke:** Cron prompt said "summarize today's research and send to 玉芬 (default feishu user) via `send_message`."
>
> **What happened:** Subagent had only `file` + `skill` tools. It could not call `send_message`. It wrote the report to the correct path and reported honestly that `send_message` was unavailable, then suggested the orchestrator do the delivery.
>
> **Lesson encoded above:** Treat subagents as write-only workers; delivery belongs to the orchestrator or the cron boilerplate.

## Fan-out research batches (parallel tasks mode) — verification and resource gates

`delegate_task(tasks=[...])` runs up to 3 tasks in parallel. Verified pattern for 华哥's "开分身调研 N 个项目" requests (2026-09-10):

1. **Gate on system resources first** — check `memory_pressure -Q` free % and swap, confirm no training jobs, BEFORE dispatching. On the M4/16GB box, 3 parallel web-research subagents are light (peak RAM impact ~30%), but the gate is mandatory per 华哥's standing rule: 跑前评估水位，跑中可挂看门狗. Report the before-number to the user in the dispatch message.
2. **Pick targets by evidence, not assumption** — rank candidate projects by thinness of materials (`find <dir> -name "*.md" | wc -l`) so the batch fills the biggest gaps.
3. **Cross-check every subagent's file claims yourself** — subagent summaries are self-reports. A batch reported "9 files written" but the first `find` verification came back empty. Re-check with a **glob-based listing** (`ls -l <glob>` / `ls <dir>/<subdir>/*pattern*.md`) — on macOS, `find` under **Chinese paths** (`~/6-产品研发/...`) can silently return nothing while `ls` with the same glob returns all files. The empty `find` is a listing-tool quirk, NOT proof of failure; never report "files missing" based on one `find`.
4. **Re-check memory after the batch completes** and include the after-number in the report (e.g. before 84% free → after 50% free), so 华哥 sees the resource cost of the fan-out.
5. **Timeout ≠ failure — verify, then redispatch surgically (2026-09-10)**: research subagents that do 15+ searches routinely blow the 600s hard timeout (`exit_reason: timeout`, summary=null). The partial work is usually already on disk. Protocol: ① `ls -l` the target dir for the expected files → ② redispatch ONLY the missing artifacts, with explicit "不要动已有 X 份，只补第 N 份" in the prompt → ③ cap the redispatch ("限用 N 次工具调用"), name the cause ("搜索轮次太多导致超时"), and order "每完成一份立刻写盘，不要最后一起写" so a second timeout still leaves partial results. One redispatch with a budget cap fixed in 1 round what a full re-run would have re-spent 3×.

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)

### If Subagent Reports Timeout — Autopsy Before Redispatch (2026-10-05 empirical)

A `600s timeout` does NOT mean zero output. Subagents write files to disk as they work; the
timeout only kills the *summarizing* turn. Before any redispatch:

1. `stat` / `ls -la` the target output paths — check size and mtime.
2. `grep '^## '` the artifact to check section completeness + read the tail for a clean ending.
3. Check companion updates (README index lines, ledger rows) — often the body landed but the
   registration line didn't; fix that by hand in one line.

**Decision rule**: small residue (missing index line, missing final section) → patch by hand in
the controller session; large residue (no file or stub only) → redispatch. Redispatching a
90%-complete artifact wastes a full subagent round and risks conflicting duplicate output.

**Dispatch-load calibration** (same session, same provider-recovery window): 3 subagents doing
web multi-source cross-research (web_search heavy) → all 3 timed out with zero-to-partial
output; 3 subagents doing local-material-only synthesis (toolsets terminal/file/search, no web)
→ 2 completed, 1 timed out *after* writing the full artifact. Rule of thumb: before dispatching,
ask "is all source material already on disk?" — if yes, explicitly forbid web retrieval in the
task context and mark external data as「待深调」; if web research is unavoidable, keep each task
to ≤5 sources or run serially instead of parallel.

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

- **`references/subagent-toolset-probe.md`** — 30-second probe to inventory a subagent's actual tools before dispatching real work. Read this whenever you're about to dispatch a subagent for a task that depends on `send_message`, `web_search`, `terminal`, or other tools that are commonly stripped from cron-style subagent contexts.

`context-budget-discipline.md` and `gates-taxonomy.md` adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).

## Plan-writing companion — writing-plans (absorbed here 2026-10-01)

Before dispatching subagents, plans are written in the bite-sized-task format preserved at `references/writing-plans.md` (the complete SKILL.md of the former `writing-plans` skill): exact absolute file paths, complete code inline in the plan, bite-sized tasks with exactly one step in progress, plan reviewed before execution. This skill is the execution half of that pair — the plans you dispatch should come from the writing-plans format.
