#!/bin/bash
# launchd wrapper — 启动 Hermes gateway
# launchd 在 macOS 26.5.1 直接调用 python 报 I/O error，通过 shell 脚本绕开
# v2 2026-08-10: 去掉 exec 避免 launchd 误杀子进程
PROFILE="$1"
export HERMES_HOME="/Users/hua/.hermes"
export PATH="/Users/hua/.hermes/hermes-agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
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
