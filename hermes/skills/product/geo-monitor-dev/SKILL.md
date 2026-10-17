---
name: geo-monitor-dev
description: 擎观 GEO 和擎索 SEO Monitor 项目开发维护。三功能架构监测优化提升、前端后端版本排障。触发 GEO SEO 项目、擎观擎索、24-GEO 30-SEO、启动geo启动ceo、新增页面API。
---

# 擎观 GEO Monitor 开发技能

> ⚠️ **2026-09-26 实测更正（老莫 GEO-01 心跳轮）**：本文档的本地开发形态已失效——`/Users/hua/6-产品研发/24-GEO/` 目录在本机**不存在**（技能早期版本路径口径）。**生产实例在阿里云 ECS 121.43.127.211**（容器 geo-backend-1，端口 8002 为**服务器本地视角**，GED_DEV_MODE=false，dev@geo.local 登录无效，认证用 users 表 api_key 作 Bearer）。运营任务（kanban GEO-* 队列：GEO-01 基线审计 / GEO-02 FAQ Schema 优化 / GEO-03 周报自动化）一律走生产 API → **先读 `references/production-ecs-deployment.md`**（SSH 方式、认证、API 契约实测、tirith 拦截绕过、GEO-01 进度、**§7 GEO-02 执行情报：两站真实服务链路 yuxinsim=3107 Next.js 容器 / lookforge=uvicorn 8642、faq-schema 契约、Next.js 预渲染页注入配方、进度台账**）。本文档其余部分仅适用于本地重建开发环境时参考。

## 项目概览

| 项 | 值 |
|----|-----|
| 代号 | 擎观 |
| 路径 | `/Users/hua/6-产品研发/24-GEO/` |
| 版本 | v0.5.0 |
| 端口 | **8001**（8000 被 RKR Docker 占用） |
| Python | 系统 Python 3.9（不支持 `str \| None`） |
| 后端 | FastAPI + SQLAlchemy + aiosqlite |
| 前端 | 纯静态 HTML（5个页面）+ Vanilla JS |

## 兄弟项目：擎索 SEO（30-SEO）

用户经常同时操作两个项目，且口语中常把「SEO」说成「ceo」。听到"ceo"/"启动ceo"时指的就是 30-SEO。

| 项 | 值 |
|----|-----|
| 代号 | 擎索 |
| 路径 | `/Users/hua/6-产品研发/30-SEO/` |
| 版本 | v0.1.0 |
| 端口 | **8002** |
| 后端 | FastAPI + SQLAlchemy + aiosqlite |
| 引擎 | 百度/360/搜狗/Google/Bing（5引擎，HTTP直接抓取） |

```bash
# 启动 SEO
cd /Users/hua/6-产品研发/30-SEO/backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8002 &

# 同时启动两个（GEO+SEO）
cd /Users/hua/6-产品研发/24-GEO/backend && GED_DEV_MODE=true python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
cd /Users/hua/6-产品研发/30-SEO/backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8002 &
```

## 启动 / 停止

```bash
# 启动 GEO（后台）
cd /Users/hua/6-产品研发/24-GEO/backend
GED_DEV_MODE=true python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &

# 同时启动 GEO + SEO（华哥常同时操作两个）
cd /Users/hua/6-产品研发/24-GEO/backend && GED_DEV_MODE=true python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
cd /Users/hua/6-产品研发/30-SEO/backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8002 &

# 停止（注意：会停掉所有 uvicorn，可能影响其他项目如 RKR）
pkill -f "uvicorn app.main:app --host 127.0.0.1 --port 8001"   # GEO
pkill -f "uvicorn app.main:app --host 127.0.0.1 --port 8002"   # SEO

# 一键启动
open /Users/hua/6-产品研发/24-GEO/start-server.command
```

**演示账号**: `dev@geo.local` / `dev123456`

## 项目结构

