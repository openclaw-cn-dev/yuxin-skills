# 2026-08-17 Codex Evolution Run Log

> 实跑记录：当次 codex-self-evolve cron 触发的完整流程 + 数据 + 决策。供下次 cron 对照（避免重复犯错 / 复用已装好的清单）。

## 当日成果

| 项 | 数字 | 备注 |
|---|---|---|
| 新装 skill 总数 | **15** | superpowers 14 + sloptrim 1 |
| Codex 用户 skill 总数 | **77**（不含 .system） | 装前 62，+15 |
| Codex 真实总 SKILL.md 数 | **83** | 77 用户 + 6 .system |
| Codex CLI 版本 | 0.147.0 | 已 up-to-date |
| Hermes 本地版本 | v0.19.0 | 落后 remote v0.20.2（~397 PRs） |
| 同步到 yuxin-skills commit | `4165ac2` | `codex-skills/`（dash），非 `codex/` |
| GitHub push 状态 | ❌ 失败 | `push declined due to repository rule violations`（main 分支保护） |
| 日报路径 | `C:/Users/Administrator/Desktop/知识库/进化日报/2026-08-17_旺财进化.md` |  |

## 实跑操作序列（下次 cron 直接抄）

### Step 1: 环境摸底
```bash
date "+%Y-%m-%d %A 周%u"   # 2026-08-17 星期一 周1
hermes --version            # Hermes Agent v0.19.0 (2026.7.20)
codex --version             # codex-cli 0.147.0
cat ~/.codex/version.json   # latest_version 0.142.5（已 stale，CLI 自己已是 0.147.0）
ls ~/.codex/skills/ | wc -l              # 62（装前）
find ~/.codex/skills -name SKILL.md | wc -l  # 68（含 .system 6）
```

### Step 2: GitHub Trending 扫描（5 个 lane）
```bash
# Lane 1: AI Agents trending 7 days
curl -s "https://api.github.com/search/repositories?q=topic:ai-agents+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=15" | python -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('items',[])[:15]:
    print(f\"  {r['full_name']:45} | ⭐{r['stargazers_count']:5} | {r.get('description','')[:90]}\")
"

# Lane 2: Claude Code / Codex skills (本月)
curl -s "https://api.github.com/search/repositories?q=claude-code+skills+created:>$(date -d '30 days ago' +%Y-%m-%d)&sort=stars&per_page=10" ...

# Lane 3: MCP servers (本月)
curl -s "https://api.github.com/search/repositories?q=mcp+server+created:>$(date -d '30 days ago' +%Y-%m-%d)&sort=stars&per_page=10" ...

# Lane 4: 营销 / 自媒体工具 (本月)
curl -s "https://api.github.com/search/repositories?q=marketing+agent+created:>$(date -d '30 days ago' +%Y-%m-%d)&sort=stars&per_page=10" ...

# Lane 5: CAD / SolidWorks (本月)
curl -s "https://api.github.com/search/repositories?q=cadquery+OR+solidworks+created:>$(date -d '60 days ago' +%Y-%m-%d)&sort=stars&per_page=8" ...
```

### Step 3: 上游 marketingskills 对比
```bash
curl -s "https://api.github.com/repos/coreyhaines31/marketingskills/contents/skills" | python -c "
import json,sys
d=json.load(sys.stdin)
if isinstance(d, list):
    names = sorted([r['name'] for r in d])
    print(f'  官方 {len(names)} 个 skill')
    for n in names: print(f'    - {n}')
"
# 输出：49 个 vs 本地 49 个 → 完全对齐，无新增可装
```

### Step 4: Hermes latest release 对比
```bash
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" | python -c "
import json,sys
d=json.load(sys.stdin)
print(f'  tag: {d.get(\"tag_name\")} | 发布: {d.get(\"published_at\")[:10]}')
"
# ⚠️ cron 模式下不跑 hermes update（被沙箱拦 pattern_key: 'hermes update (restarts gateway, kills running agents)'）
```

### Step 5: 评估 + 装 superpowers 14 个
```bash
cd /tmp && mkdir -p superpowers-pull && cd superpowers-pull
SKILLS="brainstorming dispatching-parallel-agents executing-plans finishing-a-development-branch receiving-code-review requesting-code-review subagent-driven-development systematic-debugging test-driven-development using-git-worktrees using-superpowers verification-before-completion writing-plans writing-skills"
for s in $SKILLS; do
    curl -sL "https://raw.githubusercontent.com/obra/superpowers/main/skills/$s/SKILL.md" -o "$s.md"
done

# ⚠️ 必须用绝对路径，不要用 ~（heredoc 在 git-bash 下展开失败）
TARGET="/c/Users/Administrator/.codex/skills"
for s in $SKILLS; do
    mkdir -p "$TARGET/$s"
    cp "/tmp/superpowers-pull/$s.md" "$TARGET/$s/SKILL.md"
done

# 验收
ls "$TARGET" | grep -E "^(brainstorming|dispatching|...|writing-skills)$" | wc -l
# 应 = 14
```

### Step 6: 评估 + 装 sloptrim
```bash
cd /tmp && \
  curl -sL "https://raw.githubusercontent.com/seyedehsanhadi/sloptrim/main/SKILL.md" -o sloptrim-skill.md && \
  curl -sL "https://raw.githubusercontent.com/seyedehsanhadi/sloptrim/main/scripts/detect.py" -o sloptrim-detect.py

ls -la sloptrim-skill.md sloptrim-detect.py
# 必须非 0，否则重试（不能用 -o /tmp 绝对路径，路径失活）

TARGET="/c/Users/Administrator/.codex/skills/sloptrim"
mkdir -p "$TARGET/scripts"
cp /tmp/sloptrim-skill.md "$TARGET/SKILL.md"
cp /tmp/sloptrim-detect.py "$TARGET/scripts/detect.py"
chmod +x "$TARGET/scripts/detect.py"

# 验证：Windows 下不能用 python3
PY="/c/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
echo "测试 AI 套路话术..." | "$PY" "C:/Users/Administrator/.codex/skills/sloptrim/scripts/detect.py"
# 期望：JSON {"_metrics": {...}, "ai_tell_score": 0, ...}
```

