---
name: geo-monitor-project
description: GEO（生成引擎优化）监控项目全流程——竞品分析、引擎驱动开发、定时监控cron、自进化机制。触发条件：GEO项目开发、AI搜索引擎监测、品牌AI可见度追踪。
category: product
---

# GEO Monitor 项目开发

GEO（Generative Engine Optimization）—— 针对 AI 搜索引擎的品牌监测与内容优化平台。

## 项目标准路径

```
/Users/hua/6-产品研发/24-GEO/
├── version.json          ← 铁律：代号(codename) + copyright
├── README.md             ← 铁律：(c)2026渔芯科技
├── frontend/                                ← 纯 HTML/CSS/JS（FastAPI StaticFiles 挂载）
│   ├── index.html                           ← 落地页（含登录表单）
│   ├── admin/index.html                     ← SPA 管理后台
│   ├── optimize/index.html                  ← 自动优化页
│   ├── pricing/index.html                   ← 定价页
│   ├── how-it-works/index.html              ← 技术架构页
│   └── static/
│       ├── css/geo.css                      ← 共用 CSS 变量
│       └── js/geo.js                        ← 共用 JS（escHtml, showMsg）
├── backend/
│   ├── app/
│   │   ├── main.py                          ← FastAPI + lifespan + CORS
│   │   ├── frontend.py                      ← StaticFiles 挂载 + HTML 路由
│   │   ├── api/routes.py                    ← 路由聚合（/api/*）
│   │   ├── api/monitor.py                   ← 监测任务 CRUD
│   │   ├── auth/                            ← JWT 认证模块
│   │   ├── models/                          ← SQLAlchemy ORM（8张表）
│   │   └── services/
│   │       ├── engine.py                    ← 引擎调度 + 降级链
│   │       ├── llm.py                       ← LLM 管理层（分层+用量+成本）
│   │       ├── scheduler.py                 ← APScheduler 定时任务
│   │       ├── optimizer.py                 ← GEO 分析与优化方案生成
│   │       ├── content_generator.py         ← FAQ + Schema 生成
│   │       ├── parser.py                    ← 引用提取 + 品牌提及
│   │       └── drivers/                     ← 驱动层（browser/scraper/llm-simulator）
│   └── tests/
└── docs/
    ├── competitive-analysis-YYYY-MM-DD.md   ← 竞品分析（每周更新）
    ├── optimization-plan.md                 ← 综合优化方案
    └── architecture.md                      ← 架构设计
```

## 引擎驱动架构（v0.4.0）

分层驱动架构（非独立适配器），自动降级：

```python
ENGINE_CONFIG = {
    "chatgpt":   {"driver": "llm-simulator", "available_modes": ["llm"]},
    "perplexity":{"driver": "browser",       "available_modes": ["browser","llm"]},
    "kimi":      {"driver": "browser",       "available_modes": ["browser","llm"]},
    "doubao":    {"driver": "llm-simulator", "available_modes": ["llm"]},
    "baidu":     {"driver": "llm-simulator", "available_modes": ["llm"]},
    "bing":      {"driver": "browser",       "available_modes": ["browser","scraper","llm"]},
    "google":    {"driver": "browser",       "available_modes": ["browser","scraper","llm"]},
    "xinghuo":   {"driver": "llm-simulator", "available_modes": ["llm"]},
    "xiaohongshu":{"driver": "llm-simulator","available_modes": ["llm"]},
}
```

降级链：`browser → scraper → llm`（`query_with_fallback()` 自动执行）。
LLM 仿真驱动对每个引擎有独立的 System Prompt（`ENGINE_PROMPTS` dict），离线回退用 `_OFFLINE_FALLBACKS`。

### 铁律合规检查清单

- [ ] `version.json` 含 `codename`（中文双字代号）+ `copyright`（(c)2026）
- [ ] 前端页脚：`© 2026 东莞市渔芯科技有限公司`
- [ ] 所有凭证走 `os.environ` / Pydantic `BaseSettings`
- [ ] Python 代码：snake_case + type hints + PascalCase 类名
- [ ] 禁 wildcard import（`import *`）
- [ ] `.env` 进 `.gitignore`

## 定时监控 cron 设置模式

### 每日行业监控

```python
cronjob(action='create',
    name='GEO-每日行业监控',
    schedule='0 9 * * *',
    workdir='/Users/hua/6-产品研发/24-GEO',
    enabled_toolsets=['web','terminal','file'],
    prompt='...')  # 四维度轮转：竞品/引擎/技术/中国生态
```

### 每周自进化

```python
cronjob(action='create',
    name='GEO-每周自进化',
    schedule='0 9 * * 1',
    deliver='feishu:oc_2db3b5373825567c3681d1ca580e0143',
    prompt='...')  # 竞品更新+方案审查+周报+飞书推送
```

