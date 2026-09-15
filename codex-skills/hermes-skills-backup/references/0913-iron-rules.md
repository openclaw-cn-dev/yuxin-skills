# 0913 cron 实测三条新铁律（Skill 形态判定 / Hermes 升级阈值 / 涨星异常阈值）

**来源**：2026-09-13 9:00 cron 实跑，0 装日（第 12 次）但 5 维搜索发现 3 个高星候选均**不是 Codex skill 形态**，避免误装浪费 30 分钟；同时发现 Hermes 落后 53 天未报 P1（沿用 0829 阈值不够严）+ sepia 单日涨星 +5766⭐（异常阈值未定义）。

---

## 铁律 15：5 维搜索高星候选 = **先验形态**再评内容（SKILL.md 404 = 直接拒装）

**症状（0913 实测踩坑）**：

5 维 Dim2 搜索返 3 个高星候选，看起来都跟 4 业务线沾边：

| 候选 | ⭐ | 表面看 | 实测形态 |
|---|---|---|---|
| soirihiroka/shrimply | 1014 | "shrimp 短视频"，水产爆款 | Rust 工具 + GPL-3.0 + 非 skill |
| nateherkai/scroll-craft | 2370 | 长滚动网页，**Codex skill** | **SKILL.md 404**，files 是 `.claude-plugin/ + plugins/` |
| HanyuanWang/LiveStream-Agent-Studio | 1018 | 抖音直播电商，养殖群需求 | **SKILL.md 404**，files 是 `liveagent-studio/ + live_*_agent/` |

如果按"看起来跟业务沾边 + 高星"草率决定 → 浪费 30 分钟克隆 + diff + 检查，看完才发现是 CLI 工具 / .claude-plugin 不是 Codex skill。

**根因**：

- GitHub trending 维度里"agent skill"关键词被滥用（任何标 "agent" 的 CLI 工具都进结果）
- Codex skill 形态 = **根目录有 `SKILL.md`**（含 YAML frontmatter `name` + `description`）
- Claude Code 形态 = `.claude-plugin/<name>.json` 或 `plugins/` 目录
- 普通 CLI 工具 = `bin/` + `README.md` + `setup.py` 等

**形态判定 3 步法（0913 立，先验后评）**：

```bash
# 1. 直接 GET SKILL.md — 200 = 真 skill，404 = 非 skill
curl -sL -o /dev/null -w "%{http_code}\n" \
  "https://raw.githubusercontent.com/<owner>/<repo>/main/SKILL.md"
# 期望 200；404/403 = 直接拒装

# 2. 兜底查分支（main / master / README 命 SKILL.md）
for branch in main master; do
  code=$(curl -sL -o /dev/null -w "%{http_code}" \
    "https://raw.githubusercontent.com/<owner>/<repo>/${branch}/SKILL.md")
  [ "$code" = "200" ] && echo "Found SKILL.md on $branch" && break
done

# 3. 看 repo 根目录是否有 SKILL.md（API）
curl -sL "https://api.github.com/repos/<owner>/<repo>/contents/" | \
  python -c "import json,sys; d=json.load(sys.stdin); \
    print('SKILL.md found' if any(x['name']=='SKILL.md' for x in d if isinstance(d,list)) else 'NO SKILL.md')"
```

**铁律（0913 立）**：

- ✅ **任何 5 维搜索的高星候选，第一步 = 验 SKILL.md 是否存在**（404 / 403 → 直接拒装）
- ✅ **三档分类决策矩阵**：
  - SKILL.md 200 + YAML frontmatter 合规 + 4 业务线命中 → **正常评估**
  - SKILL.md 404 但有 `.claude-plugin/` 或 `plugins/` → **拒装**（沿用 0912 铁律 10 CLAUDE.md-only 拒装模式）
  - SKILL.md 404 + 仅 `bin/` + `setup.py` 等 → **拒装**（普通 CLI 工具）
- ✅ **license 同时检查**（GPL-3.0 / AGPL 不进 yuxin-skills 商业仓）
- ❌ 不要按"看起来沾边 + 高星"草率决定
- ❌ 不要直接 `git clone` 整库再判（浪费 30+ 秒）
- ❌ 不要因为 star ≥1000 就预判是 skill

**反模式**：

- ❌ "shrimply = 1014⭐ + 描述含 shrimp → 应该有用" → 实测是 Rust 短视频生成器
- ❌ "scroll-craft = 2370⭐ + agent skill for ... → 必装" → 实测 SKILL.md 404
- ❌ "LiveStream = 1018⭐ + 抖音直播 → 养殖群命中" → 实测是 Windows 本地 CLI 工具

