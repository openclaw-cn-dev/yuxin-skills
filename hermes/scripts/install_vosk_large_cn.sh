#!/bin/bash
# 安装 vosk 大模型 — C 方案核心步骤
# 用法：bash install_vosk_large_cn.sh
# 前提：已经下载好 vosk-model-cn-0.22.zip

set -e

VOICE_DIR="$HOME/hermes/voice/models"
ZIP="$VOICE_DIR/vosk-model-cn-0.22.zip"
EXTRACTED="$VOICE_DIR/vosk-model-cn-0.22"
SMALL_DIR="$VOICE_DIR/vosk-model-small-cn-0.22"

echo "=== vosk 大模型安装器 ==="
echo ""

# 检查 zip
if [ ! -f "$ZIP" ]; then
    echo "❌ 没找到 $ZIP"
    echo "请先下载："
    echo "  curl -L -o $ZIP https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip"
    exit 1
fi

SIZE=$(stat -f%z "$ZIP" 2>/dev/null || stat -c%s "$ZIP")
SIZE_MB=$((SIZE / 1024 / 1024))
echo "📦 zip 大小: ${SIZE_MB}MB"

# 大小校验（1.3GB±10%）
if [ "$SIZE_MB" -lt 1150 ] || [ "$SIZE_MB" -gt 1500 ]; then
    echo "⚠️  大小异常，预期 ~1300MB。继续吗？[y/N]"
    read -r ans
    [[ "$ans" =~ ^[Yy]$ ]] || exit 1
fi

# 解压
if [ -d "$EXTRACTED" ]; then
    echo "⚠️  $EXTRACTED 已存在，删除老的？[y/N]"
    read -r ans
    [[ "$ans" =~ ^[Yy]$ ]] && rm -rf "$EXTRACTED"
fi

echo "📂 解压中..."
cd "$VOICE_DIR"
unzip -q "$ZIP"
echo "✅ 解压完成"

# 验证关键文件
if [ ! -f "$EXTRACTED/conf/model.conf" ]; then
    echo "❌ 解压后缺关键文件，目录可能不完整"
    exit 1
fi
echo "✅ 模型结构验证通过"

# 删除 zip 省空间（可选）
echo ""
echo "删除 zip 省 1.3GB 空间？[Y/n]"
read -r ans
[[ "$ans" =~ ^[Nn]$ ]] || rm -f "$ZIP"
echo ""

# 启动 LaunchAgent
echo "🚀 重启 LaunchAgent（让代码自动加载大模型）"
AGENT_LABEL="gui/$(id -u)/com.yuxin.voice.wake"
launchctl kickstart -k "$AGENT_LABEL" 2>/dev/null || {
    launchctl unload ~/Library/LaunchAgents/com.yuxin.voice.wake.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.yuxin.voice.wake.plist
}
sleep 3

echo ""
echo "=== 验证 ==="
PID=$(pgrep -f porcupine_listener | head -1)
if [ -z "$PID" ]; then
    echo "❌ 进程没起来"
    tail -20 ~/hermes/voice/logs/porcupine.out.log
    exit 1
fi
echo "✅ PID=$PID"
sleep 5
echo "--- 启动日志 ---"
tail -10 ~/hermes/voice/logs/porcupine.out.log

echo ""
echo "🎉 完成！现在喊 '玉芬' 试试"
echo "如果不行：bash ~/.hermes/scripts/test_wake_e2e.sh"
