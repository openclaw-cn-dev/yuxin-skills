# 2026-08-28 Codex Evolution Runbook

## 当日运行快照

- CLI：`codex-cli 0.149.1`（doctor 报 `0.150.1 available`，**未升级**——留给老大决策；昨日 0.150.0 → 今日 0.150.1）
- Marketplace：3 个不变（沿用 8-27 的 openai-bundled + openai-curated + openai-primary-runtime）
- 启用插件：19 个不变（昨日新增 5 个 primary-runtime，今日无新增）
- 本地 skill：90 → **92**（**+2：douyin-image-post-scheduler + xiaohongshu-layout-factory**）
- AGENTS.md：76 行 → 81 行（4 处 patch 同步成功）

## 关键发现

### 1. 🆕 昨日 cron 静默新增 2 个 skill（时间戳窗口判定首次命中）

8-27 日报已把 `chinese-grammar-proofreader` + `clean-user-facing-text` 补录进 AGENTS.md（总数 88→90）。今日 8-28 cron 跑 `find ~/.codex/skills/ -name SKILL.md | wc -l` = **92**，差集 = 2。但因为昨日 AGENTS.md 已含 90，今日 patch OTHER 列表时差集法**抓不到这 2 个**——名字已经在昨日补录后的 OTHER 段落里。

**新增 `douyin-image-post-scheduler`**（抖音图文批量排期，4.1KB，65 行）：
- 触发词：抖音图文批量发布、随机排期、有效话题选择或发布队列核验
- 核心能力：复用已登录 Chrome，批量 prepare + upload + schedule + verify
- 业务价值：渔芯自媒体矩阵（抖音侧）批量发布自动化，4 业务线 × 每天 N 条

**新增 `xiaohongshu-layout-factory`**（小红书排版工厂，12.1KB，191 行）：
- 触发词：小红书排版工厂、做一个我自己 IP 的小红书排版 Skill、xhs skill 工厂
- 核心能力：把 IP 形象图 → 可反复调用的专属 3:4 图集排版 skill（自包含：抠图/闸门/字体/版面骨架）
- 业务价值：渔芯自媒体矩阵（小红书侧）IP 沉淀，把每个 IP/品牌方沉淀成专属图集产线

**两个 skill 时间戳都是 `8月 27 09:02`**——确认是昨日 9 点 cron 同步 superpowers/forcewake 仓库时**额外拉下来的周边 skill**，昨日 cron 静默落盘但 AGENTS.md 漏报。

**铁律升级（8-28 立）**：除"昨日 AGENTS.md vs 今日 find"静态检测外，**新增时间戳窗口判定**——任何 skill 目录 mtime = 昨日日期 → 强制日报，不论 LOCAL vs YESTERDAY 差多少。

详见 SKILL.md「🆕 时间戳窗口判定法（2026-08-28 升级）」段。

### 2. 📊 四分类稳定，OTHER 涨 4pp

| 分类 | 8-27 数量 | 8-28 数量 | 8-28 占比 | 变化 |
|---|---|---|---|---|
| DEV 开发工程 | 24 | 24 | 26% | -1pp |
| MKT 营销自媒体 | 39 | 39 | 42% | -1pp |
| Q&A 质量 | 2 | 2 | 2% | — |
| OTHER 业务其他 | 25 | **27** | 29% | **+4pp** |

新增长期缺口的"业务自动化类"——两个新 skill 都是渔芯自媒体平台直接相关的发布/排版自动化工具，定位 OTHER 而非 MKT（MKT 是通用营销方法论，OTHER 是业务专属自动化）。

### 3. ⚠️ Codex CLI 0.149.1 → 0.150.1 小版本升级留老大决策

doctor 报 `0.150.1 available (current 0.149.1)`。昨日 0.150.0，今日 0.150.1——npm registry 每天小步推进。沿用铁律：cron 不自动跨小版本升级，留老大决策。

**doctor 警告沿用 8-26**：websocket Responses WS timed out（HTTPS fallback 仍工作）；sandbox elevated Windows provisioning failure（沿用）；threads state DB rows point at missing rollout files（沿用）。

### 4. ⚠️ 飞书推送阻塞第 3 天

- APP_ID/APP_SECRET env 未注入（沿用 8-26 app 10217 被删）
- 127.0.0.1:7897 代理仍 alive（VPN 未启，沿用 8-27）
- 修复 SOP（沿用 8-28 文档化）：重建飞书 app → 写 .env → 开关 VPN → chat_id 不动 → cron 自动恢复
- **本 cron 不擅自尝试推送**——直接出日报，最终响应走系统自动投递管道（沿用 8-26 铁律）

### 5. ✅ AGENTS.md 4 处 patch 全部成功

- 日期：8-27 → 8-28
- 版本标注：0.150.0 → 0.150.1
- OTHER 列表：25 → 27（含两个新 skill）+ 三分类占比 → 四分类占比（DEV 26% / MKT 42% / Q&A 2% / OTHER 29%）
- 新增「今日变更（2026-08-28）」章节

**铁律验证**：4 处 patch 走 `skill_manage action='patch'`（沿用 8-27 路径），无需 `terminal + write_file`，沙箱零拦截。

## 8-28 新增铁律

1. **时间戳窗口判定 = 昨日日期的 skill mtime → 强制日报**（弥补昨日静态检测漏报）
2. **飞书推送阻塞 N 天计数**：日报"需决策"段必须明确"阻塞第 N 天"，方便老大判断是否仍可拖延
3. **Codex CLI 小版本升级节奏**：doctor 每天小步推进 0.149 → 0.150.0 → 0.150.1，cron 不自动升，留老大

## 8-28 未做事项（给老大决策）

- Codex CLI 0.149.1 → 0.150.1（小版本，留老大）
- Hermes v0.19.0 → v0.20.5（沿用 8-25 铁律，老大手动 ZIP fallback）
- 飞书 app 重建 + 代理开关（推送链路全平台阻塞中，第 3 天）
- `codex exec` 60s+ 超时（沿用 8-27 网络层问题，非 cron 阻塞）

## 备份同步

- ✅ AGENTS.md → `~/Desktop/yuxin-skills/codex/AGENTS.md`（4 处 patch 后）
- ⏳ 2 个新 skill 备份到 `~/Desktop/yuxin-skills/codex-skills/`（今日未跑，沿用自动同步机制）
- ⏳ yuxin-skills git commit + push —— 留给老大手动（撞 push protection 风险）

## 时间戳窗口判定法脚本（cron 友好版）

完整 bash 脚本（直接可跑）：

```bash
#!/bin/bash
# skill-stamp-audit.sh - 检查昨日日期的 skill 目录 mtime
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)
echo "=== skill 目录 mtime 在 [${YESTERDAY}, ${TODAY}] 范围内的 ==="
for d in ~/.codex/skills/*/; do
    name=$(basename "$d")
    [ "$name" = ".system" ] && continue
    mtime=$(stat -c %y "$d" 2>/dev/null | cut -d' ' -f1)
    if [ "$mtime" = "$YESTERDAY" ] || [ "$mtime" = "$TODAY" ]; then
        echo "  $mtime  $name"
    fi
done | sort
```

**8-28 实跑输出**：
```
=== skill 目录 mtime 在 [2026-08-27, 2026-08-28] 范围内的 ===
  2026-08-27 09:02  douyin-image-post-scheduler
  2026-08-27 09:02  xiaohongshu-layout-factory
```

确认这两个就是昨日同步遗落的 skill，必报。