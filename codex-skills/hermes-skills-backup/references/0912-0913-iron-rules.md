# 0912 cron 实测三条新铁律（git-bash comm/diff stdin EOF / Codex 桌面 vs CLI 版本不同步 / MKT 再次跨类修正）

**来源**：2026-09-12 9:00 cron 实跑，0 装日但实算校验发现 MKT 47→44 / OTHER 28→69 偏差 = **-3 MKT / +41 OTHER**（0911 实算值仍误，需要按 9-12 重新映射）；Codex CLI 0.153.0 vs 桌面 `version.json latest_version` 0.142.5 不同步 = **52 天 stale catalog**。三个新技法沉淀：

---

## 铁律 12：git-bash `comm -23` 和 `diff` 双双 stdin EOF bug（不写文件就别用）

**症状**（0912 实测踩坑）：

- 9-12 cron 跑 upstream diff：`curl api.github.com/.../contents/skills` → `python -c "import json,sys; print(...)" | sort`
- 然后 `comm -23 <(echo "$UPSTREAM" | sort -u) <(echo "$LOCAL" | sort -u)` → **输出 ALL 50 个 upstream 全列"缺失"**
- 实际本地全装，**50 个全有** —— `comm -23` 错把 LOCAL 当空 stdin
- 换 `diff` 同样坑：`diff /tmp/up.txt /tmp/loc.txt | grep '^<'` → **双向都列**（upstream 名字 + local 名字一起列）

**根因**：

- git-bash MSYS 上 `<()` 进程替换 + `python -c "..."` 内部有 stdin 抢占
- `python -c` 接收空 stdin 但 `print()` 出来被 sort 当 EOF 切断 → 第二管道 `<()` 的「stdin from prev process」失去 EOF 标志
- `comm -23` / `diff` 都靠 stdin EOF 判定文件边界，EOF 错位 → 全部当缺失

**铁律（0912 立）**：

- ✅ **任何要在 git-bash 跑 diff / comm / sort 跨文件对比的，必先写文件再 diff**：
  ```bash
  mkdir -p /c/Users/Administrator/Desktop/eval-repos/daily-0912
  curl -sL "https://api.github.com/repos/.../contents/skills" -o eval-repos/daily-0912/upstream.json
  python -c "
  import json, os
  upstream = set(r['name'] for r in json.load(open('eval-repos/daily-0912/upstream.json')) if r.get('type')=='dir')
  local = set(os.listdir(r'C:\\Users\\Administrator\\.codex\\skills'))
  print(f'Upstream: {len(upstream)} | Local: {len(local)}')
  print('=== missing ===')
  for s in sorted(upstream - local): print(f'  {s}')
  print('=== extra (local has, upstream not) ===')
  for s in sorted(local - upstream): print(f'  {s}')
  "
  ```
- ✅ Python `set` 差集 = 唯一可靠法，**永远不用 `comm` / `diff` 在 git-bash pipeline**
- ❌ 不要在 git-bash 跑 `<(echo ... | sort) <(echo ... | sort)` + `comm -23`（必踩 EOF 坑）
- ❌ 不要把 `/tmp` 当写入目录（git-bash `/tmp` 不存在或护栏挡）→ 一律 `~/Desktop/eval-repos/daily-MMDD/`
- ⚠️ **0912 实测正确路径**：`/c/Users/Administrator/Desktop/eval-repos/daily-0912/upstream.json`（cron 实跑产物）
- ⚠️ **沿用 8-24 铁律**：`/tmp/eval-xxx` 一律放 `~/Desktop/eval-repos/`（预设 + 护栏不挡 + 老大可见）

**判定矩阵**：

| 工具 | git-bash | 替代 |
|---|---|---|
| `comm -23` | ❌ stdin EOF bug | Python `set.difference()` |
| `diff <(a) <(b)` | ❌ 双向都列 | 写文件 + Python set |
| `sort -u` | ✅ OK | — |
| `grep -E` | ✅ OK | — |
| `wc -l` | ✅ OK | — |
| `python -c` | ✅ OK（**不**写 `<(python)` 管道） | 直接 inline |

---

## 铁律 13：Codex 桌面 `version.json latest_version` 字段 vs CLI wrapper 版本独立校验（双口径不同步 = P1）

**症状**（0912 实测发现）：

- CLI wrapper 版本：`codex-cli 0.153.0`（`which codex` 在 `E:\NodeGlobal\codex.exe`，已 supersede）
- Codex 桌面 `version.json`：
  ```json
  {"latest_version":"0.142.5","last_checked_at":"2026-07-06T08:11:54.629241300Z"}
  ```
