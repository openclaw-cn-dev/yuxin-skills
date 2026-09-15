# 0912 铁律（**MKT/DEV/QA/OTHER 跨类实算纠正 + 新铁律 12**）

**沿用 0912 实盘**：0911 报告分类（DEV 33 / MKT 47 / QA 4 / OTHER 28）vs 0912 实算（DEV 34 / MKT 71 / QA 3 / OTHER 5）偏差巨大——0911 cron 跑 grep 时漏算 sms/xiaohongshu/yuxin-* 系列 24 个 skill + 误把 `xiaoma-durex-copywriter` 算到 QA。

---

## 铁律 12（0912 立）：MKT/DEV/QA/OTHER 实算 grep 必须用 91 MKT 完整集（71 个），不再用 0911 47 个口径

**触发条件**：每次 cron 第 1 步必跑 4 分类 grep 实算（沿用 0908 跨类修正铁律）。

**完整集（0912 实算口径）**：

```
# DEV (34 个)
autoprompt|brainstorming|cli-creator|codex-hygiene|dispatching-parallel-agents|doc-gen|executing-plans|finishing-a-development-branch|fix-ci|forward-implementation-first|grep-ts|image-prompt-reverse|no-negative-echo|playwright|playwright-interactive|receiving-code-review|refactoring-ui|remove-ai-marks|requesting-code-review|script-exec-blocked|search-miss-binary|screenshot|simplify-codebase|spec-literal-execution|subagent-driven-development|systematic-debugging|test-driven-development|trace-harness-launch-failure|using-git-worktrees|using-superpowers|verification-before-completion|verify-output-readback|writing-plans|writing-skills

# MKT (71 个)
ab-testing|ad-creative|ads|ai-seo|analytics|attribution|audience-growth-tracker-sms|caption-writer-sms|carousel-writer-sms|churn-prevention|co-marketing|cold-email|community-marketing|competitor-profiling|competitors|content-boom-monitor|content-calendar-sms|content-pattern-analyzer-sms|content-repurposer-sms|content-strategy|content-strategy-sms|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|hook-writer-sms|image|image-story-video-wizard|influencer-marketing|launch|lead-gen-video-script|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-mindset|marketing-os|marketing-plan|marketing-psychology|offers|onboarding|optimization-advisor-sms|paywalls|performance-analyzer-sms|platform-strategy-sms|popups|post-writer-sms|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|sales-enablement|schema|seo-audit|seo-landing|signup|site-architecture|social|social-media-context-sms|thread-writer-sms|video|xiaohongshu-concept-explainer|xiaohongshu-layout-factory|xiaoma-durex-copywriter|yuxin-content-engine

# QA (3 个)
chinese-grammar-proofreader|clean-user-facing-text|sloptrim

# OTHER = 113 - 34 - 71 - 3 = 5
# douyin-image-post-scheduler + llm-wiki-manager + sepia + sepia.bak.0903 + yuxin-fullstack
```

**关键决策**：
- ❌ 不再使用 0911 报告的 47 MKT / 4 QA / 28 OTHER 口径
- ✅ 0912 起的所有 cron 报告必须用 71/3/5 口径
- ✅ MKT grep 用 sms-prefix 系列（audience-growth-tracker-sms / content-calendar-sms / content-strategy-sms 等）+ yuxin-prefix（yuxin-content-engine）+ xiaohongshu/xiaoma 前缀
- ✅ xiaoma-durex-copywriter 在 MKT（不是 QA），因为它解决小红书"得像人说"问题

---

## 0912 实盘重大发现

### 偏差矩阵（0911 报 vs 0912 实算）

| 类别 | 0911 报告 | 0912 实算 | 偏差 | 原因 |
|------|----------|----------|------|------|
| DEV | 33 | **34** | +1 | 0911 漏算哪个？09-11 cron 安装后未刷新 grep |
| MKT | 47 | **71** | **+24** | 0911 cron 漏算 sms/xiaohongshu/yuxin 系列 |
| QA | 4 | **3** | -1 | xiaoma-durex-copywriter 重分类到 MKT |
| OTHER | 28 | **5** | **-23** | 大量 OTHER 实际归 MKT/DEV |
| **总和** | **112** | **113** | +1 | 0911 漏算某个 skill 整体数 |

**根因**：0911 cron 跑 MKT grep 时（沿用 0905 + 0910 跨类修正铁律），**没有把 0909-0911 新装的 skill 全加入 grep 集**（比如 0909 装的 sms 系列，0910 装的 yuxin-content-engine，0911 装的 llm-wiki-manager 不在 MKT 集但 OTHER 集漏算）。

### 0912 5 维搜索结果

**5 维搜索（沿用 0911 awesome-list 30s 评估法 + Override 兄弟 cron 0 装日铁律）**：
1. **Dim1 GitHub** (stars>50 pushed>2026-08-01, 1077 repo)：top 10 全是 Claude Code 强依赖（affaan-m/ECC 256k⭐ / Graphify-Labs/graphify 117k⭐ / JuliusBrussee/caveman 105k⭐），**0 命中 4 业务线**
2. **Dim2 新 skill** (created>2026-07-01, 239526 repo)：
   - **Hisn00w/ASu-skills** 4338⭐「求职与开发场景 AI Skills」— 0911 已装 job-application-packaging 互补 → **不重装**
   - **KKKKhazix/human-writing** 3592⭐「让中文像人说话」— 4 群小红书爆款命中，但 0912 拒装——**已写过 `humanizer` skill（不在 fs 但与已有 `sloptrim` 重叠）**
