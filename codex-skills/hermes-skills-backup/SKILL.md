---
name: codex-daily-evolution
description: Codex 每日进化巡检 cron job — 检查 marketplace 新插件、安装开发相关插件、统计 skills 目录、输出日报。**每天 9 点强制执行**（老大铁律 2026-07-31）。触发词：Codex 进化、Codex 巡检、codex daily、codex evolution。
---

# Codex 每日进化巡检

**执行时机**：每天 9 点 cron 强制执行 / 老大说"Codex 进化"/"Codex 巡检"时手动触发

**执行目标（5 项）**：① 检查 Codex 插件和 skills 状态 ② 安装新 plugins/skills ③ 用 `codex exec` 验证 ④ 同步 AGENTS.md ⑤ 备份到 yuxin-skills

**编程铁律（2026-07-31 老大立）**：所有编程必须调 Codex，不自己写。

---

## ⚠️ SKILL.md 拆 split 铁律（0910 立）

**症状**：SKILL.md > 10KB → patch/edit 工具全拒（0910 实测 = 146K 已被拒）。

**铁律**：
- ✅ SKILL.md < 10KB 必跑 `wc -c` 校验（0914 实测 = 11255 bytes > 10KB → 必拆）
- ✅ 主体内容（铁律段/今日变更）→ `references/YYYY-MM-DD-iron-rules.md`
- ✅ SKILL.md 只留：触发条件 + 5 个执行目标 + 编程铁律 + references 指针 + 状态速查

---

## 4 个必读 references 指针

| 指针 | 用途 | 优先级 |
|---|---|---|
| `references/full-skill-archive.md` | 完整原 SKILL.md 内容（145KB = 历次铁律段 + runbook） | P0 |
| `references/capability-audit-and-validation.md` | 启用态双源统计 + codex exec 真实验收 + 上下文预算治理 | P1 |
| `references/0910-iron-rules.md` | 跨日数据漂移铁律：mutable state 必须实盘校验 | P0 |
| `references/0914-iron-rules.md` | **🆕 alirezarezvani 388 mega-repo 选装法 + AGENTS.md drift 监控 + skills context budget 警告** | P0 |
| `references/2026-09-15-evolution-run.md` | **🆕 0915 0 装日：4 候选全拒/暂缓（ECC / ui-ux-pro-max / last30days / scientific-agent-skills）+ 决策树** | P1 |

**完整清单**：`references/0905-0913-iron-rules.md` + `references/2026-08-17-evolution-run.md ... 2026-09-15-evolution-run.md` + `references/codex-plugin-install-cheatsheet.md` + `references/commands-cheatsheet.md` + `references/cron-mode-tool-restrictions.md` + `references/skill-discovery-lanes.md` + `references/plugin-skills-discovery.md` + `references/zero-install-day-sop.md` + `scripts/audit-missing-references.sh`

---

## 当前状态速查（每日 cron 第 1 步必跑）

```bash
# 1. Codex CLI + 桌面 + 兄弟 runtime 三版本
cat ~/.codex/version.json | head -10   # 桌面 catalog + last_checked_at
codex --version                          # CLI wrapper

# 2. fs skills 体检（沿用 0908 铁律）
FS_COUNT=$(ls ~/.codex/skills/ -1 | grep -v "^\.system$" | wc -l)
echo "fs=${FS_COUNT} skills"

# 3. AGENTS.md 对账（0914 铁律 22：兄弟 cron 静默装必查）
MD_COUNT=$(grep -oE '`[a-z][a-z0-9-]+`' ~/.codex/AGENTS.md | sort -u | wc -l)
echo "AGENTS.md去重=${MD_COUNT}"
[ "$FS_COUNT" != "$MD_COUNT" ] && echo "⚠️ DRIFT!"

# 4. 四分类实算（0914 口径：MKT 77 / DEV 37 / QA 2 / OTHER 3 = 119 不重复 = 117 fs）
# ⚠️ autoprompt/brainstorming/image-prompt-reverse 严格归 MKT 主导（0912 铁律 14）
MKT_77="ab-testing ad-creative ads ai-seo analytics attribution audience-growth-tracker-sms autoprompt brainstorming caption-writer-sms carousel-writer-sms chinese-grammar-proofreader churn-prevention clean-user-facing-text cold-email co-marketing community-marketing competitor-profiling competitors content-boom-monitor content-calendar-sms content-pattern-analyzer-sms content-repurposer-sms content-strategy content-strategy-sms copy-editing copywriting cro customer-research directory-submissions douyin-image-post-scheduler emails free-tools hook-writer-sms image image-prompt-reverse image-story-video-wizard influencer-marketing launch lead-gen-video-script lead-magnets marketing-council marketing-ideas marketing-loops marketing-mindset marketing-os marketing-plan marketing-psychology offers onboarding optimization-advisor-sms paywalls performance-analyzer-sms platform-strategy-sms popups post-writer-sms pricing product-marketing programmatic-seo prospecting public-relations referrals revops sales-enablement schema seo-audit seo-landing signup site-architecture social social-media-context-sms thread-writer-sms video xiaohongshu-concept-explainer xiaohongshu-layout-factory xiaoma-durex-copywriter yuxin-content-engine"
DEV_37="cli-creator codex-hygiene dispatching-parallel-agents doc-gen executing-plans fastapi-expert finishing-a-development-branch fix-ci forward-implementation-first grep-ts mcp-server-builder no-negative-echo playwright playwright-interactive rag-architect react-expert receiving-code-review refactoring-ui remove-ai-marks requesting-code-review script-exec-blocked search-miss-binary screenshot simplify-codebase spec-literal-execution subagent-driven-development systematic-debugging test-driven-development trace-harness-launch-failure using-git-worktrees using-superpowers verification-before-completion verify-output-readback writing-plans writing-skills"
QA_2="sepia sloptrim"
OTHER_3="llm-wiki-manager sureforge yuxin-fullstack"

# 5. SKILL.md 自检（拆 split 后必跑）
wc -c ~/AppData/Local/hermes/skills/devops/codex-daily-evolution/SKILL.md
# 期望：< 10KB
```

**判定**：
- ✅ fs - AGENTS.md 对账差值 = 0 → 报告无 drift
- 差值 ≠ 0 → **铁律 22**：Python set 差集找漏算 skill 名（`python -c "import os; print(set(os.listdir('~/.codex/skills')) - {MKT,DEV,QA,OTHER})"`）→ patch AGENTS.md → 重算分类 → 必要时写 references/0914-iron-rules.md
- SKILL.md > 10KB → 拆 split 没成功 → 必加 references/YYYY-MM-DD-iron-rules.md（铁律 0910）

---

## 反模式

- ❌ SKILL.md 持续加段不拆（146K 已是反模式峰值）
- ❌ AGENTS.md 写「7 个 enabled」就不动（漏算 3 个 enabled 插件）
- ❌ 抄昨日报告 + 加今日新增（兄弟 cron 静默装无通知）
-  装 mega-repo 全目录（388 个 skill 撑爆 fs + 装入业务无关 skill）
- ❌ 「伪结果=失败」→ 不为了"装 1 个"硬装不适配 skill

---

## 上游触发条件

每天 9 点 cron 强制执行 / 老大说"Codex 进化"/"Codex 巡检"手动触发。
**老大铁律（2026-07-31 立）**：所有编程与项目开发必须调用 Codex 完成。
