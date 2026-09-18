# 2026-08-30 Codex Evolution Run（9 点 cron 实跑）

## 当日数字快照
- Codex CLI：`0.149.1`（0.150.1 available——老大决策，连续 5 天沿用）
- Skills：**96 个**（`ls ~/.codex/skills/ | wc -l` = 96，与昨日 AGENTS.md 写 95 差 1 → 本日补录 `remove-ai-marks` 进 Q&A 分类，95→96）
- Marketplace：3 个（bundled / curated / primary-runtime），全部 local snapshot，**无 Git 远端可升**
- 已装插件：**19 个 enabled**（bundled 7 / curated 7 / primary-runtime 5），未变
- 飞书推送：**仍阻塞第 5 天**（app 10217 unauthorized + 7897 代理 alive）—— 沿用 8-26/27/28/29 铁律走 final response 兜底

## 新增 0 个 skill（cron 校验日）

本日跑了 5 维 trending 搜索（兄弟 9am 子 agent 先落地结论），3 候选全不适配：

| 候选 | ⭐ | 不装理由 |
|---|---|---|
| `XiaoDuoYa/codex-with-chatgpt` | 931⭐ | 要 ChatGPT 网页 OAuth，老大用 DeepSeek/MiniMax 中转无 ChatGPT 账号 |
| `leopard627/fire-your-seo-agency` | 343⭐ | 韩文 skill + SEO·AEO·GEO 路线，老大 SEO 暂未投 + 已有 `seo-audit` 覆盖 |
| `HaichaoLihc/create-photo-flipbook-ui` | 124⭐ | 3D 翻页书给摄影集，水产图文笔记用不到 |

5 维搜索：ai-agents / claude-skill·mcp / xhs·douyin / cad·solidworks / crm·sales → 全部 0 新候选。

## 校验发现：补录 `remove-ai-marks` 到 Q&A

- 校验法：`find ~/.codex/skills -maxdepth 1 | wc -l` = 96 vs AGENTS.md 8-29 写 95
- 定位：`remove-ai-marks` fs 在 `~/.codex/skills/remove-ai-marks/SKILL.md`（mtime 2026-08-28 09:02:03），但 AGENTS.md 仅在 8-28 补录段提到，未列进任何分类清单
- 修复：`Q&A` 分类 3→4，`Skills 总数 95→96`
- 教训：cron 不仅要写新，也要**每日校验 fs vs AGENTS.md 一致性**（本日已落 SKILL.md「9am cron 启动铁律 3c 段」）

## 已装 skill 涨星（今日 7 日 trending 滚动）

| Skill | 昨日 ⭐ | 今日 ⭐ | Δ |
|---|---|---|---|
| `sepia` | 362 | 659 | +297 |
| `refactoring-ui` | 395 | 419 | +24 |
| `simplify-codebase` | 319 | 345 | +26 |
| `remove-ai-marks` | 819 | 819 | 持平 |

4 个全在 7 日 trending 滚动榜稳定，无重装需求。

## 飞书推送：仍阻塞第 5 天

- 错误：`code=230002, msg=bot has been kicked` / `code=10217, msg=unauthorized`
- `.env` 唯一 bot `<FEISHU_APP_ID>` 已删
- 阻塞来源：APP_ID/APP_SECRET env 未注入 + 7897 代理 alive（VPN 未启）
- 修法：老大手动 (1) 飞书开放平台建新 app → (2) 写 .env → (3) 飞书客户端把 bot 加进 home chat + 加老大自己

## Codex CLI 升级：仍 0.150.1 available

- 5 天沿用同一铁律（cron 不自动跨小版本升级）
- `codex doctor` 跑 60s 超时（exit 124）不算失败——慢 IO 阻塞，沿用 8-29 处置

## 决策日志

| 决策 | 依据 |
|---|---|
| 0 装 | 5 维 trending 全 0 候选 |
| 补录 `remove-ai-marks` | fs vs AGENTS.md 不一致，主动校验发现 |
| 跳过 patch 兄弟已写段 | 兄弟 9am 子 agent 先落地，patch 合并成同一节 10 条 |
| 不重装 `sepia/refactoring-ui/simplify-codebase` | 涨星但已是最新 |

## 教训沉淀（已落 SKILL.md）

- **SKILL.md「9am cron 启动铁律 3c 段」**：cron 启动先 grep AGENTS.md「最后更新」+「今日变更」节 → 都命中 → 跳过 patch，只跑三件套验证（`codex --version` + `codex plugin list` + `find ~/.codex/skills | wc -l`）。信 fs，不信 AGENTS.md 文字声明
- **新铁律（今日追加）**：fs vs AGENTS.md 计数对账，每日 cron 末尾跑一次 `wc -l` vs `grep -c "今日新增"`——差值 ≠ 0 立即报告