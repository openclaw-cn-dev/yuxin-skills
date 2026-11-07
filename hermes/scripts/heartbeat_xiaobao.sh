#!/bin/bash
# 小宝心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 小宝 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 小宝待处理任务：$result"
fi
