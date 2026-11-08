#!/bin/bash
# verify_all_gateways.sh — 修 .env / 改配置后必跑
# 验证 8 profile 全部 healthy: .env key 同步 + launchd 进程在跑 + 端点 200
# 飞书 DM 端到端测试必须人工跑（不能从脚本里 send_message，会被 [230002] 拒绝）

echo "=== Hermes Profiles Health Verification ==="
echo "时间: $(date)"
echo

# 1. launchd 状态
echo "[1/4] launchd 状态"
launchctl list 2>/dev/null | grep "ai.hermes" | awk '{print "  PID="$1"  "$3}'
echo

# 2. .env key 一致性 + 账户类型判断
echo "[2/4] .env MINIMAX_CN_API_KEY 一致性 + 账户类型"
for prof in default afu heidou laomo maodou quant xiaobao zhenglishi; do
  if [ "$prof" = "default" ]; then
    src="$HOME/.hermes/.env"
  else
    src="$HOME/.hermes/profiles/$prof/.env"
  fi
  if [ -f "$src" ]; then
    head=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print substr($2,1,6)}' "$src")
    sha=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$src" | shasum -a 256 | awk '{print substr($1,1,12)}')
    case "$head" in
      "sk-cp-")  acctype="订阅" ;;
      "sk-api")  acctype="按量" ;;
      *)         acctype="未知" ;;
    esac
    printf "  %-12s head=%-6s type=%-4s sha=%s...\n" "$prof" "$head" "$acctype" "$sha"
  else
    echo "  $prof: ❌ .env 不存在"
  fi
done
echo

# 3. 端点 200 单测（6 同事 + zhe + quant）
echo "[3/4] 端点 200 单测（6 同事 + 2 特殊）"
for prof in afu heidou laomo maodou quant xiaobao zhenglishi; do
  src="$HOME/.hermes/profiles/$prof/.env"
  [ -f "$src" ] || continue
  KEY=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$src")
  HTTP=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 8 \
    -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
    -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null || echo "TIMEOUT")
  case "$HTTP" in
    200) ico="✅" ;;
    401) ico="❌ 401(认证失败)" ;;
    402) ico="❌ 402(余额/额度)" ;;
    429) ico="⚠️ 429(5h限速)" ;;
    *)    ico="❓ $HTTP" ;;
  esac
  echo "  $prof: $ico"
done
echo

# 4. ⭐ 飞书 DM 端到端测 — 人工
echo "[4/4] ⭐ 飞书 DM 端到端测（人工，必须）"
echo "  请华哥在飞书里 DM 5 同事的 bot（毛豆/老莫/小宝/黑豆/阿福）"
echo "  期望: 5-15 秒内收到回复"
echo ""
echo "  排查指引（如果某个没回）："
echo "    1. 看 ~/.hermes/profiles/<prof>/logs/gateway.log 末尾 30 行"
echo "    2. grep 'connected to wss' 看 WS 连接时间（如果 < 30 秒前才连，等一会）"
echo "    3. launchctl list | grep ai.hermes 看进程 PID"
echo "    4. 4xx 错误：看 §5 已知坑 — 401/402/429 区分"
echo "    5. 进程已退出：launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist 拉起"
