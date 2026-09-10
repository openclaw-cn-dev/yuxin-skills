#!/bin/bash
# launchd wrapper — 启动 Hermes gateway
# launchd 在 macOS 26.5.1 直接调用 python 报 I/O error，通过 shell 脚本绕开
# v2 2026-08-10: 去掉 exec 避免 launchd 误杀子进程
PROFILE="$1"
export HERMES_HOME="/Users/hua/.hermes"
# v3 2026-09-06 玉芬: 补 ~/.local/bin(claude/codex CLI)与 homebrew; 显式指全局凭据目录
# 根因: 旧 PATH 使 quant 等 profile 内 claude/codex command not found (宽博士无法走代码铁律调用链)
export PATH="/Users/hua/.hermes/hermes-agent/venv/bin:/usr/local/bin:/Users/hua/.local/bin:/opt/homebrew/bin:/usr/bin:/bin"
export CODEX_HOME="/Users/hua/.codex"
export CLAUDE_CONFIG_DIR="/Users/hua/.claude"
export VIRTUAL_ENV="/Users/hua/.hermes/hermes-agent/venv"

# 转发信号给 python 子进程
PYTHON_PID=""
trap 'kill -TERM $PYTHON_PID 2>/dev/null; exit 0' TERM INT

/Users/hua/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run \
  --replace \
  --profile "$PROFILE" &
PYTHON_PID=$!
wait $PYTHON_PID
