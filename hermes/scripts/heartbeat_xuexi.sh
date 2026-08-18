#!/bin/bash
# 学习助手心跳检查（no_agent watchdog，无任务静默）
result=$(python3 /Users/hua/.hermes/scripts/heartbeat_check.py 学习助手 2>/dev/null)
if [ -n "$result" ]; then
  echo "📋 学习助手待处理任务：$result"
fi
