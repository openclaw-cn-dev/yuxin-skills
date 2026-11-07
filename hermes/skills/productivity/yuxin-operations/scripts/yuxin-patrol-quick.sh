#!/bin/bash
# 玉芬 patrol 速查脚本 — 每 4h 跑一次的标准命令集
# 来自 2026-06-30 20:02 实战，最小可执行版本
# 输出格式：简洁、可读、与 patrol-tactical-cheatsheet.md 对齐
#
# 用法：bash yuxin-patrol-quick.sh
# 完整 cheatsheet 见 yuxin-operations/references/patrol-tactical-cheatsheet.md
# 历史 patrol 报告见 references/patrol-YYYY-MM-DD-HHMM.md

set -e

NOW=$(date '+%Y-%m-%d %H:%M:%S')
NOW_EPOCH=$(date +%s)
echo "=== 玉芬 Patrol Quick Check @ $NOW ==="
echo ""

# 1. 5 profile 任务库状态（per-profile kanban.db + tasks.db 都是空 stub，但记录大小便于对比）
echo "--- 1. 任务库 stub 状态 ---"
for p in maodou laomo xiaobao heidou afu; do
  kanban_size=$(stat -f "%z" "$HOME/.hermes/profiles/$p/kanban.db" 2>/dev/null || echo 0)
  tasks_size=$(stat -f "%z" "$HOME/.hermes/profiles/$p/tasks.db" 2>/dev/null || echo 0)
  tasks_count=$(sqlite3 "$HOME/.hermes/profiles/$p/kanban.db" "SELECT COUNT(*) FROM tasks" 2>/dev/null || echo 0)
  printf "  %-10s kanban=%-7d tasks.db=%-5d tasks=%s\n" "$p" "$kanban_size" "$tasks_size" "$tasks_count"
done

# 2. 主 kanban.db（权威任务库）
echo ""
echo "--- 2. 主 kanban.db (权威任务库) ---"
MAIN_KANBAN="$HOME/.hermes/kanban.db"
if [ -f "$MAIN_KANBAN" ]; then
  total=$(sqlite3 "$MAIN_KANBAN" "SELECT COUNT(*) FROM tasks" 2>/dev/null || echo 0)
  in_progress=$(sqlite3 "$MAIN_KANBAN" "SELECT COUNT(*) FROM tasks WHERE status='in_progress'" 2>/dev/null || echo 0)
  pending=$(sqlite3 "$MAIN_KANBAN" "SELECT COUNT(*) FROM tasks WHERE status='pending'" 2>/dev/null || echo 0)
  echo "  总数=$total in_progress=$in_progress pending=$pending"
  if [ "$in_progress" -gt 0 ] || [ "$pending" -gt 0 ]; then
    echo "  ⚠️ 有任务在跑/待领："
    sqlite3 -header -separator "|" "$MAIN_KANBAN" "SELECT id, assignee, status, priority, title FROM tasks WHERE status IN ('pending','in_progress') ORDER BY priority LIMIT 20" 2>/dev/null
  fi
else
  echo "  ❌ 主 kanban.db 不存在"
fi

# 3. 5 profile 心跳 cron 健康
echo ""
echo "--- 3. 5 Profile 心跳 cron ---"
for p in maodou laomo xiaobao heidou afu; do
  log="$HOME/.hermes/profiles/$p/logs/agent.log"
  if [ -f "$log" ]; then
    last=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$log")
    age_min=$(( (NOW_EPOCH - $(stat -f "%m" "$log")) / 60 ))
    marker="✅"
    [ "$age_min" -gt 15 ] && marker="🟡"
    [ "$age_min" -gt 60 ] && marker="🔴"
    printf "  %s %-10s %s (%dmin 前)\n" "$marker" "$p" "$last" "$age_min"
  else
    echo "  ❌ $p: 无 agent.log"
  fi
done

# 4. Feishu delivery errors (last 6h)
echo ""
echo "--- 4. 飞书 delivery errors (6h 内) ---"
ERR_COUNT=0
for p in maodou laomo xiaobao heidou afu; do
  err=$(find "$HOME/.hermes/profiles/$p/logs" -name "agent.log" -mmin -360 -exec grep -l "field validation\|230002\|out of chat" {} \; 2>/dev/null | wc -l | tr -d ' ')
  if [ "$err" -gt 0 ]; then
    echo "  ⚠️ $p: 飞书 delivery 错误命中"
    ERR_COUNT=$((ERR_COUNT+1))
  fi
done
[ "$ERR_COUNT" -eq 0 ] && echo "  ✅ 无飞书 delivery 错误"

# 5. cron jobs.json 状态
echo ""
echo "--- 5. Profile cron jobs.json ---"
for p in maodou laomo xiaobao heidou afu; do
  jobs="$HOME/.hermes/profiles/$p/cron/jobs.json"
  if [ -f "$jobs" ]; then
    n_jobs=$(python3 -c "import json; d=json.load(open('$jobs')); print(len(d) if isinstance(d, list) else len(d.get('jobs', [])))" 2>/dev/null)
    printf "  %-10s %d 个 cron job\n" "$p" "$n_jobs"
  fi
done

echo ""
echo "=== Patrol Complete @ $NOW ==="