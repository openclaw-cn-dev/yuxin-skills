---
name: local-dev-server
description: 本地启动和验证全栈开发项目（FastAPI + Vite/React/PWA + 独立 Python web server）。覆盖项目查找、Python venv 路径坑、后台进程管理、前后端健康检查、**Codex 前端 file:// 协议陷阱（cookie/storage API 被浏览器阻止）**、通用 quick_serve.py 自动检测工具、React+Vite 前端可靠模式（login/auth flow、HMR 存活、API client 反模式、SSE streaming — 原 react-vite-patterns 已并入 references/）。触发条件：用户说「打开/启动/运行 X 工具」「帮我打开昨天弄好的 X」「X 在哪」「前端打不开」「双击 HTML 没反应」「SecurityError cookie」「React HMR 老是断」「SSE 流断」, 任何需要从已有代码运行本地开发服务器或调试 React+Vite 应用场景。
triggers:
  - 打开/启动/运行
  - 前端打不开
  - 双击HTML没反应
  - SecurityError cookie
  - file:// 协议
  - Codex 前端 白屏
  - quick_serve
  - 本地启动
  - React Vite HMR
  - login auth flow
  - SSE streaming
---

# 本地全栈项目启动与验证

> 📦 **2026-10-09 curator 合并**：原独立 skill `react-vite-patterns` 整档收纳至 `references/react-vite-patterns/` — React + Vite 前端可靠模式（login/auth flow、HMR 存活、API client 反模式、表单处理、SSE streaming 前后端接线见其 `references/sse-live-drawing.md`）。用 Vite dev server 构建/调试 React 应用时,先跑本 skill 的启动/健康检查,前端行为问题再翻 `references/react-vite-patterns/`。

## 1. 找到项目（最重要！）

用户说的项目名可能和目录名不完全一致。三步搜索法：

```bash
# 1) 找目录（中文/英文/拼音都试）
find /Users/hua -maxdepth 3 -type d -iname "*iching*" 2>/dev/null
find /Users/hua -maxdepth 3 -type d -iname "*八卦*" 2>/dev/null

# 2) 找文件（最全，但慢）
find /Users/hua -maxdepth 6 -type f \( -iname "*iching*" -o -iname "*i-ching*" \
  -o -iname "*bagua*" -o -iname "*周易*" -o -iname "*八卦*" \) \
  2>/dev/null | grep -v "venv/\|backups/\|node_modules/\|site-packages/\|\.git/" | head -30

# 3) 检查 session_search 查历史记录 — 用户可能昨天才建的项目
session_search(query="八卦预测工具 国际版 开发")
```

**渔业科技项目目录惯例**：
- 项目目录在 `~/` 下：`~/02-八卦预测工具-国际版/`、`~/6-产品研发/...`
- 中文目录名可能包含数字排序前缀如 `02-`
- 中文目录名可能被某些 CLI 工具（如 Claude Code）拒绝 —— 用符号链接或直接终端操作

## 2. 确认项目结构

```bash
# 查看源码文件（非 node_modules / venv）
find <project_dir> -type f ! -path "*node_modules*" ! -path "*__pycache__*" \
  ! -path "*.venv*" ! -path "*.git*" 2>/dev/null | sort | head -40

# 关键文件检查：
ls <project_dir>/backend/app/main.py  # FastAPI 入口
ls <project_dir>/frontend/package.json  # Vite/React 前端
ls <project_dir>/pyproject.toml        # 项目 Python 依赖
ls <project_dir>/docker-compose.yml    # Docker 编排
```

## 3. 启动后端（FastAPI/uvicorn）

### 核心陷阱：必须用项目 venv 的 Python，不是系统 Python

```bash
# ❌ 错误（系统 Python 找不到项目依赖）
uvicorn app.main:app --host 0.0.0.0 --port 8000
# -> ModuleNotFoundError: No module named 'app'

# ✅ 正确（用项目 venv）
cd <project_dir>
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

验证：
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000
curl -s http://localhost:8000/api/v1/health
curl -s -L http://localhost:8000/api/v1/health  # 如果 307 需要 -L
```

