---
name: blogwatcher
description: "Monitor blogs and RSS/Atom feeds with blogwatcher-cli. Use when 老大 asks for daily/weekly content digests, RSS feed aggregation, blog monitoring, 'find all X blogs', or 'subscribe to Y website' — 5+ sources to track, or wants to stop reading 100 sites by hand. Auto-discovers RSS, falls back to HTML scraping, deduplicates, and persists reads to SQLite. Triggers on 'RSS 监控', '博客订阅', '网站更新', '每日资讯', '内容聚合', '爬 RSS', 'feed reader'."
---
name: blogwatcher
description: "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. Use for daily digests, blog monitoring, RSS aggregation, content watches."
version: 2.0.0
author: JulienTant (fork of Hyaxia/blogwatcher)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [RSS, Blogs, Feed-Reader, Monitoring]
    homepage: https://github.com/JulienTant/blogwatcher-cli
prerequisites:
  commands: [blogwatcher-cli]
---

# Blogwatcher — RSS / 博客监控（class-level skill）

## 🆘 **触发场景（重要：以下情况先用这个 skill）**

⚠️ **2026-06-08 真实坑**：小弟做"每日水产简报"时**自己写 Python feedparser 解析器 + 手动 curl**，**完全忘了 blogwatcher-cli 已在 skills_list 里**。下次别再犯。

**强制用本 skill 的信号**：
- 老大要 "**每天早上给我 X 篇 Y 内容**" / "**每日简报**" / "**X 站更新提醒**" / "**监控这几个博客**"
- 老大说 "**订阅**" / "**RSS 抓取**" / "**聚合**" / "**内容聚合**"
- 老大说 "**5+ 个站都要看**" / "**别让我自己刷**"
- 任何 "**N 个信源 → 1 份报告**" 的工作流

**反面案例（2026-06-08）**：
- ❌ 自己写 `feedparser` + `urllib.request`，pip 装到不同 python 路径
- ❌ 手动 curl 20 个 RSS endpoint，每个单独 `re.findall` 解析
- ❌ 不知道 `blogwatcher-cli` 已经在 skills_list 里
- ✅ **正确做法**：`blogwatcher-cli add "<name>" "<url>"` + `blogwatcher-cli scan` + `blogwatcher-cli articles`

## 🚀 快速上手（5 分钟跑通）

```bash
# 1. 装（go 一行）
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest
# 或 Windows 预编译
curl -sL -o blogwatcher.exe https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_windows_amd64.tar.gz | tar xz

# 2. 加源
blogwatcher-cli add "中国渔业协会" "http://www.cappma.org.cn/" --feed-url "http://www.cappma.org.cn/list.php?pid=207"
blogwatcher-cli add "FAO 蓝色转型" "https://www.fao.org/fishery/en/sofia"
blogwatcher-cli add "FAO GLOBFISH" "https://www.fao.org/in-action/globefish/species-analysis/species-analysis-overview/en"

# 3. 扫
blogwatcher-cli scan

# 4. 看新文章
blogwatcher-cli articles --all
```

## 🎯 与"自写爬虫"的对比

| 维度 | 自写 (urllib + re) | blogwatcher-cli |
|---|---|---|
| RSS 自动发现 | ❌ 手写 | ✅ 内置 |
| HTML 抓取 fallback | ❌ 手写 | ✅ `--scrape-selector` |
| OPML 导入 | ❌ | ✅ `import subs.opml` |
| 去重 | ❌ 手写 dedup dict | ✅ SQLite 内置 |
| 已读管理 | ❌ | ✅ `read 1` / `read-all` |
| 多 worker 并发 | ❌ 单线程 | ✅ 默认 8 worker |
| Windows 兼容 | ⚠️ 路径/编码坑 | ✅ 预编译二进制 |
| 定时任务 | ❌ 手写 | ✅ 配 cron / Task Scheduler |
| 体积 | 自写 ~200 行 | 1 个二进制 |

## 🔧 在老大业务里的典型用法

### 用例 1：每日水产简报（2026-06-08 实测场景）

