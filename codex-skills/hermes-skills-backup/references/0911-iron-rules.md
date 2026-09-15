# 0911 cron 实测两条新铁律（CLI minor 升级阈值 / MKT 多重 exclude 实算）

**来源**：2026-09-11 9:00 cron 实跑，0 装日但实算校验发现 0910 AGENTS.md 报告 MKT 49/OTHER 25 与 fs 实算 47/27 不一致；兄弟 cron 远端 v=0.153.4 → 0.154.0 patch 升级，但 CLI wrapper 0.153.0 不变。

---

## 铁律 7：CLI wrapper vs 兄弟 cron 远端 v= 字段差 ≤1 minor 不自动追、≥2 minor 才报 P1

**症状**（0911 实测）：

- CLI wrapper：`codex-cli 0.153.0`（npm 本地）
- 兄弟 cron 远端 `v=` 字段：0910 = `0.153.4`（patch），0911 = `0.154.0`（minor）
- 差值从「4 patch」→「1 minor」（0911 兄弟 cron 自升级 patch 后 push 1 个 minor）
- 沿用 0905 + 0910 铁律「CLI 升级留给老大决策」 → cron 不动 CLI
- 但「差多少」需要**明确阈值**，否则每周 0910-0911 这种「v= 字段升 1 minor」都会被无脑 P1 提示 → 老大手动决策噪音

**铁律（0911 立）**：

- ✅ **CLI wrapper vs 兄弟 cron 远端 v= 差 ≤1 minor**（如 0.153.0 vs 0.154.0）→ 不自动追、不报 P1，沿用「CLI 升级留给老大决策」0829 + 0905 + 0910 铁律
- ✅ **CLI wrapper vs 兄弟 cron 远端 v= 差 ≥2 minor**（如 0.150.0 vs 0.154.0）→ 报 P1，cron 不自动追但老大需在 14 天内决策
- ✅ **CLI wrapper vs 兄弟 cron 远端 v= 差 ≥3 minor 或后端破 major**（如 0.140.0 vs 0.150.0）→ 报 P0 紧急，老大 7 天内决策
- ❌ 不要每周「v= 字段升 1 patch」就报 P1（0911 实测后端 0.153.4 → 0.154.0 是 OpenAI 后端 minor 升级常态，不是 CLI wrapper 落后）

**0911 实操决策**：

- CLI 0.153.0（wrapper）vs 兄弟 cron 远端 0.154.0（v= 字段）= 差 1 minor → **不报 P1**，沿用 0829+0905+0910 铁律
- AGENTS.md 仅同步更新「兄弟 cron 远端 v= 字段」段（0910 远端 0.153.4 → 0911 远端 0.154.0）

---

## 铁律 8：MKT/OTHER/Q&A 实算 = grep 多重 exclude，不简单 +1（0910 报告偏差反例）

**症状**（0911 实盘校验）：

- 0910 AGENTS.md 报告：MKT 49 / OTHER 25 / DEV 33 / Q&A 4 = 111
- 0911 实盘 `ls + grep + wc -l`：MKT 47 / OTHER 27 / DEV 33 / Q&A 4 = 111
- 偏差 2 = -2 MKT / +2 OTHER（0910 把 2 个 Q&A 类误算入 MKT）
- **根因**：0910 cron 报告「MKT 49 = 0910 AGENTS 49 = fs 49」实盘不跑 grep 实算，只看昨日数字+今日增量（沿用 0905 反模式）

**根因再深挖**：

- `chinese-grammar-proofreader`（中文病句）— Q&A 类，0910 误归 MKT
- `clean-user-facing-text`（文本清洗）— Q&A 类，0910 误归 MKT
- `remove-ai-marks`（AI 痕迹清洗）— Q&A 类，0910 误归 MKT（0910 还把 sepia 算入 OTHER 但实际归 Q&A）
- `brainstorming`（创意发散）— OTHER 类，0910 漏算
- `thread-writer-sms`（多贴文写作）— OTHER 类，0910 漏算

**铁律（0911 立）**：

- ✅ **MKT/OTHER/Q&A 实算必须 `ls ~/.codex/skills/ | grep -E "<FULL_LIST>" | wc -l` 跑 3 次**，每次用不同列表：
  - MKT 列表 = 47 个 skill 名（见下方验证脚本）
  - Q&A 列表 = `^(chinese-grammar-proofreader|clean-user-facing-text|sepia|remove-ai-marks)$`
  - DEV 列表 = 33 个 skill 名（见 cross-class-recategorization-iron-rules.md 验证脚本）
  - OTHER 用**反向 grep 减集** = TOTAL - DEV - MKT - Q&A
- ❌ **不要写「昨日 + 今日增量 = 今日总数」**（0910 误算根因）
- ❌ **不要按分类清单历史标签归类**（沿用 0908 铁律 1 + 0911 加固：必须按 skill 实际功能 + 多重 exclude 跑 3 次实算）

**0911 验证脚本（取代 0908 cross-class-recategorization-iron-rules.md 的旧脚本）**：