### 将后端放后台

```bash
# 在 terminal(background=true) 中启动
cd /Users/hua/<project> && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

然后 `sleep 3-5` 等待启动，再用 curl 验证。

## 4. 启动前端（Vite）

```bash
cd <project_dir>/frontend
npx vite --host 0.0.0.0 --port 5173
```

验证：`curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` 应返回 200。

## 5. 测试 API（以 I Ching Oracle 为例）

```bash
# 随机起卦
curl -s -L -X POST http://localhost:8000/api/v1/cast/random \
  -H "Content-Type: application/json" -d '{}'

# 时间起卦
curl -s -L -X POST "http://localhost:8000/api/v1/cast/time?dt=2026-06-28T15:30:00"

# 非 I Ching 项目 — 测试项目的核心端点
curl -s http://localhost:8000/  # root
curl -s http://localhost:8000/docs  # Swagger UI
```

## 6. 浏览器验证

如果用户想看界面，用 `browser_navigate` 访问 `http://localhost:5173/` 或 `http://localhost:5173/`。注意：
- Vite dev server 默认端口 5173（不是 3000/8080）
- 用 `browser_snapshot` 快速确认页面渲染内容
- 用 `browser_vision` 获取视觉截图（如果可用）

## 8. 检查前端 proxy 目标端口

**核心陷阱**: `frontend/vite.config.ts` 中的 `proxy` 段可能指向和后端实际端口不同的地址。

```typescript
// vite.config.ts 示例
server: {
  port: 5173,
  proxy: {
    '/api': { target: 'http://localhost:8002', changeOrigin: true },
    //                     ^^^^^^^^^^^^^ 这个端口可能不是后端实际端口
  },
}
```

如果前端 proxy target（如 `8002`）和后端实际运行端口（如 `8000`）不一致，前端发起的 `/api/*` 请求会全部 404 或连不上。

**修复方法**：
1. 查看 `vite.config.ts` 的 `proxy.target` 端口号
2. 确认后端实际端口（用 `lsof -i :PORT` 或看 uvicorn 输出）
3. 如果对不上，要么改 `vite.config.ts` 里的 target 端口，要么把后端调到匹配的端口

**最佳实践**: 前后端项目初建时就约定好 proxy target 端口，写在 README 或 CLAUDE.md 里。如果前后端由不同会话开发，代理目标端口一致性尤其容易出问题。

## 7. 通用快速启动（quick_serve.py）\n\n针对多项目、多框架的自动检测启动工具：\n\n```bash\npython3 ~/.hermes/scripts/quick_serve.py [端口]\n```\n\n自动检测并启动：\n- Vite/React/Vue/Svelte → `npm run dev`\n- package.json dev/preview script → `npm run dev`\n- FastAPI (`backend/app/main.py`, `app/main.py`, `main.py`) → `uvicorn`\n- 独立 Python web server (`voice_center.py` 等含 FastAPI+HTML 的模式)\n- dist/ 目录 → `python3 http.server`\n- 静态 HTML → `python3 http.server`\n\n## 8. Codex 前端 `file://` 协议陷阱 ⚠️\n\n**Codex 生成的前端项目双击 HTML 打开 100% 会失败**。\n\n原因：`file://` 协议下浏览器阻止 `document.cookie`、`localStorage`、`sessionStorage`、`fetch()` 等 Web API。\n\n报错特征：\n```\nUncaught SecurityError: Failed to read the 'cookie' property from 'Document':\nAccess is denied for this document.\n```\n\n**解决方案**：\n1. 每个 Codex 前端项目必须包含 `start.sh` 或启动命令\n2. 使用 `quick_serve.py` 自动检测并启动 HTTP 服务\n3. 绝对不要生成 \"双击 index.html 打开\" 的说明\n\n**在 Codex AGENTS.md 中的铁律**（已写入 ~/.codex/AGENTS.md §前端项目铁律）：\n> Codex 生成的前端项目严禁直接双击 HTML 打开！每个前端项目必须提供启动方式。\n\n## 配套资源

