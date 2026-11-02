#!/bin/bash
# default state.db rebuild FTS + VACUUM（DELETE 已完成，此处只回收 FTS tombstone 空间）
set +e
LOG=/Users/hua/.hermes/logs/state_rebuild_default.log
UID_NUM=$(id -u)

echo "=== $(date '+%F %T') 开始 default rebuild+vacuum 停机 ===" | tee -a "$LOG"

# 等待 15 秒让玉芬最后一句话送达
sleep 15

echo "[1/3] 停 gateway..." | tee -a "$LOG"
launchctl bootout gui/$UID_NUM/ai.hermes.gateway 2>&1 | tee -a "$LOG"
for i in $(seq 1 30); do
  if ! pgrep -f "hermes_cli.main gateway" >/dev/null 2>&1; then
    echo "  gateway 已停止 (${i}s)" | tee -a "$LOG"
    break
  fi
  sleep 1
done

echo "[2/3] rebuild FTS + VACUUM..." | tee -a "$LOG"
cd /Users/hua/.hermes || exit 1
python3 scripts/session_rebuild.py --db /Users/hua/.hermes/state.db 2>&1 | tee -a "$LOG"

echo "[3/3] 重启 gateway..." | tee -a "$LOG"
launchctl bootstrap gui/$UID_NUM /Users/hua/Library/LaunchAgents/ai.hermes.gateway.plist 2>&1 | tee -a "$LOG"
sleep 8
pgrep -f "hermes_cli.main gateway" >/dev/null 2>&1 && echo "  ✅ gateway 已运行" | tee -a "$LOG" || echo "  ⚠️ gateway 未检测到" | tee -a "$LOG"

echo "=== $(date '+%F %T') 完成 ===" | tee -a "$LOG"
