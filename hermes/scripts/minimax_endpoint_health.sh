#!/bin/bash
# minimax_endpoint_health.sh — 华哥口头授权时才手动跑的健康检查
# 用法：bash ~/.hermes/scripts/minimax_endpoint_health.sh
# 输出：飞书推送当前 7 profile 状态（一次性，不再循环）
# 触发条件：华哥说"检查一下端点" / "跑一下健康检查"

set -e

TS=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
ENDPOINT="https://api.minimaxi.com/anthropic/v1/messages"

# 7 个 profile：6 同事 + default (玉芬自己)
PROFILES=(default afu heidou laomo maodou quant xiaobao)

ERRORS=()
WARNINGS=()
HAS_429=0
HAS_200=0
HAS_DEEPSEEK=0
PROFILES_DOWN=()
PROFILES_UP=()

# --- 测 minimax ---
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
    401) ERRORS+=("$prof: HTTP 401 (key 认证失败)") ;;
    402) ERRORS+=("$prof: HTTP 402 (insufficient_balance)") ;;
    429) HAS_429=1; WARNINGS+=("$prof: HTTP 429 (5h 限额)"); PROFILES_DOWN+=("$prof") ;;
    TIMEOUT) WARNINGS+=("$prof: 连接超时") ;;
    *) ERRORS+=("$prof: HTTP $http") ;;
  esac
done

# --- 测 deepseek-v4-pro ---
DEEPSEEK_KEY=$(awk -F= '/^DEEPSEEK_API_KEY/ {print $2}' "$HOME/.hermes/.env" 2>/dev/null || echo "")
DEEPSEEK_BASE=$(awk -F= '/^DEEPSEEK_BASE_URL/ {print $2}' "$HOME/.hermes/.env" 2>/dev/null || echo "https://api.deepseek.com/v1")

if [ -n "$DEEPSEEK_KEY" ]; then
  ds_http=$(curl -sS -o /tmp/hc_deepseek.json -w "%{http_code}" --max-time 10 \
    -X POST "$DEEPSEEK_BASE/chat/completions" \
    -H "Authorization: Bearer $DEEPSEEK_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"deepseek-v4-pro","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
  case "$ds_http" in
    200) HAS_DEEPSEEK=1 ;;
    *) WARNINGS+=("deepseek-v4-pro: HTTP $ds_http") ;;
  esac
fi

# --- 测 ollama 本地 ---
ollama_http=$(curl -sS -o /tmp/hc_ollama.json -w "%{http_code}" --max-time 10 \
  -X POST "http://localhost:11434/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ollama" \
  -d '{"model":"qwen2.5-coder:7b","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
case "$ollama_http" in
  200) OLLAMA_OK=1 ;;
  *) OLLAMA_OK=0; WARNINGS+=("ollama 本地: HTTP $ollama_http") ;;
esac

# --- 输出 ---
echo "🔍 minimax 端点健康检查 (手动触发) @ $TS"
echo ""
echo "=== Provider 状态 ==="
if [ $HAS_200 -eq 1 ]; then
  echo "✅ minimax-cn: UP (${#PROFILES_UP[@]} profile)"
fi
if [ $HAS_429 -eq 1 ]; then
  echo "⚠️  minimax-cn: 部分 profile 429 (${#PROFILES_DOWN[@]} 个: ${PROFILES_DOWN[*]})"
fi
if [ $HAS_DEEPSEEK -eq 1 ]; then
  echo "✅ deepseek-v4-pro: UP"
else
  echo "❓ deepseek-v4-pro: 未测或不可用"
fi
if [ $OLLAMA_OK -eq 1 ]; then
  echo "✅ ollama 本地 (qwen2.5-coder:7b): UP"
else
  echo "❌ ollama 本地: DOWN"
fi

echo ""
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo "❌ 错误:"
  for e in "${ERRORS[@]}"; do echo "  - $e"; done
  echo ""
fi
if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo "⚠️ 警告:"
  for w in "${WARNINGS[@]}"; do echo "  - $w"; done
  echo ""
fi

echo "📋 说明:"
echo "  - minimax-cn: 主 provider (默认)"
echo "  - deepseek-v4-pro: 备用 (华哥授权才能切换)"
echo "  - ollama 本地: 兜底 (自动 fallback)"
echo ""
echo "🔧 应急命令:"
echo "  # 切换到 deepseek (华哥授权时)"
echo "  hermes config set provider deepseek-cn"
echo "  # 切回 minimax"
echo "  hermes config set provider minimax-cn"

# 清理
rm -f /tmp/hc_*.json