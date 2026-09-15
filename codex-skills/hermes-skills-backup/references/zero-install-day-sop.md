# 0 装日 SOP（2026-08-30 立）+ Hermes 上游监控 + AGENTS.md 完整 patch 模式

## 1. 0 装日 SOP（5 维 trending 全跑，3 候选不适配，0 装）

**判定**：5 维 trending 搜索跑完，3+ 候选全不适配 → 日报**必须显式列**所有候选 + 不适配原因。0 装 ≠ 偷懒，是业务线驱动 vs trending 驱动的差。

**日报固定 3 段**：
1. 「5 候选评估」表格：name | stars | 决定 | 原因（4 列）
2. 「已装 skill 涨星」：当周 trending 榜里命中本地已装 skill → 列出涨前→涨后（如 sepia 362→659⭐）
3. 「上游信号」：Hermes / Codex CLI 落后版本 + 上游 release 日期 + 待老大决策

**clone + 30 秒评估模板**：
```bash
cd /c/Users/Administrator/Desktop/eval-repos
git clone --depth 1 git@github.com:OWNER/REPO.git 2>&1 | tail -3
head -30 REPO/SKILL.md   # 看 description + 触发条件
ls REPO/                  # 看 mono-repo vs multi-agent vs 单 skill
```

**5 类必拒候选**（老大 4 业务线 + 渔芯 + 求职）：
| 候选类型 | 必拒原因 |
|---|---|
| 要 ChatGPT/OpenAI 账号 | 老大用 DeepSeek/MiniMax 中转，无海外账号（931⭐ codex-with-chatgpt 实测拒） |
| 韩文 / 小语种 SKILL.md | 老大不懂 + 翻译成本 > 收益 |
| SEO / GEO / AEO 路线 | 老大 SEO 暂未投 + 已有 `seo-audit` 覆盖 |
| 摄影集 / 3D 翻页 / 视觉工具 | 水产图文 + 数据看板用不到 |
| 跨平台不兼容 | Windows 跑不起来（macOS-only / Linux-only） |

**8-30 实战 3 拒**：
- `XiaoDuoYa/codex-with-chatgpt` 931⭐ → 拒（要 ChatGPT OAuth）
- `leopard627/fire-your-seo-agency` 343⭐ → 拒（韩文 + SEO 路线）
- `HaichaoLihc/create-photo-flipbook-ui` 124⭐ → 拒（摄影集 3D 翻页）

**🆕 第 6 类必拒候选（9-01 立）**：
| 候选类型 | 必拒原因 |
|---|---|
| **线下展会/活动营销类** | `events`（活动营销：webinar/会议/展会/晚宴/dinner）→ 老大 4 业务线（美食/养殖/设备/公司）**不涉大型线下展会** + `co-marketing` 已覆盖。9-01 实测拒 `coreyhaines31/marketingskills/events` 1.0.0（远端 50 vs 本地 38 唯一新增） |
| **装协议不匹配** | `nextlevelbuilder/ui-ux-pro-max-skill` 123544⭐ → 装协议是 `npx ui-ux-pro-max-cli init --ai <platform>`（CLI install pattern），不是 `cp SKILL.md`。Codex 装载协议 = 完整 SKILL.md 子树 → **不兼容**。仅观察 |
| **封装型 UI 设计类（与已有重叠）** | 同 `nextlevelbuilder` / 各种 ui-ux-* / `refactoring-ui` 之类 → 与已装 `refactoring-ui` 448⭐ 重叠，**不重复装** |

**🆕 母仓 diff 路径（9-01 立，弥补 5 维 trending 漏掉的「母仓内容增量」）**：

**症状**：8-30 SOP 只查 GitHub trending 7 日榜，**漏掉母仓（marketingskills / social-media-skills）的新增 skill**。9-01 实测 `coreyhaines31/marketingskills` 50 个 vs 本地 38 个 = 8 个未装候选，光靠 trending 搜不到。

**修法（cron Step 2.5 必跑，30 秒）**：

