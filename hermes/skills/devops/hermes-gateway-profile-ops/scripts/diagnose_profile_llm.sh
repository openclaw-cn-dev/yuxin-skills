#!/bin/bash
# diagnose_profile_llm.sh - 一键诊断 Hermes profile LLM 路由问题
# 用法: bash diagnose_profile_llm.sh <profile_name>
# 示例: bash diagnose_profile_llm.sh quant
#
# 输出:
#   1. .env LLM keys 列表
#   2. yaml custom_providers 段是否存在
#   3. gateway 状态（running/feishu/pid）
#   4. 最近 gateway.log 行
#   5. 最近 1 小时 429/404 错误计数
#   6. 判定结论 + 推荐修法
#
# 可选参数:
#   --quick   只检查进程 + 飞书 ws 长连接 + 最近 5 条 response ready 行（修完后快速确认用）

set -e

QUICK=false
if [ "${1:-}" = "--quick" ]; then
  QUICK=true
  shift
fi

PROFILE="${1:?用法: $0 [--quick] <profile_name>}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PROFILE_DIR="$HERMES_HOME/profiles/$PROFILE"

if [ ! -d "$PROFILE_DIR" ]; then
  echo "❌ profile 目录不存在: $PROFILE_DIR"
  exit 1
fi

echo "================================================"
echo "  Hermes Profile LLM 路由诊断"
echo "  profile: $PROFILE"
echo "  home:    $HERMES_HOME"
echo "  mode:    $([ "$QUICK" = true ] && echo 'quick (修完后快速确认)' || echo 'full')"
echo "================================================"
echo ""

if [ "$QUICK" = true ]; then
  # ====== QUICK MODE: 修完后快速确认 ======
  echo "=== Q1. 进程在跑？（用 ps auxww，不用 pgrep）==="
  PS_LINE=$(ps auxww | grep "hermes.*--profile $PROFILE" | grep -v grep | head -1)
  if [ -n "$PS_LINE" ]; then
    PID=$(echo "$PS_LINE" | awk '{print $2}')
    echo "  ✓ 进程 PID=$PID 在跑"
    echo "  cmd: $(echo "$PS_LINE" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')"
    
    echo ""
    echo "=== Q2. 飞书 ws 长连接活着？==="
    WS=$(lsof -nP -p "$PID" 2>/dev/null | grep "183.36.42.103:443" | grep ESTABLISHED | wc -l | tr -d ' ')
    if [ "$WS" -gt 0 ]; then
      echo "  ✓ pid=$PID 连了 $WS 个 ws 到 feishu msg-frontier"
    else
      echo "  ✗ 没飞书 ws 连接"
    fi
  else
    echo "  ✗ 进程没在跑"
  fi
  
  echo ""
  echo "=== Q3. 最近 5 条 inbound + response（最关键的跑通证据）==="
  if [ -f "$PROFILE_DIR/logs/gateway.log" ]; then
    tail -200 "$PROFILE_DIR/logs/gateway.log" | grep -E "inbound message|response ready" | tail -5
    INBOUND=$(tail -200 "$PROFILE_DIR/logs/gateway.log" | grep -c "inbound message")
    RESPONSE=$(tail -200 "$PROFILE_DIR/logs/gateway.log" | grep -c "response ready")
    FAILED=$(tail -200 "$PROFILE_DIR/logs/gateway.log" | grep -c "API call failed")
    echo ""
    echo "  最近 200 行统计: inbound=$INBOUND response=$RESPONSE failed=$FAILED"
    if [ "$RESPONSE" -gt 0 ] && [ "$FAILED" -eq 0 ]; then
      echo "  ✅ 该 profile 实际跑通"
    elif [ "$RESPONSE" -gt 0 ] && [ "$FAILED" -gt 0 ]; then
      echo "  ⚠️  部分跑通但有 failed，看具体错误"
    else
      echo "  ⚠️  没有成功响应记录"
    fi
  else
    echo "  ❌ gateway.log 不存在"
  fi
  echo ""
  exit 0
fi

# ====== FULL MODE: 初次诊断 ======
echo "=== 1. .env LLM keys ==="
grep -E "MINIMAX_CN_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY|MINIMAX_API_KEY" \
  "$PROFILE_DIR/.env" 2>/dev/null | sed 's/=.*/=***/' || echo "(空或无 LLM key)"
ENV_KEY_COUNT=$(grep -cE "MINIMAX_CN_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY" \
  "$PROFILE_DIR/.env" 2>/dev/null || echo 0)
echo "总计: $ENV_KEY_COUNT 个 LLM key"
echo ""

