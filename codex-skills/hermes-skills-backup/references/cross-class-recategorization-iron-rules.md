# 跨类修正铁律（0908 立）+ 0 装日必跑 diff（cross-class re-categorization iron rule）

**来源**：2026-09-08 cron 实测，0 装日但实算发现 2 处历史误归 + 1 处漏算。

---

## 症状

cron 0 装日（5 维 trending 全 timeout + 兄弟 0 commit）→ 看似无事，但 `ls ~/.codex/skills/ | grep -E "<LIST>" | wc -l` 实算 ≠ AGENTS.md 报告数。

## 0908 实测

- fs = **111 真 skill**（`ls ~/.codex/skills/ | grep -v "sepia.bak.0903" | wc -l` 实算）
- AGENTS.md 0905 报告 = 110（**漏算 1**）
- 偏差源：
  - `marketing-mindset`（51⭐，axelfreeman）fs 在但分类清单漏列 → **0908 归 MKT**
  - `refactoring-ui`（395⭐，0829 装）历史归 OTHER → **0908 改归 DEV**（UI 改造实属开发类）

## 3 条铁律（0908 立）

### 铁律 1：跨类清单按 skill 实际功能归类（不按历史标签）

- `marketing-mindset` 偏 MKT（B2B 决策框架 = 营销决策类）
- `refactoring-ui` 偏 DEV（UI 改造库 = 工程类）
- `content-strategy-sms` 偏 OTHER（SMS 短链非营销决策）
- `social-media-context-sms` 偏 OTHER（语境配置非营销决策）

### 铁律 2：每日 cron 第一步 = 四类 ls+grep+wc-l 实算 vs AGENTS.md 上版 diff

即使 0 装日也要列 diff —— 不允许"看上去对得上"就 patch。

### 铁律 3：跨类移动 = 重算占比（不是只动 2 类）

移 1 个 skill → 4 类占比都重算。

---

## 验证脚本（0 装日 cron prompt 头部必跑）

```bash
echo "=== fs 实算（铁律 0905 + 0908：ls + grep）==="
DEV=$(ls ~/.codex/skills/ | grep -E "^(autoprompt|cli-creator|codex-hygiene|dispatching-parallel-agents|doc-gen|executing-plans|finishing-a-development-branch|fix-ci|grep-ts|no-negative-echo|playwright|playwright-interactive|receiving-code-review|requesting-code-review|screenshot|script-exec-blocked|search-miss-binary|simplify-codebase|spec-literal-execution|subagent-driven-development|systematic-debugging|test-driven-development|trace-harness-launch-failure|using-git-worktrees|using-superpowers|verification-before-completion|verify-output-readback|writing-plans|writing-skills|refactoring-ui|forward-implementation-first|image-prompt-reverse|sloptrim)$" | sort -u | wc -l)
# 0912 立：MKT 升级为 71 完整集（iron rule 12）；DEV 升 34 / QA 缩 3
MKT=$(ls ~/.codex/skills/ | grep -E "^(ab-testing|ad-creative|ads|ai-seo|analytics|attribution|audience-growth-tracker-sms|caption-writer-sms|carousel-writer-sms|churn-prevention|co-marketing|cold-email|community-marketing|competitor-profiling|competitors|content-boom-monitor|content-calendar-sms|content-pattern-analyzer-sms|content-repurposer-sms|content-strategy|content-strategy-sms|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|hook-writer-sms|image|image-story-video-wizard|influencer-marketing|launch|lead-gen-video-script|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-mindset|marketing-os|marketing-plan|marketing-psychology|offers|onboarding|optimization-advisor-sms|paywalls|performance-analyzer-sms|platform-strategy-sms|popups|post-writer-sms|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|sales-enablement|schema|seo-audit|seo-landing|signup|site-architecture|social|social-media-context-sms|thread-writer-sms|video|xiaohongshu-concept-explainer|xiaohongshu-layout-factory|xiaoma-durex-copywriter|yuxin-content-engine)$" | sort -u | wc -l)
QA=$(ls ~/.codex/skills/ | grep -E "^(chinese-grammar-proofreader|clean-user-facing-text|sloptrim)$" | sort -u | wc -l)
OTHER=$(ls ~/.codex/skills/ | grep -vE "^(autoprompt|brainstorming|cli-creator|codex-hygiene|dispatching-parallel-agents|doc-gen|executing-plans|finishing-a-development-branch|fix-ci|forward-implementation-first|grep-ts|image-prompt-reverse|no-negative-echo|playwright|playwright-interactive|receiving-code-review|refactoring-ui|remove-ai-marks|requesting-code-review|script-exec-blocked|search-miss-binary|screenshot|simplify-codebase|spec-literal-execution|subagent-driven-development|systematic-debugging|test-driven-development|trace-harness-launch-failure|using-git-worktrees|using-superpowers|verification-before-completion|verify-output-readback|writing-plans|writing-skills|ab-testing|ad-creative|ads|ai-seo|analytics|attribution|audience-growth-tracker-sms|caption-writer-sms|carousel-writer-sms|churn-prevention|co-marketing|cold-email|community-marketing|competitor-profiling|competitors|content-boom-monitor|content-calendar-sms|content-pattern-analyzer-sms|content-repurposer-sms|content-strategy|content-strategy-sms|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|hook-writer-sms|image|image-story-video-wizard|influencer-marketing|launch|lead-gen-video-script|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-mindset|marketing-os|marketing-plan|marketing-psychology|offers|onboarding|optimization-advisor-sms|paywalls|performance-analyzer-sms|platform-strategy-sms|popups|post-writer-sms|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|sales-enablement|schema|seo-audit|seo-landing|signup|site-architecture|social|social-media-context-sms|thread-writer-sms|video|xiaohongshu-concept-explainer|xiaohongshu-layout-factory|xiaoma-durex-copywriter|yuxin-content-engine|chinese-grammar-proofreader|clean-user-facing-text|sloptrim|sepia\.bak\.0903)$" | wc -l)
TOTAL=$(ls ~/.codex/skills/ | grep -v "^sepia\.bak\.0903$" | wc -l)
echo "DEV=$DEV MKT=$MKT Q&A=$QA OTHER=$OTHER TOTAL=$TOTAL  (校验: \$((DEV+MKT+QA+OTHER)) = $((DEV+MKT+QA+OTHER)) = $TOTAL ?)"
```

