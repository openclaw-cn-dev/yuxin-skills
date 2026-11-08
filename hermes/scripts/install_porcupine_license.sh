#!/bin/bash
# Porcupine License 安装器（华哥手动跑）
# 用法：bash ~/.hermes/scripts/install_porcupine_license.sh
# 需要华哥手动输入 AccessKey 和 .ppn 文件路径

set -e

VOICE_DIR="$HOME/hermes/voice"
LICENSE_FILE="$VOICE_DIR/.porcupine_key"
PPN_DEST="$VOICE_DIR/models/hey-yuxin_mac.ppn"

echo "═══════════════════════════════════════════════════"
echo " 玉芬 Porcupine License 一键安装"
echo "═══════════════════════════════════════════════════"
echo ""

# 1. 输入 AccessKey
echo "📋 第 1 步：粘贴 AccessKey"
echo "   (在 Picovoice Console → AccessKey 页面，长得像 oP/3wxxx== 的字符串)"
echo ""
read -p "AccessKey: " ACCESS_KEY

if [ -z "$ACCESS_KEY" ]; then
    echo "❌ 没输入 AccessKey，中止"
    exit 1
fi

# 验证格式（Base64-like，30+ 字符）
if [ ${#ACCESS_KEY} -lt 20 ]; then
    echo "⚠️  AccessKey 太短（${#ACCESS_KEY} 字符），正常应该 30+。继续吗？[y/N]"
    read -r ans
    [[ "$ans" =~ ^[Yy]$ ]] || exit 1
fi

# 2. 写文件
echo "$ACCESS_KEY" > "$LICENSE_FILE"
chmod 600 "$LICENSE_FILE"
echo "✅ AccessKey 已写入 $LICENSE_FILE（权限 600）"
echo ""

# 3. .ppn 文件路径
echo "📋 第 2 步：嗨玉芬.ppn 文件位置"
echo "   (从 Picovoice Console 下载的 .ppn 文件)"
echo ""
read -p ".ppn 文件路径（拖入终端或粘贴路径）: " PPN_PATH

if [ -z "$PPN_PATH" ]; then
    echo "⚠️  未提供 .ppn 路径 → 先只装 License，用内置 jarvis 跑通流程"
    echo "   之后可以手动执行："
    echo "     cp <你的.ppn> $PPN_DEST"
    echo "     launchctl kickstart -k gui/\$(id -u)/com.yuxin.voice.wake"
elif [ ! -f "$PPN_PATH" ]; then
    echo "❌ 文件不存在：$PPN_PATH"
    exit 1
else
    cp "$PPN_PATH" "$PPN_DEST"
    chmod 644 "$PPN_DEST"
    SIZE=$(stat -f%z "$PPN_DEST" 2>/dev/null || stat -c%s "$PPN_DEST")
    echo "✅ .ppn 已复制到 $PPN_DEST（${SIZE} 字节）"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo " 🔄 切到模式 B（Porcupine）"
echo "═══════════════════════════════════════════════════"

# 4. 用 launchctl kickstart -k 软重启 LaunchAgent
AGENT_LABEL="gui/$(id -u)/com.yuxin.voice.wake"
launchctl kickstart -k "$AGENT_LABEL" 2>/dev/null || {
    echo "⚠️  kickstart 失败，尝试 unload/load"
    launchctl unload ~/Library/LaunchAgents/com.yuxin.voice.wake.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.yuxin.voice.wake.plist
}
sleep 3

echo ""
echo "📊 验证启动状态"
NEW_PID=$(pgrep -f porcupine_listener | head -1)
if [ -n "$NEW_PID" ]; then
    echo "✅ 新进程 PID=$NEW_PID"
    ps -p "$NEW_PID" -o etime,command 2>/dev/null | tail -1
else
    echo "❌ 进程没起来，查看日志:"
    tail -20 ~/hermes/voice/logs/porcupine.out.log
    tail -10 ~/hermes/voice/logs/porcupine.err.log
    exit 1
fi

echo ""
echo "⏳ 3 秒后看启动日志..."
sleep 3
echo ""
echo "--- 启动日志最后 15 行 ---"
tail -15 ~/hermes/voice/logs/porcupine.out.log

echo ""
echo "═══════════════════════════════════════════════════"
echo " 🎯 安装结果"
echo "═══════════════════════════════════════════════════"

if grep -q "模式 B\|porcupine\|Porcupine" ~/hermes/voice/logs/porcupine.out.log; then
    if grep -q "✅ 用自定义唤醒词" ~/hermes/voice/logs/porcupine.out.log; then
        echo "🎉✅ 完整成功！使用了自定义 '嗨玉芬'"
        echo "   立刻可以喊：嗨玉芬"
    elif grep -q "用内置 'jarvis'" ~/hermes/voice/logs/porcupine.out.log; then
        echo "⚠️ 部分成功：License OK 但 .ppn 没装好"
        echo "   现在喊 'jarvis' 能触发（验证 License）"
        echo "   需要补 .ppn 文件"
    else
        echo "🎉 Porcupine 已启动！喊 '嗨玉芬' 试试"
    fi
else
    echo "❌ 没看到 Porcupine 启动，可能 License 错或 pvporcupine 版本问题"
    echo "   最近错误："
    tail -20 ~/hermes/voice/logs/porcupine.err.log
fi

echo ""
echo "📊 健康检查：bash ~/.hermes/scripts/test_wake_e2e.sh"
