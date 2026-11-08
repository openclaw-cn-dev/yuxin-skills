#!/bin/bash
# ============================================================
# Hermes Model Rotation Daemon
# ============================================================
# 功能：
#   1. 定期健康检查所有免费 provider
#   2. 检测当前 provider 不可用时自动切换
#   3. 配额耗尽时自动轮换到下一个
#   4. 所有切换记录到日志
#
# 由 LaunchAgent 管理，开机自启 + 掉线自动重启
# ============================================================

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
ROUTER="$HERMES_HOME/scripts/multi_model_router.py"
LOG_DIR="$HERMES_HOME/logs"
ROTATION_LOG="$LOG_DIR/model_rotation.log"
STATE_DIR="$HERMES_HOME/state"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-300}"  # 5 分钟
COOLDOWN_FILE="$STATE_DIR/.rotation_cooldown"
COOLDOWN_MINUTES="${COOLDOWN_MINUTES:-30}"  # 切换冷却期

mkdir -p "$LOG_DIR" "$STATE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$ROTATION_LOG"
}

get_current_provider() {
    python3 -c "
import yaml, sys
try:
    with open('$HERMES_HOME/config.yaml') as f:
        c = yaml.safe_load(f)
    p = c.get('provider', c.get('model', {}).get('provider', 'unknown'))
    m = c.get('model', '')
    if isinstance(m, dict):
        m = m.get('default', 'unknown')
    print(f'{p}|{m}')
except: print('error|error')
"
}

switch_provider() {
    local new_provider="$1"
    local new_model="$2"

    log "🔄 切换 provider: $new_provider / $new_model"

    # ⚠️ 先停掉 default gateway（防止并发写 config 导致 0 字节）
    local gateway_pid=$(ps aux | grep "[h]ermes gateway run.*default" | awk '{print $2}')
    if [ -n "$gateway_pid" ]; then
        kill -TERM "$gateway_pid" 2>/dev/null || true
        sleep 2
        log "  已暂停 gateway (PID $gateway_pid)"
    fi

    # 改 config
    python3 -c "
import yaml
path = '$HERMES_HOME/config.yaml'
with open(path) as f:
    c = yaml.safe_load(f)

# 处理嵌套 model
if isinstance(c.get('model'), dict):
    c['model']['default'] = '$new_model'
    c['model']['provider'] = '$new_provider'
else:
    c['model'] = '$new_model'

c['provider'] = '$new_provider'

with open(path, 'w') as f:
    yaml.dump(c, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
" && log "  config.yaml 已更新" || { log "  ❌ config.yaml 更新失败"; return 1; }

    # 重启 gateway
    for profile in default; do
        local plist="com.yuxin.hermes-gateway-$profile"
        if launchctl list | grep -q "$plist"; then
            launchctl kickstart -k "gui/$(id -u)/$plist" 2>/dev/null && \
                log "  gateway-$profile 已重启" || \
                log "  ⚠️ gateway-$profile 重启失败"
        fi
    done

    # 设冷却期
    date +%s > "$COOLDOWN_FILE"
}

is_in_cooldown() {
    if [ -f "$COOLDOWN_FILE" ]; then
        local last=$(cat "$COOLDOWN_FILE")
        local now=$(date +%s)
        local elapsed=$(( (now - last) / 60 ))
        [ "$elapsed" -lt "$COOLDOWN_MINUTES" ] && return 0
    fi
    return 1
}

# ─── Main Loop ──────────────────────────────────────────────

log "========================================"
log "🚀 Model Rotation Daemon 启动"
log "   检查间隔: ${HEALTH_INTERVAL}s"
log "   切换冷却: ${COOLDOWN_MINUTES}min"
log "========================================"

while true; do
    # 冷却期检查
    if is_in_cooldown; then
        remaining=$(( COOLDOWN_MINUTES - ($(date +%s) - $(cat "$COOLDOWN_FILE")) / 60 ))
        log "⏳ 冷却期剩余约 ${remaining} 分钟，跳过本轮检查"
        sleep 60
        continue
    fi

    # 获取当前 provider
    current=$(get_current_provider)
    cur_provider="${current%%|*}"
    cur_model="${current##*|}"
    log "📊 当前: provider=$cur_provider model=$cur_model"

    # 测试当前 provider 是否健康
    HEALTHY=true
    if ! python3 "$ROUTER" health 2>/dev/null | grep -q "🟢.*${cur_provider}"; then
        HEALTHY=false
        log "🔴 当前 provider $cur_provider 不健康!"
    fi

    if [ "$HEALTHY" = false ] && ! is_in_cooldown; then
        log "🔍 寻找可用替代 provider..."

        # 运行路由器的健康检查，找第一个健康的免费 provider
        BEST=$(python3 "$ROUTER" health 2>/dev/null | grep "🟢" | head -1 | awk '{print $2}' | sed 's/://')

        if [ -n "$BEST" ] && [ "$BEST" != "$cur_provider" ]; then
            # 从注册表获取该 provider 的默认模型
            BEST_MODEL=$(python3 -c "
import json
with open('$HERMES_HOME/state/provider_registry.json') as f:
    r = json.load(f)
for p in r['providers']:
    if p['name'] == '$BEST':
        print(p['model'])
        break
")
            if [ -n "$BEST_MODEL" ]; then
                log "✅ 切换到: $BEST / $BEST_MODEL"
                switch_provider "$BEST" "$BEST_MODEL"
            fi
        else
            log "⚠️ 没有找到可用的替代 provider"
        fi
    fi

    sleep "$HEALTH_INTERVAL"
done
