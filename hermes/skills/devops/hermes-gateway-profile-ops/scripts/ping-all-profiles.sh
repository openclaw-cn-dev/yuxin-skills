#!/bin/bash
# ping-all-profiles.sh
# 一键扫所有 profile 的 LLM 端点连通性，输出 HTTP 码 + 错误摘要
# 用途：402/429 故障时快速定位是 key 错、余额空、还是端点挂
#
# 用法：bash ping-all-profiles.sh [profile_name ...]
#   不传参 = 扫全部 7 个
#   传参 = 只扫指定 profile
#
# 注意：此脚本不读 .env 明文显示 key，只取前 8 字符做标识

set -e

PROFILES_ALL="default afu heidou laomo maodou quant xiaobao zhenglishi"
PROFILES="${1:-$PROFILES_ALL}"

# endpoint 映射 (profile provider -> url)
endpoint_for() {
  case "$1" in
    minimax-cn) echo "https://api.minimaxi.com/anthropic" ;;
    minimax-intl) echo "https://api.MiniMax.io/anthropic" ;;
    minimax-us) echo "https://api.MiniMax.us/anthropic" ;;
    *) echo "" ;;
  esac
}

printf "%-12s %-8s %-6s %-50s\n" "PROFILE" "KEY_PFX" "HTTP" "DETAIL"
printf "%-12s %-8s %-6s %-50s\n" "-------" "-------" "----" "------"

for prof in $PROFILES; do
  cfg="$HOME/.hermes/profiles/$prof/config.yaml"
  env="$HOME/.hermes/profiles/$prof/.env"

  # 读 provider
  provider=$(grep -E "^[[:space:]]+provider:" "$cfg" 2>/dev/null | head -1 | awk '{print $2}')
  [ -z "$provider" ] && provider="unknown"

  url=$(endpoint_for "$provider")
  if [ -z "$url" ]; then
    printf "%-12s %-8s %-6s %-50s\n" "$prof" "?" "?" "unknown provider: $provider"
    continue
  fi

  # 抽 key (避免 shell 转义问题，用 awk)
  key_var=$(echo "$provider" | tr 'a-z-' 'A-Z_')_API_KEY
  KEY=$(awk -F= -v k="$key_var" '$1==k {print $2}' "$env" 2>/dev/null | head -1)

  if [ -z "$KEY" ]; then
    printf "%-12s %-8s %-6s %-50s\n" "$prof" "?" "?" "no key in .env ($key_var)"
    continue
  fi

  KEY_PFX="${KEY:0:8}"

  # 打最小请求
  resp=$(curl -sS -o /tmp/ping_body.txt -w "%{http_code}" \
    -X POST "${url}/v1/messages" \
    -H "x-api-key: $KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    --max-time 10 \
    -d '{"model":"MiniMax-M3","max_tokens":4,"messages":[{"role":"user","content":"."}]}' 2>&1) || resp="ERR"

  # 提取错误摘要
  detail=$(grep -oE '"message":"[^"]{0,60}"' /tmp/ping_body.txt 2>/dev/null | head -1 | sed 's/^"message":"//;s/"$//')
  [ -z "$detail" ] && detail=$(head -c 60 /tmp/ping_body.txt 2>/dev/null)

  printf "%-12s %-8s %-6s %-50s\n" "$prof" "$KEY_PFX" "$resp" "$detail"
done

echo ""
echo "HTTP 码速查："
echo "  200 = 正常 | 401 = key 错 | 402 = 余额空(1008)/套餐超限(2056) | 429 = 限流 | 5xx = 端点挂"
