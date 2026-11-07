# Verified Working Sources (2026-06-08)

> Each entry: the exact curl / node / Python invocation that returned usable data. Reuse these patterns.

## ✅ 中国渔业协会 (cappma.org.cn)

### Article index by category
```bash
# 20 channels that work
PIDS=(
  "5&ty=24"   # 标准资讯
  "5&ty=25"   # 团体标准
  "5&ty=26"   # 意见征求
  "5&ty=27"   # 标准查询
  "7&ty=30"   # 产业报告
  "7&ty=31"   # 行业数据
  "7&ty=32"   # 统计数据
  "7&ty=33"   # 价格行情
  "66&ty=67"  # 政策法规
  "66&ty=68"  # 质量安全
  "66&ty=69"  # 市场预警
  "66&ty=70"  # 国际资讯
  "66&ty=227" # 综合信息
  "66&ty=340" # 输美预警
  "4&ty=23"   # 展览动态
  "4&ty=61"   # 会议动态
  "1&ty=11"   # 协会活动
  "1&ty=12"   # 通知公告
  "1&ty=338"  # 刀鲚养殖
  "6&ty=28"   # 国际会议
  "6&ty=29"   # 交流合作
)
```

### Article link extraction
```python
# Pattern inside each list page HTML
r'<a[^>]+href="(view\.php\?id=(\d+))"[^>]*>(.*?)</a>'
# Full URL: http://www.cappma.org.cn/{captured_href}
```

## ✅ FAO GLOBFISH (fao.org)

### Species pages (13 verified)
```bash
SLUGS=(
  pangasius salmon shrimps tilapia tuna
  seabass-and-seabream lobster crab
  cephalopods bivalves seaweed
  groundfish small-pelagics
)
# URL: https://www.fao.org/in-action/globefish/species-analysis/${SLUG}/en
# Note: it's "shrimps" (plural), NOT "shrimp"
```

### Flagship report
```bash
curl -L -s -A 'Mozilla/5.0' --max-time 12 \
  "https://www.fao.org/fishery/en/sofia" \
  -o blue_transformation.html
# Returns ~58KB HTML with full text
```

### Model list (queue check)
```bash
curl -L -s -A 'Mozilla/5.0' --max-time 10 \
  "https://www.fao.org/fishery/en/"  # 58KB, has nav links
```

## ✅ 抖音热榜 (Douyin hot list)

```bash
# Direct API, no auth needed for /hot/search/list
cd "/c/Users/Administrator/.openclaw/workspace/skills/douyin-hot"
node scripts/douyin.js hot 100
# Returns top 100 hot topics with view counts and links
```

### Filter for aquatic / seafood keywords
```bash
node scripts/douyin.js hot 100 | grep -E "海|虾|蟹|鱼|养殖|海鲜|水产|鲍|海参|鲈|鲍|带鱼|金枪"
```

## ❌ Sources that DO NOT work on this machine

| Source | Failure mode |
|---|---|
| 微信搜狗 (weixin.sogou.com) | Aggressive anti-bot, 0/4 hit rate on first request |
| 知乎 (zhihu.com) | 403 from any agent UA |
| 微博 (weibo.com) | 403 + captcha |
| 36kr | 500 internal error |
| web.archive.org | SSL timeout, 0B response |
| 维基百科 (en/zh) | SSL timeout, 0B response |
| NOAA | 403 |
| HuggingFace Inference API | Python SSL EOF; curl works but model cold start is 1-3 min |

## 🔁 Sources that work via curl but not Python urllib

This is a **machine-specific** pattern. Python's `urllib.request` SSL is broken (EOF errors on most HTTPS). Workaround: **shell out to curl via `subprocess` or `terminal` tool**.

```python
# Works
import subprocess
r = subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "--max-time", "10",
                    "https://example.com"], capture_output=True, text=True)
html = r.stdout

# Fails
import urllib.request
r = urllib.request.urlopen("https://example.com", timeout=10)  # SSL EOF
```

## 📁 User-visible paths (boss profile)

| What | Path |
|---|---|
| Report (one per day) | `C:/Users/Administrator/Desktop/知识库/YYYY-MM-DD-水产简报.md` |
| Raw data | `C:/Users/Administrator/Desktop/知识库/YYYY-MM-DD-水产简报-raw.json` |
| Daily log | `C:/Users/Administrator/Desktop/知识库/run_YYYYMMDD_HHMMSS.log` |
| Feishu boss-control App | `<FEISHU_APP_ID>` (in chat but no msg perm) |
| Feishu mini-app | `<FEISHU_APP_ID>` (in group, can send msgs) |
| Boss group chat_id | `oc_2e78919aef957064b91aec7515a93d4b` |

## 🕐 Cron pattern (Hermes)

```python
# Already created 2026-06-08:
# job_id = 31287df0e40a
# name = "每日水产简报 9:00"
# schedule = "0 9 * * *"
# Next run: 2026-06-09T09:00:00+08:00
```

Don't recreate; if it gets lost, list first with `cronjob(action="list")`.