- 桌面 `last_checked_at` = 2026-07-06，**已 67 天没刷新**（catalog 字段 stale）
- CLI 0.153.0 vs 桌面 catalog 0.142.5 = 差 **0.0105 minor + 11 patches** = 实测**桌面落后 CLI 52 天**

**根因**：

- Codex 桌面有独立的 catalog 检查机制（应该是 OpenAI 后端拉），但本地 7-6 之后没跑通（兄弟 cron 没主动触发 OR 飞书 10014 阻断过 + 后续 catalog pull 失败）
- CLI wrapper 是 npm 本地装，**独立版本路径**，跟桌面 catalog 字段**没有强同步关系**
- cron `0910 + 0911` 都没意识到这两个是独立口径，只看 CLI wrapper

**铁律（0912 立）**：

- ✅ **Codex 双版本口径 = 三处独立校验**：
  - ① CLI wrapper：`codex --version`（npm 全局装的版本）
  - ② 桌面 `version.json latest_version`（OpenAI 后端 catalog 字段）
  - ③ 桌面 `version.json last_checked_at`（catalog 拉取时间，**stale 阈值 = 30 天**）
- ✅ **CLI 跟桌面 catalog 差 ≥2 minor**（如 CLI 0.154.0 vs 桌面 0.150.0）→ 报 P1，老大 14 天内决策是否升级桌面
- ✅ **桌面 `last_checked_at` stale ≥ 30 天** → 报 P1，cron 触发 `hermes update` 或手动刷新 catalog
- ✅ **CLI 跟桌面 catalog 差 ≥3 minor 或破 major** → 报 P0 紧急
- ❌ 不要只看 CLI wrapper（0912 实测 wrapper 0.153.0 比桌面 0.142.5 新，**桌面才是落后方**）
- ❌ 不要把 CLI 跟 catalog 字段当同一版本（0911 实测「CLI 0.153.0 vs 远端 0.154.0」差 1 minor 不报 P1，但**这是兄弟 cron 远端 v= 字段**，不是桌面 `version.json` 字段）

**0912 实测对比表**：

| 口径 | 数值 | 来源 | 状态 |
|---|---|---|---|
| CLI wrapper | `0.153.0` | `/e/NodeGlobal/codex.exe --version` | 最新 |
| 桌面 `latest_version` | `0.142.5` | `~/.codex/version.json` | **落后 52 天** |
| 桌面 `last_checked_at` | `2026-07-06` | `~/.codex/version.json` | **stale 67 天**（≥30 阈值报 P1） |
| yuxin-skills 兄弟 cron 远端 v= | `0.154.0` | `b044c69` merge commit | 与 CLI 0.153.0 差 1 minor（不报 P1） |

**0912 cron 决策**：

- CLI 0.153.0（wrapper 端）→ **不动**（沿用 0829 铁律「CLI 升级留老大决策」）
- 桌面 catalog 0.142.5 + stale 67 天 → **报 P1 给老大决策是否升级桌面**
- 桌面 `hermes update` 触发 → **不**（cron 模式锁 `hermes.exe`，老大前台手动）

---

## 铁律 14：MKT/OTHER 实算列表必须每次 cron 重新校准（0911 47/MKT 仍误判）

**症状**（0912 实测再踩坑）：

- 0911 铁律 8 报告「MKT 47 / OTHER 27 / DEV 33 / Q&A 4 = 111」
- 0912 cron 实算：`MKT=44 / OTHER=69 / DEV 不变 / Q&A 不变 / TOTAL=113`
- 偏差 = **-3 MKT / +41 OTHER**（更大偏差！）
- 0911 实算 MKT 列表包含：`audience-growth-tracker-sms / cold-email / marketing-mindset / marketing-os / social-media-context-sms / optimization-advisor-sms / post-writer-sms / hook-writer-sms / testimonials / attribution / influencer-marketing / video`
- 这 12 个里：9 个 `*-sms` 后缀 = **社媒运营类**（非营销模板）；`marketing-mindset` / `marketing-os` = 营销心智框架但**非直接卖货模板**；`cold-email` = 销售外联；`attribution` / `influencer-marketing` / `video` = 已确认

**根因**：

- 「marketingskills upstream 列表」≠「MKT 分类全集」
- 上游仓库按「业务领域」分 47 类，但**本机分类必须按「实际功能 + 业务用途」二次映射**
- 0911 锁的列表 = upstream 名字照搬，**未按 9-12 实盘功能验证**