```
24-GEO/
├── version.json          ← 版本号 + 中文代号「擎观」
├── README.md
├── start.sh / start-server.command
├── frontend/             ← 纯静态，修改即生效
│   ├── index.html        ← 首页（品牌展示 + 登录）
│   ├── admin/index.html  ← 管理后台（KPI + 监测 + 优化 + 提升 + 引擎）
│   ├── pricing/index.html ← 定价（5档 + 竞品对比）
│   ├── optimize/index.html ← 自动优化（FAQ + Schema）
│   ├── how-it-works/index.html ← 技术架构详解
│   └── static/           ← Favicon + 图片资源（CSS/JS 内联在 HTML 中）
├── backend/app/
│   ├── main.py           ← FastAPI 入口 + lifespan
│   ├── frontend.py       ← 前端页面路由注册
│   ├── api/              ← API 模块（monitor/optimize/improve/content/report等）
│   ├── services/         ← 引擎/优化/提升/解析/提取/报告
│   │   ├── engine.py     ← ① 监测：9引擎调度 + fallback（7507 bytes）
│   │   ├── optimizer.py  ← ② 优化：品牌GEO分析（analyze_brand_geo）
│   │   ├── improve.py    ← ③ 提升：闭环引擎（监测→分析→自动执行→报告，15KB 新增）
│   │   └── drivers/      ← Browser / Scraper / LLM 三层驱动
│   ├── models/           ← ORM + Pydantic Schema
│   └── core/config.py    ← Pydantic Settings（含 app_version）
├── dashboard/            ← Streamlit 仪表盘
└── docs/                 ← 调研笔记 + 竞品分析
```

## 三功能架构（监测 → 优化 → 提升）+ 执行引擎闭环

华哥 2026-08-12 明确产品方向：三个核心功能形成闭环。2026-08-12 新增共享执行引擎 `executor.py`，将"提升"扩展为完整的 5 阶段闭环。

```
┌──────────┐     ┌──────────┐     ┌──────────────────────────────────┐
│ ① 监测    │ ──→ │ ② 优化    │ ──→ │ ③ 提升（executor.py 5阶段闭环）  │
│ Monitor  │     │ Optimize │     │                                  │
├──────────┤     ├──────────┤     │ 3a. 执行 → 生成文件到 data/output │
│ 9引擎查询 │     │ LLM诊断  │     │ 3b. 验证 → 再监测 before/after对比│
│ 品牌提及  │     │ 行动计划  │     │ 3c. 追踪 → JSONL日志 + 趋势快照  │
│ 情感分析  │     │ 内容建议  │     │                                  │
└──────────┘     └──────────┘     └──────────────────────────────────┘
```

### API 端点对应

| 功能 | GEO 端点 | SEO 端点 |
|------|---------|---------|
| ① 监测 | `POST /api/monitor/tasks` `POST /api/quick-run` | `POST /api/search` `POST /api/audit` |
| ② 优化 | `POST /api/improve/analyze` `GET /api/improve/quick` | `POST /api/optimize/analyze` |
| ③ 提升（旧） | `POST /api/improve/run` `POST /api/improve/execute` | `POST /api/improve/run` |
| ③ 闭环（新）⭐ | `POST /api/improve/cycle` | `POST /api/cycle` |

### 核心服务文件

| 文件 | 职责 |
|------|------|
| `services/engine.py` | ① 监测：9引擎调度 + fallback |
| `services/optimizer.py` | ② 优化：品牌GEO分析（analyze_brand_geo） |
| `services/improve.py` | ③ 提升：闭环引擎（监测→分析→执行→报告）+ `run_optimize_with_executor()` |
| `services/executor.py` | ⭐ **共享执行引擎**：GEO/SEO 统一的 5 阶段闭环（监测→分析→执行→验证→追踪） |
| `services/reporting.py` | 效果追踪（JSONL日志 + 快照 + 报告），GEO/SEO 通过 symlink 共享 |
| `services/content_generator.py` | 内容生成（FAQ/Schema） |
| `services/publisher.py` | 多渠道发布 |

**executor.py 产出目录**：`24-GEO/data/output/{geo|seo}/` — 包含生成的 .json + .html 文件。

### 提升引擎 `improve.py`（2026-08-12 新增）

