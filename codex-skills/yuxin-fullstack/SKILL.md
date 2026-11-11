---
name: yuxin-fullstack
description: 渔芯自媒体运营平台全栈开发（Next.js + FastAPI + Playwright）
---

# 渔芯自媒体运营平台开发

## 项目背景
公司自媒体账号矩阵运营平台，覆盖小红书/抖音/知乎/快手。
基于多媒体矩阵平台改造，品牌名「渔芯」。

## 项目路径
`E:/公司项目资料/02_项目档案/多媒体矩阵平台/多媒体矩阵平台/`

## 技术栈
- 前端: Next.js 14, React 18, TypeScript, Tailwind, Recharts, Zustand
- 后端: FastAPI, SQLAlchemy, Pydantic, SQLite
- AI: OpenAI 兼容协议 (DeepSeek V4)
- 浏览器: Playwright

## 后端开发规范
- API 路径: `/api/{module}/{action}`
- 数据模型: `app/models/entities.py`
- 配置: `app/core/config.py` + `.env`
- 所有 API 返回 JSON
- 错误格式: `{"detail": "..."}`
- 启动: `cd backend && uvicorn app:app --reload --port 8000`

## 前端开发规范
- 页面路由: `src/app/{page}/page.tsx`
- 共享组件: `src/components/`
- 状态管理: `src/store/app.ts` (Zustand)
- API 调用: `src/lib/api.ts`
- 启动: `cd frontend && npm run dev`

## 浏览器自动化
- 基类: `app/services/social/base.py`
- 小红书: `app/services/social/xhs.py` (已实现)
- 抖音/知乎/快手: stub，待实现
- 工具: Playwright sync API

## 常见任务
1. 新增 API 端点 → 在 `app/api/` 下创建路由文件
2. 新增数据模型 → 在 `app/models/entities.py` 添加 Class
3. 新增前端页面 → `src/app/{page}/page.tsx`
4. 修改样式 → Tailwind CSS classes
5. 接入 AI → 配置 `.env` 的 LLM_API_KEY/LLM_BASE_URL/LLM_MODEL