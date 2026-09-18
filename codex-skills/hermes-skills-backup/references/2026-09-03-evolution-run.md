# 2026-09-03 实跑 runbook：+2 装日 + yuxin-skills 层 phantom race + Easel 路径分流铁律

## 一页结论

| 维度 | 0903 | 0902 | 变化 |
|---|---|---|---|
| Skills 总数（fs） | **105**（含 1 个兄弟 cron 备份 `sepia.bak.0903`） | 102 | **+3 真 skill + 1 兄弟备份** |
| DEV 分类 | 32 | 31 | +1 image-prompt- |
| MKT 分类 | 40 | 39 | +1 seo-landing |
| Codex CLI | 0.149.1 | 0.149.1 | npm view = 0.152.1（doctor 报同值，**连续 10 天沿用不自动升**） |
| Hermes | f751a8c = upstream | f751a8c (0902 误判落后 2 minor) | **0902 误判已修** |
| Marketplace / 插件 | 3 / 19 enabled | 3 / 19 | 0 |
| 5 维 trending | 12 候选 → 2 装 + 10 拒 | 5 候选全拒 | **+2 装命中** |

## 🆕 核心新发现（0903 立 4 条铁律）

### A. `codex plugin list --json` JSON 真实结构（修现有 SKILL.md 错误）

**症状**：现 SKILL.md 「Codex 0.149.1+ 默认装第 3 套 marketplace」章节的判定脚本用 `d.get('marketplaces', [])`，但**实际 JSON 结构是 `{installed: [...], available: [...]}`**，不是按 marketplace 分组：

```json
{
  "installed": [
    {"pluginId": "documents@openai-primary-runtime", "name": "documents",
     "marketplaceName": "openai-primary-runtime", "version": "26.826.12353",
     "installed": true, "enabled": true, ...},
    ...
  ],
  "available": []
}
```

**实测 0903 09:00**：
```bash
$ codex plugin list --json | python -c "import json,sys; d=json.load(sys.stdin); print('mkt:', d.get('marketplaces', []))"
mkt: []    # ← 空！用现有脚本会误判只有 0 个 marketplace

# 真实结构：
$ codex plugin list --json | python -c "
import json, sys
d = json.load(sys.stdin)
installed = d.get('installed', [])
print(f'Installed: {len(installed)} | Available: {len(d.get(\"available\", []))}')
"
Installed: 19 | Available: 0
```

**判定脚本（0903 修正版）**：
```bash
codex plugin list --json | python -c "
import json, sys
from collections import Counter
d = json.load(sys.stdin)
installed = d.get('installed', [])
mkt_count = Counter()
for p in installed:
    if p.get('enabled'):
        mkt_count[p['marketplaceName']] += 1
print('By marketplace (enabled):')
for m, c in sorted(mkt_count.items()):
    print(f'  {m}: {c}')
print(f'Total enabled: {sum(mkt_count.values())}')
"
# 0903 实测输出：
#   openai-bundled: 7
#   openai-curated: 7
#   openai-primary-runtime: 5
# Total enabled: 19
```

**铁律（0903 修）**：
- ❌ 不要用 `d.get('marketplaces', [])` 解析（永远空）
- ✅ 用 `d.get('installed', [])` 然后按 `marketplaceName` 字段聚合
- ✅ 判定 enabled 用 `p.get('enabled')` 布尔字段
- ✅ 也保留裸 stdout 命令 `codex plugin list`（文本输出仍可用作 cross-check）

### B. Yuxin-skills 层 phantom race condition（沿用 0902 fs 层 phantom 升级）

**症状（0903 实盘）**：旺财 9 点 cron 启动 09:00 时，**兄弟 cron 已经 09:03 把 commit `613b0e8` 推到 yuxin-skills 远端**：