四阶段闭环：

1. **监测阶段** — `run_quick_monitor()` 查询 3-9 个 AI 引擎
2. **分析阶段** — `analyze_monitoring_data()` LLM 生成诊断 + 行动计划 + 内容方案
3. **执行阶段** — `execute_improvement()` 自动执行 content/schema/faq/meta 类操作
4. **报告阶段** — 汇总时间线 + 预计效果（可见度/提及率提升）

```python
# 完整闭环
from app.services.improve import run_full_improvement_cycle
result = await run_full_improvement_cycle(
    brand="渔芯科技", keyword="RAS",
    auto_execute=True,  # 自动执行优化操作
    max_actions=5,
)
# result 包含: monitor_summary, analysis, executed_actions, timeline, estimated_impact
```

### 执行引擎 `executor.py`（⭐ 2026-08-12 新增）

GEO 和 SEO 共享的优化执行层，实现真正的 5 阶段全闭环：

```
监测(before) → 分析 → 执行(生成文件) → 验证(after) → 记录(JSONL+快照)
```

**核心入口**：`run_optimize_and_verify()` — 一键触发完整链路。

```python
# 通过 improve.py 的包装函数调用（推荐）
from app.services.improve import run_optimize_with_executor
result = await run_optimize_with_executor(
    brand="渔芯科技", keyword="智慧渔业",
    engines=["kimi", "doubao", "baidu"],
    auto_execute=True, max_actions=5,
)
# result 包含: monitor_before, analysis, execution, monitor_after, comparison, timeline
```

**支持的执行类型**：`content`（生成HTML+JSON文件）、`schema`（Schema.org结构化数据）、`meta`（Meta标签建议）、`structure`（技术SEO结构优化）

**产出物**：写入 `24-GEO/data/output/{geo|seo}/` 目录，每项操作生成 `.json` + `.html` 文件。

**与旧 `run_full_improvement_cycle` 的区别**：
- ✓ 执行后自动再监测验证效果（before/after 对比）
- ✓ 自动调用 `save_optimization_log()` 记录 JSONL 日志
- ✓ 自动调用 `save_snapshot()` 保存趋势快照
- ✓ 产出文件写入 `data/output/` 目录

**SEO 对接**：`30-SEO/backend/app/services/optimize.py` 中 `run_optimize_with_executor()` 函数同样委托给 executor。

### executor.py 同步规则

`executor.py` 位于 `24-GEO/backend/app/services/executor.py`，修改后需同步到：
```bash
cp /Users/hua/6-产品研发/24-GEO/backend/app/services/executor.py \
   /Users/hua/6-产品研发/30-SEO/backend/app/services/executor.py
```
（与 `reporting.py` 不同，`executor.py` 不走 symlink，因为 SEO 侧有独立的 `app.services.optimize` 导入路径）

### 前端管理后台（admin/index.html）

导航标签对应三功能：
- `📊 总览` — KPI面板
- `🔍 监测` — 关键词快速监测（已有）
- `🎯 优化` — 品牌分析 + 生成优化建议（**新增**，调用 `/api/improve/analyze`）
- `📈 提升` — 一键闭环（**新增**，调用 `/api/improve/run`）
- `🔧 引擎` — 引擎状态

前端 JS 函数：
- `runOptimize()` — 调用 `/api/improve/analyze`，显示诊断+行动+内容
- `runQuickAnalyze()` — 调用 `/api/improve/quick`，快速诊断
- `runImprove()` — 调用 `/api/improve/run`，完整闭环+时间线+自动执行

### SEO 的三功能架构

SEO 也有完整的三功能 API：`POST /api/search`（监测）、`POST /api/optimize/analyze`（优化）、`POST /api/improve/run`（提升）。

SEO 的 LLM 调用直接走 Gateway（`http://127.0.0.1:18888/v1/chat/completions`），不依赖 GEO 的 `call_llm` 封装。SEO optimize.py 无 GEO 依赖，可独立运行。

