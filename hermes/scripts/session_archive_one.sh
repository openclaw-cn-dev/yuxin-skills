#!/bin/bash
# session_archive_one.sh <profile>
# 归档指定 profile 的旧 session
# 策略:
#   - 7 天内: 保留 (active)
#   - 30 天内: gzip 压缩 (active 还能检索)
#   - 90 天内: 移到 sessions_archive/
#   - 超过 90 天: 移到 sessions_old/ (可手动删)

if [ -z "$1" ]; then
  echo "用法: $0 <profile>"
  echo "  profile: default | afu | heidou | laomo | maodou | quant | xiaobao | zhenglishi"
  exit 1
fi

PROF=$1
if [ "$PROF" = "default" ]; then
  SESS_DIR="$HOME/.hermes/sessions"
else
  SESS_DIR="$HOME/.hermes/profiles/$PROF/sessions"
fi

LOG="$HOME/.hermes/logs/session-archive.log"
mkdir -p "$(dirname "$LOG")"

if [ ! -d "$SESS_DIR" ]; then
  echo "[$PROF] sessions 目录不存在, 跳过"
  exit 0
fi

ARCHIVE_DIR="$SESS_DIR/../sessions_archive"
OLD_DIR="$SESS_DIR/../sessions_old"
mkdir -p "$ARCHIVE_DIR" "$OLD_DIR"

COMPRESS_COUNT=0
MOVE_ARCHIVE=0
MOVE_OLD=0
SPACE_SAVED=0

# 7 天前
CUTOFF_7=$(date -v-7d +%Y%m%d 2>/dev/null || date -d "7 days ago" +%Y%m%d)
# 30 天前
CUTOFF_30=$(date -v-30d +%Y%m%d 2>/dev/null || date -d "30 days ago" +%Y%m%d)
# 90 天前
CUTOFF_90=$(date -v-90d +%Y%m%d 2>/dev/null || date -d "90 days ago" +%Y%m%d)

echo "[$(date +%Y-%m-%d_%H:%M:%S)] [$PROF] session 归档开始" >> "$LOG"
echo "[$PROF] 阈值: 7d=$CUTOFF_7 30d=$CUTOFF_30 90d=$CUTOFF_90"

for f in "$SESS_DIR"/*.jsonl "$SESS_DIR"/*.json; do
  [ -f "$f" ] || continue
  filename=$(basename "$f")
  # 文件名格式: YYYYMMDD_xxx...
  DATE_PREFIX=$(echo "$filename" | grep -oE "20[0-9]{6}" | head -1)
  [ -z "$DATE_PREFIX" ] && continue

  if [ "$DATE_PREFIX" -lt "$CUTOFF_90" ]; then
    # 超过 90 天 → 移到 old
    SIZE=$(stat -f%z "$f" 2>/dev/null)
    mv "$f" "$OLD_DIR/$filename" 2>/dev/null
    if [ $? -eq 0 ]; then
      MOVE_OLD=$((MOVE_OLD + 1))
      SPACE_SAVED=$((SPACE_SAVED + SIZE))
    fi
  elif [ "$DATE_PREFIX" -lt "$CUTOFF_30" ]; then
    # 30-90 天 → 移到 archive
    SIZE=$(stat -f%z "$f" 2>/dev/null)
    mv "$f" "$ARCHIVE_DIR/$filename" 2>/dev/null
    if [ $? -eq 0 ]; then
      MOVE_ARCHIVE=$((MOVE_ARCHIVE + 1))
      SPACE_SAVED=$((SPACE_SAVED + SIZE))
    fi
  elif [ "$DATE_PREFIX" -lt "$CUTOFF_7" ]; then
    # 7-30 天 → gzip 压缩
    if [[ ! "$filename" =~ \.gz$ ]]; then
      SIZE_BEFORE=$(stat -f%z "$f" 2>/dev/null)
      gzip "$f" 2>/dev/null
      if [ -f "${f}.gz" ]; then
        SIZE_AFTER=$(stat -f%z "${f}.gz" 2>/dev/null)
        SAVED=$((SIZE_BEFORE - SIZE_AFTER))
        COMPRESS_COUNT=$((COMPRESS_COUNT + 1))
        SPACE_SAVED=$((SPACE_SAVED + SAVED))
      fi
    fi
  fi
done

# 报告
SPACE_MB=$((SPACE_SAVED / 1024 / 1024))
echo "[$PROF] 完成: 压缩 $COMPRESS_COUNT 个, 移到 archive $MOVE_ARCHIVE 个, 移到 old $MOVE_OLD 个, 节省 ${SPACE_MB}MB"
echo "[$(date +%Y-%m-%d_%H:%M:%S)] [$PROF] 完成: 压缩 $COMPRESS_COUNT, archive $MOVE_ARCHIVE, old $MOVE_OLD, 节省 ${SPACE_MB}MB" >> "$LOG"
