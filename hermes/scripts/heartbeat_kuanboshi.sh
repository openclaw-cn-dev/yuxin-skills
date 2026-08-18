#!/bin/bash
# 宽博士心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 宽博士 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 宽博士待处理任务：$result"
fi
