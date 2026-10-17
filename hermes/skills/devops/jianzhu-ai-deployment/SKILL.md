---
name: jianzhu-ai-deployment
description: 建筑AI助手部署问题排查 — 端口冲突、Docker镜像名、中文目录。触发条件：启动建筑AI助手、端口占用、Docker构建失败。
---

# 建筑AI助手部署问题排查

## 已知问题

### 1. Docker镜像名包含中文导致invalid reference format

**症状**：`docker-compose up` 报错 `invalid tag "ai_-frontend"`

**根因**：目录名「建筑AI助手_精简版」含中文，Docker Compose 用项目名 `ai_` + 服务名生成镜像名，但中文目录解析异常

**解法**：用 `-p` 指定纯ASCII项目名
```bash
cd "/Users/hua/Desktop/渔芯科技/6-产品研发/03-建筑AI助手/建筑AI助手_精简版"
docker-compose -p jianzhuai up -d --build
```

### 2. 端口8001被LookForge chromadb占用

**症状**：本地启动 backend 报错 `Port already in use`

**根因**：
```
lookforge-chromadb   0.0.0.0:8001->8000/tcp   # Docker占着8001
```

**解法**：改用其他端口（如8002），修改 `backend/main.py` 和 `docker-compose.yml`

### 3. 前端API URL硬编码

**位置**：`architecture-platform/vite.config.js`
```
VITE_API_URL=http://localhost:8001
```

如果后端改端口，前端也需要同步更新

## 快速启动（当前可用方式）

```bash
# 前端（已验证可用）
cd "/Users/hua/Desktop/渔芯科技/6-产品研发/03-建筑AI助手/建筑AI助手_精简版/architecture-platform"
npx serve -s dist -l 3001

# 后端（需解决端口冲突）
# 方案A：停掉LookForge的chromadb
docker stop lookforge-chromadb

# 方案B：改端口（如改到8002）
# 修改 backend/main.py 的 port 和 vite.config.js 的 VITE_API_URL
```

## 项目结构

```
建筑AI助手_精简版/
├── backend/           # FastAPI后端 (端口8001)
├── architecture-platform/  # Vue前端 (端口3001)
├── chromadb_data/     # Docker volumes
└── docker-compose.yml
```

## ⚠️ 重要：后端缺少用户认证模块

**发现**：前端登录/注册UI是空壳，后端**没有** `/auth/login` 和 `/auth/register` API。

后端只有这些端点：
- `GET /health` - 健康检查
- `POST /api/ai/chat` - AI对话
- `POST /api/calculator/*` - 计算器
- `POST /api/knowledge/*` - 知识库

**影响**：用户无法注册/登录，所有点击"登录"的操作都无效。

**解法**：需要开发用户认证模块（建议用JWT + 简单用户表）

## 前端入口
- Landing page: http://localhost:3001
- 14个工具页面: `建筑工具_*.html` (静态HTML)
