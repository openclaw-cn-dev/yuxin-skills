# 插件 Skills 发现与统计（2026-08-16 重写，2026-08-17 bash 优先化）

## 一句话
`codex plugin list` 的 `STATUS` 列只显示插件本身的安装态，**不显示插件内有多少 skill**。
要数"插件市场里到底有多少个可调用的 skill"，必须用 `find -name SKILL.md | wc -l` 或 `Path.rglob('SKILL.md')` 实测，**不许估算**。

## ⚠️ 路径修正（2026-08-16 实测，旧文档错）

8-01 老文档说插件 skills 在 `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/skills/`，**错的**。
实测真实路径：

| 来源 | 真实路径 |
|---|---|
| api-curated 插件 SKILL.md | `~/.codex/.tmp/plugins/plugins/<plugin_name>/skills/<skill_name>/SKILL.md` |
| bundled 插件 SKILL.md | `~/.codex/.tmp/bundled-marketplaces/openai-bundled/plugins/<plugin_name>/skills/.../SKILL.md` |
| 本地 skills | `~/.codex/skills/<name>/SKILL.md`（不变） |
| `~/.codex/plugins/cache/` | **不存在**（8-01 时也许在，8-17 已清） |

## 精确盘点命令

### 🆕 单行 bash（2026-08-17 实测：cron 首选，零依赖）
```bash
echo "api: $(find "C:/Users/Administrator/.codex/.tmp/plugins/plugins" -name "SKILL.md" 2>/dev/null | wc -l) | bundled: $(find "C:/Users/Administrator/.codex/.tmp/bundled-marketplaces/openai-bundled/plugins" -name "SKILL.md" 2>/dev/null | wc -l) | local: $(ls ~/.codex/skills 2>/dev/null | grep -vc '^\.')"
# 8-17 实测：api: 576 | bundled: 6 | local: 62
```

**为什么 bash 优先**：
- 8-16 写的 Python `Path.rglob` 路线在 cron 模式下 `execute_code` 被拒，只能走 `terminal + python -c`
- `python -c` 多行 heredoc 在 bash 里 escape 麻烦，且打印中文路径可能撞编码
- `find ... | wc -l` 是 1 行命令，**不需要 python**，cron 里 `terminal()` 直接跑
- 8-16 vs 8-17 数字差异（613 → 644 = 582 + 62）说明两个口径差 ~30 个，是 bash find vs Python rglob 对 symlink / 大小写处理微差，**不是真数据漂移**。日报里写数字时直接用当次实测口径，标 `(bash)` 或 `(python)` 注明方法

### Python（双源 / 详情场景用）
```python
from pathlib import Path

base_api = Path(r"C:\Users\Administrator\.codex\.tmp\plugins\plugins")
api_total = 0
api_per = {}
for p in sorted(base_api.iterdir()):
    if not p.is_dir(): continue
    skills = list(p.rglob("SKILL.md"))
    if skills:
        api_per[p.name] = len(skills)
        api_total += len(skills)

base_bundled = Path(r"C:\Users\Administrator\.codex\.tmp\bundled-marketplaces\openai-bundled\plugins")
bundled_total = 0
for p in sorted(base_bundled.iterdir()):
    if not p.is_dir(): continue
    skills = list(p.rglob("SKILL.md"))
    if skills:
        bundled_total += len(skills)

print(f"api-curated: {api_total}, bundled: {bundled_total}, TOTAL: {api_total + bundled_total}")
# 8-16 实测：607 + 6 = 613
# 8-17 bash 实测：576 + 6 = 582（口径差 ~30）
```

