#!/bin/bash
# 玉芬唤醒词看门狗 —— 检查 v7 进程是否存活

SCRIPT="/Users/hua/hermes/voice/yuxin_wake_word_v7.py"
VENV_PYTHON="/Users/hua/.hermes/hermes-agent/venv/bin/python3"
LOG="/Users/hua/hermes/voice/logs/wake_word.log"

SCRIPT_PID=$(pgrep -f "yuxin_wake_word_v7\.py" | head -1)

if [ -n "$SCRIPT_PID" ]; then
    if [ -f "$LOG" ]; then
        LAST_MOD=$(stat -f "%m" "$LOG" 2>/dev/null)
        NOW=$(date +%s)
        if [ $((NOW - LAST_MOD)) -gt 1800 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 看门狗: 进程 $SCRIPT_PID 疑似卡死，重启中" >> "$LOG"
            kill -9 "$SCRIPT_PID" 2>/dev/null
            sleep 2
            nohup "$VENV_PYTHON" "$SCRIPT" > /dev/null 2>&1 &
        fi
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 看门狗: 进程不存在，重启中" >> "$LOG"
    nohup "$VENV_PYTHON" "$SCRIPT" > /dev/null 2>&1 &
fi
