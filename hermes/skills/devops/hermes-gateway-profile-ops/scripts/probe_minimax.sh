#!/bin/bash
# probe_minimax.sh — 探测 minimax-cn 端点状态
# 用法: ./probe_minimax.sh [profile_name]
# 输出: 每把 key 的 HTTP 码 + 错误类型 + 建议下一步

set -e

PROFILE="${1:-default}"
ENV_FILE="$HOME/.hermes/profiles/$PROFILE/.env"
[ ! -f "$ENV_FILE" ] && ENV_FILE="$HOME/.hermes/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE 不存在"
  exit 1
fi

KEY=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$ENV_FILE")
KEY_LEN=${#KEY}
KEY_HEAD=$(echo "$KEY" | cut -c1-12)
KEY_TAIL=$(echo "$KEY" | cut -c$(($KEY_LEN-5))-)

echo "=== Probe minimax-cn ==="
echo "profile:    $PROFILE"
echo "env_file:   $ENV_FILE"
echo "key_len:    $KEY_LEN"
echo "key_head:   $KEY_HEAD"
echo "key_tail:   $KEY_TAIL"
echo ""

# 1. 空 key 基线
echo "--- [Step 1] 空 key 基线 ---"
BASELINE=$(curl -sS -o /tmp/probe_baseline.json -w "%{http_code}" \
  -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>&1)
echo "HTTP: $BASELINE"
head -c 200 /tmp/probe_baseline.json
echo ""
echo ""

# 2. 带 key 实测
echo "--- [Step 2] 带 key 实测 ---"
RESULT=$(curl -sS -o /tmp/probe_keyed.json -w "%{http_code}" \
  -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "x-api-key: $KEY" \
  -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>&1)
echo "HTTP: $RESULT"
head -c 300 /tmp/probe_keyed.json
echo ""
echo ""

# 3. 诊断
echo "--- [Step 3] 诊断 ---"
if [ "$RESULT" = "200" ]; then
  echo "✅ OK — key + 账户都正常"
elif [ "$RESULT" = "401" ]; then
  if [ "$BASELINE" = "401" ] && [ "$(cat /tmp/probe_baseline.json)" = "$(cat /tmp/probe_keyed.json)" ]; then
    echo "❌ 401 + 与空 key 报错完全一致 → key 字符残缺, 让用户重新复制完整 key"
  else
    echo "❌ 401 + 与空 key 报错不同 → key 已激活但被拒, 检查账户权限 / key 是否过期"
  fi
elif [ "$RESULT" = "402" ]; then
  if [[ "$KEY_HEAD" == sk-cp-* ]]; then
    echo "⚠️  402 + 订阅账户 → 5h token 池满, 等 5h 自动重置 (无需充值)"
  elif [[ "$KEY_HEAD" == sk-api* ]]; then
    echo "❌ 402 + 按量账户 → 余额耗尽, 需充值或切到订阅账户"
  else
    echo "❌ 402 → 未知账户类型, 看 message 字段"
  fi
elif [ "$RESULT" = "429" ]; then
  echo "⚠️  429 → 平台限流, 加 backoff 重试 / 启用 fallback"
else
  echo "❓ HTTP $RESULT → 见响应体"
fi

echo ""
echo "--- [Step 4] 清理 ---"
rm -f /tmp/probe_baseline.json /tmp/probe_keyed.json
