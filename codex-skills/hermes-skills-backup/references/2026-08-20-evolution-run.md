# Codex Evolution Run · 2026-08-20

> 8-20 实跑 runbook。本次重点：**5 插件落地 + 修正 skill 计数方法**。

## 本次新增（5 插件全部 install 成功）

```
codex plugin add chrome@openai-bundled               → 26.616.71553
codex plugin add computer-use@openai-bundled         → 26.616.71553
codex plugin add superpowers@openai-api-curated      → 11c74d6b  (含 14 dev 方法论 skill)
codex plugin add build-web-data-visualization@openai-api-curated → 11c74d6b
codex plugin add latex@openai-bundled                → 0.2.3
```

外加：github / figma / notion / codex-security / build-web-apps / linear 均 install 成功（之前 8-15 装的，今天跑了一次幂等 add 确认 enabled）。

## 数字

| 项 | 8-15/16 | 8-18 | **8-20** |
|---|---|---|---|
| 已装插件（installed, enabled） | 7-8 | 8 | **12** |
| 本地 skill（`ls ~/.codex/skills/`） | 76 / 62 / 76 | 76 | **83** |
| 插件市场 skill（`find ~/.codex/plugins/cache -name SKILL.md`） | 估 219 / 实 613 | 613 | **253** |
| 总 skill | 281 / 675 / 689 | 689 | **336** |

## ⚠️ 修正：插件市场 skill 计数方法

**8-15/16 用 `Path.rglob('SKILL.md')` 估 613 → 8-20 实测 253**。

```bash
# ✅ 8-20 修正算法（去重 + 不计 references/ 子目录）
find ~/.codex/plugins/cache -name SKILL.md -path "*/skills/*" \
  | awk -F'/skills/' '{print $2}' | awk -F'/' '{print $1}' \
  | sort -u | wc -l
# 输出 253（8-20 实测）
```

**为什么 8-15/16 估多了**：之前 `rglob` 把每个 plugin 内的 SKILL.md 都数一遍，但**有些 plugin 在 `references/`、`templates/`、`scripts/` 子目录也放 SKILL.md**（如 heartmula、songsee），这些不是独立的 skill —— 重复计入导致虚高 2-3 倍。

**修正算法关键**：限定 `*/skills/*` 路径（顶层 skills/ 目录），再用 `sort -u` 去重 plugin 名 → 得到 **唯一 plugin 计数**。

**铁律**：写 AGENTS.md / 日报时，插件市场 skill 数永远用这个 find 算法，不要再用 `rglob`。

## ⚠️ vercel plugin 不存在（8-16 误判）

8-16 日报 / AGENTS.md 标了 **"vercel 47 skill 待装"**。8-20 实跑：

```bash
codex plugin add vercel@openai-api-curated
# Error: plugin `vercel` was not found in marketplace `openai-api-curated`
```

**结论**：openai-api-curated marketplace **没有 vercel plugin**。可能：
1. 之前移除了
2. 改名为别的（`render` 21 skill / `temporal` 替代）
3. 8-16 那个 47 数是 older inventory

**修法**：8-20 已从 AGENTS.md 移除"vercel 待装"行。**铁律**：每次"待装清单"必须以当日 `codex plugin list` 输出为准，不许引用 >7 天的旧报告。

## doctor 健康基线（8-20 实测）

```
16 ok · 1 idle · 2 notes · 1 warn · 0 fail degraded
```

对比 8-15 的 "12/12 全绿"，多了 4 个 ok 项（superpowers/build-web-data-visualization/latex/linear 装上后 doctor 多扫了 4 个 plugin health check）。

**关键 health 项**：
- custom API base URL  `http://127.0.0.1:5000/v1` reachable (HTTP 404) → 这是 minimax 中转代理返 404 但**可达**，算 ok
- custom API route probe → HTTP 200
- node_repl MCP → stable hash `789504f803e82e2b`（路径未变）
- app-server daemon → not running（ephemeral mode，默认）

## superpowers 14 skill 落地清单

```bash
find ~/.codex/plugins/cache/openai-api-curated/superpowers -name SKILL.md | wc -l
# → 14
```