```bash
# 把简报源的 RSS 一次性加进来
blogwatcher-cli add "中国渔业协会 协会活动"   "http://www.cappma.org.cn/more.php?pid=1&ty=11"
blogwatcher-cli add "中国渔业协会 标准资讯"   "http://www.cappma.org.cn/more.php?pid=5&ty=24"
blogwatcher-cli add "中国渔业协会 产业报告"   "http://www.cappma.org.cn/more.php?pid=7&ty=30"
blogwatcher-cli add "中国渔业协会 价格行情"   "http://www.cappma.org.cn/more.php?pid=7&ty=33"
blogwatcher-cli add "FAO 蓝色转型"           "https://www.fao.org/fishery/en/sofia"
blogwatcher-cli add "FAO GLOBFISH"           "https://www.fao.org/in-action/globefish/species-analysis/species-analysis-overview/en"
blogwatcher-cli add "抖音热榜"               "https://www.douyin.com/aweme/v1/hot/search/list/"

# 配 Windows 任务计划：每天 9:00 跑
# blogwatcher-cli scan → 写一份 markdown → 桌面 知识库/2026-XX-XX.md
```

### 用例 2：朋友圈/小红书 爆款监控

```bash
blogwatcher-cli add "新榜"     "https://www.newrank.cn/"
blogwatcher-cli add "蝉妈妈"   "https://www.chanmama.com/"
blogwatcher-cli add "飞瓜数据" "https://www.feigua.cn/"
# ...每个都试 RSS 找得到就用，找不到就 scrape
```

### 用例 3：竞品公司动态监控

```bash
blogwatcher-cli add "海大集团"      "https://www.haid.com.cn/" --scrape-selector ".news-list a"
blogwatcher-cli add "通威股份"      "http://www.tongwei.com.cn/" --scrape-selector ".news-item a"
blogwatcher-cli add "粤海饲料"      "http://www.yuehaifeed.com/" --scrape-selector ".news a"
```

## 🛑 已知限制（2026-06-08 实测）

- **反爬网站不行**：小红书 / 知乎 / 微博 / 微信公众号 → 走 4 路 fallback（见 `douyin-content-extraction` 模式）
- **HTML 动态加载不行**：纯 JS 渲染的站 → 需要 `--scrape-selector` 配 SPA-aware
- **国内站 RSS 多数 404**：必须先 `curl` 试探 + `view-source:url` 找 `link rel="alternate"`
- **数据库路径**：默认 `~/.blogwatcher-cli/blogwatcher-cli.db`，Docker 模式必须用 `BLOGWATCHER_DB` + volume

## 📚 完整命令清单

### Installation
- **Go:** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker:** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **Binary (Linux amd64):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **Binary (macOS Apple Silicon):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

### Common Commands

**Managing blogs**:
- Add: `blogwatcher-cli add "My Blog" https://example.com`
- Add with explicit feed: `blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- Add with HTML scraping: `blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- List: `blogwatcher-cli blogs`
- Remove: `blogwatcher-cli remove "My Blog" --yes`
- Import OPML: `blogwatcher-cli import subscriptions.opml`

**Scanning and reading**:
- Scan all: `blogwatcher-cli scan`
- Scan one: `blogwatcher-cli scan "My Blog"`
- Unread: `blogwatcher-cli articles`
- All: `blogwatcher-cli articles --all`
- Filter: `blogwatcher-cli articles --blog "My Blog"`
- Mark read: `blogwatcher-cli read 1`
- Mark all: `blogwatcher-cli read-all --yes`

## 🌍 Environment Variables

| Variable | Description |
|---|---|
| `BLOGWATCHER_DB` | SQLite path (override default `~/.blogwatcher-cli/...`) |
| `BLOGWATCHER_WORKERS` | Concurrent scan workers (default 8) |
| `BLOGWATCHER_SILENT` | Only print "scan done" |
| `BLOGWATCHER_YES` | Skip confirmations |
| `BLOGWATCHER_CATEGORY` | Default filter for articles |

## 📌 Notes

- Auto-discovers RSS/Atom feeds from blog homepages when no `--feed-url` is provided.
- Falls back to HTML scraping if RSS fails and `--scrape-selector` is configured.
- Categories from RSS/Atom feeds are stored and can be used to filter articles.
- Import blogs in bulk from OPML files exported from Feedly, Inoreader, NewsBlur.
- Database: `~/.blogwatcher-cli/blogwatcher-cli.db` (override with `--db` or `BLOGWATCHER_DB`).
- Use `blogwatcher-cli <command> --help` to discover all flags.

## 📁 相关 skill

- **`media/douyin-content-extraction`** — 抖音单视频内容（4 路 fallback 模式可借鉴）
- **`media/douyin-content-extraction`** 的"反爬"经验 → 同样适用 RSS 站被反爬
- **`research/arxiv`** — 学术论文搜索（不是 RSS，但同属"自动聚合"）
- **`productivity/response-style-boss`** — 老大回复风格（"你看着办"红线）
