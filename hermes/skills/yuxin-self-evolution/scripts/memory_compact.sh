#!/usr/bin/env bash
# memory_compact.sh — Memory 架构 v2.0 自动 compaction
# 触发条件：L1 字节 > 4500
# 行为：合并/精简/归档老条目
# cron：每 4 小时（d845f193fdd5）

set -e

MEM_DIR="$HOME/.hermes/memories"
L1_SIZE=$(wc -c "$MEM_DIR/MEMORY.md" "$MEM_DIR/USER.md" 2>/dev/null | tail -1 | awk '{print $1}')
THRESHOLD=4500

if [ "$L1_SIZE" -gt "$THRESHOLD" ]; then
    # 备份
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp -p "$MEM_DIR/MEMORY.md" "$MEM_DIR/MEMORY.md.bak.$TIMESTAMP"
    cp -p "$MEM_DIR/USER.md" "$MEM_DIR/USER.md.bak.$TIMESTAMP"

    # 调用 hermes memory compact
    echo "yes" | hermes memory compact || true

    NEW_SIZE=$(wc -c "$MEM_DIR/MEMORY.md" "$MEM_DIR/USER.md" 2>/dev/null | tail -1 | awk '{print $1}')

    if [ "$NEW_SIZE" -lt "$L1_SIZE" ]; then
        echo "[memory_compact] ✅ $L1_SIZE → $NEW_SIZE (saved $((L1_SIZE - NEW_SIZE))B)"
    else
        echo "[memory_compact] ⚠️ compact failed, restoring backup"
        mv "$MEM_DIR/MEMORY.md.bak.$TIMESTAMP" "$MEM_DIR/MEMORY.md"
        mv "$MEM_DIR/USER.md.bak.$TIMESTAMP" "$MEM_DIR/USER.md"
    fi
else
    echo "[memory_compact] OK ($L1_SIZE / $THRESHOLD B)"
fi
