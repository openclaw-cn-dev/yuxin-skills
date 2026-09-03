# 水产内容采集死路清单（2026-06-08 验证）

> **教训**：不要让下个 session 再花 30 分钟试这些路径

## ❌ 已废数据源

### 1. Python feedparser
- **症状**：`pip install feedparser` 装到 Python 3.14，`import feedparser` 走 3.11 失败
- **诊断**：`which python` vs `which pip` 不一致
- **解决**：改用 curl + 自己写 HTML 解析（10 行代码）
- **别再试**：pip 重装 / 改 PYTHONPATH / venv 切换

### 2. 搜狗微信 weixin.sogou.com
- **症状**：19 个查询 → 4 命中 → cookie warmup 后 8 命中 → 限流
- **诊断**：搜狗有 IP 频率 + UA 黑名单 + JS challenge
- **解决路径**（未实施）：装 Puppeteer 拿真实 cookie
- **别再试**：直接 HTTP 抓、换 UA、加 cookie 头

### 3. 知乎 hot-lists
- **症状**：全 403
- **诊断**：知乎 API 严格鉴权，未登录直接拒
- **别再试**：换 UA / 加 referer / 装 cookie

### 4. 微博 hotSearch
- **症状**：全 403
- **诊断**：同知乎
- **别再试**：同

### 5. 36kr hot
- **症状**：500
- **诊断**：服务端错误
- **别再试**：放弃

### 6. 抖音搜索 /aweme/v1/search/general/search
- **症状**：返回 HTML 首页（302 → React shell）
- **诊断**：抖音搜索 API 需 `X-Bogus` 签名（2 步加密）+ msToken cookie
- **解决路径**（未实施）：装 `douyin-search` 库（GitHub 有）
- **别再试**：直接打 API 路径

### 7. 抖音分类榜
- **症状**：返回 0 字节
- **诊断**：需登录
- **别再试**：换账号 / 装 cookie

### 8. Python urllib + SSL
- **症状**：Python `urlopen` 全 SSL: CERTIFICATE_VERIFY_FAILED 或 timed out
- **诊断**：同机 `curl` 完全正常
- **解决**：**所有抓取走 terminal + curl**（Python 只负责解析）
- **别再试**：改 ssl._create_default_https_context / 装 certifi

### 9. Wikimedia Commons API
- **症状**：SSL handshake timed out
- **诊断**：墙内不稳
- **别再试**：改维基百科国内镜像

### 10. Pexels /photos/{id}（旧误判）
- **症状**：之前被认为"连续抓就限流"
- **真相（2026-06-08 验证）**：**curl 直下完全 OK，限流是误判**
- **真实原因**：之前用 Python urllib 抓，SSL 失败被误判为限流
- **正确用法**：`curl -L -A 'Mozilla/5.0' -o img.jpg 'https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?w=1200'`

## 🟢 真实活路（已验证）

1. **cappma.org.cn** 20 频道（见 pid-ty-map.md）
2. **抖音热榜 /aweme/v1/hot/search/list/**（直接打，无需签名）
3. **Pexels 图片**（curl 直下）
4. **curl** 抓任何 HTML（**Python urllib 别再用**）

## 📊 任务时间表

| 任务 | 实际耗时 | 备注 |
|---|---|---|
| 探测数据源 | 15 分钟 | 6 个源失败 |
| 抓 cappma 20 频道 | 15 秒 | curl 并发 |
| 解析 122 篇 | 2 秒 | Python regex |
| 抓 10 篇正文 | 10 秒 | curl 串行 + 0.5 秒间隔 |
| 写 Markdown 简报 | 5 秒 | 模板填充 |
| **合计** | **~30 分钟** | 实际数据流只占 30 秒 |

## 💡 教训
**抓不到 ≠ 找不到**。本机限制死了所有公开 API，但**行业协会官网**是金矿——cappma 一家就够 122 篇/天。
