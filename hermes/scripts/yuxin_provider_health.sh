#!/bin/bash
# yuxin_provider_health.sh — 手动检查 4 个 provider 健康状态
# 用法：bash ~/.hermes/scripts/yuxin_provider_health.sh
set -e

TS=$(date +%Y%m%d_%H%M%S)
ENV_FILE="$HOME/.hermes/.env"

# 从 .env 读 keys
KEY_MINIMAX=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$ENV_FILE")
KEY_DS=$(awk -F= '/^DEEPSEEK_API_KEY/ {print $2}' "$ENV_FILE")

echo "🩺 4-Provider 健康检查 @ $TS"
echo ""

HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "https://api.minimaxi.com/v1/chat/completions" \
  -H "Authorization: Bearer ${KEY_MINIMAX}" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
echo "1️⃣  minimax-cn / MiniMax-M3: HTTP $HTTP"

HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer ${KEY_DS}" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-pro","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
echo "2️⃣  deepseek-cn / deepseek-v4-pro: HTTP $HTTP"

HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "http://localhost:11434/v1/chat/completions" \
  -H "Authorization: Bearer ollama" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-r1:8b","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
echo "3️⃣  ollama-reasoning / deepseek-r1:8b (本地推理): HTTP $HTTP"

HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "http://localhost:11434/v1/chat/completions" \
  -H "Authorization: Bearer ollama" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:7b","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
echo "4️⃣  ollama-coder / qwen2.5-coder:7b (本地代码): HTTP $HTTP"

echo ""
echo "📋 当前活跃 provider:"
hermes config show 2>&1 | grep -E "Model:|provider" | head -3

echo ""
echo "🔧 切换命令 (华哥授权时玉芬调用):"
echo "   bash ~/.hermes/scripts/yuxin_switch_provider.sh minimax          # 切 minimax"
echo "   bash ~/.hermes/scripts/yuxin_switch_provider.sh deepseek         # 切 deepseek"
echo "   bash ~/.hermes/scripts/yuxin_switch_provider.sh ollama-r         # 切本地推理"
echo "   bash ~/.hermes/scripts/yuxin_switch_provider.sh ollama-coder     # 切本地代码"
