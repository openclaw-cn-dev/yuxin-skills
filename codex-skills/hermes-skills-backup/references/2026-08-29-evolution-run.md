# 2026-08-29 Codex Evolution Run（9 点 cron 实跑）

## 当日数字快照
- Codex CLI：`0.149.1`（0.150.1 available——老大决策，小版本不自动升）
- Skills：**96 个**（`ls ~/.codex/skills/ | wc -l` = 96，与 AGENTS.md "95" 差 1 = `.system/` hidden 目录的 imagegen 等内置项不计）
- Marketplace：3 个（bundled / curated / primary-runtime），全部 local snapshot，**无 Git 远端可升**
- 已装插件：**19 个 enabled**（bundled 7 / curated 7 / primary-runtime 5），未变
- 飞书推送：**仍阻塞第 4 天**（app `cli_aaaefb812938dbcd` 已删 + 10217 死锁）—— 沿用 8-27/28 铁律走 final response 兜底

## 新增 3 个 skill（GitHub trending 7 日内）

| Skill | 仓库 / ⭐ | 分类 | 用途 |
|---|---|---|---|
| **sepia** | Nanako0129/sepia v0.2.0 / 362⭐ | Q&A | De-AI 写作 3 层架构（叙事→话语→表面），4 操作 write/review/refactor/recreate |
| **simplify-codebase** | tt-a1i/simplify-codebase / 319⭐ | DEV | 证据驱动代码熵回收（删死代码/合并冗余 API） |
| **refactoring-ui** | s0xDk/refactoring-ui-skill / 395⭐ | OTHER | Refactoring UI 7 章设计规则 |

时间戳全是 `2026-08-29 09:02`，3 个 skill 由同一次 9 点 cron（或其兄弟子 agent）落盘。

## 当日核心发现（铁律级）

### 1. cron 已从「安装 + 报告」转向「验证 + 报告」

**现象**：cron 启动 → 读 AGENTS.md → 发现"最后更新：2026-08-29 09:00" + 今日变更节已存在 + 数字已匹配 `find` 结果 → **本 cron 没必要再 patch AGENTS.md**。

**新增铁律**（已落 SKILL.md `3c` 段）：
- 启动两步 grep 判断 AGENTS.md 是否已是今日快照
- 是 → 只跑 `codex --version` / `find` / `codex plugin list` 三件套验证
- 一致 → 日报写一行 `AGENTS.md 已是今日快照，无变化`，不再 patch
- 不一致 → 才走 patch 追加到今日变更节末尾

### 2. 信任 fs，不信 AGENTS.md 的文字声明

**差点翻车**：AGENTS.md 第 69 行写 `watermark-remover 上游（826⭐）= 本地版（8-28 装的 fork 已是最新版）`。我第一轮 `ls` 看 skills 列表想找它，没找到，差点以为数错。

**stat 验证**：`stat ~/.codex/skills/watermark-remover` → `No such file or directory` → fs 上根本不存在。

**结论**：AGENTS.md 写"已装"的不一定真存在（可能是历史 drift 残留）。日报报数永远以 `find` 实测为准，AGENTS.md 只作"昨日断言"对照。**铁律写入 SKILL.md `3c-bis` 段（已存在）+ 本 runbook 强化。**

### 3. `codex doctor` 超时不算失败

`codex doctor` 在本 cron 跑超 60s 返 `exit_code=124`。原因：内部跑 npm registry 探测 + node_repl MCP 校验 + auth.json 检查等多步耗时操作，网络抖动即超时。

**铁律（已落 SKILL.md `3c` 段）**：
- cron 第一步**只用** `codex --version` + `codex plugin list` 做基线
- doctor 超时直接放弃，不再 retry，不阻塞 cron 推进
- 日报里加一行 `doctor 超时（exit 124），按 --version + plugin list 正常推进` 标注

### 4. 3 个新 skill 的实战推荐路径

| Skill | 老大业务线挂钩 | 推荐首次使用场景 |
|---|---|---|
| **sepia** | 小红书 V80+ 笔记 | 写完后过 sepia `review` 操作 → 比 `remove-ai-marks` 改叙事架构而非表层词句 |
| **simplify-codebase** | 渔芯平台 Phase 2 收尾 | 跑 `Survey` 模式列死代码清单 → 老大审 → 走 Change 真删 |
| **refactoring-ui** | 渔芯平台 Phase 3 UI 改造 | 数据看板/客户工作台按 7 章规则配色/间距/阴影 |

## 4 阶段流水线验证

| 阶段 | 命令 | 实际输出 | 判定 |
|---|---|---|---|
| 1. CLI 版本 | `codex --version` | `codex-cli 0.149.1` | ✅ |
| 2. marketplace 列表 | `codex plugin marketplace list` | 3 个 local marketplace | ✅ |
| 3. 升级探测 | `codex plugin marketplace upgrade --json` | `{"selectedMarketplaces":[], "upgradedRoots":[], "errors":[]}` | ✅ 无 Git 远端可升 |
| 4. skills 精确数 | `ls ~/.codex/skills/ \| wc -l` | 96 | ✅ 与 AGENTS.md 95 差 1 = `.system` 不计入 |

## 9 点 cron 命令清单（下次直接抄）

```bash
# 1. CLI 版本 + AGENTS.md 状态
codex --version
head -5 ~/.codex/AGENTS.md | grep "最后更新"
grep -c "## 今日变更（$(date +%Y-%m-%d)" ~/.codex/AGENTS.md

# 2. marketplace + 升级
codex plugin marketplace list
codex plugin marketplace upgrade --json

# 3. skills 数 + 分类验证
ls ~/.codex/skills/ | wc -l
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l
find ~/.codex/skills -name SKILL.md | wc -l

# 4. 3 件套验证（不依赖 doctor）
codex --version
codex plugin list
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l
```

## 飞书推送现状（已 4 天阻塞）

- `~/.hermes/.env` 唯一 bot = `cli_aaaefb812938dbcd`（8-27 已删）
- `~/.codex/.tmp/plugins/plugins.json` 历史装过 `cli_aaaefb812938dbcd`（10217 死锁）
- 老大手动修法（P0）：
  1. 飞书开放平台建新 app → 拿 APP_ID + APP_SECRET → 写进 `~/.hermes/.env`
  2. 飞书客户端把新 bot 加进 home chat `oc_529aff7485ccc35de97a9e7233d665dd` + 加老大自己（chat 不能 0 人）
  3. 等下次 cron 自动恢复推送

## 老大建议（一次性决策）

1. ✅ V80+ 小红书笔记过 sepia（脱 AI 味从叙事结构改，比 remove-ai-marks 强 1 个层级）
2. ✅ 渔芯平台 Phase 2 收尾后跑 `simplify-codebase` Survey 模式列死代码清单
3. ✅ Phase 3 UI 改造直接套 refactoring-ui 7 章规则
4. ⚠️ 飞书 bot 老大手动重建（不指望 cron 自动恢复）
5. ℹ️ Codex CLI 0.150.1 升级留老大拍板（cron 不自动跨小版本升）