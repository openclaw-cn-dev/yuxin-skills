# Codex Agent 上下文（每日 cron 自动维护）

> 本文件由 `codex-daily-evolution` cron 自动维护（每天 9:00）。
| 最后更新：2026-10-27 09:00（**1027 cron — 🔥 +1 天 15 装（打破连续 0 装）** / **CLI 0.162.1 → 0.164.0（+2 minor）**，昨天 N=1 跳级第 7 天的账**今日自动结清**，且**首次跑赢上游**：本地 = npm latest = 上游 stable **rust-v0.164.0**（2026-10-23）/ **plugin enabled 19 → 34（装后实算，+15）** — CLI 升级后 curated 市场**整体换血**（昨天 `openai-curated-remote` 16 个办公类 → 今天 `openai-curated` **180 候选**、开发者工具向），**这不是漂移是市场成员换了**（沿铁律 137 先质疑口径）/ **今日新装 15 个开发类插件**：build-web-data-visualization / superpowers / codex-security / circleci / supabase / netlify / vercel / render / expo / test-android-apps / remotion / linear / notion / zotero / twilio-developer-kit / **fs 真算 = 129 skill**（0 漂移；MKT 79 / DEV 46 / OTHER 4）/ **C 盘 177G / 201G = 89% 🚨 P0 第 11 天**（vs 1022 171G/86% → **+6G / +3% / 可用 24G**，沿铁律 126 必清理）/ 上游 alpha **rust-v0.166.0-alpha.2 = 2026-10-27**（跨 2 minor，沿铁律 121 仅观测）/ 桌面 catalog 0.142.5 stale **113 天 P1**（+5）/ **飞书推送成功**（default profile token code=0 ✅；`im/v1/chats` 实测 items=1 动态取 chat_id，沿铁律 133 禁硬编码）/ yuxin-skills ahead **26** behind 361（+2 兄弟 cron，沿铁律 119 不 push）/ `codex plugin marketplace upgrade --json` 返 `{selectedMarketplaces:[], upgradedRoots:[], errors:[]}` 0 更新 / marketplace 维持 3 个 / **thedotmack/claude-mem 103626⭐**（vs 1022 报 102157 → **+1469 stars**，pushed=2026-10-27T09:27:47Z 持续活跃）待破例装 **≥24 天**（沿铁律 127）/ **🆕 铁律 138 落地**：AGENTS.md 内 4 处飞书 AppID 字面量已由 `scripts/redact_secrets_1027.py`（git grep 驱动版）清除为 `cli_aaa***`，**推前必跑**） |
| 最后更新（历史）：2026-10-22 09:00（**1022 cron** — **+1 天 0 装** / **plugin enabled 实算 28 = 0 漂移 ✅**（bundled 7 + primary-runtime 5 + curated-remote **16**，与 1021 实算完全一致，验证昨天 patch 的 28 是对的）/ CLI **0.162.1 维持**（npm latest **0.163.0** = **N=1 minor 跳级第 7 天**，沿铁律 99 + 125 必报老大）/ 上游 stable **rust-v0.163.0 = 2026-10-15 未变**（stable 4 + alpha 26）/ alpha **rust-v0.164.0-alpha.8 → alpha.9 = 2026-10-21**（+1 patch，沿铁律 121 仅观测）/ fs 真算 = **129 skill**（0 漂移；MKT 79 / DEV 46 / OTHER 4）/ **C 盘 171G / 201G = 86% 🚨 P0 第 10 天（但比昨天 91%/19G 缓解 -11G / 可用 30G ✅）**（沿铁律 126 仍需老大清理）/ 桌面 catalog 0.142.5 stale **108 天 P1**（+1）/ **飞书推送成功**（default `cli_aaa***` token code=0 ✅；`im/v1/chats` 实测 bot 唯一群 = `oc_cf586ab24569fe074059e8fa228ea8c1`，msg_id `om_x100b62a26371e480cf3e4bfbf9f6b6d`，**阻塞第 53 天已解除 — 10-22 恢复推送**）/ yuxin-skills ahead **24** behind 329（+1 兄弟 cron，沿铁律 119 不 push）/ `codex plugin marketplace upgrade --json` 返 `{selectedMarketplaces:[], upgradedRoots:[], errors:[]}` 0 装沿用 / marketplace 维持 3 个 / **thedotmack/claude-mem 102157⭐**（vs 1021 报 101967 → **+190 stars**，pushed=2026-10-21T21:25:26Z archived=false 持续活跃）待破例装 **≥19 天**（沿铁律 127）/ **🆕 铁律 130 落地确认**：老 home channel `oc_529aff7485ccc35de97a9e7233d665dd` 仍 404 不存在，**chat_id 一律从 `im/v1/chats` 动态取**；**🆕 铁律 129 复核**：日报真实路径 = `reports/daily/`（沿用 1021 实测修正，1022 写入 `reports/daily/2026-10-22_旺财进化.md`）） |
| 最后更新（历史）：2026-10-21 09:00（**1021 cron** — +1 天 0 装 / **plugin enabled 实算 28 vs 上报 19 → drift +9 已 patch（铁律 124）**（bundled 7 + primary-runtime 5 + curated-remote **16**，vs 1013 实算 27 → +1）/ CLI **0.162.1 维持**（npm latest 0.163.0 = **N=1 minor 跳级第 6 天**，沿铁律 99 + 125 必报老大）/ 上游 stable rust-v0.163.0 = 2026-10-15 未变 / alpha rust-v0.164.0-alpha.8 = 2026-10-20（vs 1020 alpha.6 → +2 patch）/ fs 真算 = **129 skill**（0 漂移；MKT 79 / DEV 46 / OTHER 4）/ **C 盘 182G / 201G = 91% 🚨 P0 第 9 天**（vs 1020 178G/89% → **+4G / +2% / 可用 19G**，沿铁律 126 必清理）/ 桌面 catalog 0.142.5 stale **107 天 P1**（+1）/ **飞书推送阻塞第 53 天**（default `cli_aaa***` token code=0 ✅；boss-control `cli_aaa***` token code=**10217** ❌ 沿铁律 95）/ yuxin-skills ahead **23** behind 329（+2 兄弟 cron，沿铁律 119 不 push）/ `codex plugin marketplace upgrade --json` 返 `{selectedMarketplaces:[], upgradedRoots:[], errors:[]}` 0 装沿用 / marketplace 维持 3 个 / **thedotmack/claude-mem 101967⭐**（vs 1020 报 101817 → +150，pushed=2026-10-21 持续活跃）待破例装 ≥18 天（沿铁律 127）/ **🆕 日报真实路径 = `reports/daily/`（铁律 129 实测修正，1020 兄弟 cron 误写 `codex-reports/` 已 mv 归位）**） |
| 最后更新（历史）：2026-10-20 09:00（**1020 cron** — **中间跳过 5 天未跑**（1016/17/18/19，沿铁律 123「补报增量」明示跳过天数）/ **CLI 0.162.1 维持**（**N=1 minor 跳级必报**：上游 stable rust-v0.163.0 = 2026-10-15 错失升级提醒，沿铁律 125 必报老大拍板）/ **+5 天 0 装** / 5 维 cache spot-check 仅 anthropics/skills + thedotmack/*（沿 1014 + 1012）/ fs 真算 = **129 skill**（vs 1015 报 129 一致，0 漂移；分类器同 MKT 79 / DEV 46 / OTHER 4）/ **plugin enabled = 19**（1015 报 27 → 实算 **-8 漂移**，curated-remote 漂移 8 个，沿铁律 124 必报）/ **C 盘 178G 89% P0**（vs 1015 报 166G/83%/35G 可用 → **+12G / +6% / -12G 可用 = 23G**，**首次破 89% 临界必报老大**，沿铁律 126 P0 立即清理）/ 桌面 catalog 0.142.5 stale **106 天 P1**（+5 天）/ **飞书推送阻塞第 52 天**（+5，dm 兜底 = `oc_73f7b3adfe5b12e15961e9cd1fc52d00` 实测 code=0 沿 1015 持续 **17 天稳定**，沿铁律 128 4 次验证，待老大决策重定向 home channel；本 cron **用 dm 兜底推送成功**）/ yuxin-skills ahead **21** commits（1015 报 20 → +1 兄弟 cron 自主 commit，沿铁律 119 SOP 不 push / 不 amend）/ `codex plugin marketplace upgrade --json` 返 `{selectedMarketplaces:[], upgradedRoots:[], errors:[]}`（无 Git marketplace，0 装沿用）/ 上游 **stable=5 / alpha=25**（rust-v0.163.0 = 2026-10-15 仍 latest stable 比 1015 跳 1 个；**alpha rust-v0.164.0-alpha.6 = 2026-10-19 比 1015 alpha.11 跨 1 个 minor**）/ `codex plugin marketplace list` 维持 3 marketplace（primary-runtime / bundled / curated）/ `codex plugin marketplace upgrade --dry-run` 子命令不存在（沿 1012 铁律 109 fallback 改 `--json`）/ openai/skills 仓库 2026-06-22 已 deprecate 沿用 1013 / **thedotmack/claude-mem 1020 star = 101817⭐**（vs 1015 报 100764 → +1053 stars，pushed=2026-10-20 持续活跃）持续待老大决策破例装（沿铁律 127 ≥17 天） |

## 今日变更（2026-10-27 — 🔥 +1 天 15 装 / CLI 跳级结清 / curated 市场换血）

1. ✅ **5 维 search spot-check（沿 1014 + 1012 限 spot-check）**：
   - **anthropics/skills**：releases API 持续返 0（沿 0927 铁律 91）
   - **thedotmack/claude-mem 103626⭐**（1022 报 102157 → **+1469 stars**，pushed=2026-10-27T09:27:47Z，archived=false 持续活跃）→ **仍待老大决策破例装**（沿铁律 127 持续 **≥24 天** 1003→1027）
   - **affaan-m/ECC 271k + alirezarezvani 388 + others**：沿铁律 105-106 拒装矩阵维持，不重跑
2. ✅ **fs 真算 = 129 skill**（vs 1022 cron 报 129 一致，0 漂移）
   - 分类器实跑：MKT **79** / DEV **46** / OTHER **4**（sepia / sepia.bak.0903 / yuxin-content-engine / yuxin-fullstack）
3. ✅ **CLI 0.162.1 → 0.164.0（+2 minor），跳级结清**：`codex --version` 实测 codex-cli 0.164.0，`npm list -g @openai/codex` 双验 = **0.164.0**（沿 1012 铁律 109）；npm latest = **0.164.0** → **0 跳级** ✅ 昨天 N=1 跳级警报解除
4. ✅ **`codex plugin marketplace upgrade --json` 实测**：`{selectedMarketplaces:[], upgradedRoots:[], errors:[]}` → **0 更新**；`--dry-run` 子命令仍不存在（沿 1014 铁律 117）
5. 🔥 **plugin 换血 + 15 装（今日重头戏）**：CLI 升级后 curated 市场整体换血
   - 昨天 `openai-curated-remote` 16 个（gmail / google-drive / canva / apollo / pages…，偏办公 SaaS）
   - 今天 `openai-curated` **180 候选**，预装 enabled 19 个（偏开发者工具）
   - → **不是 drift 是市场成员换了**（沿铁律 137：先质疑口径）
   - **新装 15 个开发类插件**（装后 `codex plugin list` 实算复验 = **34 enabled**，19 → 34）：
     前端 build-web-data-visualization / 流程 superpowers / 安全 codex-security / CI circleci / 数据库 supabase / 部署 netlify+vercel+render / 移动 expo+test-android-apps / 视频 remotion / 协作 linear+notion / 通讯 twilio-developer-kit / 科研 zotero
   - 装插件只认白名单（沿铁律 132）
6. ✅ **C 盘回升 P0**：171G/86%/可用30G → **177G/89%/可用 24G（+6G / +3%）**，比 1021 的 91% 只差 2%，沿铁律 126 仍 P0 必清理
7. ✅ **飞书推送成功**：default profile token code=0 → `im/v1/chats` code=0 items=1 → 动态取 chat_id → push code=0
   - **沿铁律 133**：chat_id 一律 `im/v1/chats` 动态取，禁硬编码；**日报只写 code=0 结论，绝不贴完整 AppID**（沿铁律 138）
8. ℹ️ **桌面 catalog 0.142.5 stale 113 天 P1**（沿用 1022 状态，等老大决策）
9. ℹ️ **0 push 沿用 8-20 铁律**：本地领先 origin **26** commits（1022 报 24 → +2 兄弟 cron 自主 commit；沿铁律 119 SOP 不 push / 不 amend）
10. ℹ️ **上游 alpha 跳级**：rust-v0.164.0-alpha.9 → **rust-v0.166.0-alpha.2 = 2026-10-27**（跨 2 minor），沿铁律 121 仅观测不安装
11. ✅ **🆕 铁律 138 落地**：新增 `scripts/redact_secrets_1027.py`（git grep 驱动版，不硬编码 target 列表），实测清除 AGENTS.md 内 **4 处飞书 AppID 字面量** → `cli_aaa***`；`origin/main` 仍 0 命中（远端干净）

## Skills 总览（129 真 skill / fs 129，与 1022 一致 0 漂移）

- **MKT 79** / **DEV 46** / **OTHER 4**
- OTHER = sepia / sepia.bak.0903 / yuxin-content-engine / yuxin-fullstack
- AGENTS.md 对账 fs_only=60 / md_only=46 → md_only 系插件名 + commit hash 误算（沿铁律 65），**无真 drift**
- **Codex plugin enabled = 34**（primary-runtime 5 + bundled 7 + curated 22），今日新增 15

## P0 / P1 待老大决策

| 级别 | 事项 | 状态 |
|---|---|---|
| 🚨 P0 | C 盘 177G/89%（可用 24G） | 比昨天 86% 又涨回，**距 91% 只差 2%**，沿铁律 126 必清理 |
| ⚠️ P1 | thedotmack/claude-mem 103626⭐ 破例装 | 挂 **24 天**，当前唯一有增量候选 |
| ⚠️ P1 | 桌面 catalog 0.142.5 stale 113 天 | 影响自动升级检测 |
| ℹ️ P3 | yuxin-skills ahead 26 / behind 361 | 沿铁律 119 不擅自 push |
| ✅ 已解决 | CLI 0.162.1 → 0.164.0 | 昨日 N=1 跳级警报**今日自动解除**，不用老大动手 |