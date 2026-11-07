#!/bin/bash
# Mnemosyne 记忆健康检查 + 自动整合（no_agent watchdog，无异常静默）
# 玉芬维护 2026-08-18：替代原"每4h记忆压缩"cron，接上 Mnemosyne
#
# 逻辑：遍历所有 profile 的 mnemosyne.db，working_memory 超阈值则触发 sleep 整合。
# 输出为空 = 健康 = 静默（cron 不打扰华哥）。有异常才输出报告。

set -u

PY=/Users/hua/.hermes/hermes-agent/venv/bin/python
MNEMO=/Users/hua/.hermes/hermes-agent/venv/bin/mnemosyne
THRESHOLD=500  # working_memory 条数阈值

PROFILES=(default afu community heidou laomo maodou quant xiaobao zhenglishi)

report=""

for p in "${PROFILES[@]}"; do
  if [ "$p" = "default" ]; then
    DATA_DIR="/Users/hua/.hermes/mnemosyne/data"
  else
    DATA_DIR="/Users/hua/.hermes/profiles/$p/mnemosyne/data"
  fi

  DB="$DATA_DIR/mnemosyne.db"
  if [ ! -f "$DB" ]; then
    report="${report}⚠️ [$p] mnemosyne.db 缺失\n"
    continue
  fi

  n=$($PY -c "import sqlite3; print(sqlite3.connect('$DB').execute('SELECT COUNT(*) FROM working_memory').fetchone()[0])" 2>/dev/null)
  if [ -z "$n" ]; then
    report="${report}⚠️ [$p] db 读取失败\n"
    continue
  fi

  if [ "$n" -gt "$THRESHOLD" ]; then
    report="${report}🗜️ [$p] working_memory ${n} 条超阈值 ${THRESHOLD}，触发 sleep 整合\n"
    MNEMOSYNE_DATA_DIR="$DATA_DIR" "$MNEMO" sleep >/dev/null 2>&1
    n2=$($PY -c "import sqlite3; print(sqlite3.connect('$DB').execute('SELECT COUNT(*) FROM working_memory').fetchone()[0])" 2>/dev/null)
    report="${report}   → 整合后 ${n2} 条\n"
  fi
done

# 有异常才输出
if [ -n "$report" ]; then
  echo -e "🧠 Mnemosyne 记忆健康检查（$(date '+%m-%d %H:%M')）\n"
  echo -e "$report"
fi