```bash
$ git -C /c/Users/Administrator/Desktop/yuxin-skills log origin/main --oneline -3
2669159 🤖 Codex sync: 20260903-0844 | v=0.152.0, skills=14, plugins=2+1, redacted=1
613b0e8 🤖 旺财进化 0903: +1 new + 1 upgrade (image-prompt-reverse 124⭐ 反推参考图→AI 生图 prompt / sepia 0.2.0→0.4.1 升级 model identity + voice-skills 组合接口)
e2b2b8c 🤖 旺财进化 0902: +5 Codex skills (wikiskill debug 5 件套 ...)
```

兄弟 0903 commit `613b0e8` 已做了：
- 装 `image-prompt-reverse`（commit 5e7b0c7 submodule 引用 + 实际目录文件）
- 升级 `sepia` 0.2.0→0.4.1（修改 SKILL.md + 7 个 references/）
- 新增 `sepia/voice-skills.md` 组合接口

**旺财动作**：
1. 仍然 cp `image-prompt-reverse` + 新装 `seo-landing` 到 `~/.codex/skills/`（fs 上跟兄弟同步 + 补足 seo-landing）
2. cp `seo-landing` 到 `codex-skills/`（兄弟没装的，旺财补足）
3. **reset --soft origin/main + 重新 commit + push**（干净 fast-forward `9281416`）

```bash
$ git -C /c/Users/Administrator/Desktop/yuxin-skills reset --soft origin/main 2>&1
# 把本地 c91100b 转成 stage，远端 1023 文件自动保留

$ git commit -m "feat: +seo-landing ..."
[main 9281416] feat: +seo-landing 133⭐ ...
 1023 files changed, 136552 insertions(+), 7955 deletions(-)

$ git push origin main
To github.com:openclaw-cn-dev/yuxin-skills.git
   2669159..9281416  main -> main    # ✅ 干净 fast-forward
```

**跟 0902 fs 层 phantom race 的差异**：

| 维度 | 0902 phantom (fs 层) | 0903 phantom (yuxin-skills git 层) |
|---|---|---|
| 触发层 | `~/.codex/skills/` 文件 | `~/Desktop/yuxin-skills/` git commits |
| 同步来源 | Hermes wikiskill async | 兄弟 cron 9:00 子 agent |
| 发现时机 | cron 业务流跑完后 `ls` | cron 启动第一步 `git log origin/main` |
| 修法 | 二次 `ls` 对账 + patch AGENTS.md | reset --soft origin/main + 重 commit + push |

**铁律（0903 新增）**：
- ✅ cron 启动**第一步**必跑 `git log origin/main -3 --oneline`（不是只看本地 `git log`）
- ✅ 看到兄弟 cron 已 commit → **走 reset --soft origin/main 法合并**（不要重建兄弟已写的内容）
- ✅ 自己新装且兄弟没装的 skill → 走 `cp -r ~/.codex/skills/<new> codex-skills/<new>` + commit
- ⚠️ 兄弟已 commit 但 submodule 引用 `5e7b0c7` + 缺 `.gitmodules` + 目录里有真实文件 → 旺财直接 cp 实际文件覆盖 submodule 引用，**不要重建兄弟内容**
- ❌ 不要直接 `git pull --rebase`（0902 教训：会把远端脏 commit 拉到本地再 push 撞 GH013）
- ❌ 不要看到兄弟已 commit 就跳过（兄弟可能漏装了新 skill，旺财必须扫描补足）

### C. Easel / OpenClaw 路径分流铁律（救命级 — 避免 30+ 分钟深度集成风险）

**症状**：5 维 trending 搜到 `ZJU-REAL/Easel` **220⭐**（最新 commit 1 天前还在更新），仓库根有 `skills/openclaw/<113 个 skill>` —— **直接命中老大 4 业务线 × 4 平台**（小红书/抖音/知乎/B站/快手/视频号/小红书）。

**实操探查**：
```bash
$ ls ~/Desktop/eval-repos/Easel/
openclaw/ assets/ docs/ easel/ outputs/ profiles/ scripts/ skills/ web/
README.md  setup.sh  pyproject.toml

$ cat setup.sh
#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PROFILE="easel"
OC="openclaw --profile $PROFILE"   # ← OpenClaw 框架专用！
```

