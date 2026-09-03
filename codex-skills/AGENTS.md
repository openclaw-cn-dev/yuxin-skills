# Codex Agent 上下文（每日 cron 自动维护）

> 本文件由 `codex-daily-evolution` cron 自动维护（每天 9:00）。
> 最后更新：2026-08-30 09:01

## Codex 版本

- CLI：`codex-cli 0.149.1`（**未升级**；doctor 报 `0.150.1 available`，**留给老大决策**——cron 不自动跨小版本升级）
- 配置：`~/.codex/config.toml`（含 notify hook + **3 marketplace + 19 个 enabled 插件**，今日未变）

## 模型配置

- Codex 默认模型未在 `config.toml` 显式指定，CLI 调用方（Hermes Agent）走 OpenAI 协议路由。
- 当前会话模型：**MiniMax-M3**（provider: minimax），通过 Hermes Agent 调度。
- `codex exec` 真实跑：model=`gpt-5.6-sol`，provider=`openai`（OpenAI 协议后端），approval=never，sandbox=read-only。

## Marketplace（3 个，+1）

| Marketplace | 源类型 | 根目录 |
|---|---|---|
| `openai-bundled` | local | `~/.codex/.tmp/bundled-marketplaces/openai-bundled` |
| `openai-curated` | local | `~/.codex/.tmp/plugins` |
| **`openai-primary-runtime`** 🆕 | local | `~/.cache/codex-runtimes/codex-primary-runtime/plugins/openai-primary-runtime` |

无 Git marketplace 配置 → `codex plugin marketplace upgrade --json` 返 `{"selectedMarketplaces":[], "upgradedRoots":[], "errors":[]}`。
三个 bundled/primary-runtime 插件目录走 local 路径，跳过 Git 升级。

## 已装插件（19 个，今日 +5）

**openai-bundled（7 个，未变）**：codex-app-tools / sites / browser / chrome / computer-use / latex / visualize

**openai-curated（7 个，未变）**：build-web-apps / build-web-data-visualization / github / cloudflare / coderabbit / sentry / figma / neon-postgres

**openai-primary-runtime（🆕 5 个，0→5，今日全 enabled）**：

| 插件 | 版本 | 分类 | 用途 | 自带 skill 数 |
|---|---|---|---|---|
| **documents** | 26.826.11250 | 办公生产力 | 文档处理（docx 读写） | 1 |
| **pdf** | 26.826.11250 | 办公生产力 | PDF 读写 | 1 |
| **spreadsheets** | 26.826.11250 | 办公生产力 | 表格处理（xlsx 读写） | 2 |
| **presentations** | 26.826.11250 | 办公生产力 | PPT 制作 | 1 |
| **template-creator** | 26.826.11250 | 工具链 | 模板创建器 | 1 |

`openai-primary-runtime` 共带来 **6 个 plugin skill**（documents/pdf/spreadsheets x2/presentations/template-creator 各 1-2）。

`openai-curated` 剩余 173 个未装，按需挑（沿用 8-26 优先级矩阵）。
**🆕 未安装 `plugin-eval@openai-curated`**（自检工具，与"装入业务插件"无关，不装）。

## Skills 总览（95 个，今日 +3）

