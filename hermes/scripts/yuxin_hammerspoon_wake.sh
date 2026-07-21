#!/bin/bash
# Hammerspoon 启动的 wake listener
# 必须 source venv，否则 porcupine / vosk / pyaudio 包都找不到

set -e

# 显式进 venv 拿环境
source ~/.hermes/hermes-agent/venv/bin/activate

# 验证关键包
python3 -c "import vosk, sounddevice, pvporcupine, pyaudio" 2>&1 || {
    echo "❌ 缺关键依赖" >&2
    exit 1
}

# 用 unbuffered 让 Hammerspoon 实时拿到 stdout（不然 echo 进 Hammerspoon console）
exec python3 -u ~/hermes/voice/porcupine_listener.py
