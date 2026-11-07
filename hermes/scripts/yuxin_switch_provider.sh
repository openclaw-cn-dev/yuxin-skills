#!/bin/bash
# yuxin_switch_provider.sh — 华哥授权时玉芬调用，切换主 provider
# 用法：
#   bash ~/.hermes/scripts/yuxin_switch_provider.sh minimax     # 切回 minimax
#   bash ~/.hermes/scripts/yuxin_switch_provider.sh deepseek    # 切到 deepseek-cn
#   bash ~/.hermes/scripts/yuxin_switch_provider.sh ollama-r    # 切到本地 deepseek-r1:8b
#   bash ~/.hermes/scripts/yuxin_switch_provider.sh ollama-c    # 切到本地 qwen2.5-coder:7b
#
# 华哥原话："我授权才触发更换大模型"
# 因此本脚本假定玉芬已经在对话里得到华哥明确授权才执行

set -e

TS=$(date +%Y%m%d_%H%M%S)
TARGET=$1

if [ -z "$TARGET" ]; then
  echo "❌ 用法: $0 <minimax|deepseek|ollama-r|ollama-c>"
  exit 1
fi

# provider 名字映射
case "$TARGET" in
  minimax|minimax-cn)
    PROVIDER="minimax-cn"
    MODEL="MiniMax-M3"
    DESC="MiniMax-M3 (minimax-cn)"
    ;;
  deepseek|deepseek-cn)
    PROVIDER="deepseek-cn"
    MODEL="deepseek-v4-pro"
    DESC="DeepSeek V4 Pro (deepseek-cn)"
    ;;
  ollama-r|ollama-reasoning)
    PROVIDER="ollama-reasoning"
    MODEL="deepseek-r1:8b"
    DESC="DeepSeek R1 8B (本地推理)"
    ;;
  ollama-c|ollama-coder)
    PROVIDER="ollama-coder"
    MODEL="qwen2.5-coder:7b"
    DESC="Qwen 2.5 Coder 7B (本地代码)"
    ;;
  *)
    echo "❌ 未知 provider: $TARGET"
    echo "   可选: minimax | deepseek | ollama-r | ollama-c"
    exit 1
    ;;
esac

echo "🔄 切换主 provider: $DESC"
echo "   provider: $PROVIDER"
echo "   model: $MODEL"

# 1. 改 .env 中的活跃 provider
# 用 hermes config set 命令（这是 Hermes 允许的方式）
hermes config set provider "$PROVIDER" 2>&1 | tail -3

# 2. 改 .env 中的活跃 model
hermes config set model.default "$MODEL" 2>&1 | tail -3

# 3. 健康检查 (轻量)
echo ""
echo "🩺 健康检查 $DESC..."
case "$PROVIDER" in
  minimax-cn|deepseek-cn)
    # 云端
    KEY_VAR=$([[ "$PROVIDER" == "minimax-cn" ]] && echo "MINIMAX_CN_API_KEY" || echo "DEEPSEEK_API_KEY")
    KEY=$(awk -F= -v k="$KEY_VAR" '$1==k {print $2}' ~/.hermes/.env)
    BASE_URL=$([[ "$PROVIDER" == "minimax-cn" ]] && echo "https://api.minimaxi.com/v1" || echo "https://api.deepseek.com/v1")
    HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 15 \
      -X POST "$BASE_URL/chat/completions" \
      -H "Authorization: Bearer $KEY" \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"$MODEL\",\"max_tokens\":5,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}" 2>/dev/null || echo "TIMEOUT")
    if [ "$HTTP" = "200" ]; then
      echo "  ✅ $DESC 健康 (HTTP 200)"
    else
      echo "  ⚠️  $DESC 异常 (HTTP $HTTP)，但已切"
    fi
    ;;
  ollama-reasoning|ollama-coder)
    HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 15 \
      -X POST "http://localhost:11434/v1/chat/completions" \
      -H "Authorization: Bearer ollama" \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"$MODEL\",\"max_tokens\":5,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}" 2>/dev/null || echo "TIMEOUT")
    if [ "$HTTP" = "200" ]; then
      echo "  ✅ $DESC 健康 (HTTP 200)"
    else
      echo "  ❌ $DESC 不可用 (HTTP $HTTP)"
    fi
    ;;
esac

# 4. 重启 gateway 让配置生效
echo ""
echo "🔁 重启 gateway..."
hermes gateway restart 2>&1 | tail -5 || echo "  ⚠️ 重启失败，请手动: hermes gateway restart"

echo ""
echo "✅ 切换完成 @ $TS"
echo "   当前 provider: $PROVIDER ($MODEL)"
echo "   下次 LLM 调用就用新 provider"