- **开发类 (DEV) 25 个（今日 +1）**：`autoprompt` / `cli-creator` / `codex-hygiene` / `dispatching-parallel-agents` / `doc-gen` / `executing-plans` / `finishing-a-development-branch` / `fix-ci` / `grep-ts` / `no-negative-echo` / `playwright` / `playwright-interactive` / `receiving-code-review` / `requesting-code-review` / `screenshot` / `sloptrim` / `subagent-driven-development` / `systematic-debugging` / `test-driven-development` / `using-git-worktrees` / `using-superpowers` / `verification-before-completion` / `writing-plans` / `writing-skills` / **`simplify-codebase`** 🆕（319⭐，证据驱动代码熵回收/删除死代码/合并冗余 API）
- **营销类 (MKT) 39 个**（未变）：ab-testing / ad-creative / ads / ai-seo / analytics / attribution / co-marketing / community-marketing / competitor-profiling / competitors / copy-editing / copywriting / cro / customer-research / emails / free-tools / influencer-marketing / launch / lead-magnets / marketing-council / marketing-ideas / marketing-loops / marketing-os / marketing-plan / marketing-psychology / offers / onboarding / pricing / product-marketing / programmatic-seo / prospecting / public-relations / referrals / revops / sales-enablement / schema / seo-audit / social / video / cold-email / churn-prevention / image
- **质量类 (Q&A) 3 个（今日 +1）**：**`chinese-grammar-proofreader`**（中文病句辨析/修改）/ **`clean-user-facing-text`**（用户文本清洗+不可见 Unicode 清除）/ **`sepia`** 🆕（362⭐，De-AI 写作 3 层架构修复：叙事结构→话语流→表面风格，基于 StoryScope arXiv:2604.03136，4 操作 write/review/refactor/recreate）
- **业务/其他 (OTHER) 28 个（今日 +1）**：audience-growth-tracker-sms / brainstorming / caption-writer-sms / carousel-writer-sms / content-boom-monitor / content-calendar-sms / content-pattern-analyzer-sms / content-repurposer-sms / content-strategy / content-strategy-sms / hook-writer-sms / lead-gen-video-script / optimization-advisor-sms / performance-analyzer-sms / platform-strategy-sms / post-writer-sms / social-media-context-sms / thread-writer-sms / xiaohongshu-concept-explainer / xiaoma-durex-copywriter / yuxin-content-engine / yuxin-fullstack / `douyin-image-post-scheduler` / `xiaohongshu-layout-factory` / **`refactoring-ui`** 🆕（395⭐，Refactoring UI 设计规则 — 渔芯平台 Phase 3 UI 改造用）

四分类占比：DEV 26% / MKT 41% / Q&A 3% / OTHER 29%（Q&A 涨 1pp，新增 sepia 写作去 AI 味；DEV/OTHER 各加 1）。

## MCP / 通知

- mcp_servers.node_repl（Hermes 注入）
- notify hook：`codex-computer-use.exe turn-ended` → 自动唤醒后续操作

## 今日变更（2026-08-30）

1. ✅ **0 装**（5 维 trending 搜索全跑，3 候选全不适配）
   - `XiaoDuoYa/codex-with-chatgpt` 931⭐ — **不装**：要 ChatGPT 网页连接 + 内置浏览器 OAuth，老大用 DeepSeek/MiniMax 中转无 ChatGPT 账号
   - `leopard627/fire-your-seo-agency` 343⭐ — **不装**：韩文 skill + SEO·AEO·GEO 路线，老大 SEO 暂未投 + 已有 `seo-audit` 覆盖
   - `HaichaoLihc/create-photo-flipbook-ui` 124⭐ — **不装**：3D 翻页书给摄影集，老大水产图文笔记用不到
2. ℹ️ 已装 skill 涨星：`sepia` 362→659⭐ / `refactoring-ui` 395→419⭐ / `simplify-codebase` 319→345⭐ / `remove-ai-marks` 819⭐ 持平（3 个全在 7 日 trending 滚动榜稳定）
3. ⚠️ Hermes 上游 **v2026.8.27 已发布**（3 天前），当前 v0.19.0 落后 5 个 minor → 沿用老铁律 cron 不自动升级
4. ⚠️ Codex CLI **0.150.1 still available**（连续 5 天沿用），留给老大决策
5. ⚠️ 飞书推送阻塞第 5 天（沿用 8-27 + 8-28 + 8-29 铁律，10217 unauthorized）
6. ℹ️ 5 维搜索完整结论：
   - ai-agents 维度：`simplify-codebase` 涨星已装
   - claude-skill/mcp 维度：`sepia`/`refactoring-ui` 涨星已装
   - xhs/douyin 维度：`douyin-image-post-scheduler` 34⭐ 持平已装
   - **cad/solidworks 维度：0 结果** — GitHub trending 本周 CAD 社区无新工具
   - crm/sales 维度：0 结果
7. ⚠️ 决策变更：本日 cron **不擅自装**任何 skill，全 3 候选均不匹配老大业务线（4 业务线：美食/养殖/设备/公司 + 渔芯平台 + 求职）
8. ℹ️ yuxin-skills 本地 21 commits 未推（沿用 8-20 secret-scanner 铁律 → 老大手动 push）

## 今日变更（2026-08-29）

