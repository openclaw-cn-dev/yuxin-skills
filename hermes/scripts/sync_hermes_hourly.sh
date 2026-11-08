#!/usr/bin/env bash
# sync_hermes_hourly.sh
# 每小时把 ~/.hermes/profiles/quant/ 的"必须用"子目录同步到项目内 hermes_data/
# 由 cron 任务每 60 分钟触发(0 * * * *)
# 同步完成后调用 sync_hermes_notify.py 通过飞书发送结果
# 通知策略:d 方案 — 首次报喜 + 之后只在异常时通知
# 作者:宽博士 · 2026-09-14

set -uo pipefail

SRC="/Users/hua/.hermes/profiles/quant"
DST="/Users/hua/6-产品研发/渔芯独角兽/00-基本完成/渔芯量化/渔芯量化/11-宽博士Hermes档案/hermes_data"
LOG="/Users/hua/.hermes/profiles/quant/cron/output/hermes_data_sync.log"
FEISHU_SENDER="/Users/hua/6-产品研发/渔芯独角兽/00-基本完成/渔芯量化/渔芯量化/01-工具代码/FisherQ/agent/feishu_sender.py"
NOTIFY_STATE="/Users/hua/.hermes/profiles/quant/cron/output/.hermes_sync_notify_state"
PYTHON="/opt/homebrew/bin/python3.11"
# 飞书发送走 hermes_cli send(无 LLM,复用 gateway 凭据,Dashboard feishu_sender 默认 chat 已解散不通)
HERMES_CLI="/Users/hua/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main"
NOTIFY_TARGET="feishu"

# 必须同步的子目录
SYNC_DIRS=(skills cron evolution mnemosyne references scripts memory)

# 锁文件防并发
LOCK="$DST/.sync.lock"
if [ -e "$LOCK" ]; then
  echo "[$(date +%FT%T)] another sync running, exit" >> "$LOG"
  exit 0
fi
trap 'rm -f "$LOCK"' EXIT
echo $$ > "$LOCK"

START=$(date +%s)
echo "[$(date +%FT%T)] start sync" >> "$LOG"

# 异常检测标志
ERROR_MSG=""
SYNCED_TOTAL=0

for sub in "${SYNC_DIRS[@]}"; do
  if [ -d "$SRC/$sub" ]; then
    rsync -a --delete "$SRC/$sub" "$DST/" 2>>"$LOG"
    if [ $? -ne 0 ]; then
      ERROR_MSG="${ERROR_MSG}rsync $sub 失败;"
    fi
    SIZE=$(du -sh "$DST/$sub" 2>/dev/null | cut -f1)
    echo "  ✓ $sub/  $SIZE" >> "$LOG"
  else
    ERROR_MSG="${ERROR_MSG}$sub 不存在;"
    echo "  ✗ $sub/ 不存在,跳过" >> "$LOG"
  fi
done

END=$(date +%s)
TOTAL_SIZE=$(du -sh "$DST" 2>/dev/null | cut -f1)
ELAPSED=$((END-START))

echo "[$(date +%FT%T)] done  total=$TOTAL_SIZE  took=${ELAPSED}s  error='$ERROR_MSG'" >> "$LOG"

# === 飞书通知(d 方案:首次报喜 + 异常告警)===
should_notify=0
notify_kind=""

# 1. 首次成功 → 报喜
if [ -z "$ERROR_MSG" ] && [ ! -f "$NOTIFY_STATE.firt_run_done" ]; then
  should_notify=1
  notify_kind="first_success"
  touch "$NOTIFY_STATE.firt_run_done"
fi

# 2. 异常 → 告警(任何后续)
if [ -n "$ERROR_MSG" ]; then
  should_notify=1
  notify_kind="error"
fi

if [ $should_notify -eq 1 ]; then
  if [ "$notify_kind" = "first_success" ]; then
    MSG="🏠 【宽博士 hermes_data 首次同步完成】
• 项目:渔芯量化(家)
• 数据规模:$TOTAL_SIZE
• 子目录:7 个 must-use(skills/cron/evolution/mnemosyne/references/scripts/memory)
• 耗时:${ELAPSED}s
• 后续策略:异常时立即告警 + 首次报喜
• 详见:11-宽博士Hermes档案/hermes_data/README.md"
  else
    MSG="⚠️ 【宽博士 hermes_data 同步异常】
• 错误:$ERROR_MSG
• 时间:$(date +%FT%T)
• 请检查 ~/.hermes/profiles/quant/ 是否正常"
  fi

  # 优先走 hermes_cli send(复用 gateway 凭据,直接发 home chat)
  if command -v "$HERMES_CLI" >/dev/null 2>&1 || [ -x /Users/hua/.hermes/hermes-agent/venv/bin/python ]; then
    $HERMES_CLI send -t "$NOTIFY_TARGET" --quiet "$MSG" >> "$LOG" 2>&1
    SEND_RC=$?
    echo "[$(date +%FT%T)] notify via hermes_cli, kind=$notify_kind, rc=$SEND_RC" >> "$LOG"
  elif [ -f "$FEISHU_SENDER" ]; then
    "$PYTHON" "$FEISHU_SENDER" "$MSG" >> "$LOG" 2>&1
    echo "[$(date +%FT%T)] notify via feishu_sender fallback, kind=$notify_kind" >> "$LOG"
  fi
fi