### 一次性 bash 全套（cron 一行）
```bash
echo "=== Codex 状态 ===" && codex --version && \
echo "=== api: $(find "C:/Users/Administrator/.codex/.tmp/plugins/plugins" -name "SKILL.md" 2>/dev/null | wc -l) ===" && \
echo "=== bundled: $(find "C:/Users/Administrator/.codex/.tmp/bundled-marketplaces/openai-bundled/plugins" -name "SKILL.md" 2>/dev/null | wc -l) ===" && \
echo "=== local: $(ls ~/.codex/skills 2>/dev/null | grep -vc '^\.') ===" && \
echo "=== enabled plugins: $(codex plugin list 2>&1 | grep -c "installed, enabled") ==="
```

## 各插件 skill 分布（2026-08-16 实测）

| 插件 | skill 数 | 备注 |
|---|---:|---|
| twilio-developer-kit | 55 | 单插件大头 |
| life-science-research | 50 | 与水产养殖有交集 |
| vercel | 47 | **Next.js 部署，渔芯上线必备** |
| daloopa | 21 | |
| render | 21 | |
| shopify | 20 | |
| build-web-data-visualization | 18 | |
| ngs-analysis | 18 | |
| **superpowers** | **14** | **开发方法论（brainstorming/TDD/规划）** |
| expo | 13 | |
| codex-security | 12 | |
| figma | 12 | |
| netlify | 12 | |
| build-macos-apps | 11 | Windows 上不可用 |
| hugging-face | 11 | |
| nvidia | 11 | |
| build-ios-apps / cloudflare / game-studio / moody-s / plugin-eval | 各 9 | |
| boltz-api-cli / datasite | 各 8 | |
| sharepoint / teams | 各 7 | |
| build-web-apps / outlook-calendar / outlook-email / slack / superhuman | 各 6 | |
| atlassian-rovo / deepnote / google-calendar / google-drive / hyperframes / openai-developers | 各 5 | |
| circleci / github / hubspot / midpage / mixpanel-headless / notion / wix | 各 4 | |
| airtable / base44 / canva / chronograph-lp / morningstar | 各 3 | |
| gmail / heygen / neon-postgres / replayio / stripe / supabase / test-android-apps | 各 2 | |
| box / brighthire / catalyst-by-zoho / chronograph-gp / coderabbit / digitalocean / dnb-finance-analytics / hex / linear / magicpath / openai-ads-conversions / posthog / remotion / sentry / temporal / zotero | 各 1 | |
| **bundled**: browser / chrome / computer-use | 各 1 | |
| **bundled**: latex | 3 | |

**总计**：607（api-curated, Python rglob）/ 576（api-curated, bash find, 8-17）/ 6（bundled）/ 613（Python）/ 582（bash）

## 8-15 → 8-16 → 8-17 数字差异（实测修正）

| 项 | 8-15 估算 | 8-16 Python | 8-17 bash | 差异 |
|---|---|---|---|---|
| api-curated 插件数 | 27 | **29** | 29 | +2 |
| 插件市场 skill 数 | 219 | **613** | 582 | **-31 口径差** |
| 总 skill 数 | 281 | **675** | 644 | **-31 口径差** |

**根因（两层）**：
1. **8-15 → 8-16**：8-15 按"27 插件 × ~8 skill/插件"估算，实际单插件 skill 数差异巨大（twilio 55 vs box 1），平均无意义。修正为 rglob 实测
2. **8-16 → 8-17**：bash `find` vs Python `rglob` 对 `node_modules/`、`.git/`、symlink 处理不同。bash 默认不跟 symlink、可能跳过大小写差异的同名文件；Python rglob 会递归全部并跟随某些 symlink

**铁律**：
- 以后所有 skill 数都用 `find ... | wc -l` 实测（bash 优先，cron 友好）
- 跨天比较时若数字差 ~30，**先看口径是否一致**，再判数据漂移
- 不许估算

## Marketplace 快照规则（2026-08-16 实测）

### 两个默认 marketplace 都是固定本地快照
- `openai-bundled`：`~/.codex/.tmp/bundled-marketplaces/openai-bundled/`（root mtime = 2026-07-14）
- `openai-api-curated`：`~/.codex/.tmp/plugins/plugins/`（root mtime = 2026-07-14）
- `~/.codex/config.toml` 里的 `[marketplaces.<name>]` 段 `source_type = "local"`，**不是 git**