---

## 铁律 16：Hermes 升级阈值 = 跨 ≥2 minor + ≥30 天 = P1（0913 加严）

**症状（0913 实测发现）**：

- 本机 Hermes：`v0.19.0 (2026.7.20)`
- 远端 latest：`v2026.9.11 = v0.21.2 (2026-09-11)`
- **落后 53 天 / 2 个 minor version**

沿用 0829 铁律「Codex CLI wrapper 升级留老大决策」只关注 Codex，**Hermes 没独立阈值**，导致 53 天落后未报 P1。

**与 Codex CLI 阈值的区别**：

| 系统 | 升级阈值（0913） | 理由 |
|---|---|---|
| Codex CLI wrapper | 跨 ≥2 minor + ≥30 天 = P1（**待定**，0913 待老大确认沿用 0829） | CLI 是 npm 全局装，cron 不动 wrapper |
| **Hermes 本体** | **跨 ≥2 minor + ≥30 天 = P1（0913 立）** | Hermes 是 cron 的 root，落后太多影响 gateway / cron 调度 |
| Codex 桌面 catalog | 跨 ≥2 minor + stale ≥30 天 = P1（沿用 0912 铁律 13） | 桌面是 GUI 应用 |

**铁律（0913 立）**：

- ✅ **Hermes 升级检查 cron 必须必跑**：
  ```bash
  CURRENT=$(hermes --version 2>&1 | grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
  LATEST=$(curl -sL "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" | \
    python -c "import json,sys; print(json.load(sys.stdin).get('tag_name','?'))")
  echo "Hermes: $CURRENT → $LATEST"
  ```
- ✅ **判定矩阵**：
  - 差 ≤1 minor 或落后 <30 天 → 不报（沿用 0911 Codex CLI 铁律）
  - **差 ≥2 minor 且落后 ≥30 天 → 报 P1**（0913 立，**比 Codex CLI 更严**）
  - 差 ≥3 minor 或破 major → 报 P0
- ✅ **`hermes update` 不在 cron 跑**（沿用 8-12 铁律 hermes.exe 锁死）
- ✅ **日报「需老大决策」段必报 P1**，cron 不擅自 force-update
- ❌ 不要只看 Codex CLI wrapper（0913 实测 Hermes 落后 53 天未发现 = Hermes 独立检查缺失）
- ❌ 不要把 Hermes 跟 Codex CLI 升级阈值混用（两者独立）

**0913 cron 决策**：

- Hermes v0.19.0 → v0.21.2，差 2 minor + 53 天 → **报 P1 给老大决策是否升级**
- 老大决策方式：前台手动跑 `hermes update`，走 ZIP fallback（沿用 8-12）
- 不擅自 force-update（避免 hermes.exe 锁死）

---

## 铁律 17：涨星追踪异常阈值 = 单日涨幅 ≥5x 历史均值 = 异常信号

**症状（0913 实测触发）**：

涨星追踪 10 个 skill：

| skill | 0912 stars | 0913 stars | 单日涨幅 | 历史均值（0912→0913） | 异常？ |
|---|---|---|---|---|---|
| image-prompt-reverse | 365 | 365 | 0 | 1x | 否 |
| seo-landing | 221 | 221 | 0 | 1x | 否 |
| sepia | **1875** | **7641** | **+5766** | **4.07x** | ⚠️ **是（**超 5x 阈值**）** |
| autoprompt | 3019 | 3019 | 0 | 1x | 否 |
| ai-seo | 49825 | 49825 | 0 | 1x | 否 |
| ab-testing | 39762 | 39762 | 0 | 1x | 否 |
| attribution | 24737 | 24737 | 0 | 1x | 否 |
| offers | 42842 | 42842 | 0 | 1x | 否 |
| pricing | 33852 | 33852 | 0 | 1x | 否 |
| programmatic-seo | N/A | N/A | - | - | - |

**sepia 单日 +5766⭐（4.07x 涨幅）异常触发**。

沿用 0908 涨星追踪 SOP「涨速 ≥50⭐/7d + version 跳 + diff 实质内容三件齐才升级」**没有单日阈值**，导致 sepia 这种 4 倍跳涨没自动标"异常"。

**铁律（0913 立）**：

- ✅ **涨星追踪 cron 加异常阈值判定**：
  - 单日涨幅 ≥**5x** 历史 7 天均值 → ⚠️ 异常
  - 单日涨幅 ≥**10x** → 🔴 严重异常（可能是 GitHub 误报 / bot 关注）
  - 单日绝对涨幅 ≥**+5000⭐** → ⚠️ 异常（**与倍数并列触发**）
