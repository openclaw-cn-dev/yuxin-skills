#!/bin/bash
# 寻元 + RKR 健康监控 — no_agent 模式
# 每30分钟检查一次，异常才出声，正常静默
# 检查：容器状态、API健康、DB连通性、同步进度

set -o pipefail

# ===== 配置 =====
FINDERA_CONTAINER="research-backend"
RKR_CONTAINER="rkr-backend"
PG_CONTAINER="rkr-postgres"
FINDERA_PORT=8003
RKR_PORT=8000
STATE_FILE="$HOME/.hermes/state/xunyuan_rkr_monitor.json"
NOW=$(date '+%Y-%m-%d %H:%M:%S')
ISSUES=""

# ===== 辅助函数 =====
check_docker() {
  local name="$1"
  local status
  status=$(docker ps --filter "name=$name" --format "{{.Status}}" 2>/dev/null)
  if [ -z "$status" ]; then
    echo "❌ $name: 未运行"
    return 1
  elif echo "$status" | grep -q "unhealthy"; then
    echo "⚠️ $name: unhealthy ($status)"
    return 1
  elif echo "$status" | grep -q "starting"; then
    echo "⏳ $name: 启动中 ($status)"
    return 1
  else
    echo "✅ $name: $status"
    return 0
  fi
}

check_http() {
  local port="$1"
  local label="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "http://localhost:$port/api/v1/health" 2>/dev/null)
  if [ "$code" = "200" ]; then
    echo "✅ $label API (:$port): 正常"
    return 0
  else
    echo "❌ $label API (:$port): HTTP $code"
    return 1
  fi
}

check_db() {
  local container="$1"
  local sql="$2"
  local label="$3"
  local result
  result=$(docker exec "$container" python3 -c "
import asyncio, asyncpg
async def q():
    try:
        conn = await asyncpg.connect('postgresql://rkr_user:rkr_dev_2026@postgres:5432/rkr_knowledge')
        val = await conn.fetchval(\"$sql\")
        await conn.close()
        print(val)
    except Exception as e:
        print(f'DB_ERROR:{e}')
asyncio.run(q())
" 2>/dev/null)
  if echo "$result" | grep -q "DB_ERROR"; then
    echo "❌ $label: $result"
    return 1
  elif [ -n "$result" ]; then
    echo "✅ $label: $result"
    return 0
  else
    echo "❌ $label: 无响应"
    return 1
  fi
}

# ===== 1. Docker 容器状态 =====
echo "=== Docker 容器 ==="
for c in "$FINDERA_CONTAINER" "$RKR_CONTAINER" "$PG_CONTAINER"; do
  out=$(check_docker "$c")
  echo "$out"
  if echo "$out" | grep -qE "❌|⚠️|⏳"; then
    ISSUES="$ISSUES
$out"
  fi
done

# ===== 2. API 健康检查 =====
echo ""
echo "=== API 健康 ==="
for port in $FINDERA_PORT $RKR_PORT; do
  label="FindEra"
  [ "$port" = "$RKR_PORT" ] && label="RKR"
  out=$(check_http "$port" "$label")
  echo "$out"
  if echo "$out" | grep -q "❌"; then
    ISSUES="$ISSUES
$out"
  fi
done

# ===== 3. RKR DB 文档统计 =====
echo ""
echo "=== RKR 知识库 ==="
if docker ps --filter "name=$RKR_CONTAINER" --format "{{.Status}}" 2>/dev/null | grep -q "healthy"; then
  out=$(check_db "$RKR_CONTAINER" \
    "SELECT COUNT(*) FROM documents WHERE processing_status='uploaded'" \
    "待处理文档(uploaded)")
  echo "$out"
  if echo "$out" | grep -qE "❌|⚠️"; then
    ISSUES="$ISSUES
$out"
  fi

  out=$(check_db "$RKR_CONTAINER" \
    "SELECT COUNT(*) FROM documents WHERE processing_status='failed' AND created_at > NOW() - INTERVAL '1 day'" \
    "今日失败文档")
  echo "$out"
  if echo "$out" | grep -qE "❌|⚠️"; then
    ISSUES="$ISSUES
$out"
  fi

  out=$(check_db "$RKR_CONTAINER" \
    "SELECT COUNT(*) FROM documents" \
    "文档总数")
  echo "$out"
else
  echo "⏭️ RKR DB: 容器未健康，跳过"
fi

# ===== 4. FindEra staging 同步状态 =====
echo ""
echo "=== FindEra 同步 ==="
if docker ps --filter "name=$FINDERA_CONTAINER" --format "{{.Status}}" 2>/dev/null | grep -q "healthy"; then
  sync_result=$(curl -s --connect-timeout 5 --max-time 15 \
    -X POST "http://localhost:$FINDERA_PORT/api/v1/scheduler/rkr-sync-now" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null)
  if [ -n "$sync_result" ]; then
    pushed=$(echo "$sync_result" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(r.get('pushed',0))" 2>/dev/null)
    errors=$(echo "$sync_result" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(r.get('errors',0))" 2>/dev/null)
    echo "同步结果: 推送=$pushed 错误=$errors"
    if [ "$pushed" -gt 0 ] 2>/dev/null; then
      ISSUES="$ISSUES
📤 FindEra→RKR 推送了 $pushed 条文档"
    fi
  else
    echo "⏳ 同步API无响应（可能正在处理中）"
  fi
else
  echo "⏭️ FindEra: 容器未健康，跳过同步检查"
fi

# ===== 5. 输出 =====
echo ""
echo "=== 汇总 ==="
if [ -z "$ISSUES" ]; then
  echo "✅ 寻元 + RKR 运行正常"
  exit 0
else
  echo "⚠️ 发现以下问题："
  echo "$ISSUES"
  exit 0
fi
