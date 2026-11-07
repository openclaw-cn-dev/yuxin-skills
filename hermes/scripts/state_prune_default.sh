#!/bin/bash
# default state.db 停机瘦身：停 gateway → prune → rebuild FTS → vacuum → 重启 gateway
# 独立于 gateway 运行（后台进程），确保最终一定重启 gateway
set +e
LOG=/Users/hua/.hermes/logs/state_prune_default.log
UID_NUM=$(id -u)

echo "=== $(date '+%F %T') 开始 default 停机瘦身 ===" | tee -a "$LOG"

# 等待 15 秒，让玉芬最后一句话送达
sleep 15

echo "[1/3] 停 gateway (ai.hermes.gateway)..." | tee -a "$LOG"
launchctl bootout gui/$UID_NUM/ai.hermes.gateway 2>&1 | tee -a "$LOG"
sleep 5

echo "[2/3] prune default state.db..." | tee -a "$LOG"
cd /Users/hua/.hermes || exit 1
python3 scripts/session_prune.py \
  --db /Users/hua/.hermes/state.db \
  --archive /Users/hua/.hermes/session_archive/default.jsonl \
  --cron-days 30 2>&1 | tee -a "$LOG"

echo "[3/3] 重启 gateway..." | tee -a "$LOG"
launchctl bootstrap gui/$UID_NUM /Users/hua/Library/LaunchAgents/ai.hermes.gateway.plist 2>&1 | tee -a "$LOG"
sleep 5

# 确认 gateway 起来了
echo "gateway 进程检查:" | tee -a "$LOG"
pgrep -f "hermes_cli.main gateway" >/dev/null && echo "  ✅ gateway 已运行" | tee -a "$LOG" || echo "  ⚠️ gateway 未检测到" | tee -a "$LOG"

echo "=== $(date '+%F %T') 完成 ===" | tee -a "$LOG"
