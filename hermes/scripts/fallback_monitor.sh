#!/bin/bash
# 监控 Hermes gateway fallback 事件，发现后推飞书通知华哥
# 用法: bash fallback_monitor.sh
# 适合 cron 每 15-30 分钟跑一次

LOG_FILE="$HOME/.hermes/logs/gateway.log"
STATE_FILE="$HOME/.hermes/scripts/.fallback_last_check"
NOW=$(date +%s)

# 读上次检查时间（默认 30 分钟前）
if [ -f "$STATE_FILE" ]; then
    LAST=$(cat "$STATE_FILE")
else
    LAST=$((NOW - 1800))
fi

# 找上次检查之后的新 fallback 事件
FALLBACKS=$(awk -v last="$LAST" '
BEGIN { count=0; lines="" }
{
    # 提取日志时间戳 "2026-07-10 14:30:00"
    ts = $1 " " $2
    gsub(/,/, "", ts)
    cmd = "date -j -f \"%Y-%m-%d %H:%M:%S\" \"" ts "\" +%s 2>/dev/null"
    cmd | getline epoch
    close(cmd)
    if (epoch > last && /fallback|FALLBACK/) {
        count++
        lines = lines $0 "\n"
    }
}
END { print count; print lines }
' "$LOG_FILE" 2>/dev/null)

COUNT=$(echo "$FALLBACKS" | head -1)
DETAILS=$(echo "$FALLBACKS" | tail -n +2)

# 更新状态文件
echo "$NOW" > "$STATE_FILE"

# 有新的 fallback 事件 → 输出
if [ "$COUNT" -gt 0 ]; then
    echo "⚠️ Hermes Fallback 告警"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "数量: $COUNT 次"
    echo ""
    echo "最近事件:"
    echo "$DETAILS" | tail -5
    echo ""
    echo "当前 fallback 链: deepseek-cn → ollama-coder"
    echo "建议: 检查火山引擎套餐余额"
fi