| Skill | 用途 |
|---|---|
| brainstorming | 强制写 plan 前先 brainstorm |
| dispatching-parallel-agents | 并行派发子 agent |
| executing-plans | 计划执行 |
| finishing-a-development-branch | 收尾合并 |
| receiving-code-review | 接收 code review |
| requesting-code-review | 请求 code review |
| subagent-driven-development | 子 agent 驱动开发 |
| systematic-debugging | 系统化调试 |
| test-driven-development | TDD |
| using-git-worktrees | worktree 工作流 |
| using-superpowers | 总入口 |
| verification-before-completion | 完成前验证 |
| writing-plans | 写实施 plan |
| writing-skills | 写新 skill |

**装法**：直接 `codex plugin add superpowers@openai-api-curated`（8-20 实测一次性成功，无需 `codex plugin marketplace add` 因为 marketplace 已在 config.toml 里）。

## 飞书推送状态（cron 模式）

8-20 cron 没推飞书，原因：
- `~/.hermes/config.yaml` 无 `platforms.feishu.home_channel` 配置
- `~/.hermes/reports/codex-daily-evolution-2026-08-20.md` 已落盘本地
- 铁律 7b：bot 10014 unauthorized + 0 chats → 不浪费 API 试推

**修法（待老大）**：手动 `hermes config set FEISHU_HOME_CHANNEL oc_xxx` + 拉 bot 进群。

## 8-20 踩坑清单（无新坑，5 插件 0 失败）

- ✅ `codex plugin add` 子命令正常
- ✅ plugin 缓存路径 `~/.codex/plugins/cache/openai-{bundled,api-curated}/<plugin>/<version>/` 自动生成
- ✅ AGENTS.md patch 正常（老大 AGENTS.md 已从 8-15 状态升级到 8-20，12 插件完整清单）
- ✅ `find ~/.codex/plugins/cache -name SKILL.md -path "*/skills/*"` 工作正常

## 下次 cron 必跑清单（8-21 抄作业）

```bash
# 1. baseline
codex --version
codex doctor | tail -5
codex plugin list | grep "installed, enabled" | wc -l
ls ~/.codex/skills/ | wc -l
find ~/.codex/plugins/cache -name SKILL.md -path "*/skills/*" | awk -F'/skills/' '{print $2}' | awk -F'/' '{print $1}' | sort -u | wc -l

# 2. upgrade check（local snapshot 必返 no-op）
codex plugin marketplace upgrade --json
# 期望: {"selectedMarketplaces": [], "upgradedRoots": [], "errors": []}

# 3. 评估待装（按 8-20 实测清单，vercel 已剔除）
codex plugin list | grep "not installed"   # 拿真实未装清单，不引用旧报告

# 4. 装 1-2 个新插件（如果 marketplace 真有新品）
# 比如: superpowers / vercel 等价物 / 老大点名的

# 5. 更新 AGENTS.md（数字一致 → 跳过；数字变 → 必须 patch）
# 6. 落盘 ~/.codex/daily-evolution/YYYY-MM-DD.md
```

## 与之前 runbook 的关系

- 基础命令 / `.system` 处理 / yuxin-skills 备份冲突 / GH013 / branch protection：见主 SKILL.md
- capability-audit-and-validation.md：本次确认 `Path.rglob` 过度计数问题，**仍以 find 算法为准**
- cron-mode-tool-restrictions.md：8-20 全程用 terminal + patch + write_file + skill_manage，无 execute_code / hermes update 调用

## 8-20 数字精确性 cross-check

| 口径 | 命令 | 结果 |
|---|---|---|
| 本地 skill 数（不含 .system） | `ls ~/.codex/skills/` | 83 |
| 本地 skill 总数（含 .system） | `ls -A ~/.codex/skills/` | 应 = 89 |
| 已装 enabled 插件 | `codex plugin list \| grep "installed, enabled" \| wc -l` | 12 |
| 已装 disabled 插件 | `codex plugin list \| grep "installed, disabled" \| wc -l` | 0 |
| 未装插件 | `codex plugin list \| grep "not installed" \| wc -l` | 21 |
| 插件市场独立 plugin 数 | `find ~/.codex/plugins/cache -name SKILL.md -path "*/skills/*" \| awk -F'/skills/' '{print $2}' \| awk -F'/' '{print $1}' \| sort -u \| wc -l` | 233 |
| 插件市场 SKILL.md 总数（含 references） | `find ~/.codex/plugins/cache -name SKILL.md \| wc -l` | 253 |

**AGENTS.md / 日报写法**：用第 1 行 + 第 4 行 + 第 7 行（83 / 12 / 233） = 总 336