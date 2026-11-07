# 9 点 Cron — Skills 调研 + Hermes 更新检查（实战参考）

**对应主 SKILL.md 第 4 节「4️⃣ 9 点 B」**。本参考记录实跑中总结的**机械流程 + 版本检查 triplet**，下次 9 点 cron 直接复制使用。

## 一、Skills 调研流程（5 步机械执行）

### Step 1：8 个 GitHub 主题搜索

```bash
# 每个主题一组：topic + 50+ stars + 30 天内 commit + per_page=3
# ⚠️ 限流警告：单 IP 未鉴权每小时 60 次请求（search + repos），多主题并发搜索会立刻撞 403
# 建议：每个 cron 跑 3-4 个主题 + 时间错开（10 分钟后再跑下一批）
for topic in "hermes-agent" "ai-agents" "stable-diffusion" "xiaohongshu" \
             "douyin" "aquaculture" "feishu-bot" "ras"; do
  curl -s "https://api.github.com/search/repositories?q=topic:$topic+stars:>50+pushed:>2026-05-21&sort=stars&order=desc&per_page=3" \
    | python -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('items', [])[:3]:
    print(f\"  ⭐ {r['stargazers_count']} | {r['full_name']} | pushed: {r['pushed_at'][:10]}\")
    print(f\"     desc: {(r.get('description') or '')[:100]}\")
"
done
```

### Step 2：过滤标准（硬规则）

✅ 候选必须满足**全部 3 条**：
1. `stargazers_count >= 50`
2. `pushed_at` 在最近 30 天内
3. 有 README（README 不存在的 repo：去 `r['full_name']` 看主页确认）

❌ 不收：
- 巨型主流项目（ComfyUI / Hermes 自身 / langchain）— 已经知道，浪费卡片位
- 与工作方向无关的（mc 钓鱼 mod、Rust 编译器等）— 即使 stars 高也不收

### Step 3：每天上限 + 推荐过滤

- **每天 3-5 个候选**（飞书卡片 ≤ 800 字约束）
- **推荐安装只挑 1-2 个** — 老大阅读疲劳点
- **水产/RAS 主题**：经常 0 候选（基本是 mc mod 或学术项目）— 写"无候选"段，不空着

### Step 4：判断"对老大工作有用"

老大工作 = **水产自媒体（小红书爆款 + 抖音脚本 + 知识库 + 公司档 + 设备图）+ AI 工程师（生图/SD 跑通/技能杠杆）**

候选按匹配度排序：
1. 直接给产能 / 数据源（小红书爆款、抖音脚本、SD 工作流）— 最优先
2. 给多 Agent 编排 / 飞书机器人基建 — 次优先
3. 通用 AI 工具 — 最后

## 二、Hermes 版本检查 Triplet（关键）

**核心问题**：GitHub 的 `releases/latest` tag 可能**远落后于 main branch**。光看 tag 报"最新"会错过中间几十个 commit 的新功能。

**3 步必跑**（缺一不可）：

### A. 本地版本 + CLI 自检

```bash
pip show hermes-agent 2>/dev/null | grep -i version
hermes --version 2>/dev/null
# 输出例：Hermes Agent v0.17.0 (2026.6.19) · upstream 857d0244
#        Update available: 55 commits behind — run 'hermes update'
```

CLI 自带的 "X commits behind" 数字**算的是 git fetch origin/main 后的差值**（本地分支 vs origin/main）。**这个数字比 release tag 准**。

### B. GitHub release tag

```bash
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | grep '"tag_name"'
# 输出例："tag_name": "v2026.6.19"
```

### C. **GitHub main HEAD vs 本地 commit**（**这是关键三角**）

```bash
cd "C:\Users\Administrator\AppData\Local\hermes\hermes-agent"
git fetch origin main 2>&1 | tail -3
echo "origin/main:" $(git rev-parse origin/main)
echo "local HEAD :" $(git rev-parse HEAD)
git status | grep -E "behind|ahead"
```

### 三种状态判定（卡片直接抄）

| 状态 | 判定条件 | 卡片用语 |
|---|---|---|
| ✅ 最新 | `releases/latest` tag 与本地 commit 描述一致 + git 报 "up to date" | `✅ 最新，无需更新` |
| ⚠️ 落后 X 个 commit | git 报 "behind 'origin/main' by X commits"，X ≤ 200 | `⚠️ 落后 X commits，建议更新` |
| ❌ 落后 / 弃用 | 本地版本号比 latest tag 旧 + git 报 fast-forward 不可用 / 冲突 | `❌ 当前版本已弃用，必须升级` |

**本会话（2026-06-21）实测**：
- 本地：`v0.17.0`（commit `857d0244`）
- release tag：`v2026.6.19`（与本地版本号一致）
- **origin/main HEAD**：`2213ea9fa73a`（与本地差 55 commits）
- 结论：**⚠️ 落后 55 commits**（虽然版本号相同，main 上有未发布新功能）

## 三、飞书卡片模板（800 字上限）

```
🛠️ 9 点 Skills 调研 - {YYYY-MM-DD}

🆕 今天找到的 skills（3-5 个）
1. {仓库名} - {一句话} | ⭐ {stars} | {commit 时间}
2. ...
（水产/RAS 主题如无候选：写"⚠️ 无 30 天内活跃候选"，不空着）

🤖 Hermes 更新检查
- 当前版本：{本地 vX.Y.Z}
- 最新 release：{tag}
- main HEAD vs 本地：{N} commits 差距
- 状态：✅ / ⚠️ / ❌
- 操作：{hermes update / 手跑 / 跳过}

🎯 推荐安装（1-2 个）
- {仓库名} - {对老大工作的帮助}
- 等待老大批准后小弟立刻装
```

## 四、本会话踩过的坑（避免下次再撞）

1. **GitHub API 限流**：8 个主题并发搜，第 5 个开始 403 rate limit。
   - **应对**：分批跑（每批 3-4 个）+ 间隔 60s；或加 `Authorization: Bearer $GH_TOKEN`（如果有 token 的话）。

2. **`compare` API 反直觉**：
   - `compare/v_tag...HEAD` 返回 `behind_by: 0, status: ahead` 是因为 release tag 落后于 main。
   - **正确做法**：直接 `git fetch + git status`，不用 `compare` API。

3. **`robots.txt` 阻止了 `github.com/topics/*` 页面的 fetch**：
   - mcp_fetch_fetch 抓 GitHub topic 页全返 robots.txt 错误。
   - **正确做法**：GitHub 搜索只走 `api.github.com/search/repositories`，**不走** `github.com/topics/*` 页面。

4. **水产/RAS 主题频繁 0 候选**：GitHub 上这两个 topic 几乎全是 mc 钓鱼 mod 或学术 IoT 项目，stars < 30，30 天无 commit。
   - **正确做法**：直接报告"无候选"，不强行凑数。

## 五、与主 SKILL.md 的对应关系

| 主 SKILL.md 段落 | 本参考细化内容 |
|---|---|
| 4️⃣ 9 点 B - 任务 1 | 上面 Step 1-4（搜索 + 过滤 + 排序） |
| 4️⃣ 9 点 B - 任务 2 | 上面第二节「版本检查 Triplet」 |
| 4️⃣ 9 点 B - 飞书卡片 | 上面第三节「卡片模板」 |
| 反模式段 | 上面第四节「本会话踩过的坑」 |

下次 9 点 cron 直接复制本参考的 5 步机械流程，不重新发明轮子。