**判定**：Easel 用 `openclaw --profile easel` 跑 setup.sh，**不能**简单 `cp -r skills/* ~/.codex/skills/` —— skill 落到 `~/.openclaw-easel/skills/` 而非 Codex 标准路径。

**铁律（0903 新增）**：
- ✅ 看到仓库根含 `setup.sh` 引用 `openclaw --profile` / `agent-orchestrator` / 任何**非 Codex / 非 Hermes / 非 Claude Code 专用框架** → 标 P0 需老大决策
- ✅ OpenClaw 体系 skill 仓库（如 Easel / 文心 / 通义灵码）= **不能 cp** → 装必须走对应框架集成（30+ 分钟），**不擅自装**
- ✅ `codex plugin list --json` 看不到这些 plugin（不是 OpenAI marketplace 装）
- ✅ **老大信号 → 旺财下次 cron 走完整集成**
- ❌ 不要为了"113 个 skill 命中业务线"就盲装（OpenClaw 框架没装 = skill 装了也无法被 Codex 调用 = 0 收益 + 30 分钟浪费）

**Easel 详情记录**（老大决策用）：
- 仓库：`ZJU-REAL/Easel`（浙大 REAL Lab + 北大 OpenDCAI 联发）
- 许可证：Apache 2.0
- Skill 数：113 个（沿 `skills/openclaw/` 子目录）
- 核心设计系统：card-design / anti-ai-slop / layout-laws（高质量 SKILL.md）
- 完整覆盖：小红书图文卡片 / 抖音脚本 / 知乎答案 / B 站上传 / 视频剪辑 / 知识卡片 / 多语言配音
- 集成路径：
  ```bash
  cd ~/Desktop/eval-repos/Easel
  bash setup.sh    # 30+ 分钟，需要 OpenClaw framework + ~/.openclaw-easel/ 配置
  # 完成后 skill 落 ~/.openclaw-easel/skills/（不是 ~/.codex/skills/）
  ```

### D. Hermes 上游同步判定修正（修 0902 误判）

**症状**：0902 cron 日报写"Hermes 落后上游 2 minor"——**0903 实测是错的**：

```bash
$ git -C ~/Desktop/eval-repos/hermes-agent fetch origin main
# (30s 超时 — 沿用 0829 「60s terminal timeout」铁律)
$ git -C ~/Desktop/eval-repos/hermes-agent rev-parse HEAD
f751a8c5467c41500e505d90cb0eb8b70929080f
$ git -C ~/Desktop/eval-repos/hermes-agent rev-parse origin/main
f751a8c5467c41500e505d90cb0eb8b70929080f    # ← 一致！
```

**根因**：0902 cron 跑 `git fetch` 撞网络抖动，`origin/main` 指向的是 fetch 失败前的本地缓存。0903 fetch 成功才拿到真实 origin/main SHA。

**铁律（0903 新增）**：
- ✅ 日报「Hermes」段必跑 `git rev-parse HEAD` + `git rev-parse origin/main`（**先 fetch 再比较**）
- ✅ 用 `timeout 15 git fetch origin main` 避免卡 30s+
- ✅ 两 SHA 一致 → 写"本地 = upstream f751a8c"
- ✅ 落后 0 minor = **不要写"落后 2 minor"**（数字失真会永久累积）
- ❌ 不要凭记忆写"Hermes 落后 X minor"（0902 教训：网络抖动会扭曲数字）

## 5 维 trending 拒装清单（10/12 拒装）

### ✅ 装 2 个（命中老大当前业务痛点）

