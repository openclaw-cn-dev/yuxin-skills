#!/bin/bash
# patrol-deadlock-check.sh — 玉芬派单死锁检测脚本
# 用法: bash patrol-deadlock-check.sh
# 触发: 每 4h patrol 时执行
# 输出: 派单死锁报告（含 KB-* pending + gateway 存活对照表）
#
# 判定逻辑: kanban.db 有 pending AND assignee gateway procs=0 AND last_run > 12h
# 退出码: 0=无死锁, 1=检测到死锁（汇报华哥）, 2=检测脚本自身错误

set -uo pipefail

KB_DB="$HOME/.hermes/kanban.db"

echo "=== Patrol Deadlock Check @ $(date '+%Y-%m-%d %H:%M:%S') CST ==="
echo ""

# 1. 玉芬派单库 pending 任务
if [ ! -s "$KB_DB" ]; then
  echo "kanban.db missing or empty: $KB_DB"
  exit 2
fi

PENDING=$(sqlite3 "$KB_DB" \
  "SELECT id, title, assignee, priority, created_at
   FROM tasks
   WHERE status IN ('pending','running')
   ORDER BY priority DESC, created_at ASC")

PENDING_COUNT=$(echo "$PENDING" | grep -c '|' || echo 0)
echo "[1] kanban.db pending+running: $PENDING_COUNT"

if [ "$PENDING_COUNT" -eq 0 ]; then
  echo "  (no pending tasks → no deadlock possible)"
  exit 0
fi

echo "$PENDING" | head -10
echo ""

# 2. 5 profile gateway 存活 + last_run 距今
echo "[2] 5 Profile Gateway 存活状态:"
for prof in maodou laomo xiaobao heidou afu; do
  PROCS=$(ps -eo pid,etime,command 2>/dev/null | grep "hermes_cli.main --profile $prof gateway" | grep -v grep | wc -l | tr -d ' ')

  # profile 端 jobs.json last_run
  PJ="$HOME/.hermes/profiles/$prof/cron/jobs.json"
  if [ -f "$PJ" ]; then
    LAST_RUN=$(python3 -c "
import json
from datetime import datetime, timezone, timedelta
CST = timezone(timedelta(hours=8))
try:
    d = json.load(open('$PJ'))
    jobs = d if isinstance(d, list) else d.get('jobs', [])
    if not jobs:
        print('no_jobs')
    else:
        lr = jobs[0].get('last_run_at', '')
        if lr:
            dt = datetime.fromisoformat(lr.replace('Z','+00:00')).astimezone(CST)
            age_h = (datetime.now(CST) - dt).total_seconds() / 3600
            print(f'{age_h:.1f}h')
        else:
            print('never')
except Exception as e:
    print(f'err:{e}')
")
  else
    LAST_RUN="no_jobs.json"
  fi

  LOG="$HOME/.hermes/profiles/$prof/logs/agent.log"
  if [ -f "$LOG" ]; then
    LOG_AGE=$(python3 -c "
import os, time
age_h = (time.time() - os.path.getmtime('$LOG')) / 3600
print(f'{age_h:.1f}h')
")
  else
    LOG_AGE="no_log"
  fi

  STATUS="🟢"
  if [ "$PROCS" = "0" ]; then
    STATUS="🔴 DEAD"
  fi

  echo "  $prof: procs=$PROCS last_run=$LAST_RUN log_age=$LOG_AGE $STATUS"
done

echo ""

# 3. 派单死锁判定
echo "[3] 派单死锁判定:"
DEADLOCK_DETECTED=0
while IFS='|' read -r id title assignee priority created_at; do
  [ -z "$id" ] && continue
  prof_map=$(echo "毛豆:maodou 老莫:laomo 小宝:xiaobao 黑豆:heidou 阿福:afu" | tr ' ' '\n' | grep "^$assignee:" | cut -d: -f2)
  if [ -z "$prof_map" ]; then
    echo "  $id ($assignee) → assignee 不在 5 profile 范围"
    continue
  fi
  PROCS=$(ps -eo pid,etime,command 2>/dev/null | grep "hermes_cli.main --profile $prof_map gateway" | grep -v grep | wc -l | tr -d ' ')
  if [ "$PROCS" = "0" ]; then
    echo "  🔴 死锁: $id → $assignee (profile: $prof_map) — gateway 死, 任务无人能领"
    DEADLOCK_DETECTED=$((DEADLOCK_DETECTED + 1))
  fi
done <<< "$PENDING"

echo ""
if [ "$DEADLOCK_DETECTED" -gt 0 ]; then
  echo "=== ⚠️ 派单死锁确认: $DEADLOCK_DETECTED 个 pending 任务无人能领 ==="
  echo "修复路径（华哥决策）:"
  echo "  1. 手动 pkill+launchctl bootstrap 5 gateway"
  echo "  2. 或在 kanban.db 标任务为 failed (reason='assignee gateway offline')"
  exit 1
else
  echo "=== ✅ 无派单死锁 ==="
  exit 0
fi
