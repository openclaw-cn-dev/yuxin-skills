#!/bin/bash
# 玉芬自进化守护 - 每 2 小时执行一次信号扫描 + 行动
# 启动前先检查华哥是否需要被汇报(单次执行 < 5 分钟)
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
LOG="$HERMES_HOME/logs/yva-self-evolution.log"
STATE_DIR="$HERMES_HOME/state"
mkdir -p "$HERMES_HOME/logs" "$STATE_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 玉芬自进化扫描开始 ===" | tee -a "$LOG"

# 1. RKR 积压
PENDING=$(docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -c "SELECT COUNT(*) FROM documents WHERE processing_status='uploaded';" 2>/dev/null | tr -d ' ' || echo 0)
FAILED=$(docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -c "SELECT COUNT(*) FROM documents WHERE processing_status='failed';" 2>/dev/null | tr -d ' ' || echo 0)
echo "[$(date '+%H:%M:%S')] RKR 积压 uploaded=$PENDING failed=$FAILED" | tee -a "$LOG"

# 2. cron 失败
FAIL_CRON=$(hermes cron list 2>/dev/null | grep -c "error:" || true)
echo "[$(date '+%H:%M:%S')] cron 失败任务数: $FAIL_CRON" | tee -a "$LOG"

# 3. Hermes Gateway
GW_PID=$(ps aux | grep "hermes_cli.main gateway" | grep -v grep | awk '{print $2}' | head -1)
echo "[$(date '+%H:%M:%S')] Hermes Gateway PID: $GW_PID" | tee -a "$LOG"

# 4. 内存
FREE_MEM=$(vm_stat | awk '/free/ {print $3}' | sed 's/\.//' | head -1)
echo "[$(date '+%H:%M:%S')] 内存空闲页数: $FREE_MEM" | tee -a "$LOG"

# 5. 写状态
cat > "$STATE_DIR/yva-self-evolution.json" <<EOF
{
  "ts": "$(date -Iseconds)",
  "rkr_pending": $PENDING,
  "rkr_failed": $FAILED,
  "cron_failed": $FAIL_CRON,
  "hermes_pid": $GW_PID,
  "free_mem_pages": $FREE_MEM
}
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 扫描完成,状态已保存 ===" | tee -a "$LOG"

# 静默退出 (除非有需要立即处理的紧急情况)
# 这里可以加自动修复逻辑,但保守起见先只汇报
exit 0
