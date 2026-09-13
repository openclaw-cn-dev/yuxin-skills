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
|------|---------|
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
- Prefer file-scoped test/lint/typecheck commands; include full builds only when no narrower command is available.
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
|------|---------|
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

## Profile-Agent Path-Resolution Asymmetry — write succeeds, `~`-prefixed verify returns empty (2026-08-29)

The basic HOME hijack (§ above) says "use absolute paths for both writes and reads". A subtler variant discovered by 黑豆 heidou profile on 2026-08-29: **hermes internal tools (`write_file`, `skill_view`) resolve `~` to the real home `/Users/hua`, but a `terminal`-spawned shell resolves `~` to the sandbox `~/.hermes/profiles/<name>/home/`.** This means:

- `write_file(path="~/.hermes/profiles/heidou/skills/foo.md", content=...)` **succeeds and lands at `/Users/hua/.hermes/profiles/heidou/skills/foo.md`** (correct location)
- A subsequent `find ~/.hermes/profiles/heidou/ -name "*.md"` from a `terminal` call **returns empty** because the shell parsed `~` to the sandbox home
- The agent then thinks "the write failed" and risks rewriting — potentially polluting the sandbox home this time

Mandatory rules for profile agents (sharper version):

- ✅ `write_file` / `skill_view` / `patch` calls: `~/.hermes/profiles/<name>/...` is safe (hermes tool layer corrects the path)
- ✅ `terminal` verification commands: ALWAYS use absolute paths `/Users/hua/.hermes/profiles/<name>/...`
- ❌ Never `find ~/.hermes/...`, `ls ~/.hermes/...`, `stat ~/.hermes/...` from a terminal call expecting to see profile files
- ❌ Never re-write a file just because a `~`-prefixed terminal verify returned empty — re-verify with an absolute path first
- ❌ Never use `Path.home() / ".hermes/profiles/<name>/..."` or `os.path.expanduser("~")` inside a terminal script meant to verify profile files

This is the **third layer** of the HOME hijack defense (layer 1: §4.1-4.3 "write to wrong location"; layer 2: §4.4 "fabricate data for nonexistent path"; layer 3: §4.5 "verify returns false negative, agent rewrites").

Encode the asymmetry in every profile's `AGENTS.md` "写资料前必做" section as a **two-line rule**:

```markdown
# 写操作用 ~ 安全（hermes 内部校正），terminal 验证用绝对路径
write_file(path="~/.hermes/profiles/<name>/skills/x.md", ...)  # ✅ OK
find ~/.hermes/profiles/<name>/ -name "*.md"                   # ❌ 假阴性
find /Users/hua/.hermes/profiles/<name>/ -name "*.md"          # ✅ OK
```

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

## SOP / 子流程 vs AGENTS.md 漂移检测 — Profile 通用坑 (2026-09-13 黑豆 self-evolve cron 实战)

子流程 / profile-local SKILL.md(尤其是 cron self-evolution SOP)容易在跨版本 AGENTS.md 更新时**携带过期反模式**,直到下一次 cron 跑出矛盾时才被发现。

**黑豆实战命中(2026-09-13 10:00 round)**:`***SECRET***/SKILL.md` §3 反模式第 3 行写着 ❌ 直接写 ~/rkr_staging/ 路径(违反 AGENTS.md 严禁清单第 1 条),但 AGENTS.md v3 已把"直接 write_file 到 rkr_staging 文档库"定为新标准。这条 SOP 反模式与现行政策**正相反**,误导了整整一个 round 的"严禁清单第 1 条"。

**检测方法(self-evolution cron 启动 30 秒内可执行)**:

```bash
# 1. 找到 profile 的所有 SKILL.md(SOP 类)
SKILLS_DIR=/Users/hua/.hermes/profiles/<name>/skills
ls -lt "$SKILLS_DIR"/*/SKILL.md

# 2. 对每个 SKILL.md,grep 出"反模式/严禁/不允许/❌"相关段落
grep -nE "反模式|严禁|不允许|❌|❗" "$SKILLS_DIR"/*/SKILL.md

# 3. 拿每条 ❌ 项对照 AGENTS.md v? 的"严禁清单"和"资料落位速查",判断是否冲突
#    - 冲突 = 必修;老化但未冲突 = 记入下一轮 update 候选
```

**Profile 强制规则**:

- ✅ **每月 / 每次 AGENTS.md 更新后**:profile 的所有 SOP 类 SKILL.md 必须 grep "❌" 与 AGENTS.md 严禁清单做一次对照
- ✅ **AGENTS.md 严禁清单变动**:第一周内必须同步更新受影响的 SOP
- ✅ **SOP 的"严禁清单"必须写明参照 AGENTS.md 的哪个版本**(如 v3 / v6),方便未来 cron 一次 diff 出冲突
- ❌ **不要让 SOP 缓存禁止规则超过 2 个 AGENTS.md 版本**——SOP 是政策的影子,政策的版本就是 SOP 的天花板

**配套**:本节在 `references/***SECRET***.md` §6 展开,含实战命中记录和修复 SOP 模板。

## 合规信号侦察 — 用证件库 mtime 扫描发现政策窗口 (2026-09-13 黑豆 self-evolve cron 实战)

