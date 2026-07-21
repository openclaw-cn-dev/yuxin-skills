#!/bin/bash
# 玉芬巡视 — no_agent 模式，零token消耗
# 检查所有同事gateway状态 + kanban任务
# 异常才出声，正常静默

KANBAN_DB="$HOME/.hermes/kanban.db"

echo "【玉芬巡视】$(date '+%Y-%m-%d %H:%M')"
echo ""

# 1. 检查同事 gateway 进程
echo "=== Gateway 状态 ==="
ALL_OK=true
for p in maodou laomo xiaobao heidou afu quant zhenglishi; do
  pid=$(launchctl list 2>/dev/null | awk -v lbl="ai.hermes.gateway-$p" '$3==lbl {print $1}')
  if [ -n "$pid" ]; then
    echo "✅ $p (launchd PID=$pid)"
  else
    # 也查手动进程
    manual_pid=$(ps aux | grep "hermes.*gateway.*$p" | grep -v grep | awk '{print $2}')
    if [ -n "$manual_pid" ]; then
      echo "⚠️ $p (manual PID=$manual_pid, 建议注册launchd)"
    else
      echo "❌ $p (未运行)"
      ALL_OK=false
    fi
  fi
done

echo ""

# 2. 检查 kanban 任务
if [ -f "$KANBAN_DB" ]; then
  TASKS=$(sqlite3 "$KANBAN_DB" "SELECT assignee, status, title FROM tasks WHERE status IN ('pending','in_progress') ORDER BY assignee, status" 2>/dev/null)
  if [ -n "$TASKS" ]; then
    echo "=== 任务池 ==="
    echo "$TASKS" | while IFS='|' read -r assignee status title; do
      ICON="📋"
      [ "$status" = "in_progress" ] && ICON="🔄"
      echo "$ICON $assignee: [$status] $title"
    done
  else
    echo "任务池：空"
  fi
else
  echo "⚠️ kanban.db 不存在"
fi

echo ""
echo "=== 汇总 ==="
if $ALL_OK; then
  echo "✅ 所有gateway正常运行"
else
  echo "⚠️ 有gateway未运行，需关注"
fi