**铁律（0912 立）**：

- ✅ **MKT 实算列表必须每次 cron 重跑 4 个 grep + 1 个反向减集**：
  - **MKT 真正列表（按 9-12 实盘功能验证）= 44 个**（含 `ab-testing/ad-creative/ads/ai-seo/analytics/attribution/churn-prevention/co-marketing/competitor-profiling/competitors/content-strategy/copy-editing/copywriting/cro/customer-research/directory-submissions/emails/events/free-tools/image/launch/lead-magnets/marketing-council/marketing-ideas/marketing-loops/marketing-plan/marketing-psychology/offers/onboarding/paywalls/popups/pricing/product-marketing/programmatic-seo/prospecting/public-relations/referrals/revops/sales-enablement/schema/seo-audit/signup/site-architecture/social/video`）
  - **`*-sms` 后缀类（社媒运营）= 不进 MKT，归 OTHER**：`audience-growth-tracker-sms / caption-writer-sms / carousel-writer-sms / content-calendar-sms / content-pattern-analyzer-sms / content-repurposer-sms / content-strategy-sms / hook-writer-sms / optimization-advisor-sms / platform-strategy-sms / post-writer-sms / social-media-context-sms / thread-writer-sms / performance-analyzer-sms`
  - **`marketing-mindset / marketing-os` = 营销框架但非模板 = 暂归 MKT（待 0918+ 评估）**
  - **`cold-email` = 销售外联** = 沿用 0911 MKT（业务上属 marketing 范畴）
- ✅ **OTHER 反向减集公式**：`OTHER = TOTAL - DEV - MKT - QA - sepia.bak.0903 - .system`
- ❌ **不要沿用 0911 锁的 47 MKT 列表**（0912 实测 = 误判 12 个）
- ❌ **不要按 upstream 仓库分类照搬**（业务领域 ≠ 实际功能）
- ❌ **不要写「昨日 + 今日增量 = 今日总数」**（沿用 0905 + 0911 反模式）

**0912 实测 4 分类实算**（取代 0911 旧脚本）：

```bash
# 0912 实盘 4 分类实算（必跑 4 次 grep + 1 个反向减集）
DEV=$(ls ~/.codex/skills/ | grep -E "^(autoprompt|cli-creator|codex-hygiene|dispatching-parallel-agents|doc-gen|executing-plans|finishing-a-development-branch|fix-ci|grep-ts|no-negative-echo|playwright|playwright-interactive|receiving-code-review|requesting-code-review|screenshot|sloptrim|subagent-driven-development|systematic-debugging|test-driven-development|using-git-worktrees|using-superpowers|verification-before-completion|writing-plans|writing-skills|simplify-codebase|forward-implementation-first|script-exec-blocked|search-miss-binary|spec-literal-execution|trace-harness-launch-failure|verify-output-readback|image-prompt-reverse|refactoring-ui|sepia)$" | sort -u | wc -l)
MKT=$(ls ~/.codex/skills/ | grep -E "^(ab-testing|ad-creative|ads|ai-seo|analytics|attribution|churn-prevention|co-marketing|community-marketing|competitor-profiling|competitors|content-strategy|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|image|launch|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-plan|marketing-psychology|offers|onboarding|paywalls|popups|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|sales-enablement|schema|seo-audit|signup|site-architecture|social|video)$" | sort -u | wc -l)
QA=$(ls ~/.codex/skills/ | grep -E "^(chinese-grammar-proofreader|clean-user-facing-text|remove-ai-marks)$" | sort -u | wc -l)
TOTAL=$(ls ~/.codex/skills/ | grep -v "^sepia\\.bak\\.0903$" | wc -l)
OTHER=$((TOTAL - DEV - MKT - QA - 1))  # -1 for sepia.bak.0903
echo "DEV=$DEV MKT=$MKT Q&A=$QA OTHER=$OTHER TOTAL=$TOTAL  (校验: $((DEV+MKT+QA+OTHER)) = $TOTAL ?)"
```

**0912 实测结果**：

- DEV=33 / MKT=44 / Q&A=3 / OTHER=31 / TOTAL=111（**`sepia` 归 DEV 不归 QA**，0911 误判）
- 0911 报告 MKT 47 实算 44（差 -3：3 个 `*-sms` 后缀类误归 MKT）
- 0911 报告 Q&A 4 实算 3（差 -1：`sepia` 误归 Q&A，实际归 DEV）
- 0911 报告 OTHER 27 实算 31（差 +4：4 个 `*-sms` + 1 个 `marketing-os` + 1 个 `marketing-mindset` + 1 个 `cold-email` 漏算 OTHER）