### Step 7: 备份到 yuxin-skills
```bash
# ⚠️ 用 codex-skills/（dash），不是 codex/（slash）
# ⚠️ 同事的 hermes/scripts/codex_self_evolution.py 已经占 codex/，跟它零冲突
cd /c/Users/Administrator/Desktop/yuxin-skills

# 先 pull 远端（同事每小时 sync，可能有领先 commit）
GIT_TERMINAL_PROMPT=0 git pull --rebase origin main 2>&1 | tail -5

# 同步新装的 15 个 skill
for s in brainstorming dispatching-parallel-agents executing-plans finishing-a-development-branch receiving-code-review requesting-code-review subagent-driven-development systematic-debugging test-driven-development using-git-worktrees using-superpowers verification-before-completion writing-plans writing-skills sloptrim; do
    cp -r "/c/Users/Administrator/.codex/skills/$s" "codex-skills/"
done

# 更新 STATUS.md（同步数字 + 新装清单）

# ⚠️ 排除 .system/ 内置 skill（Codex 自动生成，不属于用户资产）
# ⚠️ 排除 cp -r 带过来的 .git 目录（embedded git repo warning）

git add codex-skills/
git commit -m "🤖 旺财进化 8-17: +15 skills (superpowers 14 + sloptrim 1) → codex-skills/"
# ⚠️ git push 失败：push declined due to repository rule violations
# 铁律：cron 不绕过，老大手动 push 或改 branch rule
```

### Step 8: 写日报
```bash
mkdir -p "/c/Users/Administrator/Desktop/知识库/进化日报"
# 路径含中文，echo heredoc 可能撞坑 → 用 write_file 工具最稳
```

### Step 9: 更新 memory
```bash
memory add "8-17 进化要点：..."
```

## 当日评估候选清单（10 个 GitHub Trending，按优先级）

| # | 项目 | ⭐ | 决策 | 理由 |
|---|---|---|---|---|
| 1 | obra/superpowers | 272k | ✅ 装 14 个 | 开发方法论黄金框架 |
| 2 | seyedehsanhadi/sloptrim | 148 | ✅ 装 1 个 | 去 AI 味 CLI，匹配小红书爆款刚需 |
| 3 | Vincentwei1021/video-shotcraft | 5231 | ⏸ 待装 | Remotion 短视频，渔芯视频号可用 |
| 4 | petergyang/human-review | 1022 | ⏸ 待装 | HTML/MD 视觉评审，渔芯页面可用 |
| 5 | lennney/stop-that-shit | 123 | ⏸ 待装 | Codex 行为约束器（防过度工程） |
| 6 | Leutenegger/book-to-skill | 1154 | ⏸ 待装 | PDF → Claude Code skill 转换器 |
| 7 | QoderAI/better-harness | 1867 | ❌ 跳过 | session evidence → loop insights，AGENTS.md 已替代 |
| 8 | makecindy/cindy | 2091 | ❌ 跳过 | 通用 AI Agent 平台，渔芯已有 Next.js |
| 9 | Prism-Shadow/penguin-harness | 1384 | ❌ 跳过 | "Harness for RSI / AI Build AI"，功能重复 |
| 10 | soumatheusgomes/vibe-coding-toolkit | 149 | ❌ 跳过 | Claude Code 插件集合，质量待验 |

## 下次 cron 待办（优先级）

1. **video-shotcraft**（⭐5231）— 渔芯视频号是空缺，必装
2. **human-review**（⭐1022）— 渔芯 Next.js 页面评审有用
3. **stop-that-shit**（⭐123）— Codex 行为约束器
4. **book-to-skill**（⭐1154）— 把水产业务的 PDF 书转 skill

## 踩坑清单（避免重犯）

1. **`~` 在 git-bash heredoc 不展开** → cp / mkdir 用绝对路径
2. **`curl -o /tmp/foo.md` 路径失活** → 先 `cd /tmp && curl -o foo.md`
3. **`#!/usr/bin/env python3` Windows 跑失败** → 用 venv python 绝对路径
4. **`ls ~/.codex/skills/ | wc -l` 漏 .system** → 用 `find` 排除 `.system/`
5. **`codex/` vs `codex-skills/`** → 同事占 codex/，我用 codex-skills/
6. **`push declined due to repository rule violations`** → cron 不绕过，本地 commit + 老大手动
7. **`hermes update` cron 模式被拦** → 不在 cron 跑，日报 P0 提示老大手动
8. **`marketingskills 49 个 vs 本地 49 个完全对齐** → 上游已无新增可装，找下一个源

## 4 个 cron 健康度（8-17 顺带报告）

| cron | job_id | 状态 |
|---|---|---|
| 6 点总结 | 4247b6d7d564 | ✅ |
| 6 点发笔记 | 0ccb49899a10 | ⚠️ 飞书 230002（AppSecret 待老大续） |
| 8 点爆款分析 | 1eb07ab303dc | ⚠️ 5 天无新报告 |
| 9 点简报 + RAG | 31287df0e40a | ⚠️ Token 限额 2056 |
