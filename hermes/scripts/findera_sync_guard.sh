#!/bin/bash
# FindEra→RKR 持续同步（no_agent + 夜间窗口守卫）
# 华哥 2026-08-30 定调：容器只在 23:30–次日 8:00 运行，白天静默跳过，绝不拉起容器。
# 输出语义（no_agent cron）：stdout 非空才投递，空则静默。
set -u

# ── 夜间窗口守卫 ──
HHMM=$(TZ=Asia/Shanghai date +%H%M)
if [ "$HHMM" -ge 0800 ] && [ "$HHMM" -lt 2330 ]; then
  exit 0
fi

# ── 检测 RKR(8000) 与 FindEra(8003) 是否在线，任一离线则静默 ──
if ! curl -sf --max-time 5 http://localhost:8000/api/v1/health >/dev/null 2>&1; then
  exit 0
fi
if ! curl -sf --max-time 5 http://localhost:8003/api/v1/health >/dev/null 2>&1; then
  exit 0
fi

# ── 调用同步 API（只走 API，禁止 docker exec fallback）──
python3 /Users/hua/.hermes/scripts/findera_sync_once.py
