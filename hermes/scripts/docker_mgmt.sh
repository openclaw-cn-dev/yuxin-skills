#!/bin/bash
# Docker 容器管理脚本 — 每 2 小时自动优化
# 渔芯科技 · 玉芬维护 · 2026-08-11

set -euo pipefail
LOG="/Users/hua/.hermes/logs/docker_mgmt.log"
mkdir -p "$(dirname "$LOG")"

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 容器管理开始 ==="

# ── 0. Docker 就绪检查 ──
if ! docker ps >/dev/null 2>&1; then
    echo "Docker 不可用，跳过本轮"
    exit 0
fi
docker context use desktop-linux 2>/dev/null || true

# ── 1. 清理已停止超过 24h 的容器 ──
STOPPED=$(docker ps -a --filter "status=exited" --format '{{.ID}} {{.Names}} {{.Status}}' 2>/dev/null)
if [ -n "$STOPPED" ]; then
    echo "$STOPPED" | while read id name status; do
        # 提取退出时间，只清理超过 24h 的
        if echo "$status" | grep -q "days\|day"; then
            echo "  清理僵尸容器: $name ($status)"
            docker rm "$id" 2>/dev/null || echo "  跳过 $name (可能被占用)"
        fi
    done
fi

# ── 2. 清理悬空镜像（dangling） ──
DANGLING=$(docker images -f "dangling=true" -q 2>/dev/null)
if [ -n "$DANGLING" ]; then
    COUNT=$(echo "$DANGLING" | wc -l | tr -d ' ')
    echo "  清理悬空镜像: $COUNT 个"
    docker rmi $DANGLING 2>/dev/null || echo "  部分镜像清理失败(可能被依赖)"
fi

# ── 3. 清理未使用的卷（仅限不在运行的项目的卷） ──
# 先标记所有运行容器的卷为受保护
RUNNING_CIDS=$(docker ps -q 2>/dev/null)
if [ -n "$RUNNING_CIDS" ]; then
    RUNNING_VOLUMES=$(docker inspect $RUNNING_CIDS --format '{{range .Mounts}}{{.Name}} {{end}}' 2>/dev/null | tr ' ' '\n' | sort -u)
else
    RUNNING_VOLUMES=""
fi
UNUSED_VOLUMES=$(docker volume ls -q --filter "dangling=true" 2>/dev/null)
if [ -n "$UNUSED_VOLUMES" ]; then
    CLEAN_COUNT=0
    for v in $UNUSED_VOLUMES; do
        if ! echo "$RUNNING_VOLUMES" | grep -qFx "$v"; then
            echo "  清理未使用卷: $v"
            docker volume rm "$v" 2>/dev/null && CLEAN_COUNT=$((CLEAN_COUNT+1)) || true
        fi
    done
    echo "  卷清理: $CLEAN_COUNT 个已删除"
fi

# ── 4. 截断超大容器日志 (>200MB) ──
for cid in $(docker ps -q 2>/dev/null); do
    LOG_PATH=$(docker inspect "$cid" --format '{{.LogPath}}' 2>/dev/null)
    if [ -f "$LOG_PATH" ]; then
        SIZE=$(stat -f%z "$LOG_PATH" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt 209715200 ] 2>/dev/null; then  # 200MB
            cname=$(docker inspect "$cid" --format '{{.Name}}' 2>/dev/null | sed 's|^/||')
            SIZE_MB=$((SIZE / 1048576))
            echo "  截断日志: $cname ($SIZE_MB MB)"
            sudo truncate -s 0 "$LOG_PATH" 2>/dev/null || echo "  跳过 $cname (无权限)"
        fi
    fi
done

# ── 5. 内存状态报告 ──
echo ""
echo "── 资源状态 ──"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null | head -20

# ── 6. 磁盘回收统计 ──
echo ""
echo "── 磁盘回收 ──"
docker system df 2>/dev/null

# ── 7. 运行容器健康检查 ──
echo ""
echo "── 健康检查 ──"
UNHEALTHY=$(docker ps --filter "health=unhealthy" --format '{{.Names}}' 2>/dev/null)
if [ -n "$UNHEALTHY" ]; then
    echo "⚠️  异常容器:"
    echo "$UNHEALTHY"
else
    echo "✅ 所有容器健康"
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 容器管理结束 ==="
echo ""
