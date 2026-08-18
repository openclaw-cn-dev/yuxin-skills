#!/bin/bash
# 启动寻元(FindEra) + 知识库(RKR) — 每天 0:00 触发
# 成功静默(exit 0)，失败输出错误到 stdout 并 exit 1（cron 告警投递）
LOG=/Users/hua/.hermes/logs/rkr_findera_schedule.log
mkdir -p "$(dirname "$LOG")"

cd /Users/hua/6-产品研发/渔芯科技/00-FindEra寻元 && docker compose up -d >>"$LOG" 2>&1 || {
  echo "❌ FindEra 寻元启动失败，详见 $LOG"; exit 1; }

cd /Users/hua/6-产品研发/渔芯科技/01-RKR知识库 && docker compose up -d >>"$LOG" 2>&1 || {
  echo "❌ RKR 知识库启动失败，详见 $LOG"; exit 1; }

sleep 15
if ! curl -sf --max-time 10 http://localhost:8000/api/v1/health >/dev/null 2>&1; then
  echo "❌ RKR backend 健康检查失败 (localhost:8000)，详见 $LOG"; exit 1
fi
# 成功：静默退出
exit 0
