#!/bin/bash
# 玉芬巡视 v2 — Windows 版 (2026-11-10 迁移重写, 零 token)
# 检查所有同事 gateway 状态 + kanban 任务
# 异常才出声，正常静默 (stdout 空 = cron 静默)
# 依赖: git-bash tasklist / python kanban_task_ops.py

OPS="D:/yuxin/hermes/scripts/kanban_task_ops.py"
PROFILES="maodou laomo xiaobao heidou afu quant zhenglishi"

# 1. gateway 进程检测 (Windows: hermes.exe 全体, 再按 profile 数对 PID)
TL=$(tasklist //FI "IMAGENAME eq hermes.exe" 2>/dev/null)
HERMES_PIDS=$(echo "$TL" | grep -c "hermes.exe")
DEAD=""
for p in $PROFILES; do
  # 通过 gateway status 单查太慢; 用端口法不可靠; 折中: 只要 hermes.exe 总数 >= 7 就认为全体在
  :
done
if [ "$HERMES_PIDS" -ge 7 ]; then
  GW_OK=true
else
  GW_OK=false
  DEAD="hermes.exe 进程数=$HERMES_PIDS (<7), 疑有同事 gateway 掉线"
fi

# 2. kanban 任务面 (调 python ops)
SUP_OUT=$(python "$OPS" supervise 2>&1)
SUP_CODE=$?

# 3. 汇总: 全正常 → 静默(空输出); 有异常 → 输出告警
FAIL_LINES=$(echo "$SUP_OUT" | grep -E "❌|⚠️" )
if [ "$GW_OK" = true ] && [ "$SUP_CODE" -eq 0 ] && [ -z "$FAIL_LINES" ]; then
  # 静默: 什么都不输出
  exit 0
fi

echo "【玉芬巡视】$(date '+%Y-%m-%d %H:%M')"
echo ""
if [ "$GW_OK" != true ]; then
  echo "=== Gateway 异常 ==="
  echo "❌ $DEAD"
  echo ""
fi
echo "=== 任务池/资源 ==="
echo "$SUP_OUT"
