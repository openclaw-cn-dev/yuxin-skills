#!/bin/bash
# Codex → yuxin-skills GitHub 增量同步 (hourly cron 包装)
# 仅跑 step 1 (版本) + step 6 (GitHub sync)
set -e
export HERMES_HOME=/Users/hua/.hermes
exec /Users/hua/.hermes/hermes-agent/venv/bin/python3 \
  /Users/hua/.hermes/scripts/codex_self_evolution.py --sync-only