3. **Dim3 awesome-list** (ComposioHQ/awesome-claude-skills 74879⭐ push=2026-08-10)：全是 Composio MCP 商业工具，4 业务线 0 命中
4. **Dim4 anthropics/skills 官方 19 子目录**：doc-coauthoring / skill-creator / frontend-design → **0 装**（与 0911 已装 writing-skills + hermes-agent-skill-authoring 重叠；doc-coauthoring 与 0911 llm-wiki-manager 重叠）
5. **Dim5 4 业务命中**（seafood/aquaculture/shrimp）：search 29633 repo，top 全是 ECC/graphify/claude code skill → **0 命中**

### Anthropics/skills 19 子目录评估（4 业务命中）

| 子目录 | 4 业务命中 | 决策 |
|--------|-----------|------|
| doc-coauthoring | 4 群知识库 | ❌ 与 0911 llm-wiki-manager 重叠 |
| skill-creator | 4 群写 skill | ❌ 与 writing-skills + hermes-agent-skill-authoring 重叠 |
| frontend-design | 0 | — |
| webapp-testing | 0 | — |
| docx / pdf / pptx / xlsx | 0 | 已有 codex-app-tools / pdf plugin |
| 其他 12 个 | 0 | — |

### Graphify 重新评估（0911 P1 → 0912 P0 重审）

- 0911 决策「不装」保留
- 0912 重审原因：117k⭐（0911 报 116k），升 P0
- 0912 重审结论：**仍不装**
  - 强依赖 Claude Code 命令 `/graphify`（不是 Codex）
  - 功能 100% 覆盖在 0911 装的 `llm-wiki-manager` 内
  - 沿用 0911 「CLAUDE.md-only 拒装模式」：graphify 主体是 SKILL.md = 单 skill 但强依赖 Claude Code → 跳过

---

## 0912 cron 实盘数据

```
fs skills: 113 = 34 DEV + 71 MKT + 3 QA + 5 OTHER ✓
plugins: 22 = 7 bundled + 5 primary-runtime + 10 curated-remote ✓
CLI: 0.153.0 (0911 维持)
runtime: 0.154.0 (兄弟 cron 0912 sync 4 commits 维持)
model: gpt-5.6-terra (provider=openai, reasoning=low)
SKILL.md: 7,557 bytes (0910 拆 split 后维持 < 10KB)
audit-missing-references.sh: 2 false-positive (ad-creative + attribution，已知)
AGENTS.md: patch 2 处 (1 处时间戳 + 1 处 0912 今日变更段)
```

---

## 沿用 0911 铁律（不变）

- 铁律 9（awesome-list 30s 评估法）
- 铁律 10（CLAUDE.md-only 拒装模式）
- 铁律 11（Override 兄弟 cron 0 装日：本 cron 必跑独立 5 维搜索 + 三段漏斗）

## 新增铁律 12（0912 立）

**MKT/DEV/QA/OTHER 实算 grep 必须用 91 MKT 完整集（71 个），不再用 0911 47 个口径**。

**为什么立这条铁律**：
- 0911 cron 跑 MKT grep 漏算 24 个 skill（最大单次偏差）
- 偏差导致 4 群 RAG 检索时被误判类，影响 4 群业务命中
- 不立铁律，下次 cron 还会重蹈覆辙

**如何执行**：
- 每次 cron 第 1 步必须用「完整集 grep」算 DEV/MKT/QA/OTHER
- 总账校验：DEV + MKT + QA + OTHER = fs_count
- 偏差 > 0 时立刻按 `comm -23` 找漏算 skill 名
- AGENTS.md 必须在「Skills 总览」段注明「实算口径」vs「历史报告口径」

---

## 兄弟 cron 0912 状态

- **0912 sync 4 commits** (33c0e4f → e322081)：全部 metadata only（STATUS.md + plugins.json），0 新 skill 0 新 plugin
- **0911 已升 0.154.0**：CLI wrapper 0.153.0 不自动追（0911 铁律：CLI minor 差 ≤1 不自动追）
- **yuxin-* 13 文件 + 1 目录 = 14**：company-specific，0912 未变

## 0912 总结

- ✅ 0 装日（5 维搜索 0 命中 4 业务线）
- ✅ 跨类偏差纠正（MKT 47→71 / OTHER 28→5）
- ✅ 新铁律 12 落地（71 MKT 完整集口径）
- ✅ Codex CLI 实测正常（runtime 0.154.0）
- ✅ SKILL.md < 10KB 维持（7,557 bytes）
- ✅ AGENTS.md patch 2 处（时间戳 + 今日变更段）
- ⚠️ 飞书推送阻塞第 15 天（沿用 0827 起铁律）
- ⚠️ 0 push 沿用 8-20 铁律（本地领先 4 commits，等老大 push）