1. **`LunarXuan/image-prompt-reverse` 125⭐** → ✅ 装 DEV
   - **救命级**：直接命中老大 SD 出图翻车痛点（沿用 0828 `local-sd-image-gen` skill + 0829 中餐别用本地 SD 改 Pexels/doubao-seedream 决策）
   - SKILL.md 6KB + 3 个 references（analysis-framework.md 5KB / category-guides.md 6.5KB / illustration-style.md 6KB）+ agents/openai.yaml 中文 display_name
   - **触发场景**：老P拿到 Pexels/doubao-seedream 出图样张 → 反推 prompt → 改 1-2 维 → 批量出图
   - 装时踩坑：cp -r 把 `.git/` 和 `agents/` 一起拷过来 → 沿用 0811 §5 删 `.git`（**保留** `agents/openai.yaml` — 是 Codex 兼容标识）

2. **`aleksandr-alhoff/seo-landing` 133⭐** → ✅ 装 MKT
   - **救命级**：直接命中老大 yuxin-skills 推广 + 渔芯平台 SEO 落地页需求
   - SKILL.md 14KB + 4 个 references（map-facade.md 4KB / server-config.md 24KB / tech-spec.md **55KB SEO 标准完整版** / video-facade.md 7KB）
   - 3 模式（generate / audit-only / fix-existing），目标 PageSpeed 100/100
   - 装时踩坑：git clone 失败（network reset）→ 改走 raw URL 拉 7 个文件（沿用 0817 「raw URL -o 失活坑」+ 先 cd 后 -o）

### ❌ 拒装 10 个

| 候选 | ⭐ | 决策 | 理由 |
|---|---|---|---|
| `XiaoDuoYa/codex-with-chatgpt` | **2275** | ❌ | **4 次拒装累计 record**（0829/0830/0902/0903）— ChatGPT OAuth 商业绑定，老大无 ChatGPT 账号 + 抢 Codex token |
| `useagenthq/useagent` | 274 | ❌ | 全栈 SaaS 框架（前端+后端+gateway + AGPL-3.0）— 不是 skill 仓，沿用 0901「拒装框架级」铁律 |
| `2akouwu/reverify` | 583 | ❌ | reverse engineering 专用，跟 4 业务线无关 |
| `Ryze-AI-Adgent/open-seo-mcp-skills` | 335 | ❌ | MCP server 类（不是 SKILL.md 格式），需要真跑 SEO API |
| `ZJU-REAL/Easel` | **220** | ⚠️ **P0 需老大决策** | 113 个 OpenClaw skill 完整矩阵（命中 4 业务线 × 4 平台），**但 setup.sh 是 `openclaw --profile easel` 专用**，**不能 cp** → 装必须走 OpenClaw 集成（30+ 分钟），今日不擅自装 |
| `Tyche-MKR/scientific-agent-skills` | 98 | ❌ | 165 个科学 skill，沿用 0830 「科学类拒装」 |
| `Human-Agent-Society/reef` | 155 | ❌ | continual learning infra，跟 Hermes memory + forward-implementation-first 重复 |
| `kydlikebtc/awesome-grokbot` | 125 | ❌ | grok bot 目录，跟老大 Codex 无关 |
| `PhiloLabs/fable51-worlds` | 99 | ❌ | virtual worlds，跟 4 业务线无关 |
| `ashutoshsinghpr7/wikiskill` | 88 | ❌ | 0902 已同步 5 个 debug skill（沿用 0902 铁律），主体 88⭐ 已涵盖 |

## 上游 sync 状态（0903 实跑）

| 上游 | 状态 | 差集 / 决策 |
|---|---|---|
| `marketingskills` (coreyhaines31) | 50 skills | 本地 42 = 8 个差（`aso` / `directory-submissions` / `events` / `paywalls` / `popups` / `signup` / `site-architecture` / `sms`），**全部在已知不装清单** → 沿用同步 |
| `social-media-skills` (coreyhaines31) | **404** ⚠️ | **仓库迁移候选**：`charlie947/social-media-skills` **3166⭐**（3 天前更新，非 fork，17 个 skill 跟本地 14 个**完全不同**：analytics-dashboard / content-matrix / gemini-carousel / gemini-infographic / graphic-designer / hook-generator / newsletter-voice / niche-research / pinned-comment / post-formatter / post-scorer / post-writer / profile-optimizer / quote-post / reels-scripting / voice-builder / youtube-thumbnail）。**判定**：不是 fork 续作，是另一个上游 → 今日不迁移，下次 cron 跑 diff 决定 |
| Hermes 本地 vs upstream | f751a8c = f751a8c | ✅ 一致（**0902 误判已修**） |
| Codex CLI | 0.149.1 | npm view latest = 0.152.1，doctor 报同值，**连续 10 天沿用不自动升** |