## 竞品分析模板

见 `docs/competitive-analysis-template.md`：全球格局 + 中国市场 + 渔芯定位 + 护城河 + 短板优先级。

## P0-P3 优化框架

| 优先级 | 关注点 | 典型方案 |
|:---:|------|------|
| P0 | 引擎稳定性 | 选择器降级链、反检测升级、指数退避重试 |
| P1 | 数据质量 | LLM替代关键词做情感分析、域名权威度、URL语义去重 |
| P2 | 规模化 | asyncio.gather并发、关键词动态发现、历史趋势存储 |
| P3 | 产品化 | 多租户、报告模板引擎、飞书推送 |

## 已知坑

- **浏览器到AI引擎直连被登录墙挡住**：Kimi/豆包需手机号登录。实际开发用行业公开最佳实践+架构判断合成方案，不比直接问差。
- **web_extract 后端为 DuckDuckGo**：只能搜索不能提取内容。set `web.extract_backend` 到 firecrawl/tavily/exa。
- **大文件 rsync 超时**：`rkr_v1.2.0_export` 12GB 导致 rsync 超时。分批用 cp 迁移小文件，大文件单独处理。
- **APScheduler 重启陷阱**：`scheduler.shutdown()` 后不能对旧实例调 `add_job()`/`start()`，必须重建 `AsyncIOScheduler()`。用懒加载单例 + `_scheduler = None` 强制重建。
- **版本号分散在三处**：`config.py`(app_version)、`frontend/index.html`(nav bar)、`frontend/admin/index.html`(topnav)。改版本时三处需同步。
- **LLM Gateway URL 不一致**：`llm_base_url` 应无 `/v1` 后缀（OpenAI SDK 自动追加）。`optimizer.py` 绕过 `call_llm()` 直接 HTTP 调时需手动拼 `/v1/chat/completions`。

## 擎索 SEO（30-SEO）—— 姊妹项目

与擎观 GEO 共用前端样式和架构模式，监测传统搜索引擎排名。端口 8001。

```
/Users/hua/6-产品研发/30-SEO/
├── backend/app/
│   ├── services/engine.py     ← httpx+BS4 抓取 Google/Bing/百度/360/搜狗
│   ├── api/routes.py          ← /api/search, /api/audit, /api/health
│   └── core/config.py         ← env_prefix="SEO_", port 8001
└── frontend/                  ← 与 24-GEO 共用 CSS 变量模式（品牌色橙色--accent:#E89640）
```

**两个项目对比（可互相借鉴）：**

| 特性 | 24-GEO 擎观 | 30-SEO 擎索 | 谁领先 |
|------|------------|------------|--------|
| 认证系统 | ✅ JWT auth 模块 | ❌ 缺失 | GEO |
| 定时调度 | ✅ APScheduler | ❌ 缺失 | GEO |
| 用量追踪 | ✅ llm.py token/cost | ❌ 缺失 | GEO |
| 前端架构 | ✅ CSS/JS 分离 | ⚠️ 全部内联 | GEO |
| SEO 站点审计 | ❌ 无 | ✅ site_health_check | SEO |
| SERP 特征检测 | ❌ 无 | ✅ 7 种特征识别 | SEO |

**30-SEO 特有已知坑：**
- `engine.py` 的 `site_health_check()` 使用同步 `httpx.get()`，应改为 async 避免阻塞事件循环。
- 缺少数据库初始化（已修复 2026-08-11：添加 lifespan + create_all）。
- 缺少前端内联 `escHtml()`/`showMsg()` 共用 JS，直接从 admin HTML 内 copy。

## 每日 cron 优化轮次

每个产品项目每天跑一轮代码质量 + 优化（已配 cron）：

1. `git diff` 看上次优化后的变更
2. 后端：类型注解、异常处理、硬编码值、API 响应
3. 前端：重复代码、加载性能、响应式
4. 两项目功能对比，找可互相借鉴的特性
5. 小问题直接修，复杂改动写 `/Users/hua/6-产品研发/项目优化建议.md`
6. 中文汇报本轮简报

## 配套资源

- 渔芯铁律：`/Users/hua/6-产品研发/公共组件/渔芯项目开发_习惯与准则_铁律.md`
- 竞品分析模板：`references/competitive-analysis-template.md`
- APScheduler 重启模式：`references/apscheduler-restart-pattern.md`
- 前端 FastAPI 挂载模式：`references/frontend-serving-pattern.md`
- GEO 竞品分析：`docs/competitive-analysis-2026-08-10.md`
- 综合优化方案：`docs/optimization-plan-v1.0.md`
- 项目优化建议（每日 cron 输出）：`/Users/hua/6-产品研发/项目优化建议.md`
