#!/bin/bash
# 阿福心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 阿福 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 阿福待处理任务：$result"
fi
