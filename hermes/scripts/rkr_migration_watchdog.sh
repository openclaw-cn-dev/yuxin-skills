#!/bin/bash
# RKR 重嵌入看门狗 — 异常告警 + 每 4 小时进度简报（正常静默，省 token）
# 通过 Hermes cronjob no_agent 模式运行

SSH="sshpass -p 'Aa14472128+' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@121.43.127.211"
STATE_FILE="$HOME/.hermes/scripts/.rkr_migration_watchdog_state"

# 查迁移 status
STATUS=$($SSH "docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -A -c \"SELECT value FROM platform_settings WHERE key='embedding_migration_status'\"" 2>/dev/null)

# 查迁移进程存活
PROC=$($SSH "ps aux | grep 'run_migration' | grep -v grep | wc -l" 2>/dev/null | tr -d ' ')

# 解析字段
parse() { echo "$STATUS" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('$1',''))" 2>/dev/null; }
MIGRATED=$(parse migrated); TOTAL=$(parse total); FAILED=$(parse failed); S=$(parse status)

# 状态为空 = 未启动或已清空
if [ -z "$S" ]; then
    echo "⚠️ RKR 重嵌入状态为空（可能未启动或异常清空）"
    exit 0
fi

if [ "$S" == "completed" ]; then
    echo "✅ RKR 重嵌入全部完成：migrated=$MIGRATED/$TOTAL，failed=$FAILED"
    rm -f "$STATE_FILE"
    exit 0
fi

if [ "$S" == "error" ]; then
    echo "🚨 RKR 重嵌入出错：$STATUS"
    exit 0
fi

if [ "$S" == "running" ] && [ "$PROC" == "0" ]; then
    echo "🚨 RKR 重嵌入进程已消失但状态 running：migrated=$MIGRATED/$TOTAL，failed=$FAILED"
    exit 0
fi

# 正常运行中：每 4 小时输出一次进度简报
NOW=$(date +%s)
LAST=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
INTERVAL=$(( NOW - LAST ))
if [ "$INTERVAL" -ge 14400 ]; then
    PCT=$(python3 -c "print(f'{$MIGRATED*100//$TOTAL}%')" 2>/dev/null)
    echo "📊 RKR 重嵌入进度：migrated=$MIGRATED/$TOTAL（$PCT），failed=$FAILED"
    echo "$NOW" > "$STATE_FILE"
fi
# 否则静默（空输出）
