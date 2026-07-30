# Codex 核心编码规范
> 来源: 渔芯项目开发习惯与准则 · 自动同步

## 沟通风格
- 直接、结果导向。不反复确认。
- "自己测" = 直接测 / "执行" = 立即动手
- 看到结果先汇报再问

## 前端项目铁律 ⚠️

**严禁直接双击 HTML 打开前端项目！** `file://` 协议下浏览器禁止 cookie/storage/fetch。

每个前端项目必须提供启动方式：
```bash
# 快捷启动（任意项目）
python3 ~/.hermes/scripts/quick_serve.py [端口]
```

## Python 规范
- 4空格缩进 + snake_case + type hints + Google docstring
- 禁止 wildcard import
- 依赖: uv + pyproject.toml（优先）
- 测试: pytest, 核心模块 >80% 覆盖率
- 测试命名: test_<功能>_<场景>_<预期结果>

## JS/TS 规范
- 2空格缩进 + camelCase + strict 模式
- 依赖: pnpm 优先, package-lock.json 必提交
- 测试: vitest/vitest Browser Mode

## Git 规范
- 分支: feature/xxx / fix/xxx / chore/xxx
- 提交: <type>(<scope>): <描述>
- 禁止: git push --force main, 直推 main, rm -rf

## 命令禁区
- rm -rf, git push --force main
- 改 ~/.ssh/ ~/.aws/ /etc/
- sudo, chmod 777

## 效率原则
- 多任务并行（开多个 tmux）
- 一次性任务: codex exec "任务" --sandbox danger-full-access
- /context >70% 立即压缩

## 技术栈 (2026)
- 前端: Zustand + TanStack Query + shadcn/ui + Tailwind + Vite 8
- 后端: FastAPI + SQLAlchemy 2.0 + pgvector + Redis
- AI: DeepSeek V4 Pro (主力) + Claude (备用)
- 部署: Cloudflare Pages + Workers + Fly.io + Supabase
- 工具链: Ruff + uv + Biome + Oxc