**关键设计**：`OTHER` 用**反向 grep（减集）**而非硬列清单 —— 比硬列清单稳：

- 新增 skill 自动归 OTHER（不在 DEV/MKT/Q&A 列表）
- 跨类修正后自动减 1（`refactoring-ui` 移 DEV 后，OTHER 列表里就**没有它了**，自动正确）
- 兄弟 cron 备份 `sepia.bak.0903` 在 exclude 列表里，不污染真 skill 总数

**完整权威清单（0912 立铁律 12）**：

- DEV = **34 个**（autoprompt / brainstorming / cli-creator / codex-hygiene / dispatching-parallel-agents / doc-gen / executing-plans / finishing-a-development-branch / fix-ci / forward-implementation-first / grep-ts / image-prompt-reverse / no-negative-echo / playwright / playwright-interactive / receiving-code-review / refactoring-ui / remove-ai-marks / requesting-code-review / script-exec-blocked / search-miss-binary / screenshot / simplify-codebase / spec-literal-execution / subagent-driven-development / systematic-debugging / test-driven-development / trace-harness-launch-failure / using-git-worktrees / using-superpowers / verification-before-completion / verify-output-readback / writing-plans / writing-skills）
- MKT = **71 个**（ab-testing / ad-creative / ads / ai-seo / analytics / attribution / audience-growth-tracker-sms / caption-writer-sms / carousel-writer-sms / churn-prevention / co-marketing / cold-email / community-marketing / competitor-profiling / competitors / content-boom-monitor / content-calendar-sms / content-pattern-analyzer-sms / content-repurposer-sms / content-strategy / content-strategy-sms / copy-editing / copywriting / cro / customer-research / directory-submissions / emails / free-tools / hook-writer-sms / image / image-story-video-wizard / influencer-marketing / launch / lead-gen-video-script / lead-magnets / marketing-council / marketing-ideas / marketing-loops / marketing-mindset / marketing-os / marketing-plan / marketing-psychology / offers / onboarding / optimization-advisor-sms / paywalls / performance-analyzer-sms / platform-strategy-sms / popups / post-writer-sms / pricing / product-marketing / programmatic-seo / prospecting / public-relations / referrals / revops / sales-enablement / schema / seo-audit / seo-landing / signup / site-architecture / social / social-media-context-sms / thread-writer-sms / video / xiaohongshu-concept-explainer / xiaohongshu-layout-factory / xiaoma-durex-copywriter / yuxin-content-engine）
- QA = **3 个**（chinese-grammar-proofreader / clean-user-facing-text / sloptrim）
- OTHER = 113 - 34 - 71 - 3 = **5**（douyin-image-post-scheduler + llm-wiki-manager + sepia + sepia.bak.0903 + yuxin-fullstack）