```bash
mkdir -p /c/Users/Administrator/Desktop/eval-repos/{mkt-dist,sms-dist}
# 1) SSH clone（沿用 0831 铁律：git-bash SSH 一开始就跑通，HTTPS 必 Connection reset）
cd /c/Users/Administrator/Desktop/eval-repos/mkt-dist && \
  git clone --depth 1 git@github.com:coreyhaines31/marketingskills.git coreyhaines31-marketingskills 2>&1 | tail -3
cd /c/Users/Administrator/Desktop/eval-repos/sms-dist && \
  git clone --depth 1 git@github.com:blacktwist/social-media-skills.git blacktwist-social-media-skills 2>&1 | tail -3

# 2) diff 找本地未装
LOCAL=$(ls /c/Users/Administrator/.codex/skills/ | sort)
REMOTE_MKT=$(ls /c/Users/Administrator/Desktop/eval-repos/mkt-dist/coreyhaines31-marketingskills/skills/ | sort)
REMOTE_SMS=$(ls /c/Users/Administrator/Desktop/eval-repos/sms-dist/blacktwist-social-media-skills/skills/ | sort)

echo "=== 市场类新候选 ==="
comm -13 <(echo "$LOCAL") <(echo "$REMOTE_MKT")
echo "=== sms 新候选 ==="
comm -13 <(echo "$LOCAL") <(echo "$REMOTE_SMS")
```

**判定矩阵**：
| diff 结果 | 决策 |
|---|---|
| 远端新候选 ≥ 1 → 全在已知不装清单（aso/paywalls/popups/signup/site-architecture/directory-submissions/sms 0829 立） | 0 装 + 日报显式列「8 候选在已知不装」 |
| 远端新候选有未在已知清单里的（如 `events` 9-01） | 评估：业务线匹配？装协议兼容？→ 装 / 不装 / 仅观察 |
| 远端 = 本地（完全同步） | 0 装 + 日报写「X 仓远端 N = 本地 N 完全同步」 |

**9-01 实测**：
- `social-media-skills` 远端 14 = 本地 14 **完全同步**（0829 装的 14 个仍最新，0 增量）
- `marketingskills` 远端 50 vs 本地 38 → 8 候选 = `aso / directory-submissions / events / paywalls / popups / signup / site-architecture / sms`
- **7 个在已知不装**（0829 立），**1 个新增**（`events` 9-01 评估拒）

**铁律**：
- ✅ 0 装日 cron Step 2.5 必跑母仓 diff（不是只看 trending）
- ✅ SSH `git clone --depth 1`（沿用 0831 + 8-24 铁律：git-bash SSH 一开始就跑通）
- ✅ 必放 `~/Desktop/eval-repos/`（不是 `/tmp`，护栏挡）
- ✅ 已知不装清单 = 0829 立 7 项（aso/paywalls/popups/signup/site-architecture/directory-submissions/sms）+ 9-01 立 3 项（线下展会/装协议不匹配/UI 重叠）
- ✅ diff 出的新候选必须**逐项评估**业务线 + 装协议 → 不一律拒
- ❌ 不因为「diff 有 N 个就装」——逐项评估
- ❌ 不漏跑 diff（0829 装 14 个 = 当时已全同步；下次同步有差异才报）

**铁律**：
- 0 装日日报首段必写明「5 维全跑，3 候选不适配，0 装」
- 涨星追踪 ≠ 新装，但日报里必报（老大看 Codex 桌面时要知道已装 skill 在生态里的相对位置）
- 每个候选 clone 后必读 SKILL.md 头 30 行（不只靠 README 描述）
- 不因为「老大的业务线没人提过 X」就跳过 trending X 维（5 维都跑才能保证零盲点）
- 不因为「本周 X 维 trending 0 结果」就跳过 cron（**显式报 0 结果**，跟「漏跑」区分）
- 不因为「母仓上次同步过」就跳过本次 diff（母仓可能在 cron 间歇期新增 skill）

---

## 2. 已装 skill 涨星追踪