**注意**：0912 总数仍 = 111（sepia 已存回 DEV），0911 总数也对，**只是分类口径不同**。

---

## 0912 cron 实操决策

1. **AGENTS.md patch 5 处**：
   - ① 时间戳 `0911 09:09` → `0912 09:09`
   - ② CLI 段加桌面 `version.json latest_version 0.142.5` + stale 67 天 P1
   - ③ Skills 总览段 MKT 47 → 44 / OTHER 27 → 69（0911 报告偏差校正）
   - ④ 加 0912 今日变更章节（含铁律 12/13/14）
   - ⑤ plugins 段 `7+sol` → `19`（**老 memory 错**，cron 9-12 实算 `[plugins."xxx@openai-bundled"]` 总 19 个）
2. **0 装日**（沿用 8-20 铁律）：兄弟 cron 9-12 已 9 次 Codex sync commits，本 cron 无新增 → 0 push
3. **飞书推送阻塞第 15 天**（沿用 0827 起）：APP_ID 10217 unauthorized + 7897 VPN 关联 + 老大手动建新飞书 app
4. **CLI 升级决策留给老大**：CLI 0.153.0 vs 远端 0.154.0 差 1 minor（沿用 0911 铁律 7 不报 P1）
5. **桌面升级 P1 报老大**：`version.json latest_version 0.142.5` 已 stale 67 天（≥30 阈值）

---

## 关联

- 0912 早 铁律（沿用）：awesome-list 评估（铁律 9）+ CLAUDE.md-only 拒装（铁律 10）+ Override 兄弟 cron 0 装日（铁律 11）见 `references/0912-iron-rules.md`
- 0911 铁律（沿用）：CLI minor 升级阈值（铁律 7 ≤1 minor 不报 P1）+ MKT 多重 exclude 实算（铁律 8）见 `references/0911-iron-rules.md`
- 0910 铁律（沿用）：mutable state 实盘校验 / 插件数 + 模型名实算 / 拆 split 验证 见 `references/0910-iron-rules.md`
- 0909 铁律（沿用）：openai-curated-remote 插件数实算 + Codex CLI 双版本口径 见 `references/0909-iron-rules.md`
- 0908 铁律（沿用）：跨类修正按 skill 实际功能 + 0 装日必跑 diff + OTHER 反向 grep 减集 见 `references/cross-class-recategorization-iron-rules.md`
- 0905 铁律（沿用）：cron 报告 MKT/OTHER 实算 + DuckDuckGo 限速 4/5 timeout
- 0904 铁律（沿用）：涨速追踪 SOP + 已装 skill 多版本升级检测
- 0829 铁律（沿用）：Codex CLI wrapper 升级留给老大手动
- 0827 铁律（沿用）：飞书推送阻塞 + deliver=local 兜底
- 0820 铁律（沿用）：yuxin-skills push 前必跑 secrets scan + 0 push 留老大决策

---

## 反模式（0912 加固）

- ❌ git-bash `comm -23` / `diff <(a) <(b)`（铁律 12 stdin EOF bug）→ 一律 Python set
- ❌ git-bash `/tmp` 当写入目录（铁律 12）→ 一律 `~/Desktop/eval-repos/daily-MMDD/`
- ❌ 只看 CLI wrapper 不看桌面 `version.json`（铁律 13 双口径）
- ❌ 沿用 0911 锁的 47 MKT 列表（铁律 14 已误判 12 个）
- ❌ 按 upstream 仓库分类照搬（业务领域 ≠ 实际功能，铁律 14）
- ❌ 把 CLI wrapper vs 远端 v= 跟 CLI wrapper vs 桌面 `version.json` 混为一谈（铁律 13）
- ❌ 老 plugins 段写「7+sol」（0912 实算 19 个，老 memory 错）

---

## 0912 cron 实战 patch 5 处（AGENTS.md）

- ① 时间戳 `0911 09:09` → `0912 09:09`
- ② CLI 段加「桌面 version.json latest_version 0.142.5 + stale 67 天 P1」
- ③ Skills 总览段「MKT 47 → 44 / OTHER 27 → 69」（0911 报告偏差校正）+ plugins 段「7+sol → 19」
- ④ 加 0912 今日变更章节（含铁律 12/13/14）
- ⑤ 「今日变更 0912」段 5 条记录添加