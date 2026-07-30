#!/bin/bash
# 毛豆心跳 — no_agent 模式，零token消耗
# 有任务才出声，无任务静默
# 配合 cron: no_agent=true, script=maodou_heartbeat.sh

KANBAN_DB="$HOME/.hermes/kanban.db"

if [ ! -f "$KANBAN_DB" ]; then
  echo "⚠️ kanban.db 不存在"
  exit 0
fi

# 查毛豆的待处理任务
TASKS=$(sqlite3 "$KANBAN_DB" "SELECT id, title, status, priority FROM tasks WHERE assignee='毛豆' AND status IN ('pending','in_progress') ORDER BY priority, created_at" 2>/dev/null)

if [ -z "$TASKS" ]; then
  # 无任务 → 静默退出（no_agent 空输出 = 不发送）
  exit 0
fi

# 有任务 → 输出通知
echo "【毛豆】有任务待处理："
echo "$TASKS" | while IFS='|' read -r id title status priority; do
  ICON="🔴"
  [ "$status" = "in_progress" ] && ICON="🟡"
  echo "$ICON [$status] $title (P$priority)"
done
