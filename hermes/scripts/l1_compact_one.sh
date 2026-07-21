#!/bin/bash
# l1_compact_one.sh <profile>
# 压缩单个 profile 的 L1 memory
# 触发: L1 超过 2KB 时, 备份当前 + 截断到 1.5KB

if [ -z "$1" ]; then
  echo "用法: $0 <profile>"
  echo "  profile: default | afu | heidou | laomo | maodou | quant | xiaobao | zhenglishi"
  exit 1
fi

PROF=$1
if [ "$PROF" = "default" ]; then
  MEM_DIR="$HOME/.hermes/memories"
else
  MEM_DIR="$HOME/.hermes/profiles/$PROF/memories"
fi

MEM_FILE="$MEM_DIR/MEMORY.md"
USER_FILE="$MEM_DIR/USER.md"
THRESHOLD=2048  # 2KB
MAX_SIZE=1536    # 压缩后不超过 1.5KB
LOG="$HOME/.hermes/logs/l1-compact.log"

mkdir -p "$(dirname "$LOG")"

if [ ! -f "$MEM_FILE" ]; then
  echo "[$PROF] L1 不存在, 跳过"
  exit 0
fi

CURRENT_SIZE=$(wc -c < "$MEM_FILE")
echo "[$(date +%Y-%m-%d_%H:%M:%S)] [$PROF] L1 = ${CURRENT_SIZE}B (阈值 ${THRESHOLD}B)"

if [ "$CURRENT_SIZE" -le "$THRESHOLD" ]; then
  echo "[$PROF] L1 正常, 不需要压缩"
  exit 0
fi

# 超过阈值, 备份
TS=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$MEM_FILE.bak.$TS"
cp -p "$MEM_FILE" "$BACKUP_FILE"
echo "[$PROF] 备份: $BACKUP_FILE"

# 简单压缩: 保留前 70% 行
TOTAL_LINES=$(wc -l < "$MEM_FILE")
KEEP_LINES=$((TOTAL_LINES * 70 / 100))
KEEP_LINES=$((KEEP_LINES > 0 ? KEEP_LINES : 10))

head -n $KEEP_LINES "$BACKUP_FILE" > "$MEM_FILE"
NEW_SIZE=$(wc -c < "$MEM_FILE")
echo "[$PROF] 压缩: ${CURRENT_SIZE}B → ${NEW_SIZE}B (保留前 $KEEP_LINES 行)"

# 清理超过 3 个的旧备份
BACKUP_COUNT=$(ls -1 "$MEM_DIR"/MEMORY.md.bak.* 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 3 ]; then
  ls -1t "$MEM_DIR"/MEMORY.md.bak.* 2>/dev/null | tail -n +4 | xargs rm -f
  echo "[$PROF] 清理旧备份, 保留最新 3 个"
fi

# 写日志
echo "[$(date +%Y-%m-%d_%H:%M:%S)] [$PROF] L1: ${CURRENT_SIZE}B → ${NEW_SIZE}B (阈值 ${THRESHOLD}B)" >> "$LOG"
