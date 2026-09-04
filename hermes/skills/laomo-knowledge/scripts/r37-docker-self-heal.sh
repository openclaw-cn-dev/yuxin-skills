#!/bin/bash
# R37 SOP: 老莫 cron 心跳检测到 docker daemon DOWN 时的标准自愈流程
# 触发条件: verify-heartbeat-infra.sh 输出 "Docker daemon: DOWN" 或 API :8000 返回 000
# 用法: bash ~/.hermes/skills/laomo-knowledge/scripts/r37-docker-self-heal.sh
# 退出码: 0 = 全部 healthy, 1 = 自愈失败需要人工介入

set -u

# R166 (2026-09-03): cron 心跳在 profile HOME 劫持态下跑, 必须显式 real-home override,
# 否则 open -a Docker 会拉起 foreign VM context (无 rkr 镜像, R157 context mismatch)
# 且 docker CLI 后续命令也会去读 hijacked socket 路径报 "no such file"。
export HOME=/Users/hua

CONTAINERS=(rkr-postgres rkr-redis rkr-minio rkr-elasticsearch rkr-backend
            rkr-frontend rkr-celery-beat rkr-processing-pool rkr-processing-pool-2
            rkr-staging-pool)

echo "=== R37 SOP: docker daemon + RKR 10 容器自愈 ==="

# Step 1: 检查 daemon 状态
DAEMON_UP=$(docker info 2>&1 | grep -c "Server Version" || true)
if [ "$DAEMON_UP" = "0" ]; then
  echo "[1/4] daemon DOWN → open -a Docker"
  open -a Docker
  # 等 daemon 启动 (历史观测 15-25s)
  for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 5
    DAEMON_UP=$(docker info 2>&1 | grep -c "Server Version" || true)
    if [ "$DAEMON_UP" = "1" ]; then
      echo "    daemon UP @ ~$((i*5))s"
      break
    fi
  done
  if [ "$DAEMON_UP" = "0" ]; then
    echo "FAIL: daemon 30s 内未启动, 需人工 open -a Docker 重试"
    exit 1
  fi
else
  echo "[1/4] daemon 已 UP, 跳过 open"
fi

# Step 2: 启动所有 RKR 容器
echo "[2/4] docker start 10 容器"
docker start "${CONTAINERS[@]}" 2>&1 | tail -11

# Step 3: 等 healthy (历史观测 40-55s)
echo "[3/4] 等容器 healthy"
HEALTHY=0
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  sleep 5
  HEALTHY=$(docker ps --filter "name=rkr-" --format "{{.Names}} {{.Status}}" | grep -c "healthy\|Up" || true)
  echo "    T+$((i*5))s: $HEALTHY/10 容器 Up"
  if [ "$HEALTHY" -ge "10" ]; then
    break
  fi
done

# Step 4: 验证 RKR API
echo "[4/4] 全栈健康验证"
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>&1 || echo "000")
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>&1 || echo "000")
echo "    API :8000      = $API_CODE"
echo "    Frontend :5173 = $FRONTEND_CODE"

if [ "$API_CODE" = "200" ] && [ "$HEALTHY" -ge "10" ]; then
  echo "=== R37 SOP: 自愈成功 ==="
  exit 0
else
  echo "=== R37 SOP: 自愈失败 (healthy=$HEALTHY api=$API_CODE) ==="
  exit 1
fi