- ✅ **异常时 cron 触发「三件齐」预审**（沿用 0908 SOP）：
  - ① 涨速 ✅（异常已满足）
  - ② version 跳 → `curl https://api.github.com/repos/<owner>/<repo>/releases/latest` 看 version 字段
  - ③ diff 实质内容 → `git clone` 浅拉 + `git log -p` 看 SKILL.md 是否真有内容更新
- ✅ **日报「需老大决策」段标"⚠️ sepia 异常 +5766⭐"**，cron 不擅自升级
- ❌ **三件齐**才升级（沿用 0908）
- ❌ 不要因为单日涨幅大就装（避免 GitHub 数据污染）
- ❌ 不要把"涨星异常"当"涨星合格"（0908 SOP 升级条件 = 三件齐，异常只是触发预审）

**0913 cron 决策**：

- sepia 单日 +5766⭐（4.07x）→ **报 P1 给老大查 version + diff**
- 老大决策方式：查 mob-sakai/UIEEffect 最新 release + 看 SKILL.md diff
- 不擅自升级（0908 SOP 三件齐，缺 ②③）

---

## 0913 cron 实操决策汇总

1. **0 装日（第 12 次）**：5 维搜索 0 命中 4 业务线，沿用 0911+0912 拒装铁律
2. **AGENTS.md patch 2 处**：
   - ① 时间戳 `0912 09:08` → `0913 09:02`
   - ② 头部说明加「Hermes 落后 53 天 P1 / sepia 涨星异常 / 飞书阻塞第 16 天」
3. **日报落盘**：`知识库/进化日报/2026-09-13_旺财进化.md`（5.9KB / 93 行）
4. **飞书推送阻塞第 16 天**（沿用 0827 起）：走 final response 兜底
5. **Hermes 升级 P1 报老大**：v0.19.0 → v0.21.2 落后 53 天（沿用 0913 新立铁律 16）
6. **sepia 涨星异常 P1 报老大**：+5766⭐（沿用 0913 新立铁律 17）
7. **Codex CLI 落后 1 minor**（沿用 0911 铁律 ≤1 不报 P1，**今天沿用**）

---

## 关联

- 铁律 12（0912 立）：git-bash `comm` / `diff` stdin EOF bug → 一律 Python set + `~/Desktop/eval-repos/` — 见 `references/0912-0913-iron-rules.md`
- 铁律 13（0912 立）：Codex 桌面 `version.json` 双口径独立校验 + 30 天 stale 阈值 — 见 `references/0912-0913-iron-rules.md`
- 铁律 14（0912 立）：MKT 实算列表每次 cron 重跑 4 grep + 反向减集 — 见 `references/0912-0913-iron-rules.md`
- 铁律 11（0912 立）：Override 兄弟 cron 0 装日 — 见 `references/0912-iron-rules.md`
- 铁律 10（0912 立）：CLAUDE.md-only 拒装模式 — 见 `references/0912-iron-rules.md`
- 铁律 9（0912 立）：awesome-list 30 秒评估法 — 见 `references/0912-iron-rules.md`
- 铁律 7（0911 立）：CLI minor 升级阈值 ≤1 minor 不报 P1 — 见 `references/0911-iron-rules.md`
- 铁律 8（0911 立）：MKT 多重 exclude 实算 — 见 `references/0911-iron-rules.md`
- 0908 涨星追踪 SOP「三件齐才升级」 — 见 `references/cross-class-recategorization-iron-rules.md`
- 0829 铁律（沿用）：Codex CLI wrapper 升级留老大决策（**0913 升级为 Hermes 也走老大决策**）
- 0827 铁律（沿用）：飞书推送阻塞 + deliver=local 兜底
- 0820 铁律（沿用）：yuxin-skills push 前必跑 secrets scan

---

## 反模式（0913 加固）

- ❌ 5 维搜索高星候选草率决定（铁律 15）
- ❌ 直接 `git clone` 整库再判形态（铁律 15，浪费 30+ 秒）
- ❌ "star ≥1000 = 应该是 skill"（铁律 15）
- ❌ GPL-3.0 / AGPL skill 进 yuxin-skills 商业仓（铁律 15 + 0820 兼容）
- ❌ 把 Hermes 跟 Codex CLI 升级阈值混用（铁律 16）
- ❌ 单日涨星异常未触发预审就升级（铁律 17）
- ❌ 三件齐缺 ② 或 ③ 就装（沿用 0908 SOP）