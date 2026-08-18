#!/bin/bash
# 黑豆心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 黑豆 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 黑豆待处理任务：$result"
fi
