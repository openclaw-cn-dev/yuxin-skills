#!/bin/bash
# RKR 每日 200 条补齐守护:检查今天完成数,<200 则跑 50 条补齐
# 退出码: 0=已达标/跑了一轮 1=出错 2=guard 跳过
set -e
SCRIPT_DIR="/Users/hua/6-产品研发/01-RKR知识库/scripts"
STATE_FILE="$HOME/.hermes/state/rkr_daily_batch.json"
QUOTA=200
BATCH=50

# 已有进程在跑? 不重复启动
if pgrep -f "rkr_daily_batch.*--once" >/dev/null; then
  echo "[guard] 已有 rkr_daily_batch 进程在跑,跳过本次"
  exit 2
fi

# 看今天完成数
TODAY=$(TZ=Asia/Shanghai date +%Y-%m-%d)
DONE=$(python3 -c "import json; s=json.load(open('$STATE_FILE')); print(len(s.get('history',{}).get('$TODAY',[])))" 2>/dev/null || echo 0)

if [ "$DONE" -ge "$QUOTA" ]; then
  echo "[ok] $TODAY 已完成 $DONE/$QUOTA, 达标"
  exit 0
fi

NEED=$((QUOTA - DONE))
if [ "$NEED" -lt "$BATCH" ]; then
  BATCH=$NEED
fi

echo "[run] $TODAY 已完成 $DONE/$QUOTA, 启动 $BATCH 条补齐"
cd /Users/hua/6-产品研发/01-RKR知识库
python3 scripts/rkr_daily_batch.py --once --limit "$BATCH" 2>&1 | tail -20
exit 0