**判定**：当周 GitHub trending 7 日榜里出现**已经在本地 `~/.codex/skills/` 装过的同名同 repo** → 不是新装，是涨星追踪。

**强信号 grep**：
```bash
# 抓 trending 命中本地的 skill（必须 description 字段含 SKILL.md 同指纹）
for repo in $(curl -s "https://api.github.com/search/repositories?q=claude-skill+OR+codex-skill+created:>2026-08-23+stars:>50+sort:stars&per_page=20" \
  | python -c "import json,sys;[print(r['full_name']) for r in json.load(sys.stdin).get('items',[])]"); do
  name=$(basename $repo)
  [ -d "/c/Users/Administrator/.codex/skills/$name" ] && echo "$repo → 已装涨星"
done
```

**8-30 涨星追踪实测**：
- `sepia` 362→659⭐（Nanako0129/sepia 7 日榜稳）
- `refactoring-ui` 395→419⭐（s0xDk/refactoring-ui-skill）
- `simplify-codebase` 319→345⭐（tt-a1i/simplify-codebase）

**铁律**：
- 涨星追踪在「5 候选评估」表外单列「已装 skill 涨星」段（避免跟新装混淆）
- 涨前数字从昨日 AGENTS.md「今日变更」节抓（如有）
- 第一次见某 repo 涨星 = 必报（即使 0 装也说明生态在动）

---

## 3. Hermes 上游 release 周期监控

**判定**：Hermes 上游**落后 ≥ 3 minor 版本** + 上游近 7 日有新 release → 日报「待决策」段首条 P0。

**检测脚本（1 行）**：
```bash
curl -s -L "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" \
  | python -c "import json,sys;d=json.load(sys.stdin);print(d.get('tag_name','?'),d.get('published_at','?')[:10])"
```

**判定矩阵**：
| 本地版本 | 上游最新 | release 日期差 | 决策 |
|---|---|---|---|
| 落后 < 3 minor | - | - | 不报 |
| 落后 ≥ 3 minor | 上游 < 7 日新 release | < 7 天 | **P0 待决策**（老大前台 `hermes update`） |
| 落后 ≥ 3 minor | 上游 ≥ 7 日旧 release | ≥ 7 天 | P1 提醒（等周报再说） |
| 落后 ≥ 5 minor | 任意 | 任意 | **P0** + 日报首条强提示（5 个 minor = 上游半年没同步） |

**8-30 实测**：本地 `v0.19.0`（2026-07-20）→ 上游 `v2026.8.27`（8-27 发布）→ **落后 5 minor + 3 天** → 列入 P0。

**铁律**：
- `vYYYY.M.D` tag 格式（上游新版）+ `v0.X.Y` 格式（本地旧版）→ minor 比较看月份差
- cron **不自动升级**（沿用老铁律：`hermes update` 在 cron 重启 gateway 杀进程）
- 日报写「本地 X → 上游 Y（Z 天前发布）」，**不**只写「落后」
- 不因为「落后但功能稳定」就不报（老大可能想跟上游安全 advisory）

---

## 4. AGENTS.md 完整 patch 模式（弥补 8-29 跳过模式盲点）

**症状**：cron 启动第一步 grep AGENTS.md，发现「今日变更（YYYY-MM-DD）」节**不存在**（昨日 cron 没写，或昨日是 0 装日没动）。**不能**只 patch 改日期（8-29 跳过模式），**必须**完整追加新节。

**判定（启动第一步，2 个 grep + 1 个比较）**：
```bash
# 1) 看最后更新时间（应是昨日或更早）
head -5 ~/.codex/AGENTS.md | grep "最后更新"

# 2) 看今日变更节是否存在
grep -c "## 今日变更（$(date +%Y-%m-%d)" ~/.codex/AGENTS.md
# 0 = 不存在 → 走完整 patch 模式（追加新节）
# 1 = 已存在 → 8-29 跳过模式（只验证）

# 3) 真实状态 vs AGENTS.md 文字声明是否一致（信 fs）
LOCAL=$(find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l)
YESTERDAY=$(grep -oE 'Skills 总览（[0-9]+' ~/.codex/AGENTS.md | grep -oE '[0-9]+')
[ "$LOCAL" -ne "$YESTERDAY" ] && echo "DRIFT" || echo "OK"
```