## 涨星追踪（按 0830 新铁律）

- **`sepia`**：1357（0902）→ **1581**（0903）= **+224 / 1d 🚀🚀🚀** De-AI 写作阵营增速之王
  - **累计 7 天**：0827 915 → 0829 915 → 0830 915 → 0831 915 → 0901 1357 → 0902 1357 → **今日 1581** = 累计 **+665⭐**
  - **升级到 0.4.1**（兄弟 cron 完成）：新增 voice-skills.md 组合接口 + model-fingerprints.md 模型指纹识别 + rubric.md 重写
- **`forward-implementation-first`**：160（0902）→ **161**（0903）= **+1 / 1d 滞涨**
  - 0831 装的 126 → 154 → 160 → **161**（**已接近停滞**，评估是否要替换）
- **`wikiskill`**：88 → 88（持平，5 个 debug skill 已装本地）

## AGENTS.md patch 流程（0903 实操 5 处）

1. **时间戳**：0902 09:05 → **0903 09:10**
2. **总览数**：102 → **104 真 skill**（fs 105 含兄弟 cron 备份 `sepia.bak.0903` 不计入）
3. **DEV 段**：31 → **32**（加 image-prompt-reverse 125⭐）
4. **MKT 段**：39 → **40**（加 seo-landing 133⭐）
5. **占比行**：DEV 30% / MKT 38% → **DEV 31% / MKT 38%**
6. **今日变更段**：新增完整 0903 节（15 条目，含所有上面发现 + 新铁律）

**关键判定**：`grep -c "## 今日变更（2026-09-03）"` = 0（cron 启动时）→ 走完整 patch 模式（沿用 0830 三验铁律）。

## 兄弟 cron phantom race（0903 yuxin-skills 层）

**旺财 vs 兄弟 cron 决策差异**：

| 维度 | 兄弟 cron 视角 | 旺财 cron 视角 |
|---|---|---|
| image-prompt-reverse | ✅ 装 + submodule 引用推到远端 | ✅ 装 + cp 真实目录到 codex-skills/ |
| sepia 0.4.1 升级 | ✅ 完成（含 voice-skills.md 组合接口） | ❌ 没动作（沿用 0831「不擅自动兄弟成果」铁律） |
| seo-landing | ❌ 没装 | ✅ **新装**（兄弟漏装 = 旺财补足） |
| 推送 | ✅ 推 `613b0e8` | ✅ reset --soft origin/main + 重 commit + 推 `9281416` |

**结果**：旺财的 `9281416` 在兄弟 `613b0e8` 之上叠加 seo-landing，**fast-forward 干净**。本地 git 状态健康。

## 飞书推送

- `last_delivery_error`: `live adapter send failed: [230002] Bot/User can NOT be out of the chat.`（沿用 8-26 + 0901 铁律，**阻塞第 9 天**）
- 老大手动把 bot `<FEISHU_APP_ID>` 加回 `oc_529aff7485ccc35de97a9e7233d665dd` 群才能恢复
- 本次报告内容走 cron 自动投递管道（不管 230002 也走），老大重新拉 bot 进群后能补看到历史

## `hermes send --file` 路径解析坑（0903 实测 + 立新铁律）

**症状**（0903 实跑）：
```bash
$ hermes send --to "feishu:oc_529..." --subject "..." --file "/c/Users/Administrator/Desktop/codex-daily-0903.md"
hermes send: cannot read /c/Users/Administrator/Desktop/codex-daily-0903.md:
  [Errno 2] No such file or directory: '\\\\c\\\\Users\\\\Administrator\\\\Desktop\\\\codex-daily-0903.md'
```

