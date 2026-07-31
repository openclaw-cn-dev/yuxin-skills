#!/bin/bash
# ~/.hermes/scripts/migrate_incremental.sh
# 增量迁移 agent 历史资料到 RKR 中转站（每周 cron 调用）
# 只迁移新增/修改过的文件（用 manifest 跟踪）

set -e
export HOME=/Users/hua
export HERMES_AGENT="${HERMES_AGENT:-cron-migrate}"

LOG_FILE="/Users/hua/.hermes/logs/migrate_incremental_cron.log"
mkdir -p "$(dirname "$LOG_FILE")"

{
  echo ""
  echo "==============================================="
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 增量迁移开始"
  echo "==============================================="

  /Users/hua/.hermes/hermes-agent/venv/bin/python3 \
    /Users/hua/.hermes/scripts/migrate_agent_artifacts.py \
    --incremental --execute

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 增量迁移结束"
} >> "$LOG_FILE" 2>&1

# 不发消息（除非出错）
if [ $? -ne 0 ]; then
  echo "❌ 增量迁移失败，请查看 $LOG_FILE"
fi
