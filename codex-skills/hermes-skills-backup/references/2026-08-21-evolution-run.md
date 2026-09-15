# 2026-08-21 Codex 进化巡检 Runbook

## 当日摘要

| 维度 | 结果 |
|---|---|
| Codex CLI | v0.147.0（npm available 0.149.0，**未升级**，待老大拍板） |
| Marketplace | 2 个，均为 local snapshot，**不支持 Git 升级** |
| 已装插件 | 12 个（与 8-20 持平，**0 升级**） |
| 未装插件 | 21 个（高价值候选：sentry/remotion/render/coderabbit） |
| 本地 skills | **83**（实测 `find ~/.codex/skills -name SKILL.md \| wc -l`，含 6 个 .system） |
| doctor | 16 ok / 1 idle / 2 notes / 1 warn（MCP）/ 0 fail |
| 今日新增 | 0 插件 / 0 skill（无 marketplace 自动同步机制） |
| AGENTS.md | 已 patch 增量段（35 行） |

## 关键实测命令

### 1. Marketplace 状态
```bash
codex plugin marketplace list
# 输出 2 行：openai-bundled / openai-api-curated

codex plugin marketplace upgrade --json
# {"selectedMarketplaces":[],"upgradedRoots":[],"errors":[]}
# 全部 local snapshot → no-op
```

### 2. 插件清单
```bash
codex plugin list | grep -c "installed, enabled"
# 12
```

### 3. 本地 skills 真实数（**修正后权威算法**）
```bash
# 用户可见本地 skill（不含 .system）
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l
# 77（83 - 6 system）

# 全部（含 .system 内置）
find ~/.codex/skills -name SKILL.md | wc -l
# 83
```

### 4. Codex CLI 升级信号
```bash
codex doctor | head -5
# ↑ updates      0.149.0 available (current 0.147.0)
```

## 本次新发现（已入 SKILL.md）

### A. 插件 SKILL.md 实际复制到本地目录（superpowers 实测）
- 现象：`superpowers@openai-api-curated` 启用后，14 个纯 SKILL.md 类子 skill **复制**到 `~/.codex/skills/<name>/`，不仅在 plugin cache
- 影响：本地 skill 统计**双计**风险——既是 plugin cache 里的 SKILL.md，又是 `~/.codex/skills/` 下的目录
- 修正：日报 / AGENTS.md 写本地数时用真实 `find` 命令，注明"含 superpowers 等 plugin 本地化复制"

### B. `codex plugin marketplace upgrade -- --dry-run` 语法陷阱
- 现象：`upgrade --dry-run` 报 `unexpected argument`；`upgrade -- --dry-run` 报 `marketplace '--dry-run' is not configured as a Git marketplace`
- 结论：v0.147.0 `upgrade` 子命令**无 `--dry-run`** 参数
- 替代：直接 `upgrade --json`（已 8-17 实测可用）

### C. Codex CLI 升级信号解读
- `codex doctor` 顶部 `↑ updates` 段是 npm registry 的 `@openai/codex` 包版本，**不是** marketplace 插件版本
- 日报需拆开报：CLI 版本 / marketplace 插件版本

## AGENTS.md 增量规则（沿用 8-11 + 8-21）

数字与昨日**完全一致 → 不动 AGENTS.md**。今日数字变化：
- 本地 skill 76 → 83（**+7**，superpowers 本地化首次实测确认）
- 分类占比变化（开发类 9 → 18，营销类 53 → 55，浏览器类 0 → 3，其他类 0 → 7）

→ 触发"分类占比变动 ≥5pp"和"skill 总数变化"双例外 → **必须 patch AGENTS.md**

## 老大决策待办

| 优先级 | 待办 | 触发命令 |
|---|---|---|
| 🟢 高 | 是否装 `sentry` / `remotion` / `render` / `coderabbit` | 老大说"装" / "干" → 批量 `codex plugin add <name>@openai-api-curated` |
| 🟡 中 | 是否升级 Codex CLI 到 0.149.0 | 老大说"升" → `npm install -g @openai/codex`（先看 doctor MCP 警告） |
| ⚪ 低 | 修复 MCP env 警告 | 老大说"修" → 看 `~/.codex/config.toml` `[mcp_servers]` 段缺什么 env |

## 踩坑 / Pitfall

1. **`codex plugin marketplace upgrade -- --dry-run` 无效** → 改用 `upgrade --json`（已记 SKILL.md）
2. **本地 skill 数虚高/漏数风险** → 必跑 `find ~/.codex/skills -name SKILL.md | wc -l`，不用 `ls | wc -l`（漏 `.system`）/ 不用 `ls -A`（含隐藏目录）
3. **superpowers 14 skill 双计** → 日报必须注明"含 superpowers plugin 本地化复制的 N 个 skill"

## 下次 cron 任务清单

1. 跑 `codex plugin marketplace upgrade --json` → 看 `selectedMarketplaces` 是否变
2. 跑 `codex --version` → 看 CLI 是否升级
3. 跑 `find ~/.codex/skills -name SKILL.md | wc -l` → 看本地数
4. 跑 `codex plugin list | grep -c "installed, enabled"` → 看插件数
5. 数字 vs 今日对比 → 触发 AGENTS.md patch 决策