echo "=== 2. yaml custom_providers ==="
if grep -q "^custom_providers:" "$PROFILE_DIR/config.yaml" 2>/dev/null; then
  echo "⚠️  config.yaml 含 custom_providers 段"
  echo "--- 段内容 ---"
  grep -A 12 "^custom_providers:" "$PROFILE_DIR/config.yaml" | head -15
  echo "--- 建议: 检查是否与 env 层 MINIMAX_CN_API_KEY 冲突 ---"
else
  echo "✅ config.yaml 不含 custom_providers 段（推荐，无冲突）"
fi
echo ""

echo "=== 3. gateway 进程 + 状态 ==="
# 注意：用 ps auxww 不用 pgrep（macOS 上 pgrep 对 hermes-gateway 假阴性）
PS_LINE=$(ps auxww | grep "hermes.*--profile $PROFILE" | grep -v grep | head -1)
if [ -n "$PS_LINE" ]; then
  PID=$(echo "$PS_LINE" | awk '{print $2}')
  echo "  ✓ 进程 PID=$PID 在跑"
  # 飞书 ws 长连接
  WS=$(lsof -nP -p "$PID" 2>/dev/null | grep "183.36.42.103:443" | grep ESTABLISHED | wc -l | tr -d ' ')
  echo "  飞书 ws 长连接: $WS 个"
else
  echo "  ✗ 进程没在跑"
fi
# gateway_state.json（如果存在）
if [ -f "$PROFILE_DIR/gateway_state.json" ]; then
  python3 -c "
import json
s = json.load(open('$PROFILE_DIR/gateway_state.json'))
print(f'  gateway_state.json: state={s.get(\"gateway_state\")} feishu={s.get(\"platforms\",{}).get(\"feishu\",{}).get(\"state\")}')
"
fi
echo ""

echo "=== 4. 最近 10 行 gateway.log ==="
if [ -f "$PROFILE_DIR/logs/gateway.log" ]; then
  tail -10 "$PROFILE_DIR/logs/gateway.log"
else
  echo "❌ gateway.log 不存在"
fi
echo ""

echo "=== 5. 最近 1 小时 429/404 错误计数 ==="
if [ -f "$PROFILE_DIR/logs/gateway.error.log" ]; then
  RECENT=$(grep -cE "$(date '+%Y-%m-%d %H')" "$PROFILE_DIR/logs/gateway.error.log" 2>/dev/null || echo 0)
  TOTAL_429=$(grep -c "RateLimitError\|已达到 Token Plan" "$PROFILE_DIR/logs/gateway.error.log" 2>/dev/null || echo 0)
  TOTAL_404=$(grep -c "404 page not found" "$PROFILE_DIR/logs/gateway.error.log" 2>/dev/null || echo 0)
  echo "  最近 1 小时新错误: $RECENT"
  echo "  历史 429 计数:     $TOTAL_429"
  echo "  历史 404 计数:     $TOTAL_404"
else
  echo "(无 gateway.error.log)"
fi
echo ""

echo "=== 6. MiniMax 配额全局检查 ==="
GLOBAL_429=$(grep -c "已达到 Token Plan 用量上限" "$HERMES_HOME/logs/gateway.log" 2>/dev/null || echo 0)
echo "  default gateway 配额 429 计数: $GLOBAL_429"
if [ "$GLOBAL_429" -gt 0 ]; then
  echo "  ⚠️  MiniMax Token Plan 配额已用完（任何 profile 调 LLM 都会 429）"
fi
echo ""

echo "=== 7. 判定结论 ==="
if [ "$ENV_KEY_COUNT" -eq 0 ]; then
  echo "  🔴 根因: env 层缺 MINIMAX_CN_API_KEY"
  echo "  📋 修法: 把 default 同款 key 追加到 $PROFILE_DIR/.env"
  echo "           grep '^MINIMAX_CN_API_KEY=*** ' $HERMES_HOME/.env >> $PROFILE_DIR/.env"
  echo "           然后 kill -TERM <pid> + gateway run --profile $PROFILE --replace"
elif grep -q "^custom_providers:" "$PROFILE_DIR/config.yaml" 2>/dev/null; then
  echo "  🟡 根因: yaml custom_providers 可能与 env 冲突"
  echo "  📋 修法: 删除 yaml 里的 custom_providers 段，只保留 env 层"
elif [ "$GLOBAL_429" -gt 0 ]; then
  echo "  🟢 配置已正确，但配额用完"
  echo "  📋 行动: 建议用户升级 MiniMax Token Plan 或买积分"
else
  echo "  ✅ 配置看起来正常，如仍有问题需进一步日志分析"
fi
echo ""
echo "================================================"