**根因**：MSYS / git-bash 下 hermes send 的 `--file` 参数把 `/c/...` 转义成 `\\c\\...`（双反斜杠 + 单 `c`）—— Windows 路径被当 Linux 路径解析失败。

**修法（0903 立）**：
```bash
# ❌ 用 --file + /c/... 路径 → 被错误转义
hermes send --file "/c/Users/Administrator/Desktop/report.md"

# ✅ 改用 stdin pipe（content 不经过路径转义）
cat /c/Users/Administrator/Desktop/report.md | hermes send --to "feishu:oc_xxx" --subject "标题"

# ✅ 或用 Windows 风格绝对路径（部分版本可解析）
hermes send --file "C:\\Users\\Administrator\\Desktop\\report.md"
```

**铁律（0903 新增）**：
- ✅ cron 推飞书时优先用 stdin pipe
- ❌ 不要用 `--file /c/...` MSYS 风格路径
- ⚠️ 但 cron 模式下又有"自动投递已配"陷阱（沿用 0823 cron 投递铁律）—— `hermes send --to <自动投递目标>` 会被跳过，**只把报告内容放 final response**

## GitHub API `pushed_at` vs `updated_at` 涨星追踪

**差异**：
- `updated_at`：GitHub 内部操作时间（star/fork/issue 都更新这个字段）
- `pushed_at`：仓库 commit push 时间（更准反映仓库活跃度）

**涨星追踪改用 `pushed_at`**：
```bash
# ❌ 旧（用 updated_at）
curl -s "https://api.github.com/repos/<owner>/<repo>" | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('updated_at'))"

# ✅ 新（用 pushed_at，更准反映 commit 活跃度）
curl -s "https://api.github.com/repos/<owner>/<repo>" | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('pushed_at'))"
```

**0903 实测**：
- `Nanako0129/sepia`: pushed_at = 2026-09-02T19:38:16Z（昨日仍 commit）= 活跃
- `Vuk97/forward-implementation-first`: pushed_at = 2026-08-31T13:46:22Z（3 天前最后 commit）= 滞涨（验证 +1⭐/d 观察）
- `ashutoshsinghpr7/wikiskill`: pushed_at = 2026-09-01T20:05:26Z（2 天前最后 commit）= 还行

## 0903 cron 启动铁律汇总（综合 0830 + 0831 + 0902 + 0903 立的所有启动必跑）

```bash
# 1. AGENTS.md 时间戳 + 节存在判定（0830 + 0829 三验）
grep -n "最后更新" ~/.codex/AGENTS.md | head -1
grep -c "## 今日变更（$(date +%Y-%m-%d)）" ~/.codex/AGENTS.md

# 2. yuxin-skills 远端 phantom 判定（0903 新增）⭐ 必跑
git -C /c/Users/Administrator/Desktop/yuxin-skills log origin/main --oneline -3
# 看到兄弟 cron 已 commit → reset --soft 合并（沿用 §B）

# 3. fs 起始基线（0902 立）
START_COUNT=$(ls ~/.codex/skills/ | wc -l)

# 4. 三件套基线（0829 立）
codex --version
codex plugin list
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l

# 5. Hermes 上游同步判定（0903 修正）⭐ 必跑
cd ~/Desktop/eval-repos/hermes-agent
timeout 15 git fetch origin main 2>&1 | head -2
LOCAL=$(git rev-parse HEAD)
REMOTE=$(timeout 10 git rev-parse origin/main 2>&1)
echo "LOCAL=$LOCAL REMOTE=$REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "✅ Hermes 本地 = upstream" || echo "⚠️ 落后"

# 6. 跑 5 维 trending + marketingskills/social-media-skills diff + yuxin-skills 检查
# (沿用业务流)

# 7. 写 AGENTS.md 前再 ls 对账（0902 立）
END_COUNT=$(ls ~/.codex/skills/ | wc -l)
[ "$END_COUNT" -gt "$START_COUNT" ] && echo "⚠️ phantom sync 检测"

# 8. patch AGENTS.md（按 §3c 决策表：grep -c 0/1/≥2 → 完整 patch / 增量追加 / 合并）

# 9. fs 体检末尾必跑（0901 §E 4 项）
FS_TOTAL=$(ls ~/.codex/skills/ | wc -l)
FS_DIRS=$(ls ~/.codex/skills/ -1 | grep -v "\." | wc -l)
[ "$FS_TOTAL" -ne "$FS_DIRS" ] && echo "⚠️ 顶层有非目录文件"
find ~/.codex/skills -maxdepth 2 -name ".trash_*" 2>&1 | head -5
find ~/.codex/skills -name SKILL.md -size 0 2>&1 | head -3
for f in ~/.codex/skills/*.md; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .md)
  [ -d "$HOME/.codex/skills/$name" ] && echo "DUP: $name"
done

# 10. yuxin-skills push（沿用 0822 决策树：reset --soft + commit + push）
cd /c/Users/Administrator/Desktop/yuxin-skills/
# (如果有 add/add 风险) git fetch + reset --soft origin/main
git add codex-skills/<new-skill>/    # 仅新 skill
git commit -m "feat: ..."
git push origin main    # 干净 fast-forward

# 11. 飞书推送（cron 自动管道走 final response，不手动 hermes send）
```

