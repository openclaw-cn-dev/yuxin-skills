# 0905 cron 三大新铁律（参考文件）

> 补强主 SKILL.md「Hermes 上游同步判定」「Easel 路径分流」「兄弟 cron phantom 同步识别」三段之外的 3 条新铁律。每日 cron 跑前必读。

## 1. MKT/OTHER 计数铁律（0905 立）

**症状**：0904 cron 报告 "MKT 45（+5）/ OTHER 29（+1）"，fs 实盘 "MKT 48 / OTHER 26" —— **0904 cron 漏算 3 个 MKT**（`cro` / `churn-prevention` / `cold-email`，均 0820 装的），导致分类数与 fs 不一致。

**根因**：cron 报告按 "昨日+今日增量" 推算分类数，没回 fs 实算。

**铁律**：cron 报告 MKT/OTHER 数 = 实算：

```bash
# MKT 实算（替换 <MKT_LIST> 为 AGENTS.md 58 行完整列表 48 个名字）
ls ~/.codex/skills/ | grep -v "^sepia.bak" | grep -E "^($(echo ab-testing ad-creative ads ai-seo analytics attribution co-marketing community-marketing competitor-profiling competitors copy-editing copywriting cro customer-research emails free-tools influencer-marketing launch lead-magnets marketing-council marketing-ideas marketing-loops marketing-os marketing-plan marketing-psychology offers onboarding pricing product-marketing programmatic-seo prospecting public-relations referrals revops sales-enablement schema seo-audit social video cold-email churn-prevention image seo-landing signup site-architecture popups paywalls directory-submissions | tr ' ' '|'))$" | wc -l

# OTHER 实算（同样方法）
ls ~/.codex/skills/ | grep -v "^sepia.bak" | grep -vE "^($(echo <DEV_LIST> | tr ' ' '|')|$(echo <MKT_LIST> | tr ' ' '|')|$(echo <QA_LIST> | tr ' ' '|'))$" | wc -l
```

**禁止**："昨日 40 + 今日 +5 = 45" 这类推算（昨日基线本身可能就漏算）。

## 2. Cron 启动 git 仓铁律补强（0905 立）

**症状**：0904 cron 立 "phantom race reset --soft origin/main" 铁律。0905 实测 `cd ~/.codex && git log origin/main -3` → `fatal: not a git repository` —— **`~/.codex` 不是 git 仓**。

**根因**：0904 立的"cron 启动第一步 `git log origin/main -3`"只对 git 仓有效。`~/.codex/skills/` 是 Hermes 同步层，**不参与 git push 流程**。真正参与 git push 的是 `~/Desktop/yuxin-skills/`（yuxin-skills 私仓）。

**铁律**：cron 启动第一步 = **跑 yuxin-skills**（不是 `~/.codex`）：

```bash
# 正确
cd ~/Desktop/yuxin-skills && git log origin/main -3 --oneline
git rev-parse HEAD
git rev-parse origin/main

# 错误（~/.codex 不是 git 仓）
cd ~/.codex && git log origin/main -3   # → fatal: not a git repository
```

**判断 phantom race 状态**：

- HEAD = origin/main → **0 phantom race 风险**（今日 0905 实测：HEAD = `03a2390` = origin/main = `03a2390`）
- HEAD ahead origin/main N commits → 走 reset --soft origin/main + 重 commit + push
- HEAD behind origin/main → 走 git pull --rebase + 重 commit + push

## 3. Marketingskills upstream 9 commits 0 新 skill 模式（0905 立）

**症状**：0905 cron 跑 `git log origin/main --oneline -15` 看到 9 commits ahead（`b1aaa36..5cd4a7e`）→ 第一反应是"upstream 大更新，需要重装/补装"。实际查 diff：

```bash
cd ~/Desktop/eval-repos/marketingskills
git log origin/main --name-only --pretty=format:"%h %s" | head -50
```

发现 9 commits 全是：
- 5 个 partner onboarding (Ploy/Converly) — `partners.json` + `tools/integrations/<name>.md` + `tools/REGISTRY.md`
- 1 个 docs merge (#569 docs/partner-program-rules)
- 3 个已有 skill (ab-testing/ad-creative/ads) 的 `references/` 扩 + `evals/evals.json` 新增

**0 个新 skill**。partner onboarding 是商业赞助模式，不算 skill 增量。

**铁律**：upstream diff 看到 N commits ahead → **先验"是否真有新 skill"**：

```bash
# 一行验"upstream N commits ahead 是否带新 skill"
cd ~/Desktop/eval-repos/<repo>
git log origin/main --diff-filter=A --name-only --pretty=format: 2>&1 | grep -E "^skills/" | sort -u
```

- 输出非空 → 有新 skill，按"5 维 trending 命中"流程评估
- 输出空 → **partner onboarding / docs / 已有 skill patches**，cron 报告写 "9 commits ahead / 0 new skill"，无需装

**应用范围**：marketingskills 已知稳定（0829 起持续观测），其他 upstream 仓（affaan-m-ECC / K-Dense-AI / sci-agent-skills）首次出现 N commits ahead 时也走这一行验。

## 4. 5 维 trending DDG 限速策略（0905 实战）

**症状**：0905 cron 跑 5 维 trending 搜索（`anthropics/skills` / `marketingskills-updates` / `image-prompt-reverse-stars` / `ZJU-REAL/Easel` / 默认 trending）→ **4/5 timeout 30s**，1 个拿到（Easel/OpenClaw 维度）。

**铁律**（沿用 0904 立 "B/C/D/E 7d 窗口常态空"）：

- DuckDuckGo 30s timeout ≥ 3 次 → **当日 cron 不重试**，直接走 fallback 路径
- Fallback：跑 `git fetch origin main` 拉 3 个核心 upstream diff（marketingskills + social-media-skills + wikiskill）补足"今日能力变化"段
- "5 维 trending 4/5 timeout" 不算 cron 失败，**算"DDG 限速常态"**

## 5. 历史偏差修正归档铁律（0804 + 0905 立）

**症状**：cron 日报每写一次，**昨日基线 = 今日基线** 容易放大误差。0904 报告 MKT 45 → 0905 实算 MKT 48，差 3 个 = 0820 装的 3 个 MKT 一直没在 0902/0903/0904 三轮日报中列。

**铁律**：

- **每日 cron 启动第二步必跑** `ls ~/.codex/skills/ | grep -v "sepia.bak" | sort > /tmp/skills_today.txt` 实算
- 跟昨日 AGENTS.md 报告的"分类数 + 总数"对账：
  - 一致 → 走"昨日+今日增量"推算
  - **不一致 → 必写"历史偏差修正"段**（不擅自改昨日基线，新写一段"0905 校验发现 0904 漏算 3 个 MKT"）
- **禁止**：直接覆盖昨日报告里的分类数（破坏日报可追溯性）
