#!/bin/bash
# Codex → yuxin-skills GitHub 增量同步 (hourly cron 包装)
# 仅跑 step 1 (版本) + step 6 (GitHub sync)
# 2026-11-11: Mac 路径残留修复 (HERMES_HOME + venv python → Windows 本机路径)
set -e
export HERMES_HOME="D:/yuxin/hermes"
exec python "D:/yuxin/hermes/scripts/codex_self_evolution.py" --sync-only
