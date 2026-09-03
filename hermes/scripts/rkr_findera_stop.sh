#!/bin/bash
# 停止寻元(FindEra) + 知识库(RKR) — 每天 8:00 触发
# 成功静默(exit 0)，失败输出错误到 stdout 并 exit 1（cron 告警投递）
LOG=/Users/hua/.hermes/logs/rkr_findera_schedule.log
mkdir -p "$(dirname "$LOG")"

cd /Users/hua/6-产品研发/渔芯科技/01-FindEra寻元 && docker compose stop >>"$LOG" 2>&1 || {
  echo "❌ FindEra 寻元停止失败，详见 $LOG"; exit 1; }

cd /Users/hua/6-产品研发/渔芯科技/02-RKR知识库 && docker compose stop >>"$LOG" 2>&1 || {
  echo "❌ RKR 知识库停止失败，详见 $LOG"; exit 1; }

sleep 3
RUNNING=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -cE 'rkr-|research-')
if [ "$RUNNING" != "0" ]; then
  echo "❌ 仍有 $RUNNING 个寻元/知识库容器在运行：$(docker ps --format '{{.Names}}' | grep -E 'rkr-|research-' | tr '\n' ' ')"
  exit 1
fi
# 成功：静默退出
exit 0