- `scripts/quick_serve.py` — 通用项目自动检测启动脚本
- `references/***SECRET***.md` — Codex 前端 file:// 协议修复详细模式

## 常见 Pitfalls

1. **uvicorn 用错 Python**：系统 Python 的 uvicorn 找不到项目模块。必须用 `project/.venv/bin/uvicorn`
2. **端口 5173 被占**：先 `lsof -i :5173` 检查，必要时改端口。**已知占用**：知识库的 python-http-server 也在 5173。移到 5174/5175 即可。
3. **项目目录含中文**：CLI 中路径用双引号包裹，或者用绝对路径
4. **后端启动但不健康**：检查 .env 中的 DATABASE_URL 等依赖服务（PostgreSQL/Redis）是否启动
5. **前端 CORS 错误**：后端需要配置 `allow_origins` 包含前端地址
6. **响应是 307 重定向**：加 `curl -L` 跟随重定向
7. **后台进程无声死亡**：`process(action='poll')` 检查进程状态，`process(action='log')` 看完整日志
8. **Vite proxy target 和后端实际端口不同**：前端 `vite.config.ts` 里 `proxy: { '/api': { target: 'http://localhost:XXXX' } }` 可能和后端实际端口不一致（尤其前后端由不同人/会话开发时）。**启动前必读 `vite.config.ts` 的 `proxy` 段**，如果目标端口对不上，要么改 vite.config 要么改后端端口。不改的话前端发 `/api/*` 请求会 404 或连不上。
9. **FastAPI read_text() 缓存 HTML**：`frontend.py` 中常见模式是在模块加载时 `path.read_text()` 赋值给变量，之后路由返回该变量。改了前端 HTML 文件后必须**重启 uvicorn**，否则 curl 返回的永远是旧版。验证三步：① `grep -c "新内容" frontend/xxx.html` 确认磁盘正确 ② `pkill -f "uvicorn.*PORT"` 杀旧进程 ③ 重启 `python -m uvicorn app.main:app --port PORT &` ④ `curl` 确认。
10. **僵尸进程占端口 + 旧通知混淆**：多次尝试启动服务会产生多个僵尸进程（启动失败但旧进程仍监听），新进程报 `Errno 48 address already in use`。清理：`pkill -f "uvicorn.*PORT"`（比 `lsof -ti :PORT | xargs kill` 更可靠，`lsof` 在残缺 PATH 环境不可用）。旧僵尸进程退出通知 `[IMPORTANT: Background process ... completed]` 是历史日志，不代表当前服务状态——始终用当前会话 `curl` 验证。
11. **SQLite 老库加新列：CREATE TABLE IF NOT EXISTS 不会 ALTER**：给已有 `.db` 的项目加表结构字段时，`SCHEMA` 里的 `CREATE TABLE IF NOT EXISTS ...` 对**已存在的表不生效**，新列不会补上；服务不重启时一切正常，重启后触到新列的端点直接 `sqlite3.OperationalError: no such column: X`（且容易是"加了代码没跑迁移"的延迟爆炸）。修法：在 `db()` 连接函数里做幂等迁移——`cols = {r["name"] for r in conn.execute("PRAGMA table_info(表名)")}`，缺列就 `ALTER TABLE ... ADD COLUMN ... DEFAULT`。每个新列一次 PRAGMA 检查，用户无感。2026-08-29 情商助手 auto_send 列实测踩中。

## 已吸收：Pydantic v2 venv 搭建与 RecursionError 规避（原 python-pydantic-venv-setup）
2026-09-02 curator 合并：整档见 `references/pydantic-venv-setup/`。macOS 上 FastAPI/Pydantic v2 项目的 venv 搭建 + `Optional[Literal]` 字段触发 RecursionError / SchemaGenerationError 的诊断与绕过——与本文件 §3 的 venv 路径坑互补，搭 FastAPI 项目 venv 时两处都查。