**铁律 12（0912 立）**：MKT grep **必须用 71 完整集**校验，不要沿用 0908-0911 的 47 集口径。**历史 bug**：0911 cron 用 47 集漏算 24 个 skill（9 个 sms 系列 + 2 个 xiaohongshu 前缀 + yuxin-content-engine + 其他 12 个），导致 MKT 47 / OTHER 28 误报；0912 实盘纠正为 MKT 71 / OTHER 5。

**反向 grep 集必须随正向集同步更新**：DEV/MKT/QA 任一加新 skill 时，**OTHER 反向 grep 也必须立刻同步**——0912 偏差就是没同步。

## ⚠️ 「可用反向 grep ≠ 不要正向列清单」陷阱

0910 实测反向 grep 看似"新 skill 自动归 OTHER"，**前提是 DEV/MKT/QA 正向集覆盖完整**。如果漏写 sms 系列 → 那些 skill 全归 OTHER → OTHER 计数虚高 → MKT 计数偏低。**双轨校验**：

1. 正向 grep：算出 DEV/MKT/QA 各自数
2. 反向 grep 校验：OTHER = TOTAL - DEV - MKT - QA
3. 两次结果一致 → 报告可用；不一致 → 立刻 diff 找漏算

## 配合 0905 铁律

- **0905**：「MKT/OTHER 数 = `ls + grep + wc -l` 实算，不按昨日+今日增量推算」
- **0908**：「跨类 = 按 skill 实际功能，不按历史标签」+「0 装日也要跑 diff」+「OTHER 用减集自动归类」

## AGENTS.md patch 模板（0 装日也要 patch，不是只在装日才动）

1. 时间戳（昨日 → 今日）
2. 总览段 N → N+Δ（如 110 → 111 = +1 marketing-mindset 补入）
3. MKT/OTHER/DEV/Q&A 各自 Δ
4. 占比行重算（DEV 30% / MKT 44% / Q&A 4% / OTHER 23%）
5. 「今日变更」段必含 0 装说明 + diff 列表 + 跨类修正逻辑
6. （如版本号修正）Codex CLI 版本号（0908 实测：0.149.1 → 0.153.0）

## 反模式

- ❌ 0 装日不动 AGENTS.md（错过跨类修正机会）
- ❌ AGENTS.md 报告数 = fs 数 = "看上去对" 就放过（漏算会越积越多）
- ❌ 跨类清单硬编码（用反向 grep 减集自动归 OTHER 更可靠）

## 0908 cron 实战 patch 4 处

1. ① 时间戳 `0905 09:30` → `0908 09:30`
2. ② 总览段 110 → **111**（marketing-mindset 0905 补入）+ `refactoring-ui` 从 OTHER 移 DEV
3. ③ MKT 48 → **49**（+marketing-mindset）/ OTHER 26 → **25**（-refactoring-ui）/ DEV 32 → **33**（+refactoring-ui）
4. ④ 占比行 DEV 29% → **30%** / MKT 44% 持平 / OTHER 24% → **23%**
5. ⑤ 加今日变更 0908 完整日报
6. ⑥ Codex CLI 版本号 `0.149.1` → `0.153.0`（沿用 0829 「CLI 升级留给老大」铁律）

## 关联

- 0905 铁律（沿用）：cron 报告 MKT/OTHER 数 = `ls + grep + wc -l` 实算，不按昨日+今日增量推算
- 0829 铁律（沿用）：Codex CLI 升级留给老大手动，cron 不自动跨版本号
- AGENTS.md 文件路径：`~/.codex/AGENTS.md`（自动维护）

## 已知坑

1. **反向 grep 列表太长**：当前 75+ 关键词，未来再加 10+ skill 时清单要更新（**手动维护成本**）。替代方案：每加新 skill 时在 DEV/MKT/Q&A 任一类加一行 grep 模式，但增加维护负担。
2. **兄弟 cron 备份 `sepia.bak.0903`** 必须 exclude，否则 OTHER 计数 +1 误导。
3. **`marketing-mindset` 3 个 SKILL.md 变体**（SKILL.md + SKILL.lite.md + SKILL.deepseek-flash.md）都归 1 个 skill，不影响计数。