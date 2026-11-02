#!/bin/bash
# 修复被 CC Switch 改坏的 Codex config.toml → 恢复 ZAI 直连智谱
# 用法: bash fix_codex_config.sh [--test]
#   --test  顺带 curl 实测智谱 key 是否有效

set -uo pipefail

# 绝对路径（勿用 $HOME/~，agent profile 下会被劫持到镜像 home）
CONFIG="/Users/hua/.codex/config.toml"
CCDB="/Users/hua/.cc-switch/cc-switch.db"
TEMPLATE="$(cd "$(dirname "$0")/.." && pwd)/templates/config.toml.zai"
TS=$(date +%Y%m%d_%H%M%S)

echo "🔧 修复 Codex config.toml（恢复 ZAI 直连智谱）"

# 1. 备份当前（可能已坏的）config
if [ -f "$CONFIG" ]; then
  cp "$CONFIG" "$CONFIG.bak-$TS"
  echo "✅ 1. 已备份: $CONFIG.bak-$TS"
else
  echo "⚠️ 1. $CONFIG 不存在，跳过备份"
fi

# 2. 从 cc-switch db 读最新智谱 Coding key（glm provider 的 api_key 字段）
KEY=$(sqlite3 "$CCDB" "SELECT settings_config FROM providers WHERE id='glm';" 2>/dev/null \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('api_key',''))" 2>/dev/null)
if [ -z "$KEY" ] || [ "$KEY" = "None" ]; then
  echo "❌ 2. 从 cc-switch db 读不到 glm provider 的 key"
  echo "   手动查: sqlite3 ~/.cc-switch/cc-switch.db \"SELECT settings_config FROM providers WHERE id='glm';\""
  exit 1
fi
echo "✅ 2. key: ${KEY:0:10}...${KEY: -4} (len=${#KEY})"

# 3. 用黄金模板 + key 写 config
if [ ! -f "$TEMPLATE" ]; then
  echo "❌ 3. 模板缺失: $TEMPLATE"
  exit 1
fi
sed "s|__ZAI_KEY__|$KEY|" "$TEMPLATE" > "$CONFIG"
echo "✅ 3. 已写入正确 ZAI 直连结构（model_provider=ZAI + base_url=/api/v1）"

# 4. TOML 语法验证
python3 -c "
import tomllib
d = tomllib.load(open('$CONFIG','rb'))
assert d.get('model_provider') == 'ZAI', 'model_provider != ZAI'
assert 'ZAI' in d.get('model_providers',{}), '[model_providers.ZAI] 段缺失'
print('✅ 4. TOML 有效: model_provider=ZAI, [model_providers.ZAI] 存在')
" || { echo "❌ 4. TOML 验证失败，回滚到备份"; cp "$CONFIG.bak-$TS" "$CONFIG"; exit 1; }

# 5. 可选：实测 key
if [ "${1:-}" = "--test" ]; then
  echo "🔍 5. 实测 key（/api/v1/responses, glm-5.3）..."
  RESP=$(curl -s --max-time 30 https://open.bigmodel.cn/api/v1/responses \
    -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
    -d '{"model":"glm-5.3","input":"回复ok"}' 2>/dev/null)
  if echo "$RESP" | grep -qE '"code":(401|1113|429)|令牌已过期|余额不足'; then
    echo "❌ 5. key 无效: $(echo "$RESP" | head -c 200)"
    echo "   → 需华哥去智谱开放平台核实 Coding 包月续费"
  elif echo "$RESP" | grep -q '"object":"response"'; then
    echo "✅ 5. key 有效，链路正常"
  else
    echo "⚠️ 5. 返回异常，需人工判断: $(echo "$RESP" | head -c 200)"
  fi
fi

echo
echo "✅ 修复完成。请华哥重新打开 ChatGPT 对话串。"
echo "⚠️ 若发消息报 401/1113 = key 失效（结构没问题，是 key 过期），去智谱续费。"
echo "⚠️ CC Switch 会再次覆盖 config —— 根治需停 CC Switch 自启（见 SKILL.md 坑点 2）。"
