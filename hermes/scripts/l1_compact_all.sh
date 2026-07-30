#!/bin/bash
# l1_compact_all.sh
# 遍历 8 profile, 检查 L1 容量, 超阈值自动压缩
# 触发: cron (建议每 4 小时)

LOG="$HOME/.hermes/logs/l1-compact.log"
mkdir -p "$(dirname "$LOG")"

echo "[$(date +%Y-%m-%d_%H:%M:%S)] L1 compact 全员检查" >> "$LOG"

for prof in default afu heidou laomo maodou quant xiaobao zhenglishi; do
  bash ~/.hermes/scripts/l1_compact_one.sh "$prof" >> "$LOG" 2>&1
done
