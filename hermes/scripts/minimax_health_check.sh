#!/bin/bash
# minimax_health_check.sh (v2 — 含 default profile + 429 lock + recovery 触发)
# 用途：每 5 分钟 ping minimax 端点，检测 401/402/200/429
#       - 429 → 写 lock 文件（5h 限额触发）
#       - 200 → 删 lock + 推飞书"恢复通知"
# 触发条件：订阅套餐额度耗尽、5h 限额、并发上限、网络抖动
# Cron: 3d1cf3a9627c minimax-endpoint-health-check (*/5 * * * *)

set -e

TS=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
ENDPOINT="https://api.minimaxi.com/anthropic/v1/messages"
ALERT_CHANNEL="feishu:***SECRET***"  # 玉芬 home
LOCK_FILE="$HOME/.hermes/state/minimax_429.lock"
STATE_DIR="$HOME/.hermes/state"
NOTIFY_DIR="$STATE_DIR/notifications"

# 7 个 profile：6 同事 + default (玉芬自己)
PROFILES=(default afu heidou laomo maodou quant xiaobao)

ERRORS=()
WARNINGS=()
HAS_429=0
HAS_200=0
PROFILES_DOWN=()
PROFILES_UP=()

mkdir -p "$STATE_DIR" "$NOTIFY_DIR"

for prof in "${PROFILES[@]}"; do
  if [ "$prof" = "default" ]; then
    env_file="$HOME/.hermes/.env"
  else
    env_file="$HOME/.hermes/profiles/$prof/.env"
  fi

  if [ ! -f "$env_file" ]; then
    WARNINGS+=("$prof: .env 不存在 (skip)")
    continue
  fi

  key=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$env_file")

  http=$(curl -sS -o /tmp/hc_$prof.json -w "%{http_code}" --max-time 10 \
    -X POST "$ENDPOINT" \
    -H "x-api-key: $key" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")

  case "$http" in
    200) HAS_200=1; PROFILES_UP+=("$prof") ;;
    401) ERRORS+=("$prof: HTTP 401 (key 认证失败 — 立即检查订阅)") ;;
    402) ERRORS+=("$prof: HTTP 402 (insufficient_balance — 订阅额度耗尽)") ;;
    429) HAS_429=1; WARNINGS+=("$prof: HTTP 429 (5h 限额触发 — 自动恢复中)"); PROFILES_DOWN+=("$prof") ;;
    TIMEOUT) WARNINGS+=("$prof: 连接超时 (>10s)") ;;
    *) ERRORS+=("$prof: HTTP $http (未知错误)") ;;
  esac
done

# ────────────────────────────────────────
# 429 Lock 管理
# ────────────────────────────────────────
if [ $HAS_429 -eq 1 ]; then
  # 写 lock (覆盖式)
  cat > "$LOCK_FILE" <<EOF
{
  "detected_at": "$TS",
  "date": "$DATE",
  "time": "$TIME",
  "profiles_down": [$(printf '"%s",' "${PROFILES_DOWN[@]}" | sed 's/,$//')],
  "severity": "5h_rate_limit",
  "auto_recovery": true
}
EOF
elif [ $HAS_200 -eq 1 ] && [ -f "$LOCK_FILE" ]; then
  # 恢复！删 lock + 推飞书
  rm -f "$LOCK_FILE"
  RECOVERY_MSG="✅ minimax 端点已恢复 @ $TS"
  RECOVERY_MSG+=$'\n'"   UP: ${PROFILES_UP[*]}"
  RECOVERY_MSG+=$'\n'"   之前 lock 已删除，玉芬会自动继续登记的任务。"
  echo "$RECOVERY_MSG" > "$NOTIFY_DIR/recovery_$TS.txt"
  # 触发恢复脚本（no_agent 模式不行，脚本自己 echo 即可）
fi

# ────────────────────────────────────────
# 输出结果 (no-agent 模式)
# ────────────────────────────────────────
if [ ${#ERRORS[@]} -gt 0 ] || [ ${#WARNINGS[@]} -gt 0 ]; then
  echo "🚨 minimax 端点健康检查 @ $TS"
  echo ""
  if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "❌ 错误 (${#ERRORS[@]}):"
    for e in "${ERRORS[@]}"; do echo "  - $e"; done
  fi
  if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ 警告 (${#WARNINGS[@]}):"
    for w in "${WARNINGS[@]}"; do echo "  - $w"; done
  fi
  echo ""
  if [ $HAS_429 -eq 1 ]; then
    echo "🔒 429 Lock 已写入: $LOCK_FILE"
    echo "   5h 限额触发，预计自动恢复。Lock 删了 = 玉芬自动续任务。"
  fi
  if [ $HAS_200 -eq 1 ] && [ ! -f "$LOCK_FILE" ]; then
    echo "✅ 端点正常，无 lock"
  fi
  echo ""
  echo "🔧 应急命令："
  echo "  # 查看 lock"
  echo "  cat $LOCK_FILE 2>/dev/null || echo 'no lock'"
  echo "  # 手动删 lock（强制续任务）"
  echo "  rm -f $LOCK_FILE"
fi

# 清理
rm -f /tmp/hc_*.json