#!/bin/bash
# 玉芬主动巡视脚本 - 多 Profile API Key & Cron 健康检查
# 由 cron 玉芬-主动巡视汇报 每日触发
# 也可手动执行: ~/.hermes/scripts/yuxin_patrol.sh

PROFILES="default afu heidou laomo maodou quant xiaobao zhenglishi"
REPORT=""
ERRORS=0
WARNINGS=0
NOW_STR=$(date '+%Y-%m-%d %H:%M:%S')

# 1. 检查所有 profile 的 MINIMAX_CN_API_KEY 是否一致
echo "=== [1] API Key 一致性检查 ==="
DEFAULT_KEY=""
if [ -f "$HOME/.hermes/.env" ]; then
    DEFAULT_KEY=$(grep '^MINIMAX_CN_API_KEY=***' "$HOME/.hermes/.env" | head -1 | cut -d= -f2-)
fi
if [ -z "$DEFAULT_KEY" ]; then
    REPORT+="[CRITICAL] default .env 没有 MINIMAX_CN_API_KEY"$'\n'
    ERRORS=$((ERRORS+1))
else
    echo "Default key: ${DEFAULT_KEY:0:8}...${DEFAULT_KEY: -4} (len=${#DEFAULT_KEY})"
    REPORT+="Default MINIMAX key: ${DEFAULT_KEY:0:8}...${DEFAULT_KEY: -4} (len=${#DEFAULT_KEY})"$'\n'
fi

for prof in $PROFILES; do
    env="$HOME/.hermes/profiles/$prof/.env"
    if [ ! -f "$env" ]; then
        REPORT+="[WARN] $prof: .env 文件不存在"$'\n'
        WARNINGS=$((WARNINGS+1))
        continue
    fi
    key=$(grep '^MINIMAX_CN_API_KEY=***' "$env" | head -1 | cut -d= -f2-)
    if [ -z "$key" ]; then
        REPORT+="[ERROR] $prof: MINIMAX_CN_API_KEY 缺失"$'\n'
        ERRORS=$((ERRORS+1))
    elif [ "$key" != "$DEFAULT_KEY" ]; then
        REPORT+="[ERROR] $prof: MINIMAX key 与 default 不一致 (${key:0:8} vs ${DEFAULT_KEY:0:8})"$'\n'
        ERRORS=$((ERRORS+1))
    else
        echo "OK $prof: key 一致"
    fi
done

# 2. 检查每个 profile cron 最近一次运行的错误
echo ""
echo "=== [2] Cron 健康检查 (近 24h error) ==="
for prof in $PROFILES; do
    cron_out=$(HERMES_PROFILE=$prof hermes cron list 2>&1 || echo "")
    err_lines=$(echo "$cron_out" | grep -E "Last run.*error:" | grep -v "ok" || true)
    if [ -n "$err_lines" ]; then
        err_count=$(echo "$err_lines" | wc -l | tr -d ' ')
        REPORT+="[WARN] $prof: $err_count 个 cron 最近 error"$'\n'
        REPORT+="$err_lines"$'\n'
        WARNINGS=$((WARNINGS+1))
    else
        echo "OK $prof: 所有 cron ok"
    fi
done

# 3. 检查关键 cron 触发频率 (超 24h 未跑)
echo ""
echo "=== [3] 关键 Cron 触发频率 ==="
for prof in $PROFILES; do
    cron_out=$(HERMES_PROFILE=$prof hermes cron list 2>&1 || echo "")
    while IFS= read -r line; do
        if [[ "$line" =~ Last\ run:\ ([0-9-]+)T([0-9:]+)\.[0-9]+  ]]; then
            last_date="${BASH_REMATCH[1]} ${BASH_REMATCH[2]}"
            last_ts=$(date -j -f "%Y-%m-%d %H:%M:%S" "$last_date" "+%s" 2>/dev/null || echo 0)
            if [ -n "$last_ts" ] && [ "$last_ts" != "0" ]; then
                now_ts=$(date "+%s")
                diff=$((now_ts - last_ts))
                if [ $diff -gt 86400 ]; then
                    REPORT+="[WARN] $prof: cron 超 24h 未跑 ($line)"$'\n'
                    WARNINGS=$((WARNINGS+1))
                fi
            fi
        fi
    done <<< "$cron_out"
done

# 4. 输出汇总
echo ""
echo "=========================================="
echo "[玉芬巡视报告] $NOW_STR"
echo "ERRORS=$ERRORS  WARNINGS=$WARNINGS"
echo "=========================================="
printf "%b" "$REPORT"

[ $ERRORS -eq 0 ] || exit 2
exit 0