**SEO admin 页面**（frontend/admin/index.html, 31KB）：5个 Tab 全部内联在单文件 SPA 中：
- `📊 总览` — KPI面板 + 引擎状态
- `🔍 监测` — 排名查询 + 站点健康审计
- `🎯 优化` — AI诊断 → 问题列表 → 行动计划 → 关键词机会 → 自动生成Meta/内容/结构
- `📈 提升` — 一键闭环（排名查询→分析→自动优化内容生成）
- `📋 报告` — 日报/周报/月报 + 趋势柱状图 + 优化历史

### 统一报告引擎（2026-08-12 新增）

`services/reporting.py` 是 GEO 和 SEO 共享的效果追踪引擎，SEO 通过 symlink 复用：
```bash
ln -sf /Users/hua/6-产品研发/24-GEO/backend/app/services/reporting.py \
       /Users/hua/6-产品研发/30-SEO/backend/app/services/reporting.py
```

核心功能：
- **优化历史** — `save_optimization_log()` / `get_optimization_history()`，JSONL 存储
- **趋势快照** — `save_snapshot()` / `get_snapshots()`，时间序列对比
- **效果报告** — `generate_report()`，前后对比 + 趋势 + 建议

存储位置：`24-GEO/data/reports/optimization_log_{geo,seo}.jsonl` + `snapshots_{geo,seo}.jsonl`

⚠️ 如果修改 reporting.py，SEO 自动生效（symlink），但需重启两个后端。

> 📖 **执行引擎完整架构**：见 `references/executor-architecture.md` — executor.py 在执行阶段自动调用 reporting.py 的日志/快照函数。

### 报告 API 端点

| 端点 | 用途 |
|------|------|
| `GET /api/reporting/history?brand=X` | 优化操作历史 |
| `GET /api/reporting/trend?brand=X&days=30` | 趋势数据（柱状图用） |
| `GET /api/reporting/report?brand=X&project=geo\|seo&days=7` | 日报/周报/月报 |
| `POST /api/reporting/snapshot` | 保存快照 |

### GEO 前端完整 Tab 清单（admin/index.html）

```
📊 总览     — KPI + 快速操作 + 系统状态
🔍 监测     — 9引擎关键词快速监测
🎯 优化     — 品牌分析 + 诊断评分 + 行动计划 + 内容建议（runOptimize/runQuickAnalyze）
📈 提升     — 一键闭环：监测→分析→自动执行→效果预估（runImprove）
📋 报告     — 日报/周报/月报 + 趋势图 + 优化历史（genGEOReport/loadGEOTrend/loadGEOHistory）
🚀 自动优化 — 独立页面（/optimize）
🔧 引擎     — 引擎状态表
⚙️ 设置     — 账户 + 用量统计
```

## 新增前端页面

有两种方式：

**方式 A：内联 Tab（推荐用于管理后台功能）**
在 `frontend/admin/index.html` 中：
1. 在 `.nav-links` 添加 `<a>` 标签（`data-page="xxx"`）
2. 添加 `<div class="page" id="page-xxx">` 页面区块
3. 在 `<script>` 中添加对应的 JS 函数
4. 无需注册路由——admin 页面是单文件 SPA

**方式 B：独立 HTML 页面**
1. 在 `frontend/<name>/index.html` 创建 HTML 文件
2. 在 `backend/app/frontend.py` 的 `setup_frontend()` 中添加路由
3. 更新首页 footer 导航链接
4. 无需重启后端（静态 HTML 运行时读取文件）

## 版本号同步（4处）

版本升级时需同步：
1. `version.json` — `"version": "0.5.0"`（⚠️ 编辑时先删除旧行再添加新行，避免重复键）
2. `backend/app/core/config.py` — `app_version: str = "0.5.0"`
3. `frontend/index.html` — `<span class="ver">v0.5.0</span>`
4. `frontend/admin/index.html` — `<span class="ver">v0.5.0</span>`

**验证命令**：
```bash
grep -rn "0\.5\.0\|v0\.5\.0" --include='*.py' --include='*.html' --include='*.json' | grep -v __pycache__ | grep -v .git/
# 应返回恰好 4 行（version.json / config.py / index.html / admin/index.html）
```

