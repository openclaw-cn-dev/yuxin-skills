---
name: tokencut
description: >
  本地 CLI + MCP，把 Codex 冗长 tool 输出折叠成可恢复的短摘要（docker 18360→107、cargo 3795→185）。
  当 Codex 跑 pytest / docker build / cargo test 输出几万行 token 时用 — 用 `tc fold` 或 MCP server。
  工具：uv 装的 `tokencut` CLI 或 MCP server。装后跑 `uv tool install tokencut`。
license: MIT
---

# TokenCut — 折叠 Codex 冗长 tool 输出

> 把 docker 18,360→107 行 / cargo 3,795→185 行 / pytest 1,562→174 行 — 信号留着，噪声砍掉。

## 触发

- Codex `terminal` 输出几万行 token 撑爆 context
- pytest / cargo / docker / eslint / mypy 测试输出刷屏
- 想看"测试失败原因"但不想读全部 stdout

## 装

```bash
uv tool install tokencut
```

## 用法

```bash
# 折叠 docker build 输出
docker build . 2>&1 | tc fold
# pytest 输出折叠
pytest -v 2>&1 | tc fold --keep-errors
# 看折叠摘要
tc fold < big.log
```

## MCP server

启动 MCP server 后挂 Codex：

```bash
tokencut mcp serve
```

## 跟老大 cron 适配

- 9 点 cron 跑 Codex 时输出极长 → 装 tokencut 后接 pipe 折叠
- 老大报"context 撑爆" → 第一动作 `pip install tokencut`