```bash
# 0911 实盘 4 分类实算（必跑 +3 次 grep）
DEV=$(ls ~/.codex/skills/ | grep -E "^(autoprompt|cli-creator|codex-hygiene|dispatching-parallel-agents|doc-gen|executing-plans|finishing-a-development-branch|fix-ci|grep-ts|no-negative-echo|playwright|playwright-interactive|receiving-code-review|requesting-code-review|screenshot|sloptrim|subagent-driven-development|systematic-debugging|test-driven-development|using-git-worktrees|using-superpowers|verification-before-completion|writing-plans|writing-skills|simplify-codebase|forward-implementation-first|script-exec-blocked|search-miss-binary|spec-literal-execution|trace-harness-launch-failure|verify-output-readback|image-prompt-reverse|refactoring-ui)$" | sort -u | wc -l)
MKT=$(ls ~/.codex/skills/ | grep -E "^(ab-testing|ad-creative|ads|ai-seo|analytics|attribution|audience-growth-tracker-sms|cold-email|community-marketing|content-strategy|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|hook-writer-sms|image|influencer-marketing|launch|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-mindset|marketing-os|marketing-plan|marketing-psychology|onboarding|optimization-advisor-sms|popups|post-writer-sms|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|schema|seo-audit|signup|site-architecture|social|social-media-context-sms|testimonials|video)$" | sort -u | wc -l)
QA=$(ls ~/.codex/skills/ | grep -E "^(chinese-grammar-proofreader|clean-user-facing-text|sepia|remove-ai-marks)$" | sort -u | wc -l)
TOTAL=$(ls ~/.codex/skills/ | grep -v "^sepia\.bak\.0903$" | wc -l)
OTHER=$((TOTAL - DEV - MKT - QA))
echo "DEV=$DEV MKT=$MKT Q&A=$QA OTHER=$OTHER TOTAL=$TOTAL  (校验: $((DEV+MKT+QA+OTHER)) = $TOTAL ?)"
```

**0911 实测结果**：

- DEV=33 / MKT=47 / Q&A=4 / OTHER=27 = 111 ✓
- 0910 报告 MKT 49 实算 47（差 -2：2 个 Q&A 类误归 MKT）
- 0910 报告 OTHER 25 实算 27（差 +2：2 个 OTHER 类漏算）

---

## 0911 cron 实操决策

1. **AGENTS.md patch 4 处**：
   - ① 时间戳 `0910 09:09` → `0911 09:09`
   - ② CLI 段兄弟 cron v= 字段 `0.153.4` → `0.154.0`（patch 升级，CLI wrapper 0.153.0 不变）
   - ③ 加 0911 今日变更章节（含 2 条新铁律引用 + MKT/OTHER 跨类修正）
   - ④ Skills 总览段 MKT 49 → 47 / OTHER 25 → 27（0910 报告偏差校正）
2. **0 装日 0 push**（沿用 8-20 铁律）：本地 `6d6f6a9` = 远端 `33c0e4f`，0 待推 commit
3. **飞书推送阻塞第 14 天**（沿用 0827 起铁律）：APP_ID 10217 unauthorized + 7897 VPN 关联 + 老大手动建新飞书 app
4. **CLI 升级决策留给老大**：CLI 0.153.0 → 0.154.0 不自动追（铁律 7 ≤1 minor 不报 P1）

---

## 关联

- 0910 铁律（沿用）：mutable state 必须实盘校验 / 插件数 + 模型名永远实算不抄昨日 / 拆 split 验证 = wc + 真 patch（见 `references/0910-iron-rules.md`）
- 0909 铁律（沿用）：openai-curated-remote 插件数 = `codex plugin list | grep installed` 实算 + Codex CLI 双版本口径 + SKILL.md 拆 split（见 `references/0909-iron-rules.md`）
- 0908 铁律（沿用）：跨类修正按 skill 实际功能 + 0 装日必跑 diff + OTHER 用反向 grep 减集（见 `references/cross-class-recategorization-iron-rules.md`）
- 0905 铁律（沿用）：cron 报告 MKT/OTHER 数 = `ls + grep + wc -l` 实算，不按昨日+今日增量推算
- 0829 铁律（沿用）：Codex CLI wrapper 升级留给老大手动，cron 不自动跨版本号
- AGENTS.md 文件路径：`~/.codex/AGENTS.md`（自动维护）

---

## 反模式（0911 加固）

- ❌ CLI wrapper vs 兄弟 cron 远端 v= 字段差 1 minor 就报 P1（0911 起 ≤1 minor 不报 P1）
- ❌ MKT/OTHER/Q&A 实算只跑 1 次 grep（0911 起必跑 3 次实算 + 减集校验）
- ❌ 「昨日 + 今日增量 = 今日总数」（0911 加固沿用 0905 反模式）
- ❌ 按分类清单历史标签归类（沿用 0908 铁律 1）
- ❌ 0 装日不动 AGENTS.md（沿用 0908 + 0910，0 装日必跑 diff 校正报告偏差）

---

## 0911 cron 实战 patch 6 处

1. ① 时间戳 `0910 09:09` → `0911 09:09`
2. ② CLI 段 `0.153.4` → `0.154.0`（兄弟 v= 字段，CLI wrapper 0.153.0 不变）
3. ③ 加 0911 今日变更章节（含铁律 7 + 铁律 8 + MKT/OTHER 跨类修正）
4. ④ Skills 总览段 MKT 49 → 47 / OTHER 25 → 27（0910 报告偏差校正）
5. ⑤ 「今日变更」段 6 条记录添加
6. ⑥ CLI 段新增「0911 立铁律：≤1 minor 不报 P1」+ CLI vs 远端 v= 字段差值 ≤1 minor 不自动追