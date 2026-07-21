#!/bin/bash
# verify_fallback_chain.sh — 自动验证 minimax → ollama fallback 链路
# 5 层检查：服务 / 接口 / 配置 / 解析 / 端到端
# 用法：bash ~/.hermes/skills/minimax-fallback-to-ollama/scripts/verify_fallback_chain.sh

set -e
TS=$(date +%Y%m%d_%H%M%S)
PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  local expected="$3"
  echo ""
  echo "── [$((PASS+FAIL+1))] $name ──"
  if eval "$cmd" 2>&1 | grep -q "$expected"; then
    echo "  ✅ PASS"
    PASS=$((PASS+1))
  else
    echo "  ❌ FAIL"
    FAIL=$((FAIL+1))
  fi
}

echo "════════════════════════════════════════════════════════"
echo " minimax → Ollama Fallback 链路验证 @ $TS"
echo "════════════════════════════════════════════════════════"

# L1: Ollama 进程在跑
check "L1 Ollama 进程" \
  "lsof -i :11434 2>/dev/null" \
  "LISTEN"

# L2: OpenAI 兼容接口响应
check "L2 Ollama /v1/chat/completions" \
  "curl -sS -X POST http://localhost:11434/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{\"model\":\"qwen2.5-coder:7b\",\"max_tokens\":5,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}'" \
  "qwen2.5-coder"

# L3: config.yaml fallback_providers 配了
check "L3 config.yaml fallback_providers" \
  "grep fallback_providers ~/.hermes/config.yaml" \
  "ollama"

# L4: custom_providers 里有 ollama entry
check "L4 custom_providers ollama entry" \
  "grep -A 6 'name: ollama' ~/.hermes/config.yaml" \
  "localhost:11434"

# L5: Hermes fallback 解析代码就位
check "L5 Hermes fallback 解析代码" \
  "grep _try_resolve_fallback_provider ~/.hermes/hermes-agent/gateway/run.py" \
  "_try_resolve_fallback_provider"

echo ""
echo "════════════════════════════════════════════════════════"
echo " 结果: ✅ $PASS 通过 / ❌ $FAIL 失败"
echo "════════════════════════════════════════════════════════"

# L6 (高耗时): 端到端 fallback 测试（可选用）
if [ "$1" = "--with-e2e" ]; then
  echo ""
  echo "── [BONUS] L6 端到端 fallback E2E ──"
  ENV_BACKUP="/tmp/env_backup_$TS.bak"
  cp ~/.hermes/.env "$ENV_BACKUP"

  # 替换 MINIMAX_CN_API_KEY（锚定行首，避免动到注释行 74）
  sed -i '' '/^MINIMAX_CN_API_KEY=/c\
MINIMAX_CN_API_KEY=FAKE_KEY_FOR_E2E_TEST_'"$TS" \
    ~/.hermes/.env

  echo "  • .env 已临时改坏 key"
  echo "  • 触发 Hermes 跑一次最小任务（hermes -p 'ping'，timeout 60s）"

  E2E_RESULT=$(timeout 60 hermes -p "ping" 2>&1 | head -20 || echo "TIMEOUT")
  echo "$E2E_RESULT" > "/tmp/e2e_$TS.log"

  if echo "$E2E_RESULT" | grep -qiE "ollama|qwen|fallback"; then
    echo "  ✅ L6 PASS: 看到 ollama/fallback 字样"
  elif echo "$E2E_RESULT" | grep -q "Hello\|Hi\|好"; then
    echo "  ⚠️  L6 LIKELY PASS: 看到正常回答，但日志没说 fallback（可能 fast path）"
  else
    echo "  ❌ L6 FAIL: 未看到 fallback 痕迹 — 看 /tmp/e2e_$TS.log"
  fi

  # 恢复
  cp "$ENV_BACKUP" ~/.hermes/.env
  rm -f "$ENV_BACKUP"
  echo "  • .env 已恢复"
fi

exit $FAIL