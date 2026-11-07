#!/bin/bash
# 玉芬主动巡视脚本 - 多 Profile API Key & Cron 健康检查
# 由 cron 玉芬-主动巡视汇报 触发 (未来挂接)
# 也可手动执行: ~/.hermes/scripts/yuxin_patrol.sh
# 创建: 2026-06-27 (zhenglishi 学习助手 cron 修复实战)
# 维护: 玉芬（华哥 6-27 授权"管理与巡视是你的工作"）

PROFILES="default afu heidou laomo maodou quant xiaobao zhenglishi"
REPORT=""
ERRORS=0
WARNINGS=0
NOW_STR=$(date '+%Y-%m-%d %H:%M:%S')

# 1. default 的 inline key 检查（路径特殊，在根目录）
echo "=== [1] default profile inline key 检查 ==="
default_cfg="$HOME/.hermes/config.yaml"
if [ -f "$default_cfg" ]; then
    inline_count=$(grep -cF "sk-cp-" "$default_cfg" 2>/dev/null || echo 0)
    echo "default inline sk-cp count: $inline_count"
    if [ "$inline_count" -lt 10 ]; then
        REPORT+="[ERROR] default inline sk-cp 不足 (count=$inline_count)"$'\n'
        ERRORS=$((ERRORS+1))
    fi
else
    REPORT+="[CRITICAL] ~/.hermes/config.yaml 不存在"$'\n'
    ERRORS=$((ERRORS+1))
fi

# 2. 7 profile .env key 一致性（用 grep -F 防 * regex 坑）
echo ""
echo "=== [2] 7 profile .env MINIMAX_CN_API_KEY 一致性 ==="
for prof in afu heidou laomo maodou quant xiaobao zhenglishi; do
    env="$HOME/.hermes/profiles/$prof/.env"
    if [ ! -f "$env" ]; then
        REPORT+="[ERROR] $prof: .env 文件不存在"$'\n'
        ERRORS=$((ERRORS+1))
        continue
    fi
    # 用行首锚定避免历史脱敏占位符问题（-F 'MINIMAX_CN_API_KEY=***' 引号不闭合会导致整脚本语法错误）
    key=$(grep '^MINIMAX_CN_API_KEY=' "$env" 2>/dev/null | head -1 | cut -d= -f2-)
    if [ -z "$key" ]; then
        REPORT+="[ERROR] $prof: MINIMAX_CN_API_KEY 缺失"$'\n'
        ERRORS=$((ERRORS+1))
    else
        echo "OK $prof: ${key:0:8}...${key: -4} (len=${#key})"
    fi
done

# 3. 每个 profile cron 最近错误检查
echo ""
echo "=== [3] 8 profile cron 健康检查 ==="
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

# 4. cron 超 24h 未跑检查
echo ""
echo "=== [4] Cron 超 24h 未跑检查 ==="
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

# 5. 输出汇总
echo ""
echo "=========================================="
echo "[玉芬巡视报告] $NOW_STR"
echo "ERRORS=$ERRORS  WARNINGS=$WARNINGS"
echo "=========================================="
printf "%b" "$REPORT"

# 退出码：ERRORS=0 用 0, >0 用 2
[ $ERRORS -eq 0 ] || exit 2
exit 0