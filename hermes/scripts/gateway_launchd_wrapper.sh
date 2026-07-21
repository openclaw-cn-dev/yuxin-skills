#!/bin/bash
# launchd wrapper — 启动 Hermes gateway
# launchd 在 macOS 26.5.1 直接调用 python 报 I/O error，通过 shell 脚本绕开
PROFILE="$1"
export HERMES_HOME="/Users/hua/.hermes"
export PATH="/Users/hua/.hermes/hermes-agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
export VIRTUAL_ENV="/Users/hua/.hermes/hermes-agent/venv"

exec /Users/hua/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run \
  --profile "$PROFILE" --replace
