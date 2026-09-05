#!/bin/bash
# 心博士心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 心博士 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 心博士待处理任务：$result"
fi