## Python 3.9 兼容性

系统 Python 3.9 不支持 `str | None` / `list[list[str]] | None` 等 PEP 604 语法。

**修复**：在文件顶部 `import` 之前添加：

```python
from __future__ import annotations
```

检查是否已有其他 3.10+ 语法：
```bash
grep -rn "| None\| str\| int\| float\b" backend/app/ --include='*.py' | grep -v __pycache__
```

## P0-P3 优化框架

| 优先级 | 关注点 | 典型方案 |
|:---:|------|------|
| P0 | 引擎稳定性 | 选择器降级链、反检测升级、指数退避重试 |
| P1 | 数据质量 | LLM替代关键词做情感分析、域名权威度、URL语义去重 |
| P2 | 规模化 | asyncio.gather并发、关键词动态发现、历史趋势存储 |
| P3 | 产品化 | 多租户、报告模板引擎、飞书推送 |

## 已知陷阱

### 端口 8000 被 RKR 占用
RKR 平台的 Docker 容器 `rkr-backend` 映射了 `0.0.0.0:8000→8000`。GEO Monitor 必须用 **8001**。
不要试图停 RKR Docker——它在线服务中。

### 引擎驱动：LLM 仿真为主
目前 9 个引擎中，浏览器驱动的仅 Perplexity/Kimi/Bing/Google 配置了 selector chains，
其余（ChatGPT/豆包/百度/星火/小红书）走 LLM 仿真。添加新引擎浏览器驱动需在
`drivers/browser.py` 中：
1. 添加 `ENGINE_URLS` 条目
2. 添加 `INPUT_SELECTOR_CHAINS` 三级选择器链
3. 测试登录墙（Kimi/豆包 有登录拦截）

### version.json 重复键陷阱
手动编辑 `version.json` 时容易保留旧版本行导致 JSON 出现两个 `"version"` 键。
JSON 标准取最后一个值所以功能上没问题，但会造成数据混乱。
**预防**：编辑时删除旧行再添加新行，或使用 `patch` 工具做替换。
**检测**：
```bash
python3 -c "import json; d=json.load(open('version.json')); print(d['version'])"
# 如果输出 2 行则说明有重复键
```

### 前端 CSS/JS 实际位置
项目结构中 `frontend/static/` 目录仅存放 favicon 和收款码图片。
所有 CSS 和 JavaScript 均内联在各自的 HTML 文件的 `<style>` 和 `<script>` 标签中。
修改样式时直接编辑对应 HTML 文件，无需在 static/ 目录下查找。

### dashboard/recent-tasks 端点修复模式
如果某个 API 端点返回空数据（死端点），标准修复模式是从 `app.main` 导入 `async_session` 直接查询 DB：
```python
from app.main import async_session
async with async_session() as db:
    result = await db.execute(select(Model).order_by(Model.created_at.desc()).limit(N))
    tasks = result.scalars().all()
```
避免在 API 层创建新的 session factory — 复用 `main.py` 中已有的单例。

### SEO admin 页面升级注意事项
SEO 的 admin 页面（`30-SEO/frontend/admin/index.html`）是完整的单文件 SPA（31KB），不通过 `backend/app/frontend.py` 注册路由——它直接由 main.py 中第 61-62 行的 `frontend/admin/index.html` 通配路由覆盖。新增 Tab 时直接在 HTML 中添加 `<div class="page">` 和 JS 函数即可，无需改后端路由。

### 新增 API 端点时的路由冲突陷阱 ⚠️
FastAPI 按文件中 `@router.post()` 出现的顺序匹配路由。如果 `api/improve.py` 中已有 `POST /execute`，再追加一个新的 `POST /execute`，**旧端点始终优先**，新端点返回 404。

**症状**：curl 新端点返回 `{"detail": "Not Found"}`，但 openapi.json 只显示旧端点。