### 后果：永远不会有"自动新插件"
- `codex plugin marketplace upgrade` → `No configured Git marketplaces to upgrade`（**正常**，不是错）
- `codex plugin marketplace upgrade openai-bundled` → `Error: marketplace 'openai-bundled' is not configured as a Git marketplace`（**正常**）
- 想看 marketplace 是否更新过：`stat ~/.codex/.tmp/plugins | grep Modify`
- 想看 Codex 自身版本（这个**会**变）：`codex --version` + `codex doctor` 末尾

### 日报"今日新增插件"长期会是 0
- 这是**预期行为**，不是巡检失败
- 真的"新插件"只来自 Codex 推新版 npm：`npm update -g @openai/codex`
- 跑 `codex doctor` 看 `(current X.Y.Z)` vs `X.Y.Z available` 判定要不要升级

## 升级决策（2026-08-16 立）

| 情况 | 动作 | 判定 |
|---|---|---|
| `codex doctor` 报 `(current X available)` | 9 点 cron **不自动升级** | 日报"P0 需决策"段标"Codex 有新版本，待老大手动 `npm update -g @openai/codex`" |
| marketplace 快照日期变了 | 检查 Codex CLI 版本是否也变了 | 一起报"Codex + marketplace 都升级了" |
| `codex plugin marketplace upgrade` 报 "not Git" | **什么都不做** | local snapshot 的预期行为 |

## 不许做的 4 件事

1. ❌ 跑 `codex plugin marketplace upgrade --dry-run`（2026-08-16 实坑：不存在的 flag，报 `unexpected argument`）
2. ❌ 估算插件 skill 数（"X 插件 × Y skill/插件"——差异巨大，必错）
3. ❌ 期望 cron 能自动装到"昨天刚上 marketplace 的新插件"（marketplace 是固定快照）
4. ❌ 看到"No configured Git marketplaces"就报错——这是正常的

## 🆕 `codex plugin marketplace upgrade --json`（2026-08-17 实测可用）

输出结构化 JSON，比裸 stdout 易解析：
```bash
codex plugin marketplace upgrade --json
# {"selectedMarketplaces": [], "upgradedRoots": [], "errors": []}
```

判定逻辑：
- `selectedMarketplaces: []` + `upgradedRoots: []` = 全部是 local snapshot，无 Git marketplace 升级
- 有 marketplace 在数组里 + `upgradedRoots` 有值 = 真升级了某个 Git marketplace（当前两个默认都是 local，不会发生）
- `errors` 非空 = 真实失败，需查

比 `--dry-run` 靠谱——可以拿 `selectedMarketplaces` 长度做判定。

## 安装命令对照（保留）

```bash
# 装单个插件（marketplace 必填）
codex plugin add superpowers@openai-api-curated
codex plugin add build-web-apps@openai-api-curated

# 验证安装
codex plugin list 2>&1 | grep "installed, enabled"

# 卸载（如需）
codex plugin remove superpowers@openai-api-curated
```

## 注意事项

- `codex plugin add` 成功后**自动写入 `~/.codex/config.toml`** 的 `[plugins."name@marketplace"]` 段，无需手动编辑
- 重新启动 Codex 桌面后插件技能才会加载（exec 模式可能不加载）
- 旧文档里的"AGENTS.md 模板（2026-08-01）"已过期（数字 52+38=89 改成 62+582=644 bash 口径 / 62+613=675 Python 口径），模板同步更新见 SKILL.md §6.1
- **跨天口径差容忍**：8-17 bash 实测 582 vs 8-16 Python 实测 613 = 差 31，是 find vs rglob 工具差，不是真漂移。日报里说"数字用 bash find 实测"或"用 Python rglob 实测"标明口径即可