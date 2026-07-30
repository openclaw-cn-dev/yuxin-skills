#!/bin/bash
# 玉芬语音交互 - 统一入口
# 华哥在任意目录运行：~/.hermes/scripts/yuxin_voice.sh [模式]
# 模式: phase1 (回车) | phase2 (菜单栏/快捷键) | phase3 (唤醒词) | phase4 (双向对话) | continuous | text | status

set -e

source ~/.hermes/hermes-agent/venv/bin/activate

MODE=${1:-phase1}
TEXT=${2:-}
TURNS=${3:-0}

case "$MODE" in
  phase1|press_enter)
    echo "⏎  Phase 1: 按回车开始录音"
    python3 ~/hermes/voice/yuxin_voice.py
    ;;

  continuous)
    echo "🔁  Phase 1+: 连续对话（自动静音停止）"
    python3 ~/hermes/voice/yuxin_voice.py --continuous
    ;;

  phase4|dialogue)
    echo "🎙️  Phase 4: 双向对话循环（说'拜拜'退出）"
    python3 ~/hermes/voice/yuxin_dialogue.py --max-turns "$TURNS"
    ;;

  phase3|wake)
    echo "🎤  Phase 3: 唤醒词监听（常驻进程）"
    python3 ~/hermes/voice/porcupine_listener.py
    ;;

  text)
    if [ -z "$TEXT" ]; then
      echo "用法：$0 text \"你要说的话\""
      exit 1
    fi
    echo "📝 文字模式（不录音）"
    python3 ~/hermes/voice/yuxin_voice.py --text "$TEXT"
    ;;

  status)
    echo "=== 玉芬语音系统状态 ==="
    echo ""
    echo "--- Phase 1/4 脚本 ---"
    ls -la ~/hermes/voice/*.py 2>/dev/null
    echo ""
    echo "--- Phase 2 Hammerspoon ---"
    if [ -f ~/.hammerspoon/init.lua ]; then
      echo "✅ 配置存在：~/.hammerspoon/init.lua"
    else
      echo "❌ 未配置"
    fi
    echo ""
    echo "--- Phase 3 LaunchAgent ---"
    launchctl list 2>/dev/null | grep -i yuxin.voice && echo "✅ 唤醒词监听运行中" || echo "❌ 未运行"
    echo ""
    echo "--- Porcupine License ---"
    if [ -f ~/hermes/voice/.porcupine_key ]; then
      echo "✅ License 已配置"
    else
      echo "❌ 缺 license → https://console.picovoice.ai/"
    fi
    echo ""
    echo "--- Python 依赖 ---"
    python3 -c "import vosk; print('✅ vosk')" 2>&1 | head -1
    python3 -c "import pyaudio; print('✅ pyaudio')" 2>&1 | head -1
    python3 -c "import webrtcvad; print('✅ webrtcvad')" 2>&1 | head -1
    python3 -c "import pvporcupine; print('✅ pvporcupine')" 2>&1 | head -1
    echo ""
    echo "--- 模型 ---"
    ls ~/hermes/voice/models/ 2>/dev/null
    ;;

  *)
    echo "玉芬语音 - 用法："
    echo "  $0 phase1         # 按回车录音（Phase 1）"
    echo "  $0 continuous     # 连续对话（自动静音停止）"
    echo "  $0 phase4 [轮数]  # 双向对话循环（Phase 4）"
    echo "  $0 wake           # 唤醒词监听（Phase 3）"
    echo "  $0 text \"你好\"    # 跳过录音，文字直接问"
    echo "  $0 status         # 系统状态总览"
    exit 1
    ;;
esac