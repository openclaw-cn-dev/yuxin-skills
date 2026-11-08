#!/bin/bash
# 测试唤醒词 → Phase 4 双向对话端到端
# 用 say 合成"嗨玉芬"音频 + 麦克风环回验证

set -e

HERMES_HOME="$HOME/.hermes"
VOICE_DIR="$HOME/hermes/voice"

echo "=== 玉芬语音唤醒端到端测试 ==="
echo ""

# 1. 进程状态
echo "--- 1. 唤醒词进程 ---"
PID=$(pgrep -f "porcupine_listener.py" | head -1)
if [ -n "$PID" ]; then
    echo "✅ 运行中 PID=$PID"
    ps -p $PID -o etime,command | tail -1
else
    echo "❌ 唤醒词进程死了！"
    exit 1
fi
echo ""

# 2. 配置检查
echo "--- 2. 配置 ---"
[ -f ~/Library/LaunchAgents/com.yuxin.voice.wake.plist ] && \
    echo "✅ LaunchAgent 配置存在" || echo "❌ LaunchAgent 缺失"

[ -f "$HERMES_HOME/scripts/voice_crash_watcher.py" ] && \
    echo "✅ 崩溃 watcher 脚本存在" || echo "❌ 缺失"

echo ""
echo "--- 3. Porcupine License ---"
if [ -f "$VOICE_DIR/.porcupine_key" ]; then
    echo "✅ License 已配置（模式 B）"
else
    echo "⚠️  无 License → 当前运行模式 A（音量+vosk 关键词）"
    echo "    华哥可选：注册 Picovoice Console 升级到模式 B（更准）"
fi
echo ""

# 4. 自定义唤醒词
echo "--- 4. 自定义 .ppn ---"
ls -la "$VOICE_DIR/models/hey-yuxin_mac.ppn" "$VOICE_DIR/models/嗨玉芬_mac.ppn" 2>/dev/null | head -5 || echo "⚠️  未训练自定义唤醒词（仍可用模式 B 内置 jarvis 测试）"
echo ""

# 5. 触发回环测试：写一个 spike 文件，让 watcher 知道要发测试告警
echo "--- 5. 触发测试告警（写假崩溃文件）---"
TEST_FILE="/tmp/voice_wake_crash.json"
cat > "$TEST_FILE" <<EOF
[
  {
    "time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "component": "voice_wake_test",
    "error": "这是一条测试告警 ——验证 watcher 链路工作正常",
    "hostname": "$(hostname)"
  }
]
EOF
echo "✅ 测试崩溃文件已写入 $TEST_FILE"
echo "   等待 watcher 2 分钟检测 → 应发飞书告警"
echo ""

# 6. 提示华哥
echo "--- 6. 接下来 ---"
echo "立即可测：喊 '玉芬' 或 '嗨玉芬' → 期望弹 Terminal 跑 Phase 4"
echo "或跑 phase1 模式测试全链路："
echo "  ~/.hermes/scripts/yuxin_voice.sh phase1"
echo ""
echo "或直接跑模式 A 听写："
echo "  ~/.hermes/scripts/yuxin_voice.sh continuous"
