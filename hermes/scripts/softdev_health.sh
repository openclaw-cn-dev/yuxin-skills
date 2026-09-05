#!/bin/bash
# 07-软件项目开发 — 健康检查脚本
# 检查后端 :8006 是否在线，不在则自动拉起

PORT=8006
PROJECT_DIR="/Users/hua/6-产品研发/渔芯独角兽/01-开发中/软件项目开发/backend"

if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/api/health" 2>/dev/null | grep -q '200'; then
    # 在线，静默
    exit 0
else
    echo "⚠️ 07-软件项目开发(:$PORT) 离线，尝试拉起..."
    cd "$PROJECT_DIR" || exit 1
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > /tmp/softdev.log 2>&1 &
    sleep 3
    if curl -s "http://localhost:$PORT/api/health" | grep -q 'ok'; then
        echo "✅ 07-软件项目开发 已恢复 (PID $!)"
    else
        echo "❌ 07-软件项目开发 拉起失败，请检查 /tmp/softdev.log"
    fi
fi