**正确做法**：
1. 给新端点用不同的路径名（如 `/cycle` 而非 `/execute`）
2. 或者合并到已有端点中用 `action` 参数区分
3. 修改后必须 `kill` + 重启服务（代码热重载不会重新注册路由）

**检测命令**：
```bash
python3 -c "import urllib.request,json; r=urllib.request.urlopen('http://127.0.0.1:8001/openapi.json'); \
  print([p for p in json.loads(r.read())['paths'] if 'improve' in p])"
# 应包含 '/api/improve/cycle'

### pkill 停止时注意影响范围
`pkill -f "uvicorn app.main"` 会停掉**所有** uvicorn 进程，可能影响 RKR 等其他项目。
应该用更精确的命令：`pkill -f "uvicorn app.main:app --host 127.0.0.1 --port 8001"` 指定端口。

### .env 覆盖版本号（第5处隐藏同步点）
pydantic-settings 会从 `.env` 读取环境变量，**优先级高于** `config.py` 中的类默认值。如果 `.env` 中有旧版本号如 `GED_APP_VERSION=0.4.0`，它会静默覆盖代码中 `config.py` 设定的 `0.5.0`，导致 `admin/summary`、`ops/check` 等运行时端点返回错误版本。

**检测**：
```bash
grep APP_VERSION /Users/hua/6-产品研发/24-GEO/backend/.env
# 如果输出不为空且版本号与 version.json 不一致，就是隐藏覆盖
```

**修复**：更新 `.env` 中 `GED_APP_VERSION` 为目标版本，或删除该行让 `config.py` 默认值生效。修改后需重启 GEO 后端。

### 引擎全部显示「不可用」(drivers.__init__ 缺少 ready 字段)
`services/drivers/__init__.py` 中 `list_available_drivers()` 返回的 dict 只包含 `available_modes` 和 `default_mode`，没有 `ready` 字段。`ops.py` 和 `admin/summary` 使用 `d.get("ready")` 读取，始终返回 None/False，导致前端显示 0/9 engines ready。

**修复**：在 `list_available_drivers()` 的返回 dict 中添加 `"ready": True`（只要有 LLM 驱动就算可用）：
```python
drivers_info[engine_id] = {
    "available_modes": available_modes,
    "default_mode": ...,
    "ready": True,  # 有 LLM 驱动就算可用
}
```

## 竞品情报

完整分析见 `docs/***SECRET***.md`。

关键竞品：
- **geomonitor.app**（同名！）— $10/500cr, 6引擎
- **答序科技** — 中国诊断型GEO，极客公园评测第一
- **搜极星** — 火山引擎生态，12+模型
- **大迈数字** — 东莞同城，人工代运营 ¥16,800-36,800/年

擎观差异化：自动化SaaS（非代运营）、9引擎、浏览器真实访问、¥0 起步。

## 上线检查

运行 `references/launch-checklist.md` 中的完整检查脚本，覆盖铁律合规、页面品牌、Python 语法、API 端点、核心功能 5 个维度。

## 优化效果追踪与报告

GEO+SEO 共享一套统一报告引擎 (`services/reporting.py`)，支持:

| 功能 | API | 说明 |
|------|-----|------|
| 优化历史 | `GET /api/reporting/history` | JSONL 时间序列，记录每次优化前后对比 |
| 趋势快照 | `GET /api/reporting/trend` | 柱状图数据，可见度/排名变化 |
| 效果报告 | `GET /api/reporting/report` | 日报/周报/月报，含前后对比+建议 |
| 保存快照 | `POST /api/reporting/snapshot` | 手动保存当前状态用于趋势追踪 |

**数据存储**: `data/reports/optimization_log_{geo,seo}.jsonl` + `data/reports/snapshots_{geo,seo}.jsonl`

**前端入口**:
- GEO: `http://127.0.0.1:8001/admin` → 📋 报告 Tab
- SEO: `http://127.0.0.1:8002/admin` → 📋 报告 Tab

SEO 也通过 symlink 共享同一 `reporting.py`:
```bash
ln -sf 24-GEO/backend/app/services/reporting.py 30-SEO/backend/app/services/reporting.py
```