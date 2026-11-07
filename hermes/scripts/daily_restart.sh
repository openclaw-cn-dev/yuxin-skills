#!/bin/bash
# 每日重启脚本 - 清理缓存，释放内存

echo "=== $(date) 重启开始 ==="

# 1. 重启Docker容器（lookforge系列 + memos）
echo "重启Docker容器..."
docker restart lookforge-chromadb lookforge-backend lookforge-redis lookforge-db memos 2>/dev/null
echo "Docker容器重启完成"

# 2. 重启Hermes Gateway（所有profile + openclaw）
echo "重启Hermes Gateway..."

# 默认profile
pkill -f "hermes_cli.main gateway run" || true
sleep 2

# 各profile gateway（用launchctl管理）
for profile in laomo heidou maodou afu xiaobao quant zhenglishi; do
    PID=$(ps aux | grep "hermes_cli.main --profile $profile gateway run" | grep -v grep | awk '{print $2}' | head -1)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null
        echo "已停止 $profile (PID: $PID)"
    fi
done

sleep 3

# 重启各profile gateway
for profile in laomo heidou maodou afu xiaobao quant zhenglishi; do
    nohup hermes gateway run --profile $profile --replace > /dev/null 2>&1 &
    echo "已启动 $profile"
done

# 默认profile
nohup hermes gateway run --replace > /dev/null 2>&1 &
echo "已启动 default"

# openclaw gateway
openclaw_pid=$(ps aux | grep "openclaw/dist/index.js gateway" | grep -v grep | awk '{print $2}' | head -1)
if [ -n "$openclaw_pid" ]; then
    kill $openclaw_pid 2>/dev/null
    echo "已停止 openclaw gateway (PID: $openclaw_pid)"
fi
sleep 2
nohup openclaw gateway > /dev/null 2>&1 &
echo "已启动 openclaw gateway"

echo "=== $(date) 重启完成 ==="
