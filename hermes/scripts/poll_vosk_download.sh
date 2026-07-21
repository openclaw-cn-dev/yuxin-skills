#!/bin/bash
# vosk 大模型下载进度监控
# 每次 cron 跑都会输出当前进度
# 下载完成 → 自动解压 + 重启服务

set -e

VOICE_DIR="$HOME/hermes/voice/models"
ZIP="$VOICE_DIR/vosk-model-cn-0.22.zip"
EXTRACTED="$VOICE_DIR/vosk-model-cn-0.22"
EXPECTED_MB=1295

# 检查进程
DL_PID=$(pgrep -f "curl.*vosk-model-cn" | head -1)

if [ -z "$DL_PID" ]; then
    if [ -d "$EXTRACTED" ] && [ -f "$EXTRACTED/conf/model.conf" ]; then
        echo "✅ vosk 大模型已安装 ($EXTRACTED)"
        exit 0
    fi
    echo "❌ 下载已停止且模型未解压，请检查"
    exit 1
fi

# 进度
if [ ! -f "$ZIP" ]; then
    echo "0MB / ${EXPECTED_MB}MB （zip 还没创建）"
    exit 0
fi

SIZE_MB=$(du -m "$ZIP" | awk '{print $1}')
PCT=$(echo "scale=1; $SIZE_MB * 100 / $EXPECTED_MB" | bc 2>/dev/null || echo "0")
echo "📥 vosk 大模型: ${SIZE_MB}MB / ${EXPECTED_MB}MB (${PCT}%)"

# 下完没？1.25GB 以上认为基本完成
if [ "$SIZE_MB" -ge 1250 ]; then
    echo "✅ 下载基本完成！自动解压..."
    cd "$VOICE_DIR"
    unzip -q "$ZIP"
    rm -f "$ZIP"
    echo "🎉 已解压到 $EXTRACTED"

    # 重启 LaunchAgent
    launchctl kickstart -k "gui/$(id -u)/com.yuxin.voice.wake" 2>/dev/null || {
        launchctl unload ~/Library/LaunchAgents/com.yuxin.voice.wake.plist 2>/dev/null
        sleep 1
        launchctl load ~/Library/LaunchAgents/com.yuxin.voice.wake.plist
    }
    echo "🚀 LaunchAgent 已重启，喊 '玉芬' 试试"
fi