行政/财务/法务/合规 agent 的 self-evolution cron 不应只读 web_search,还应**主动扫描本地证件/资质/合同库**——mtime 变化本身就是合规信号。

**黑豆实战命中(2026-09-13 10:00 round)**:

```bash
# 触发:扫描公司证件库
ls -la /Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/公司证件/
# 输出发现:营业执照_东莞市渔芯科技有限公司_2026-09新版.jpg
#          (2026-09-12 09:50 出现,旧证最后修改 2026-08-13)
# → 信号:主体资质 1 个月内换证,触发"新证 vs 旧证字段比对 + 主体一致性扫描"流程
```

**侦察 SOP(profile agent 通用,每轮 cron 必跑)**:

```bash
# 1. 扫证件库(营业执照/公章/资质证书/ICP/软著/专利)
for DIR in 公司证件 资质证书 备案信息 印章管理; do
  ROOT=/Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/$DIR
  [ -d "$ROOT" ] || continue
  # 找 7 天内的新增/更新文件
  find "$ROOT" -type f -mtime -7 -ls
done

# 2. 扫合同/SOP 库(新增合同、修订模板、关键 SOP 改动)
find /Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/<自己>/ \
     -name "*.md" -o -name "*.docx" -o -name "*.pdf" 2>/dev/null \
  | xargs -I {} stat -f "%Sm %N" {} 2>/dev/null \
  | sort -r | head -20
```

**新发现信号 → 必查项(触发即跑)**:

| 信号类型 | mtime 信号 | 必查动作 |
|---|---|---|
| 营业执照换证 | `公司证件/营业执照_*_新版.jpg/pdf` | 8 字段比对(法人/注册资本/经营范围/地址/期限/信用代码/类型/机关)+ 8 项主体一致性扫描(税务/银行/社保/ICP/软著/专利/商户/企业认证) |
| 合同模板升级 v3.x → v4.x | `workspace/knowledge/合同模板库_*_v*.md` | 旧合同存量盘点 + 过渡期条款适配 |
| 资质过期 | 资质证书 mtime < 当前日 - 11 个月 | 到期预警 + 续期启动 |
| 印章备案变更 | 印章管理目录新增 | 用印流程 SOP 同步更新 |
| 公司法/增值税/数据安全法 重大修订 | web_search 命中 + 公文核验 | 引用既有 class-level skill(如 `***SECRET***` / `compliance-quick-ref` 等),避免重复造轮 |

**Profile 强制规则**:

- ✅ **每轮 self-evolution cron 第 1 步**(`阶段 0` 之后、`阶段 1 政策学习`之前):跑一次证件/资质/合同库的 mtime 扫描
- ✅ **新发现 mtime 信号**:在 evolution 报告中独立列"本轮信号"小节,不并入通用政策研究
- ✅ **重复主题**:发现已有 class-level skill 覆盖(如新公司法 5 年实缴 → `***SECRET***`),直接 `skill_view` 引用,**不要在本 profile 重新写完整版**
- ❌ **不要把本地证件库侦察当 web_search 的替代品**——两者互补,不是二选一

## Tooling Pitfalls in Cron Mode (2026-09-13 黑豆 cron 实战)

Profile cron 模式下,**`execute_code` 工具会被运行时阻断**,报错:

```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks).
Cron jobs run without a user present to approve it. Use normal tools instead, or set
approvals.cron_mode: approve only if this cron profile is intentionally trusted.
```

**强制规则**(任何 cron 调度的 profile):

- ❌ **不要在 cron 自进化 SOP 里推荐 `execute_code`** —— 它对 cron 不可用,SOP 里推荐 = 误导
- ✅ **多步处理/批量循环/JSON 解析**:用多个独立的 `terminal` / `write_file` / `patch` / `read_file` 替代,或写成 shell 脚本用 `terminal` 跑
- ✅ **`terminal` 内的 `python3 -c` / heredoc**:cron 模式下**也可用**(走 shell approval 而非 execute_code approval),但每次仍是独立 terminal 调用
- ✅ **跨工具的状态传递**:用 `write_file` 落临时 JSON/MD 文件,再由下一个工具读

类似地,**`web_extract` 在 DuckDuckGo 后端下不可用**(只搜不抓),若配置了 ddgs 则会失败,profile agent 应默认走 `web_search` 多轮查询 + 摘要交叉,而非期待 `web_extract` 拿到原文。

## Support Files

- `references/***SECRET***.md` — full playbook for the **seven** profile-agent failure modes (HOME hijack / registry scope / stale skill腐化 / cross-profile write guard / cross-profile interface gap / **SOP-vs-AGENTS.md drift** / **compliance signal reconnaissance**), plus cron-mode tool pitfalls.
- `templates/***SECRET***.md` — reusable 8-field contract template for the cross-profile "发起方侧单向接口卡" pattern (type 14). Copy and rename with sender/receiver names when a downstream profile is silent on a known handoff.
- `scripts/skill-health-check.sh <profile-name>` — automated probe; runs the mtime scan, lists stale skills (>90 days), and reminds about L1 vs L3 registry scope.