1. ✅ **新增 3 个本地 skill**（GitHub trending 7 日内）：
   - **`sepia`**（362⭐，Nanako0129/sepia v0.2.0）— De-AI 写作 3 层架构（叙事/话语/表面），互补已有 `remove-ai-marks` + `clean-user-facing-text`。**强烈推荐**老大 V80+ 小红书笔记过 sepia `review` 操作 → 比 remove-ai-marks 更深（修叙事架构而非表层词句）
   - **`simplify-codebase`**（319⭐，tt-a1i/simplify-codebase）— 代码熵回收。渔芯平台 Phase 2 完成后跑一次 `Survey` 模式，**列候选削减清单**（老大审 → 老大批 → 走 Change 模式真删）
   - **`refactoring-ui`**（395⭐，s0xDk/refactoring-ui-skill）— Refactoring UI 7 章设计规则。渔芯平台 Phase 3 UI 改造（数据看板/客户工作台）按这个 skill 配色/间距/阴影 → **SaaS 视觉档次拉升**
2. ℹ️ `watermark-remover` 上游（826⭐）= 本地版（8-28 装的 fork 已是最新版）→ 不重装
3. ℹ️ `codex plugin marketplace list` 被护栏拦（cron 模式）。沿用 8-27 marketplace 状态（3 个 bundled/curated/primary-runtime，19 个 enabled 插件）
4. ⚠️ 飞书推送阻塞第 4 天（沿用 8-27 + 8-28 铁律）
5. ⚠️ Codex CLI 0.150.1 still available（昨日同，沿用）
6. ℹ️ AGENTS.md 已同步：Skills 92→95，分类调整（DEV 24→25 / Q&A 2→3 / OTHER 27→28），MKT 39 不变

## 今日变更（2026-08-28）

1. ✅ **新增 2 个本地 skill**（昨日 cron 漏报补录）：`douyin-image-post-scheduler`（抖音图文批量排期，复用已登录 Chrome 队列化发布）/ `xiaohongshu-layout-factory`（小红书图集排版工厂，IP→专属 xhs skill）→ skill 总数 90→92
2. ⚠️ **两个 skill 时间戳是 8-27 09:02**（昨日 cron 同步时间），确认是昨日同步 superpowers/forcewake 仓库时拉下来的周边 skill，今日补录
3. ⚠️ **飞书推送阻塞第 3 天**（沿用 8-27 铁律：APP_ID/APP_SECRET env 未注入 + 7897 代理 alive，VPN 未启）→ 老大手动建新飞书 app + 关代理客户端
4. ⚠️ **Codex CLI 0.150.1 available**（昨日 0.150.0 → 今日 0.150.1，小版本升级，留给老大决策）
5. ℹ️ **AGENTS.md 已同步**：OTHER 分类 25→27，四分类占比更新

## 今日变更（2026-08-27）

1. ✅ **新增第 3 个 marketplace `openai-primary-runtime`** + 5 个 enabled 插件（documents/pdf/spreadsheets/presentations/template-creator，办公生产力全套）→ enabled 插件 14→19
2. ✅ **新增 2 个本地 skill**：`chinese-grammar-proofreader`（中文病句）+ `clean-user-facing-text`（文本清洗）→ skill 总数 88→90
3. ✅ **AGENTS.md 已同步**：新增 Q&A 分类（24+39+2+25=90 三分类+1 修正），marketplace 表格 2→3，插件表格加 primary-runtime 段
4. ⚠️ **飞书 bot 仍被踢群**（今日 `hermes cron list | grep -c 230002` = 1，沿用 8-25 铁律 → 老大手动加 bot 回 `oc_529aff7485ccc35de97a9e7233d665dd`）
5. ⚠️ **Hermes 升级落后**（沿用 8-25 铁律 v0.19.0 → v0.20.5，老大手动 `hermes update` ZIP fallback）
6. ⚠️ **Codex CLI 0.150.0 available**（小版本升级，留给老大决策）

## 决策逻辑（沿用 8-26 + 8-27 新增）

- **新 marketplace 决策**：`openai-primary-runtime` 自动出现（Codex 0.149.1+ 才有的第三套官方插件），其中 5 个插件**自动 enabled**（无 `codex plugin add` 动作）。判断为"必装"因为是 Codex 默认交付的办公生产力，对应 office 文档读写——Excel/PDF/PPT 是渔芯平台数据看板/报告导出潜在需求
- **新 skill 来源不明**：`chinese-grammar-proofreader` + `clean-user-facing-text` 时间戳是 `8月 26 09:03`（昨日 9 点 cron 时间），**疑似 8-26 cron 装 openai-curated 时**额外拉下来的周边 skill（来自 superpowers / forcewake 仓库）；昨日日报漏报。今日补录 + 备份到 `codex-skills/`
- **批量装 plugin 决策**：`openai-curated` 未装清单 173 个，按需挑，**老大业务线用不到的不装**