**完整 patch 模式（今日变更节不存在时）**：

```python
# old_string 必须锚定"最后一个今日变更节标题 + 节内首行"
# new_string 必须是 "新节标题 + 新节内容 + 旧节标题 + 旧节首行"
old_string = """## 今日变更（2026-08-29）

1. ✅ **新增 3 个本地 skill**"""

new_string = """## 今日变更（2026-08-30）

1. ✅ **0 装日**（3 候选全不适配）
2. ℹ️ 已装 skill 涨星追踪...
...

## 今日变更（2026-08-29）

1. ✅ **新增 3 个本地 skill**"""
```

**铁律（8-30 立）**：
- 启动第一步 = `grep -c` 判定（不是「想当然」看 AGENTS.md 头 5 行）
- 今日变更节不存在 → 走完整 patch（旧节标题 + 旧节首行作 old_string 锚点）
- 今日变更节已存在 + LOCAL == YESTERDAY → 走 8-29 跳过模式（只验证不重写）
- 今日变更节已存在 + LOCAL ≠ YESTERDAY → drift，patch 在现有节末尾**追加**新行（不重建节）
- 不要「日期虽然不一致但好像没问题」就跳过 patch（drift 会累积成永久性失真）
- 不要只 patch 改日期（不更新节内容）——AGENTS.md 文字声明必须反映当日真实状态

**关联**：跟 8-29「cron AGENTS.md 已含今日日期 → 跳过重写」互补——8-29 模式是「节已存在 + 一致」，8-30 模式是「节不存在 / 节存在但 drift」。

---

## 8-30 cron runbook 速查（与 SKILL.md 8-29 runbook 配套）

| 步骤 | 命令 / 动作 | 期望 |
|---|---|---|
| Step 0 | `date "+%Y-%m-%d %A"` | 2026-08-30 星期日 |
| Step 0b | `head -5 ~/.codex/AGENTS.md \| grep 最后更新` + `grep -c "## 今日变更（$(date +%Y-%m-%d)"` | 判定走「跳过模式」还是「完整 patch 模式」 |
| Step 1 | `codex --version` + `codex plugin list` + `find ~/.codex/skills -name SKILL.md \| wc -l` | 三件套基线（不跑 doctor，超时不算失败） |
| Step 2 | 5 维 GitHub API trending（ai-agents / claude-skill+codex-skill+mcp / xhs+douyin+social / cad+solidworks / crm+sales） | 5 个 curl 全跑，**0 结果也要显式报** |
| Step 3 | 评估候选 → 装 / 不装 / 涨星追踪 / 弃 | 装：clone + diff + cp 到 ~/.codex/skills + cp 到 yuxin-skills/codex-skills + git commit |
| Step 4 | Hermes 上游版本检查 + Codex CLI available 版本 | 落后 ≥ 3 minor → P0 报老大 |
| Step 5 | patch AGENTS.md（按 Step 0b 判定走哪条路径） | 完整 patch / 跳过模式二选一 |
| Step 6 | `cd /c/.../yuxin-skills && git add + commit` | commit 不 push（沿用 secret-scanner 铁律） |
| Step 7 | 写日报到 `C:\Users\Administrator\Desktop\知识库\进化日报\YYYY-MM-DD_旺财进化.md` | 4 段：Codex / Hermes / 新发现 / 需决策 |
| Step 8 | final response 兜底（飞书 10217 阻塞第 5 天） | 不调 hermes send，直接 final response |

**8-30 完整时序**：
- 09:00:58 cron 启动
- 09:01:00 AGENTS.md patch（节不存在 → 完整 patch 模式）
- 09:01:30 5 维 trending 全跑完
- 09:01:45 3 候选 clone + 评估
- 09:02:00 决策完成：0 装
- 09:02:15 yuxin-skills commit `ef970ce`
- 09:02:30 日报写完 + final response