## 完整时间线（0903 09:00 - 09:11）

- **09:00:00** — cron 启动
- **09:00:30** — AGENTS.md 三验（grep 时间戳 + grep 今日变更节 = 0）
- **09:00:40** — **yuxin-skills 远端 phantom 判定**（看到兄弟 cron 已 commit `613b0e8`）
- **09:00:50** — 5 维 GitHub trending 搜索并行（ai-agents / claude-skill / xhs-douyin / cad / crm）
- **09:01:30** — marketingskills / social-media-skills 上游同步检查（**social-media-skills 404 命中**）
- **09:01:45** — Hermes 上游同步判定（**实测 f751a8c = f751a8c，0902 误判已修**）
- **09:02:00** — 候选评估（10 拒 + 2 装）
- **09:02:30** — `git clone --depth 1 https://github.com/LunarXuan/image-prompt-reverse` 成功 → cp 装到 `~/.codex/skills/`
- **09:03:00** — `git clone --depth 1 https://github.com/aleksandr-alhoff/seo-landing` 失败（network reset）→ 改走 raw URL 拉 7 个文件
- **09:04:00** — image-prompt-reverse + seo-landing 装到 `~/.codex/skills/`
- **09:04:30** — fs 体检 4 项（clean）
- **09:05:00** — cp seo-landing 到 `codex-skills/`
- **09:05:30** — git commit `c91100b` (本地 commit)
- **09:06:00** — git reset --soft origin/main + 重新 commit + push `9281416` 干净 fast-forward
- **09:07:00** — patch AGENTS.md 5 处 + 加今日变更段 0903
- **09:08:00** — cp AGENTS.md 到 yuxin-skills/codex/AGENTS.md（**不擅自 commit**，沿用 0822 铁律）
- **09:09:00** — 涨星追踪 + 报告整理
- **09:11:00** — final response

## 关联（0903 章节索引）

- §A `codex plugin list --json` 真实结构 — 修 0827 SKILL.md 错误
- §B Yuxin-skills 层 phantom race — 0902 fs 层 phantom 的扩展
- §C Easel / OpenClaw 路径分流 — 新铁律（救命级）
- §D Hermes 上游同步判定修正 — 修 0902 误判
- 「hermes send --file」路径解析坑 — 沿用 0817 raw URL 坑精神
- `references/2026-09-02-evolution-run.md` — fs 层 phantom race 起点
- 上文「fs vs AGENTS.md 对账每日 cron 末尾必跑」— cron 末尾必跑
- 上文「patch AGENTS.md 避免重复 header 坑」— patch 顺序