#!/bin/bash
# session_archive_all.sh
# 遍历 8 profile 归档旧 session
# 触发: cron (建议每周日凌晨 3 点)

LOG="$HOME/.hermes/logs/session-archive.log"
mkdir -p "$(dirname "$LOG")"

echo "[$(date +%Y-%m-%d_%H:%M:%S)] session 归档全员" >> "$LOG"

for prof in default afu heidou laomo maodou quant xiaobao zhenglishi; do
  bash ~/.hermes/scripts/session_archive_one.sh "$prof" >> "$LOG" 2>&1
done
