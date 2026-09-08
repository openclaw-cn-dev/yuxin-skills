#!/usr/bin/env bash
# R198 批量恢复一键脚本 — 工作窗口内 daemon UP 时全量恢复 daemon 反弹群死的 12 Exited 容器
# 节奏基线 (R289 2026-09-07 13:05 CST 实测闭环, R256 后第二次完整执行):
#   Phase1 infra 四件套 docker start -> 20s 后全 healthy (含 elasticsearch)
#   Phase2 应用六件套 + Phase3 research 2 docker start -> 25s 后 RKR API/:5173 双 200
#   fleet 扫描无 NOT_UP 行 = 17/17 全 Up
# 前置条件: daemon _ping=200 且处于工作窗口 (13:00-17:xx)。
#   窗口外全栈启动违反 Pitfall #45(a); 单容器 OOM 退出走 R198 单容器变体 (见 SKILL.md 工作窗口 SOP), 不用本脚本。
# 用法: bash /Users/hua/.hermes/skills/laomo-heartbeat/scripts/r198_batch_recover.sh

set -u
export DOCKER_HOST=unix:///Users/hua/.docker/run/docker.sock

INFRA="rkr-postgres rkr-redis rkr-minio rkr-elasticsearch"
APPS="rkr-backend rkr-frontend rkr-celery-beat rkr-staging-pool rkr-processing-pool rkr-processing-pool-2"
RESEARCH="research-frontend research-backend"

fail=0

echo "== Phase 1/3: infra 四件套 =="
docker start $INFRA || fail=1
sleep 20
docker ps --filter name=rkr --format '{{.Names}}\t{{.Status}}'

echo "== Phase 2/3: 应用六件套 =="
docker start $APPS || fail=1

echo "== Phase 3/3: research 2 =="
docker start $RESEARCH || fail=1
sleep 25

echo "== 复验 (R267 一体化命令变体) =="
curl -s -o /dev/null -w 'RKR_API=%{http_code}\n' http://localhost:8000/api/health
curl -s -o /dev/null -w 'FRONTEND_5173=%{http_code}\n' http://localhost:5173
NOT_UP=$(docker ps -a --format '{{.Names}}\t{{.Status}}' | awk '$2!~/^Up/')
if [ -n "$NOT_UP" ]; then echo "NOT_UP:"; echo "$NOT_UP"; fail=1; else echo "fleet 扫描: 无 NOT_UP 行"; fi
docker ps --format '{{.Names}}\t{{.Status}}' | sort

echo "== 期望: RKR_API=200 + FRONTEND_5173=200 + 无 NOT_UP 行 = 17/17 全 Up =="
echo "注: rkr-frontend / research-frontend 无 healthcheck, Status 无 (healthy) 徽标属正常, 非启动失败"
exit $fail
